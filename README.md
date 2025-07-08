# jllm

This project uses Django for the web UI. To enable DICOM image conversion you need a few optional dependencies:

```bash
pip install pydicom Pillow pandas openpyxl
```

Without these packages DICOM uploads will be skipped and images will not be saved.

When uploading DICOM files, unsupported formats will simply be ignored and logged to the console so that the rest of the inference can proceed normally.

## Batch inference

You can run multiple inferences from an Excel file using the management command:

```bash
python manage.py batch_infer_excel path/to/data.xlsx --user <username>
```

The spreadsheet must include the following columns: `솔루샨 종류`, `환자 ID`, `성별`, `나이`, `검사 일시`, `AI 분석 결과 (JSON)`, `파일경로 list` (semicolon separated).
