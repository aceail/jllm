USER_COLORS = [
    "text-red-600",
    "text-blue-600",
    "text-green-600",
    "text-purple-600",
    "text-orange-600",
]


def get_user_color(username: str) -> str:
    """Return a stable color class for the given username."""
    return USER_COLORS[hash(username) % len(USER_COLORS)]


def dicom_to_png(uploaded_file):
    """Convert an uploaded DICOM file to a PNG SimpleUploadedFile.

    The caller is responsible for ensuring ``pydicom`` and ``Pillow`` are
    installed. If conversion fails, ``None`` is returned.
    """
    try:
        import io
        from django.core.files.uploadedfile import SimpleUploadedFile
        import pydicom
        from PIL import Image

        ds = pydicom.dcmread(uploaded_file)
        pixel_array = ds.pixel_array

        # normalise pixel data to 0-255
        pixel_array = pixel_array.astype('float32')
        pixel_array -= pixel_array.min()
        if pixel_array.max() > 0:
            pixel_array = pixel_array / pixel_array.max() * 255.0
        image = Image.fromarray(pixel_array.astype('uint8'))

        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)
        return SimpleUploadedFile(
            uploaded_file.name.rsplit('.', 1)[0] + '.png',
            buf.read(),
            content_type='image/png'
        )
    except Exception:
        return None
