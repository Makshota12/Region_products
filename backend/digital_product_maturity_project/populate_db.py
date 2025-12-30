import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_product_maturity.settings')
django.setup()

from digital_product_maturity.core.models import Product, Domain, Criterion, RatingScale, Role

# Create Roles
roles_data = ['admin', 'expert', 'owner', 'observer']
for role_name in roles_data:
    Role.objects.get_or_create(name=role_name)
print("[OK] Roles created")

# Create Products
products_data = [
    {
        'name': 'Региональный портал государственных услуг',
        'description': 'Единое окно для получения государственных и муниципальных услуг региона',
        'department_owner': 'Министерство цифрового развития',
        'product_link': 'https://gosuslugi.region.ru',
        'launch_date': date(2021, 3, 15)
    },
    {
        'name': 'Мобильное приложение "Моя школа"',
        'description': 'Цифровой дневник и образовательная платформа для школьников и родителей',
        'department_owner': 'Министерство образования',
        'product_link': 'https://myschool.region.ru',
        'launch_date': date(2022, 9, 1)
    },
    {
        'name': 'Система мониторинга общественного транспорта',
        'description': 'Отслеживание движения общественного транспорта в реальном времени',
        'department_owner': 'Департамент транспорта',
        'product_link': 'https://transport.region.ru',
        'launch_date': date(2020, 6, 1)
    },
    {
        'name': 'Платформа "Здоровье онлайн"',
        'description': 'Электронная медицинская карта и запись к врачам',
        'department_owner': 'Министерство здравоохранения',
        'product_link': 'https://health.region.ru',
        'launch_date': date(2021, 11, 20)
    },
]

for product_data in products_data:
    Product.objects.get_or_create(
        name=product_data['name'],
        defaults=product_data
    )
print(f"[OK] {len(products_data)} products created")

# Create Domains
domains_data = [
    {
        'name': 'Технологическая зрелость',
        'description': 'Оценка технологического стека, архитектуры и инфраструктуры',
        'weight': 30.00
    },
    {
        'name': 'UX/UI и доступность',
        'description': 'Оценка пользовательского интерфейса и опыта взаимодействия',
        'weight': 25.00
    },
    {
        'name': 'Безопасность',
        'description': 'Оценка мер информационной безопасности',
        'weight': 25.00
    },
    {
        'name': 'Аналитика и данные',
        'description': 'Оценка работы с данными и аналитическими системами',
        'weight': 20.00
    },
]

created_domains = []
for domain_data in domains_data:
    domain, created = Domain.objects.get_or_create(
        name=domain_data['name'],
        defaults=domain_data
    )
    created_domains.append(domain)
print(f"[OK] {len(domains_data)} domains created")

# Create Criteria and Rating Scales
criteria_data = {
    'Технологическая зрелость': [
        {
            'name': 'Современность технологического стека',
            'description': 'Использование актуальных технологий и фреймворков',
            'weight': 30.00,
            'scales': {
                1: 'Устаревшие технологии, отсутствие обновлений',
                3: 'Частичное использование современных технологий',
                5: 'Актуальные технологии, регулярные обновления',
                7: 'Передовые технологии, best practices',
                10: 'Инновационный технологический стек, лидерство в отрасли'
            }
        },
        {
            'name': 'Масштабируемость архитектуры',
            'description': 'Способность системы выдерживать рост нагрузки',
            'weight': 35.00,
            'scales': {
                1: 'Монолитная архитектура без возможности масштабирования',
                3: 'Ограниченные возможности горизонтального масштабирования',
                5: 'Микросервисная архитектура с возможностью масштабирования',
                7: 'Автоматическое масштабирование, контейнеризация',
                10: 'Cloud-native архитектура, full автоматизация'
            }
        },
        {
            'name': 'Качество кода и документации',
            'description': 'Соблюдение стандартов разработки',
            'weight': 35.00,
            'scales': {
                1: 'Отсутствие стандартов, нет документации',
                3: 'Базовая документация, минимальные стандарты',
                5: 'Хорошая документация, code review практики',
                7: 'Отличная документация, автотесты, CI/CD',
                10: 'Полная автоматизация, 100% покрытие тестами'
            }
        },
    ],
    'UX/UI и доступность': [
        {
            'name': 'Удобство интерфейса',
            'description': 'Интуитивность и простота использования',
            'weight': 40.00,
            'scales': {
                1: 'Сложный и запутанный интерфейс',
                3: 'Требует обучения для использования',
                5: 'Интуитивно понятный интерфейс',
                7: 'Отличный UX, минимум кликов для задач',
                10: 'Эталонный дизайн, награды за UX'
            }
        },
        {
            'name': 'Адаптивность',
            'description': 'Работа на различных устройствах',
            'weight': 30.00,
            'scales': {
                1: 'Только десктопная версия',
                3: 'Частичная адаптация под мобильные',
                5: 'Полностью адаптивный дизайн',
                7: 'Native мобильные приложения',
                10: 'Кроссплатформенность, PWA'
            }
        },
        {
            'name': 'Доступность для людей с ограниченными возможностями',
            'description': 'Соответствие стандартам WCAG',
            'weight': 30.00,
            'scales': {
                1: 'Не учитывается доступность',
                3: 'Базовые функции доступности',
                5: 'WCAG 2.0 уровень A',
                7: 'WCAG 2.1 уровень AA',
                10: 'WCAG 2.1 уровень AAA, голосовое управление'
            }
        },
    ],
    'Безопасность': [
        {
            'name': 'Защита данных',
            'description': 'Шифрование и защита персональных данных',
            'weight': 40.00,
            'scales': {
                1: 'Отсутствие шифрования данных',
                3: 'Базовое шифрование транспорта (HTTPS)',
                5: 'Шифрование данных в покое и транзите',
                7: 'Полное шифрование, токенизация',
                10: 'Zero-knowledge архитектура'
            }
        },
        {
            'name': 'Аутентификация и авторизация',
            'description': 'Механизмы контроля доступа',
            'weight': 30.00,
            'scales': {
                1: 'Слабая аутентификация, нет ролей',
                3: 'Базовая аутентификация, простые роли',
                5: 'Многофакторная аутентификация, RBAC',
                7: 'SSO, биометрия, детальные политики',
                10: 'Zero Trust архитектура'
            }
        },
        {
            'name': 'Соответствие стандартам безопасности',
            'description': 'Сертификации и аудиты безопасности',
            'weight': 30.00,
            'scales': {
                1: 'Нет сертификаций и аудитов',
                3: 'Базовый внутренний аудит',
                5: 'Регулярные аудиты, сертификат ISO 27001',
                7: 'Penetration testing, bug bounty программы',
                10: 'Международные сертификации, SOC 2 Type II'
            }
        },
    ],
    'Аналитика и данные': [
        {
            'name': 'Сбор и анализ метрик',
            'description': 'Мониторинг использования и производительности',
            'weight': 50.00,
            'scales': {
                1: 'Отсутствие аналитики',
                3: 'Базовые метрики посещаемости',
                5: 'Детальная аналитика поведения пользователей',
                7: 'Real-time дашборды, предиктивная аналитика',
                10: 'AI-driven инсайты, автоматизация решений'
            }
        },
        {
            'name': 'Работа с данными',
            'description': 'Качество и управление данными',
            'weight': 50.00,
            'scales': {
                1: 'Хаотичное хранение данных',
                3: 'Структурированное хранение',
                5: 'Data warehouse, ETL процессы',
                7: 'Data lake, ML pipeline',
                10: 'Data mesh архитектура'
            }
        },
    ],
}

for domain in created_domains:
    if domain.name in criteria_data:
        for criterion_data in criteria_data[domain.name]:
            criterion, created = Criterion.objects.get_or_create(
                domain=domain,
                name=criterion_data['name'],
                defaults={
                    'description': criterion_data['description'],
                    'weight': criterion_data['weight']
                }
            )
            
            # Create rating scales
            for score, description in criterion_data['scales'].items():
                RatingScale.objects.get_or_create(
                    criterion=criterion,
                    score=score,
                    defaults={'description': description}
                )

print(f"[OK] Criteria and rating scales created")
print("\n[SUCCESS] Database populated successfully!")
print("\nSummary:")
print(f"  - Products: {Product.objects.count()}")
print(f"  - Domains: {Domain.objects.count()}")
print(f"  - Criteria: {Criterion.objects.count()}")
print(f"  - Rating Scales: {RatingScale.objects.count()}")
print(f"  - Roles: {Role.objects.count()}")

