import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_product_maturity.settings')
django.setup()

from digital_product_maturity.core.models import AssignedCriterion, EvaluationSession, Criterion
from django.db import transaction

print("="*60)
print("ПОЛНАЯ ОЧИСТКА И ПЕРЕСОЗДАНИЕ КРИТЕРИЕВ")
print("="*60)

sessions = EvaluationSession.objects.all()
criteria = Criterion.objects.all()

print(f"\nВсего сессий: {sessions.count()}")
print(f"Всего критериев в системе: {criteria.count()}")

current_total = AssignedCriterion.objects.count()
expected_total = sessions.count() * criteria.count()

print(f"\nТекущее количество AssignedCriterion: {current_total}")
print(f"Ожидаемое количество: {expected_total}")

if current_total != expected_total:
    print(f"\n[!] ПРОБЛЕМА: Разница = {abs(current_total - expected_total)}")
else:
    print("\n[OK] Количество соответствует ожидаемому")

# Статистика по сессиям
print("\n" + "-"*60)
print("Статистика по сессиям:")
print("-"*60)
for session in sessions:
    count = AssignedCriterion.objects.filter(evaluation_session=session).count()
    status = "[OK]" if count == criteria.count() else f"[ERROR] {count}"
    print(f"  Сессия {session.id} ({session.product.name}): {status}")

# Подтверждение
print("\n" + "="*60)
print("ЧТО БУДЕТ СДЕЛАНО:")
print("="*60)
print("1. УДАЛИТЬ все AssignedCriterion")
print("2. ПЕРЕСОЗДАТЬ критерии для каждой сессии")
print(f"3. Будет создано ровно {expected_total} критериев")
print("="*60)

confirm = input("\nПродолжить? (yes/no): ").strip().lower()

if confirm != 'yes':
    print("\n[ОТМЕНЕНО] Операция отменена")
    exit(0)

print("\n" + "-"*60)
print("Выполнение очистки и пересоздания...")
print("-"*60)

with transaction.atomic():
    # 1. Удаляем все AssignedCriterion
    deleted_count = AssignedCriterion.objects.all().delete()[0]
    print(f"[1/2] Удалено {deleted_count} старых критериев")
    
    # 2. Создаем заново для каждой сессии
    total_created = 0
    for session in sessions:
        created_for_session = 0
        for criterion in criteria:
            AssignedCriterion.objects.create(
                evaluation_session=session,
                criterion=criterion,
                assigned_to=session.created_by,
                is_verified=False
            )
            created_for_session += 1
            total_created += 1
        print(f"  Сессия {session.id}: создано {created_for_session} критериев")
    
    print(f"\n[2/2] Всего создано {total_created} критериев")

# Финальная проверка
print("\n" + "="*60)
print("ФИНАЛЬНАЯ ПРОВЕРКА")
print("="*60)

final_total = AssignedCriterion.objects.count()
print(f"Всего AssignedCriterion: {final_total}")
print(f"Ожидалось: {expected_total}")

if final_total == expected_total:
    print("\n[SUCCESS] Все критерии пересозданы правильно!")
else:
    print(f"\n[ERROR] Несоответствие: {final_total} вместо {expected_total}")

print("\nСтатус каждой сессии:")
all_ok = True
for session in sessions:
    count = AssignedCriterion.objects.filter(evaluation_session=session).count()
    status = "[OK]" if count == criteria.count() else f"[ERROR] {count}"
    if count != criteria.count():
        all_ok = False
    print(f"  Сессия {session.id} ({session.product.name}): {count} критериев {status}")

if all_ok:
    print("\n" + "="*60)
    print("[SUCCESS] ВСЕ СЕССИИ ИМЕЮТ ПРАВИЛЬНОЕ КОЛИЧЕСТВО КРИТЕРИЕВ!")
    print("="*60)
else:
    print("\n[WARNING] Некоторые сессии имеют неправильное количество критериев")

