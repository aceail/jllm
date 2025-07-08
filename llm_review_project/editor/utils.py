import json
import requests

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


# ---------------------------------------------------------------------------
# Prompt configuration and helper functions shared by views and commands
# ---------------------------------------------------------------------------

VLLM_API_URL = "http://localhost:8001/v1/completions"

SOLUTIONS_DATA = {
    "JLK-CMB": {"base": "GRE", "info": "열공 뇌경색 위치 및 부피 정량 분석 정보"},
    "JLK-CTI": {"base": "NCCT", "info": "뇌경색 유무 및 의심 영역 위치/부피 분석 정보"},
    "JLK-CTL": {"base": "NCCT", "info": "대혈관폐색 (Large vessel occlusion, LVO) 위험 예측"},
    "JLK-CTP": {"base": "CTP", "info": "Infarct core 및 Penumbra 부피 정보"},
    "JLK-DWI": {"base": "DWI + ADC", "info": "뇌경색 병변 검출, 위치/크기/패턴 분석, 뇌경색 원인별 확률 제공"},
    "JLK-ICH": {"base": "NCCT", "info": "뇌출혈 유무 및 뇌출혈 영역 검출, 위치 및 크기 정량 분석"},
    "JLK-LAC": {"base": "FLAIR", "info": "열공 뇌경색 위치 및 부피 정량 분석 정보"},
    "JLK-LVO": {"base": "CTA", "info": "대혈관폐색 Large vessel occlusion, LVO) 의심 영역 검출, 중대뇌동맥 양측 혈관 밀도 비교 정보"},
    "JLK-PWI": {"base": "DWI + PWI", "info": "Infarct core 및 Penumbra 부피 정보"},
    "JLK-UIA": {"base": "MRA", "info": "비파열 뇌동맥류 검출, 크기 및 부피 등 형태 분석 정보"},
    "JLK-WMH": {"base": "FLAIR", "info": "백질 고강도 병변 검출 및 정량 분석 정보"},
    "JLK-WMHC": {"base": "NCCT", "info": "대뇌 백질변성 영역 시각화 및 정량 분석 정보"},
}

PROMPT_CONFIG = {
    "default": {
        "system": "You are a helpful assistant.",
        "user_template": None,
    },
    "medical": {
        "system": """**Developer: [역할 정의]**

당신은 급성기 뇌졸중 환자를 담당하는 **신경영상의학 전문의**입니다. 당신의 역할은 단순 영상 묘사를 넘어, AI가 분석한 **다양한 영상 모달리티(NCCT, CTA, CTP, MRA, DWI, 등)의 정량적/정성적 데이터**를 비판적으로 검토하고, 모든 소견을 종합하여 임상적으로 가장 유의미한 진단을 내리는 것입니다. 당신의 판독문은 응급실 의사나 신경과 의사가 환자의 다음 치료 단계를 즉시 결정하는 데 사용하는 **핵심적인 컨설팅 자료**가 됩니다.

**당신의 임무는 다음과 같습니다:**
1.  **종합적 해석 (Comprehensive Interpretation):** AI가 제시한 개별 데이터(예: **Infarct core/Penumbra 부피, ASPECTS 점수, 출력량, 혈관 폐색 위치 등**)를 나열하는 데 그치지 말고, 이들을 **유기적으로 연결하여 가장 가능성 높은 단일 진단(Single most-likely diagnosis)**을 제시하세요.
2.  **상세한 영상 소견 기술 (Detailed Findings Description):** 병변의 정확한 해부학적 위치, 크기, 분포 양상을 명시하세요.
3.  **비판적 사고 및 AI 한계점 분석 (Critical Thinking & AI Limitation Analysis):** AI 결과의 신뢰도와 임상적 적용의 한계를 지적하세요.
4.  **임상적 맥락 부여 및 실행 가능한 권고 (Clinical Context & Actionable Recommendations):** 최종 결론은 환자의 치료 방침 결정에 직접적인 도움을 주어야 합니다.

## Output Format
```json
{ai_json}
```
첨부된 이미지 {image_count}장를 함께 참고하여 판독 소견을 작성해 주십시오.""",
        "user_template": """[{solution_name} ({solution_base})]
{solution_info}

환자ID: {patient_id}
성별: {sex}
나이: {age}
검사 일시: {exam_time}

AI 분석 결과:
{ai_json}
""",
    },
}


def clean_json_keys(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            new_key = k.replace(' ', '_').replace('(', '').replace(')', '')
            new_obj[new_key] = clean_json_keys(v)
        return new_obj
    elif isinstance(obj, list):
        return [clean_json_keys(elem) for elem in obj]
    else:
        return obj


def parse_json_from_string(text):
    try:
        if '```json' in text:
            json_str = text.split('```json')[1].split('```')[0].strip()
        else:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                return None
            json_str = text[json_start:json_end]

        data = json.loads(json_str)
        cleaned_data = clean_json_keys(data)
        return cleaned_data
    except (json.JSONDecodeError, IndexError, AttributeError):
        return None


def perform_inference(user, solution_name, patient_id='', sex='', age='', exam_time='', ai_json='{}', images=None):
    """Run inference and store the result sequentially."""
    if images is None:
        images = []

    from django.core.files.uploadedfile import SimpleUploadedFile
    from .models import InferenceResult, InferenceImage, EditHistory

    converted_files = []
    for f in images:
        if f.name.lower().endswith('.dcm'):
            png = dicom_to_png(f)
            if png:
                converted_files.append(png)
        else:
            converted_files.append(f)

    config_key = 'medical' if solution_name in SOLUTIONS_DATA else 'default'
    config = PROMPT_CONFIG[config_key]
    system_prompt = config['system']
    user_prompt_template = config['user_template']

    if config_key == 'medical' and user_prompt_template:
        solution_data = SOLUTIONS_DATA.get(solution_name, {})
        solution_base = solution_data.get('base', '')
        solution_info = solution_data.get('info', '')

        user_input_data = user_prompt_template.format(
            solution_name=solution_name,
            solution_base=solution_base,
            solution_info=solution_info,
            patient_id=patient_id,
            sex=sex,
            age=age,
            exam_time=exam_time,
            ai_json=ai_json,
            image_count=len(converted_files),
        )
        db_prompt = ai_json or '상세 입력'
    else:
        user_input_data = ai_json
        db_prompt = user_input_data

    if not user_input_data:
        return None

    final_prompt = f"{system_prompt}\n\n[사용자 요청]:\n{user_input_data}\n\n[응답]:\n"
    payload = {
        "model": "/home/yjpark/data_72/model/gemma-merged-model",
        "prompt": final_prompt,
        "max_tokens": 2048,
        "temperature": 0.7,
        "stop": ["<end_of_turn>", "[사용자 요청]"],
        "echo": False,
    }
    response = requests.post(VLLM_API_URL, json=payload)
    response.raise_for_status()
    generated_text = response.json()['choices'][0]['text'].strip()

    parsed_data = parse_json_from_string(generated_text)

    new_result = InferenceResult.objects.create(
        prompt=db_prompt,
        original_text=generated_text,
        edited_text=generated_text,
        parsed_result=parsed_data,
        patient_id=patient_id,
        solution_name=solution_name,
        last_modified_by=user,
    )

    EditHistory.objects.create(
        result=new_result,
        editor=user,
        edited_data=parsed_data,
    )

    for uploaded_file in converted_files:
        try:
            InferenceImage.objects.create(
                inference_result=new_result,
                image=uploaded_file,
            )
        except Exception as img_exc:
            print(f"Image save failed: {img_exc}")

    return new_result
