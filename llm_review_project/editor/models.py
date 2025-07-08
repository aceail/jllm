from django.db import models
from django.utils import timezone

class InferenceResult(models.Model):
    prompt = models.TextField("프롬프트 요약")
    original_text = models.TextField("원본 추론 결과 (Raw Text)")
    edited_text = models.TextField("수정된 텍스트 (Raw Text)", blank=True)
    # 파싱된 JSON 결과를 저장할 필드 추가
    parsed_result = models.JSONField("파싱된/수정된 결과", null=True, blank=True)
    created_at = models.DateTimeField("생성 시각", default=timezone.now)

    def __str__(self):
        return f"Result for '{self.prompt[:30]}...'"

    def get_display_text(self):
        return self.edited_text if self.edited_text else self.original_text

# 이미지를 저장할 별도의 모델 생성
class InferenceImage(models.Model):
    inference_result = models.ForeignKey(InferenceResult, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='inference_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for result {self.inference_result.id}"
