import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_product_maturity.settings')
django.setup()

from digital_product_maturity.core.models import AssignedCriterion, EvaluationSession, Criterion
from django.db import transaction

print("="*60)
print("ДОБАВЛЕНИЕ НЕДОСТАЮЩИХ КРИТЕРИЕВ")
print("="*60)

sessions = EvaluationSession.objects.all()
all_criteria = list(Criterion.objects.all())
criteria_count = len(all_criteria)

print(f"\nВсего сессий: {sessions.count()}")
print(f"Всего критериев: {criteria_count}")

fixed_sessions = 0
added_criteria = 0

with transaction.atomic():
    for session in sessions:
        existing_assigned = AssignedCriterion.objects.filter(evaluation_session=session)
        existing_count = existing_assigned.count()
        
        if existing_count < criteria_count:
            print(f"\n[!] Сессия {session.id} ({session.product.name}):")
            print(f"    Текущих критериев: {existing_count}")
            print(f"    Недостает: {criteria_count - existing_count}")
            
            # Находим, какие критерии уже есть
            existing_criterion_ids = set(existing_assigned.values_list('criterion_id', flat=True))
            
            # Добавляем недостающие
            for criterion in all_criteria:
                if criterion.id not in existing_criterion_ids:
                    AssignedCriterion.objects.create(
                        evaluation_session=session,
                        criterion=criterion,
                        assigned_to=session.created_by,
                        is_verified=False
                    )
                    added_criteria += 1
                    print(f"    + Добавлен критерий: {criterion.name}")
            
            fixed_sessions += 1
        elif existing_count == criteria_count:
            print(f"[OK] Сессия {session.id} ({session.product.name}): {existing_count} критериев")
        else:
            print(f"[!] Сессия {session.id} ({session.product.name}): {existing_count} критериев (больше ожидаемого!)")

print("\n" + "="*60)
print("РЕЗУЛЬТАТ")
print("="*60)
print(f"Исправлено сессий: {fixed_sessions}")
print(f"Добавлено критериев: {added_criteria}")
print(f"\nВсего AssignedCriterion: {AssignedCriterion.objects.count()}")
print(f"Ожидается: {sessions.count() * criteria_count}")

# Финальная проверка
print("\n" + "-"*60)
print("Финальная проверка:")
print("-"*60)
all_ok = True
for session in sessions:
    count = AssignedCriterion.objects.filter(evaluation_session=session).count()
    status = "[OK]" if count == criteria_count else f"[ERROR] {count}"
    if count != criteria_count:
        all_ok = False
    print(f"  Сессия {session.id}: {status}")

if all_ok:
    print("\n[SUCCESS] Все сессии имеют правильное количество критериев!")
else:
    print("\n[WARNING] Некоторые сессии все еще имеют проблемы")

