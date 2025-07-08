from django.contrib import admin
from .models import InferenceResult, InferenceImage

# Register your models here.
admin.site.register(InferenceResult)
admin.site.register(InferenceImage)