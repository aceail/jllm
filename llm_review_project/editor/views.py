import requests
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import InferenceResult, InferenceImage

USER_COLORS = [
    "text-red-600",
    "text-blue-600",
    "text-green-600",
    "text-purple-600",
    "text-orange-600",
]

def get_user_color(username: str) -> str:
    return USER_COLORS[hash(username) % len(USER_COLORS)]



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
        "user_template": None # 일반 입력은 템플릿을 사용하지 않음
    },
    "medical": {
        "system": """**Developer: [역할 정의]**

당신은 급성기 뇌졸중 환자를 담당하는 **신경영상의학 전문의**입니다. 당신의 역할은 단순한 영상 묘사를 넘어, AI가 분석한 **다양한 영상 모달리티(NCCT, CTA, CTP, MRA, DWI, 등)의 정량적/정성적 데이터**를 비판적으로 검토하고, 모든 소견을 종합하여 임상적으로 가장 유의미한 진단을 내리는 것입니다. 당신의 판독문은 응급실 의사나 신경과 의사가 환자의 다음 치료 단계를 즉시 결정하는 데 사용하는 **핵심적인 컨설팅 자료**가 됩니다.

**당신의 임무는 다음과 같습니다:**

1.  **종합적 해석 (Comprehensive Interpretation):**
    *   AI가 제시한 개별 데이터(예: **Infarct core/Penumbra 부피, ASPECTS 점수, 출력량, 혈관 폐색 위치 등**)를 나열하는 데 그치지 말고, 이들을 **유기적으로 연결하여 가장 가능성 높은 단일 진단(Single most-likely diagnosis)**을 제시하세요.
    *   영상 소견들을 인과관계에 따라 설명하며, 가장 설득력 있는 **병태생리학적 시나리오**를 구축해야 합니다. (예: 'CTA에서 확인된 M1 폐색'과 'CTP의 큰 Penumbra'를 근거로, '기계적 혈전제거술의 잠재적 이득이 큰 대뇌혈관 폐색성 뇌경색' 등으로 진단)
    *   **영상 결과 해석(Interpretation of Image Results):** 각 영상의 결과에 대한 명확한 해석을 추가하세요. 예를 들어, 혈관 폐색의 위치나 정도 등에 대해 이미지 기반 세부적 해석이 필요합니다.

2.  **상세한 영상 소견 기술 (Detailed Findings Description):**
    *   병변의 정확한 해부학적 위치(예: Lentiform nucleus, Insular ribbon), 크기, 분포 양상, 그리고 주변 구조물과의 관계를 정확하게 묘사하세요. 각 병변의 위치는 구조적인 혈관 구역 및 해부학적 영역을 모두 포함하여 명시하세요.
    *   AI가 분석한 영역과 수치(예: Core/Penumbra 부피, 혈관 협착 및 폐색 지점)를 근거로 하되, 단순 번역이 아닌 **전문의의 언어로 재구성하여 서술**해야 합니다.

3.  **비판적 사고 및 AI 한계점 분석 (Critical Thinking & AI Limitation Analysis):**
    *   **AI 분석 결과를 맹신하지 마세요.** AI 결과에서 나타날 수 있는 잠재적 오류나 비일관성(예: **CTP 맵의 노이즈, penumbra 과대평가, 작은 출력 누락, 혈관 협착과 폐색의 오분류**)을 날카롭게 지적하고, 그에 대한 전문적인 교정 의견을 제시하세요.
    *   AI 결과의 신뢰도와 임상적 적용의 한계를 명확히 언급하여, 임상의가 정보를 받아들이는 데 주의할 점을 알려주세요.

4.  **임상적 맥락 부여 및 실행 가능한 권고 (Clinical Context & Actionable Recommendations):**
    *   최종 결론은 환자의 **치료 방침 결정에 직접적인 도움**을 주어야 합니다.
    *   진단적 불확실성을 해소하거나 치료 계획(예: 기계적 혈전제거술, **정맥내 혈전용해술(IV tPA)**)의 적용증을 평가하기 위해 필요한 **다음 단계(Next step)**를 구체적이고 명확하게 권고하세요. (예: 'CTP 결과상 유리한 mismatch를 보이므로 즉시 기계적 혈전제거술을 위한 인터벤션팀 호출을 권고함')
    *   당신의 판독이 환자의 예후를 결정한다는 책임감을 가지고 작성해야 합니다.

## Output Format

출력은 반드시 아래와 같은 JSON 형식으로 하며, 모든 필드는 누락 없이 채워야 합니다.
{
  "환자ID": "문자열",
  "성별": "문자열",
  "나이": 숫자,
  "영상 종류": "문자열", // 예: "NCCT, CTA, CTP", "DWI" 등
  "검사 일시": "문자열", // ISO 8601 포맷 (예: "2024-06-16T14:23:00")
  "JLK 결과": {
    "Lesion Location (Vessel territory)": "문자열", // 예: "Right MCA territory (superior division), left PCA territory 등" - 방향 포함
    "Lesion Location (Anatomic location)": "문자열", // 예: "Right insular cortex and adjacent parietal lobe"
    "Lesion Location (Direction)": "문자열", // 예: "Right, superior, medial, bilateral 등" - 공간적 방향
    "정량적 결과": "문자열", // 반드시 {병변 위치(혈관구역, 해부학구역, 방향), 병변 크기(정량값), 양측성, 분포 양상} 모두 포함하여, 전문의 시각에서 상세 기술
  },
  "종합적 결과": "문자열" // 임상·병태생리학 해석, AI 비판, 최종 권고 포함
}

※ **추가 주의사항:**
-   해부학적 용어 또는 임상 용어는 **영어 표준 표기**로 작성하세요.
-   모든 필드는 반드시 채워야 하며, 누락이나 자료형 오류 발생 시 "알 수 없음" 또는 관련 오류 메시지를 명시하고 JSON 전체의 형태는 반드시 유지해야 합니다.
-   검사 일시는 반드시 ISO 8601 포맷이어야 합니다 (예: "2024-06-16T14:23:00").
-   입력값이 불충분하거나 오류 발견 시, 예를 들어 `{ "종합적 결과": "입력된 AI 분석 데이터가 불충분하여 정확한 판독이 어렵습니다." }` 형식으로 출력할 수 있습니다.
-   각 필드/서술의 순서는 위에 정의된 순서로 고정하여 출력하세요.""",
        "user_template": """다음으로 제공되는 인공지능 판독 결과는 {solution_name} 솔루션을 통해 생성되었으며, 이는 {solution_base} 기반 {solution_info} 정보에 대한 병변 검출, 위치, 크기, 영상 특성 및 예측 병태생리 정보를 포함합니다.
환자 ID : {patient_id}
성별 : {sex}
나이 : {age}
검사 일시 : {exam_time}
아래는 AI 분석 결과입니다:
```json
{ai_json}
```
첨부된 이미지 {image_count}장를 함께 참고하여 판독 소견을 작성해 주십시오."""
    }
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

@login_required
def main_editor_view(request, result_id=None):
    all_results = InferenceResult.objects.order_by('-created_at')
    current_result = None
    if result_id:
        current_result = get_object_or_404(InferenceResult, pk=result_id)
    
    context = {
        'all_results': all_results,
        'current_result': current_result,
        'solutions_data': SOLUTIONS_DATA,
        'user_color': get_user_color(request.user.username),
    }
    return render(request, 'editor/main_editor.html', context)

@login_required
def create_inference(request):
    if request.method == 'POST':
        solution_name = request.POST.get('solution', 'default')
        
        config_key = "medical" if solution_name in SOLUTIONS_DATA else "default"
        config = PROMPT_CONFIG[config_key]
        
        system_prompt = config["system"]
        user_prompt_template = config["user_template"]
        
        user_input_data = ""
        db_prompt = ""

        if config_key == 'medical' and user_prompt_template:
            solution_data = SOLUTIONS_DATA.get(solution_name, {})
            solution_base = solution_data.get('base', '')
            solution_info = solution_data.get('info', '')

            user_input_data = user_prompt_template.format(
                solution_name=solution_name,
                solution_base=solution_base,
                solution_info=solution_info,
                patient_id=request.POST.get('patient_id', ''),
                sex=request.POST.get('sex', ''),
                age=request.POST.get('age', ''),
                exam_time=request.POST.get('exam_time', ''),
                ai_json=request.POST.get('ai_json_input', '{}'),
                image_count=len(request.FILES.getlist('images'))
            )
            db_prompt = request.POST.get('ai_json_input', '상세 입력')
        else:
            user_input_data = request.POST.get('prompt')
            db_prompt = user_input_data

        if not user_input_data:
            return redirect('editor:main_editor')

        final_prompt = f"{system_prompt}\n\n[사용자 요청]:\n{user_input_data}\n\n[응답]:\n"

        try:
            payload = {
                "model": "/home/yjpark/data_72/model/gemma-merged-model",
                "prompt": final_prompt,
                "max_tokens": 2048,
                "temperature": 0.7,
                "stop": ["<end_of_turn>", "[사용자 요청]"],
                "echo": False
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
                patient_id=request.POST.get('patient_id', ''),
                solution_name=solution_name,
                last_modified_by=request.user,
            )

            for uploaded_file in request.FILES.getlist('images'):
                InferenceImage.objects.create(inference_result=new_result, image=uploaded_file)

            return redirect('editor:editor_with_id', result_id=new_result.id)
        except Exception as e:
            print(f"An error occurred: {e}")
            return redirect('editor:main_editor')
    return redirect('editor:main_editor')

@login_required
def save_edit(request, result_id):
    result = get_object_or_404(InferenceResult, pk=result_id)
    if request.method == 'POST':
        try:
            updated_data = {
                "환자ID": request.POST.get("환자ID"),
                "성별": request.POST.get("성별"),
                "나이": int(request.POST.get("나이")),
                "영상_종류": request.POST.get("영상_종류"),
                "검사_일시": request.POST.get("검사_일시"),
                "JLK_결과": {
                    "Lesion_Location_Vessel_territory": request.POST.get("JLK_결과__Lesion_Location_Vessel_territory"),
                    "Lesion_Location_Anatomic_location": request.POST.get("JLK_결과__Lesion_Location_Anatomic_location"),
                    "Lesion_Location_Direction": request.POST.get("JLK_결과__Lesion_Location_Direction"),
                    "정량적_결과": request.POST.get("JLK_결과__정량적_결과"),
                },
                "종합적_결과": request.POST.get("종합적_결과")
            }
            result.parsed_result = clean_json_keys(updated_data)
            result.edited_text = json.dumps(updated_data, ensure_ascii=False, indent=2)
            result.patient_id = request.POST.get("환자ID", result.patient_id)
            result.last_modified_by = request.user
            result.save()
        except (ValueError, TypeError) as e:
            print(f"Error reconstructing JSON: {e}")

    return redirect('editor:editor_with_id', result_id=result_id)

@login_required
def delete_result(request, result_id):
    result = get_object_or_404(InferenceResult, pk=result_id)
    if request.method == 'POST':
        result.delete()
    return redirect('editor:main_editor')
