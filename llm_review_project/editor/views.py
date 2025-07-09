import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
import ast
from .models import InferenceResult, EditHistory
from .utils import (
    get_user_color,
    SOLUTIONS_DATA,
    PROMPT_CONFIG,
    perform_inference,
    clean_json_keys,
    dicom_to_png,
)


@login_required
def main_editor_view(request, result_id=None):
    all_results = InferenceResult.objects.order_by('-created_at')
    current_result = None
    if result_id:
        current_result = get_object_or_404(InferenceResult, pk=result_id)

    for res in all_results:
        if res.last_modified_by:
            res.user_color = get_user_color(res.last_modified_by.username)
        else:
            res.user_color = ''
        res.editors = [
            {'name': name, 'color': get_user_color(name)}
            for name in res.get_editors()
        ]

    if current_result:
        if current_result.last_modified_by:
            current_result.user_color = get_user_color(current_result.last_modified_by.username)
        current_result.editors = [
            {'name': name, 'color': get_user_color(name)}
            for name in current_result.get_editors()
        ]
    
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

        ai_json_input = request.POST.get('ai_json_input', '{}')
        prompt_text = request.POST.get('prompt', '')

        result = perform_inference(
            user=request.user,
            solution_name=solution_name,
            patient_id=request.POST.get('patient_id', ''),
            sex=request.POST.get('sex', ''),
            age=request.POST.get('age', ''),
            exam_time=request.POST.get('exam_time', ''),
            ai_json=ai_json_input if solution_name in SOLUTIONS_DATA else prompt_text,
            images=request.FILES.getlist('images'),
        )

        if result:
            return redirect('editor:editor_with_id', result_id=result.id)
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
                "Lesion_Location_Vessel_territory": request.POST.get("Lesion_Location_Vessel_territory"),
                "Lesion_Location_Anatomic_location": request.POST.get("Lesion_Location_Anatomic_location"),
                "Lesion_Location_Direction": request.POST.get("Lesion_Location_Direction"),
                "정량적_결과": request.POST.get("정량적_결과"),
                "종합적_결과": request.POST.get("종합적_결과")
            }
            result.parsed_result = clean_json_keys(updated_data)
            result.edited_text = json.dumps(updated_data, ensure_ascii=False, indent=2)
            result.patient_id = request.POST.get("환자ID", result.patient_id)
            result.last_modified_by = request.user
            result.save()

            EditHistory.objects.create(
                result=result,
                editor=request.user,
                edited_data=result.parsed_result,
            )
        except (ValueError, TypeError) as e:
            print(f"Error reconstructing JSON: {e}")

    return redirect('editor:editor_with_id', result_id=result_id)

@login_required
def delete_result(request, result_id):
    result = get_object_or_404(InferenceResult, pk=result_id)
    if request.method == 'POST':
        result.delete()
    return redirect('editor:main_editor')


@login_required
def delete_selected(request):
    if request.method == 'POST':
        ids = request.POST.getlist('selected_ids')
        if ids:
            InferenceResult.objects.filter(id__in=ids).delete()
    return redirect('editor:main_editor')


@login_required
def upload_excel(request):
    """Handle Excel uploads for batch inference sequentially."""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        for _, row in pd.read_excel(excel_file).iterrows():
            solution_name = row.get('솔루션 종류', 'default')
            patient_id = row.get('환자 ID', '')
            sex = row.get('성별', '')
            age = row.get('나이', '')
            exam_time = row.get('검사 일시', '')
            ai_json = row.get('AI 분석 결과', '{}')
            path_list = ast.literal_eval(row.get('파일경로', ''))

            images = []
            for p in path_list:
                p = p.strip()
                if not p:
                    continue
                try:
                    with open(p, 'rb') as f:
                        if p.lower().endswith('.dcm'):
                            img = dicom_to_png(f)
                            if img:
                                images.append(img)
                        else:
                            images.append(SimpleUploadedFile(p.split('/')[-1], f.read()))
                except FileNotFoundError:
                    print(f'Missing file: {p}')

            perform_inference(
                user=request.user,
                solution_name=solution_name,
                patient_id=patient_id,
                sex=sex,
                age=age,
                exam_time=exam_time,
                ai_json=ai_json,
                images=images,
            )

        return redirect('editor:main_editor')

    return redirect('editor:main_editor')
