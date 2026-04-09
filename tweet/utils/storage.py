import uuid
import logging
from django.core.exceptions import ValidationError
from django.conf import settings

logger = logging.getLogger(__name__)

ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
BUCKET = 'tweet-photos'


def upload_to_supabase(file, folder: str = '') -> str:
    """
    Upload *file* (Django InMemoryUploadedFile / TemporaryUploadedFile)
    to Supabase Storage and return the public URL.

    Raises ValidationError with a user-friendly message on any failure.
    """
    if not file:
        return ''

    # ── Validation ────────────────────────────────────────────────────────
    if file.size > MAX_SIZE_BYTES:
        raise ValidationError(
            f'The image is too large ({file.size / 1024 / 1024:.1f} MB). '
            f'Maximum allowed size is 5 MB.'
        )

    if file.content_type not in ALLOWED_TYPES:
        raise ValidationError(
            f'Unsupported file type "{file.content_type}". '
            'Please upload a JPEG, PNG, WebP, or GIF image.'
        )

    # ── Upload ────────────────────────────────────────────────────────────
    supabase = getattr(settings, 'SUPABASE', None)
    if supabase is None:
        raise ValidationError(
            'Image upload is currently unavailable (storage not configured). '
            'Please try again later or post without an image.'
        )

    ext = (file.name.rsplit('.', 1)[-1]).lower() if '.' in file.name else 'jpg'
    unique_name = f"{folder}/{uuid.uuid4()}.{ext}".lstrip('/')

    try:
        file.seek(0)
        response = supabase.storage.from_(BUCKET).upload(
            unique_name,
            file.read(),
            {'content-type': file.content_type},
        )
        # The Supabase Python SDK raises an APIError on failure,
        # but older versions return a response with an 'error' key.
        if hasattr(response, 'error') and response.error:
            raise RuntimeError(response.error.get('message', 'Unknown error'))
    except ValidationError:
        raise
    except Exception as exc:
        logger.error('Supabase upload failed: %s', exc)
        raise ValidationError(
            'Image upload failed. This could be a network issue or a server problem. '
            'Please try again. If the problem persists, post without an image.'
        )

    try:
        public_url = supabase.storage.from_(BUCKET).get_public_url(unique_name)
        # Some SDK versions return an object; ensure we get a plain string.
        if hasattr(public_url, 'replace'):
            return public_url
        return str(public_url)
    except Exception as exc:
        logger.error('Could not retrieve public URL after upload: %s', exc)
        raise ValidationError(
            'Image was uploaded but the public link could not be generated. '
            'Please try again.'
        )


def delete_from_supabase(url: str) -> None:
    """
    Delete the file at *url* from Supabase Storage.
    Logs but does NOT raise on failure so that tweet deletion is never blocked.
    """
    if not url:
        return

    supabase = getattr(settings, 'SUPABASE', None)
    if supabase is None:
        return

    try:
        # Extract the path inside the bucket from the public URL.
        # Pattern: /storage/v1/object/public/<bucket>/<path>
        marker = f'/storage/v1/object/public/{BUCKET}/'
        if marker in url:
            path = url.split(marker, 1)[1]
        else:
            # Fallback: take everything after the last occurrence of the bucket name
            path = url.split(f'{BUCKET}/')[-1]

        supabase.storage.from_(BUCKET).remove([path])
    except Exception as exc:
        logger.warning('Failed to delete Supabase object "%s": %s', url, exc)
