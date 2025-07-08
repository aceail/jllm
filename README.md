# jllm

This project uses Django for the web UI. To enable DICOM image conversion you need a few optional dependencies:

```bash
pip install pydicom Pillow
```

Without these packages DICOM uploads will be skipped and images will not be saved.

When uploading DICOM files, unsupported formats will simply be ignored and logged to the console so that the rest of the inference can proceed normally.
