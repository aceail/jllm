from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd

from ...models import InferenceResult, InferenceImage, EditHistory
from ...utils import perform_inference

class Command(BaseCommand):
    help = "Run inference sequentially from an Excel file"

    def add_arguments(self, parser):
        parser.add_argument('excel_path', help='Path to Excel file')
        parser.add_argument('--user', required=True, help='Username performing the inference')

    def handle(self, excel_path, user, **options):
        User = get_user_model()
        try:
            user_obj = User.objects.get(username=user)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'User {user} not found'))
            return

        for chunk in pd.read_excel(excel_path, chunksize=1):
            row = chunk.iloc[0]
            solution_name = row.get('솔루샨 종류', 'default')
            patient_id = row.get('환자 ID', '')
            sex = row.get('성별', '')
            age = row.get('나이', '')
            exam_time = row.get('검사 일시', '')
            ai_json = row.get('AI 분석 결과 (JSON)', '{}')
            path_list = str(row.get('파일경로 list', '')).split(';')
            images = []
            for p in path_list:
                p = p.strip()
                if not p:
                    continue
                try:
                    with open(p, 'rb') as f:
                        if p.lower().endswith('.dcm'):
                            img = perform_inference.__globals__['dicom_to_png'](f)
                            if img:
                                images.append(img)
                        else:
                            images.append(SimpleUploadedFile(p.split('/')[-1], f.read()))
                except FileNotFoundError:
                    self.stderr.write(f'Missing file: {p}')
            perform_inference(
                user=user_obj,
                solution_name=solution_name,
                patient_id=patient_id,
                sex=sex,
                age=age,
                exam_time=exam_time,
                ai_json=ai_json,
                images=images,
            )
            self.stdout.write(self.style.SUCCESS(f'Processed {patient_id}'))

