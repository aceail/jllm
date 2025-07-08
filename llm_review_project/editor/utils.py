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

    """Convert an uploaded DICOM file to a PNG ``SimpleUploadedFile``.

    ``pydicom`` and ``Pillow`` must be installed. If they are missing or an
    error occurs during conversion, ``None`` is returned so the caller can
    gracefully skip the file.
    """
    try:
        import io
        from django.core.files.uploadedfile import SimpleUploadedFile
        import pydicom
        from pydicom.pixel_data_handlers.util import apply_voi_lut
        from PIL import Image

        ds = pydicom.dcmread(uploaded_file, force=True)

        if "PixelData" not in ds:
            raise ValueError("No pixel data found")

        pixel_array = ds.pixel_array
        if pixel_array.ndim > 2:
            pixel_array = pixel_array[0]

        # apply windowing if available
        try:
            pixel_array = apply_voi_lut(pixel_array, ds)
        except Exception:
            pass

        pixel_array = pixel_array.astype("float32")
        pixel_array -= pixel_array.min()
        if pixel_array.max() > 0:
            pixel_array = pixel_array / pixel_array.max() * 255.0

        if getattr(ds, "PhotometricInterpretation", "MONOCHROME2") == "MONOCHROME1":
            pixel_array = 255 - pixel_array

        image = Image.fromarray(pixel_array.astype("uint8"))

        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)
        return SimpleUploadedFile(
            uploaded_file.name.rsplit('.', 1)[0] + '.png',
            buf.read(),
            content_type='image/png'
        )
    except Exception as exc:
        # If required libraries are missing or any conversion error occurs,
        # log the issue and return ``None`` so the caller can ignore this file.
        print(f"DICOM conversion failed: {exc}")
        return None
