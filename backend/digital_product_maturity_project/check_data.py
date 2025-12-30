#!/usr/bin/env python
"""
Скрипт для проверки данных в базе данных
"""
import os
import sys
import django

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_product_maturity.settings')
django.setup()

from digital_product_maturity.core.models import (
    Product, Domain, Criterion, EvaluationSession, 
    AssignedCriterion, EvaluationAnswer
)

def check_data():
    print("=" * 60)
    print("ПРОВЕРКА ДАННЫХ В БАЗЕ")
    print("=" * 60)
    
    # Проверяем продукты
    products = Product.objects.all()
    print(f"\n[ПРОДУКТЫ] Всего: {products.count()}")
    for p in products[:5]:
        print(f"  - {p.id}: {p.name}")
    
    # Проверяем домены
    domains = Domain.objects.all()
    print(f"\n[ДОМЕНЫ] Всего: {domains.count()}")
    for d in domains:
        print(f"  - {d.id}: {d.name} (вес: {d.weight})")
    
    # Проверяем критерии
    criteria = Criterion.objects.all()
    print(f"\n[КРИТЕРИИ] Всего: {criteria.count()}")
    for c in criteria[:5]:
        print(f"  - {c.id}: {c.name} (домен: {c.domain.name}, вес: {c.weight})")
    
    # Проверяем сессии оценки
    sessions = EvaluationSession.objects.all()
    print(f"\n[СЕССИИ ОЦЕНКИ] Всего: {sessions.count()}")
    
    for session in sessions:
        print(f"\n  СЕССИЯ {session.id}:")
        print(f"    Продукт: {session.product.name}")
        print(f"    Статус: {session.status}")
        
        # Назначенные критерии
        assigned = AssignedCriterion.objects.filter(evaluation_session=session)
        print(f"    Назначенных критериев: {assigned.count()}")
        
        # Ответы
        answers = EvaluationAnswer.objects.filter(assigned_criterion__evaluation_session=session)
        print(f"    Ответов (EvaluationAnswer): {answers.count()}")
        
        if answers.exists():
            print("    Ответы:")
            for ans in answers[:5]:
                print(f"      - Критерий: {ans.assigned_criterion.criterion.name}")
                print(f"        Балл: {ans.score_value}, Метрика: {ans.metric_value}")
        
        # Расчет индекса
        overall_index = session.get_overall_maturity_index()
        print(f"    Общий индекс зрелости: {overall_index}")
        
        for domain in domains:
            domain_score = session.get_domain_score(domain.id)
            print(f"      - {domain.name}: {domain_score}")

if __name__ == '__main__':
    check_data()

