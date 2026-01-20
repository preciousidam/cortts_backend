from io import BytesIO
from typing import Optional
import httpx

from openai import OpenAI

from app.core.config import settings
from app.models.document import MediaFile

_http: Optional[httpx.Client] = None

try:
    from pypdf import PdfReader  # lightweight PDF text extractor
except Exception:
    PdfReader = None

_client: Optional[OpenAI] = None


def _get_http() -> httpx.Client:
    """
    Lazily create a shared httpx client with sensible timeouts.
    """
    global _http
    if _http is None:
        _http = httpx.Client(timeout=httpx.Timeout(10.0, connect=5.0))
    return _http


def _get_client() -> Optional[OpenAI]:
    """
    Lazily create an OpenAI client if an API key is present.
    """
    global _client
    if not settings.OPENAI_API_KEY:
        return None
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def _get_text_preview(media_file: MediaFile, max_chars: int = 2000) -> str | None:
    """
    Best-effort fetch of a text preview when the file is a text asset.
    """
    file_type = (media_file.file_type or "").lower()
    if not media_file.file_path or not file_type.startswith("text/"):
        return None
    try:
        response = _get_http().get(media_file.file_path)
        response.raise_for_status()
        text = response.text.strip()
        return text[:max_chars] if text else None
    except Exception as e:
        print(f"_get_text_preview error: {e}")
        return None


def _get_pdf_preview(media_file: MediaFile, max_chars: int = 2000, max_bytes: int = 1_000_000) -> str | None:
    """
    Fetch the first chunk of a PDF and extract a short text preview.
    """
    is_pdf = (
        ("pdf" in (media_file.file_type or "").lower())
        or ((media_file.file_name or "").lower().endswith(".pdf"))
    )
    if not media_file.file_path or not is_pdf or not PdfReader:
        return None

    try:
        with _get_http().stream("GET", media_file.file_path) as response:
            response.raise_for_status()
            content = bytearray()
            for chunk in response.iter_bytes():
                content.extend(chunk)
                if len(content) >= max_bytes:
                    break

        reader = PdfReader(BytesIO(bytes(content)))
        extracted: list[str] = []
        for page in reader.pages[:3]:  # sample a few pages
            text = page.extract_text() or ""
            extracted.append(text)
            if sum(len(t) for t in extracted) >= max_chars:
                break
        preview = "\n".join(extracted).strip()
        return preview[:max_chars] if preview else None
    except Exception as e:
        print(f"_get_pdf_preview error: {e}")
        return None


def generate_media_description(media_file: MediaFile | None, kind: str) -> str | None:
    """
    Use OpenAI to generate a short description for a media file.
    """
    client = _get_client()
    if not client or not media_file:
        return None

    preview = _get_text_preview(media_file) or _get_pdf_preview(media_file)
    summary_request = (
        f"Summarize this {kind} file in one or two sentences for a dashboard.\n"
        f"File name: {media_file.file_name}\n"
        f"File type: {media_file.file_type}\n"
        f"Approx size (bytes): {media_file.file_size}\n"
    )
    if preview:
        summary_request += f"\nPreview:\n{preview}"
    else:
        summary_request += "\nNo preview content available; infer from the file metadata."

    try:
        response = client.responses.create(
            model=(settings.OPENAI_MODEL or "gpt-4o-mini"),
            input=[
                {"role": "system", "content": "You write concise, neutral document descriptions."},
                {"role": "user", "content": summary_request},
            ],
            max_output_tokens=100,
            temperature=0.4,
        )
        return _extract_response_text(response)
    except Exception as e:
        print(f"generate_media_description error: {e}")
        return None


def _extract_response_text(response: object) -> str | None:
    """
    Extract plain text from a Responses API result, handling both typed objects and dicts.
    """

    try:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()
    except Exception:
        pass

    if isinstance(response, dict):
        output_text = response.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

    try:
        outputs = getattr(response, "output", None) or []
    except Exception:
        outputs = []

    texts: list[str] = []
    for item in outputs:
        content = getattr(item, "content", None) or getattr(item, "get", lambda *_: None)("content") or []
        for block in content:
            text_part = getattr(block, "text", None)
            if isinstance(text_part, str):
                candidate = text_part
            elif text_part is not None:
                candidate = getattr(text_part, "value", None) or getattr(text_part, "text", None)
            elif isinstance(block, dict):
                candidate = block.get("text") or (block.get("text", {}) or {}).get("value")
            else:
                candidate = None
            if candidate:
                texts.append(str(candidate).strip())

    return " ".join(t for t in texts if t).strip() if texts else None
