from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_evaluationanswer_metric_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignedcriterion',
            name='verification_comment',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий верификатора'),
        ),
        migrations.AddField(
            model_name='assignedcriterion',
            name='verification_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Ожидает проверки'),
                    ('changes_requested', 'Запрошены уточнения'),
                    ('verified', 'Подтверждено'),
                ],
                default='pending',
                max_length=32,
                verbose_name='Статус верификации',
            ),
        ),
    ]
