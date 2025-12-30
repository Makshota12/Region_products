from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import EvaluationSession, Criterion, AssignedCriterion, Profile, Role
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


# ОТКЛЮЧЕН: Критерии теперь создаются вручную в ViewSet
# @receiver(post_save, sender=EvaluationSession)
# def create_assigned_criteria(sender, instance, created, **kwargs):
#     pass


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Автоматически создаем профиль для нового пользователя
    """
    if created:
        # Получаем роль "Наблюдатель" по умолчанию
        observer_role, _ = Role.objects.get_or_create(name='observer')
        
        Profile.objects.get_or_create(
            user=instance,
            defaults={'role': observer_role}
        )
        logger.info(f"Создан профиль для пользователя {instance.username}")

