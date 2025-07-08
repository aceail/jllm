from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0002_inferenceresult_parsed_result_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inferenceresult',
            name='patient_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='환자ID'),
        ),
        migrations.AddField(
            model_name='inferenceresult',
            name='solution_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='솔루션 이름'),
        ),
        migrations.AddField(
            model_name='inferenceresult',
            name='last_modified_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='modified_results',
                to=settings.AUTH_USER_MODEL,
                verbose_name='마지막 수정자',
            ),
        ),
    ]
