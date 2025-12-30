from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
# Сигналы в signals.py, НЕ ИМПОРТИРОВАТЬ ЗДЕСЬ!

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    department_owner = models.CharField(max_length=255, verbose_name="Ответственное ведомство/владелец")
    product_link = models.URLField(verbose_name="Ссылка на продукт", blank=True, null=True)
    launch_date = models.DateField(verbose_name="Дата запуска", blank=True, null=True)
    is_archived = models.BooleanField(default=False, verbose_name="В архиве")

    class Meta:
        verbose_name = "Цифровой продукт"
        verbose_name_plural = "Цифровые продукты"
        ordering = ['name']

    def __str__(self):
        return self.name

class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название домена")
    description = models.TextField(verbose_name="Описание домена", blank=True, null=True)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100.00)],
        verbose_name="Вес в индексе зрелости (%)", default=100.00
    )

    class Meta:
        verbose_name = "Домен оценки"
        verbose_name_plural = "Домены оценки"
        ordering = ['name']

    def __str__(self):
        return self.name

class Criterion(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='criteria', verbose_name="Домен")
    name = models.CharField(max_length=255, verbose_name="Название критерия")
    description = models.TextField(verbose_name="Описание критерия", blank=True, null=True)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100.00)],
        verbose_name="Вес в домене (%)"
    )

    class Meta:
        verbose_name = "Критерий оценки"
        verbose_name_plural = "Критерии оценки"
        unique_together = ('domain', 'name')
        ordering = ['domain', 'name']

    def __str__(self):
        return f"{self.domain.name} - {self.name}"

class RatingScale(models.Model):
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE, related_name='rating_scales', verbose_name="Критерий")
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Балл"
    )
    description = models.TextField(verbose_name="Дескриптор балла")

    class Meta:
        verbose_name = "Шкала оценки"
        verbose_name_plural = "Шкалы оценки"
        unique_together = ('criterion', 'score')
        ordering = ['criterion', 'score']

    def __str__(self):
        return f"{self.criterion.name}: {self.score} - {self.description[:50]}..."

# New models for evaluation sessions
class EvaluationSession(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='evaluations', verbose_name="Продукт")
    start_date = models.DateField(auto_now_add=True, verbose_name="Дата начала")
    end_date = models.DateField(blank=True, null=True, verbose_name="Дата окончания")
    status = models.CharField(max_length=50, default='pending', verbose_name="Статус",
                              choices=[('pending', 'В ожидании'), ('in_progress', 'В процессе'),
                                       ('completed', 'Завершено'), ('archived', 'В архиве')])
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_evaluations', verbose_name="Создана")

    class Meta:
        verbose_name = "Оценочная сессия"
        verbose_name_plural = "Оценочные сессии"
        ordering = ['start_date']

    def __str__(self):
        return f"Оценка продукта {self.product.name} от {self.start_date}"

    def get_criterion_score(self, assigned_criterion_id):
        try:
            assigned_criterion = self.assigned_criteria.get(id=assigned_criterion_id)
            return assigned_criterion.answer.score_value if hasattr(assigned_criterion, 'answer') else None
        except AssignedCriterion.DoesNotExist:
            return None

    def get_domain_score(self, domain_id):
        """Расчет балла по домену с учетом весов критериев"""
        domain_score = 0
        total_weight = 0
        
        # Получаем критерии домена с ответами
        criteria_in_domain = self.assigned_criteria.filter(
            criterion__domain__id=domain_id
        ).select_related('criterion', 'answer')
        
        for ac in criteria_in_domain:
            try:
                # Проверяем наличие ответа через OneToOne связь
                answer = getattr(ac, 'answer', None)
                if answer and answer.score_value is not None:
                    weight = float(ac.criterion.weight) if ac.criterion.weight else 1.0
                    score = float(answer.score_value)
                    domain_score += (score * weight)
                    total_weight += weight
            except ObjectDoesNotExist:
                # OneToOneField выбрасывает исключение если связи нет
                continue
            except Exception:
                continue
        
        # Нормализуем: если есть веса, делим сумму на сумму весов
        if total_weight > 0:
            return domain_score / total_weight
        return 0

    def get_overall_maturity_index(self):
        """Расчет общего индекса зрелости с учетом весов доменов"""
        overall_index = 0
        total_domain_weight = 0
        domains = Domain.objects.all()
        
        domain_results = []  # Для отладки

        for domain in domains:
            domain_score = self.get_domain_score(domain.id)
            domain_weight = float(domain.weight)
            
            domain_results.append({
                'domain': domain.name,
                'score': domain_score,
                'weight': domain_weight
            })
            
            # Учитываем только домены с оценками
            if domain_score > 0:
                overall_index += (domain_score * domain_weight)
                total_domain_weight += domain_weight
        
        # Нормализуем
        if total_domain_weight > 0:
            return overall_index / total_domain_weight
        return 0

class AssignedCriterion(models.Model):
    evaluation_session = models.ForeignKey(EvaluationSession, on_delete=models.CASCADE, related_name='assigned_criteria', verbose_name="Оценочная сессия")
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE, verbose_name="Критерий")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_criteria', verbose_name="Назначено")
    is_verified = models.BooleanField(default=False, verbose_name="Верифицировано")

    class Meta:
        verbose_name = "Назначенный критерий"
        verbose_name_plural = "Назначенные критерии"
        unique_together = ('evaluation_session', 'criterion')
        ordering = ['evaluation_session', 'criterion__name']

    def __str__(self):
        return f"{self.evaluation_session} - {self.criterion.name}"

class EvaluationAnswer(models.Model):
    assigned_criterion = models.OneToOneField(AssignedCriterion, on_delete=models.CASCADE, related_name='answer', verbose_name="Назначенный критерий")
    score_value = models.IntegerField(blank=True, null=True, verbose_name="Балл по шкале",
                                      validators=[MinValueValidator(1), MaxValueValidator(10)])
    metric_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Числовое значение метрики")
    file_evidence = models.FileField(upload_to='evaluation_evidence/', blank=True, null=True, verbose_name="Файл-доказательство")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = "Ответ на оценку"
        verbose_name_plural = "Ответы на оценку"
        ordering = ['submitted_at']

    def __str__(self):
        return f"Ответ на {self.assigned_criterion} (Балл: {self.score_value or '-'}, Метрика: {self.metric_value or '-'})"

# User and Role Management
class Role(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Администратор системы'),
        ('expert', 'Эксперт/Аудитор'),
        ('owner', 'Владелец продукта'),
        ('observer', 'Наблюдатель'),
    )
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name="Название роли")

    class Meta:
        verbose_name = "Роль пользователя"
        verbose_name_plural = "Роли пользователей"

    def __str__(self):
        return self.get_name_display()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, verbose_name="Роль")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username}'s profile ({self.role.get_name_display() if self.role else 'No Role'})"

# ВАЖНО: Сигналы перенесены в signals.py
# НЕ ДОБАВЛЯТЬ СИГНАЛЫ ЗДЕСЬ!

