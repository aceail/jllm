from django.db import models
from django.utils import timezone
from django.conf import settings

class InferenceResult(models.Model):
    prompt = models.TextField("프롬프트 요약")
    original_text = models.TextField("원본 추론 결과 (Raw Text)")
    edited_text = models.TextField("수정된 텍스트 (Raw Text)", blank=True)
    # 파싱된 JSON 결과를 저장할 필드 추가
    parsed_result = models.JSONField("파싱된/수정된 결과", null=True, blank=True)
    patient_id = models.CharField("환자ID", max_length=100, blank=True)
    solution_name = models.CharField("솔루션 이름", max_length=100, blank=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="마지막 수정자",
        related_name="modified_results",
    )
    created_at = models.DateTimeField("생성 시각", default=timezone.now)

    def __str__(self):
        return f"Result for '{self.prompt[:30]}...'"

    def get_display_text(self):
        return self.edited_text if self.edited_text else self.original_text

    def get_editors(self):
        """Return a list of usernames who edited this result."""
        names = list(self.history.exclude(editor=None).values_list('editor__username', flat=True).distinct())
        if self.last_modified_by and self.last_modified_by.username not in names:
            names.append(self.last_modified_by.username)
        return names

# 이미지를 저장할 별도의 모델 생성
class InferenceImage(models.Model):
    inference_result = models.ForeignKey(InferenceResult, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='inference_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for result {self.inference_result.id}"


class EditHistory(models.Model):
    """Track changes to an InferenceResult so each user's edits can be highlighted."""

    result = models.ForeignKey(InferenceResult, related_name='history', on_delete=models.CASCADE)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    edited_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"History for {self.result_id} by {self.editor}"
