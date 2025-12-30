import os
import django
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_product_maturity.settings')
django.setup()

from digital_product_maturity.core.models import AssignedCriterion, EvaluationSession, Criterion

print("="*60)
print("ОЧИСТКА ДУБЛИКАТОВ КРИТЕРИЕВ")
print("="*60)

# Статистика по сессиям
sessions = EvaluationSession.objects.all()
criteria_count = Criterion.objects.count()

print(f"\nВсего сессий: {sessions.count()}")
print(f"Всего уникальных критериев в системе: {criteria_count}")
print(f"Ожидаемое количество AssignedCriterion: {sessions.count() * criteria_count}")

total_assigned = AssignedCriterion.objects.count()
print(f"Фактическое количество AssignedCriterion: {total_assigned}")

if total_assigned > sessions.count() * criteria_count:
    print(f"\n[!] ОБНАРУЖЕНЫ ДУБЛИКАТЫ: {total_assigned - (sessions.count() * criteria_count)} лишних записей")
else:
    print("\n[OK] Дубликаты не обнаружены на уровне статистики")

print("\n" + "-"*60)
print("Поиск дубликатов по каждой сессии...")
print("-"*60)

# Анализ по сессиям
session_stats = defaultdict(int)
duplicates_to_delete = []

for session in sessions:
    assigned = AssignedCriterion.objects.filter(evaluation_session=session)
    session_stats[session.id] = assigned.count()
    
    if assigned.count() > criteria_count:
        print(f"\n[!] Сессия {session.id} ({session.product.name}):")
        print(f"    Критериев: {assigned.count()} (ожидалось {criteria_count})")
        print(f"    ДУБЛИКАТОВ: {assigned.count() - criteria_count}")
        
        # Находим дубликаты для этой сессии
        seen_criteria = set()
        for ac in assigned.order_by('id'):
            if ac.criterion_id in seen_criteria:
                # Это дубликат
                duplicates_to_delete.append(ac.id)
                print(f"    -> Дубликат ID={ac.id}, критерий='{ac.criterion.name}'")
            else:
                seen_criteria.add(ac.criterion_id)
    elif assigned.count() < criteria_count:
        print(f"\n[!] Сессия {session.id} ({session.product.name}):")
        print(f"    Критериев: {assigned.count()} (ожидалось {criteria_count})")
        print(f"    НЕДОСТАЕТ: {criteria_count - assigned.count()}")

# Удаление дубликатов
if duplicates_to_delete:
    print("\n" + "="*60)
    print(f"НАЙДЕНО {len(duplicates_to_delete)} ДУБЛИКАТОВ")
    print("="*60)
    
    confirm = input("\nУдалить дубликаты? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        print("\nУдаление дубликатов...")
        deleted_count = AssignedCriterion.objects.filter(id__in=duplicates_to_delete).delete()[0]
        print(f"[OK] Удалено {deleted_count} дубликатов!")
        
        # Финальная статистика
        print("\n" + "="*60)
        print("ФИНАЛЬНАЯ СТАТИСТИКА")
        print("="*60)
        print(f"Всего AssignedCriterion: {AssignedCriterion.objects.count()}")
        print(f"Ожидалось: {sessions.count() * criteria_count}")
        
        for session in sessions:
            count = AssignedCriterion.objects.filter(evaluation_session=session).count()
            status = "[OK]" if count == criteria_count else f"[!] {count}"
            print(f"  Сессия {session.id}: {status}")
    else:
        print("[ОТМЕНЕНО] Дубликаты не удалены")
else:
    print("\n" + "="*60)
    print("[OK] ДУБЛИКАТЫ НЕ НАЙДЕНЫ!")
    print("="*60)
    
    # Проверка каждой сессии
    print("\nСтатус каждой сессии:")
    for session in sessions:
        count = AssignedCriterion.objects.filter(evaluation_session=session).count()
        status = "[OK]" if count == criteria_count else f"[!] {count}"
        print(f"  Сессия {session.id} ({session.product.name}): {status}")

