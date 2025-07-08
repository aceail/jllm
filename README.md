# jllm

This project uses Django for the web UI. To enable DICOM image conversion you need a few optional dependencies:

```bash
pip install pydicom Pillow
```

Without these packages DICOM uploads will be skipped.
