# 🎯 Система оценки зрелости цифровых продуктов региона

Информационная система для оценки зрелости цифровых продуктов региона с веб-интерфейсом на Django (backend) и React (frontend).

## 📋 Функциональные возможности

### Управление продуктами
- Создание, редактирование и архивирование карточек продуктов
- Атрибуты: название, описание, владелец, ссылка, дата запуска

### Конструктор модели оценки
- Настройка иерархической модели оценки (домены → критерии)
- Веса для доменов и критериев
- Шкала оценки 1-10 с текстовыми описаниями

### Сессии оценки
- Инициация оценок для продуктов
- Динамические анкеты на основе модели критериев
- Частичное сохранение (можно заполнять постепенно)
- Статусы: В ожидании → В процессе → Завершено

### Расчёт и визуализация
- Автоматический расчёт индекса зрелости с учётом весов
- Интерактивные дашборды:
  - Радарный график по доменам
  - Столбчатая диаграмма
  - Круговая диаграмма прогресса

### Отчётность
- PDF-паспорт зрелости продукта (на русском языке)
- Сводный отчёт по портфелю продуктов

### Пользователи и роли
- Регистрация и авторизация
- Профили пользователей
- Роли: Администратор, Эксперт, Владелец продукта, Наблюдатель

## 🛠 Технологии

| Компонент | Технология |
|-----------|------------|
| Backend | Python 3.11, Django 4.2, Django REST Framework |
| Frontend | React 18, Chart.js, Axios |
| База данных | SQLite (разработка) / PostgreSQL (production) |
| Контейнеризация | Docker, Docker Compose |

## 🚀 Быстрый старт

### Вариант 1: Локальный запуск

#### Backend
```bash
cd backend/digital_product_maturity_project
pip install -r ../requirements.txt
python manage.py migrate
python create_superuser.py  # Создаёт admin/admin123
python populate_db.py       # Наполняет тестовыми данными
python manage.py runserver
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### Доступ
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Логин: `admin` / Пароль: `admin123`

### Вариант 2: Docker Compose

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/

## 📁 Структура проекта

```
digital_product_maturity_system/
├── backend/
│   ├── digital_product_maturity_project/
│   │   ├── digital_product_maturity/
│   │   │   ├── core/           # Основное приложение
│   │   │   │   ├── models.py   # Модели данных
│   │   │   │   ├── views.py    # API endpoints
│   │   │   │   ├── serializers.py
│   │   │   │   └── urls.py
│   │   │   └── settings.py
│   │   ├── manage.py
│   │   ├── create_superuser.py
│   │   └── populate_db.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/              # Страницы приложения
│   │   │   ├── ProductList.js
│   │   │   ├── DomainList.js
│   │   │   ├── EvaluationInput.js
│   │   │   ├── EvaluationResults.js
│   │   │   └── ...
│   │   ├── App.js
│   │   └── App.css
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 📊 Модели данных

### Product (Цифровой продукт)
- name, description, department_owner, product_link, launch_date, is_archived

### Domain (Домен оценки)
- name, description, weight (вес в общем индексе)

### Criterion (Критерий)
- name, description, weight, domain (FK)

### EvaluationSession (Сессия оценки)
- product (FK), status, start_date, end_date, created_by

### AssignedCriterion (Назначенный критерий)
- evaluation_session (FK), criterion (FK), assigned_to, is_verified

### EvaluationAnswer (Ответ на оценку)
- assigned_criterion (FK), score_value (1-10), metric_value, comment

## 🔌 API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET/POST | `/api/products/` | Список/создание продуктов |
| GET/PUT/DELETE | `/api/products/{id}/` | Операции с продуктом |
| GET/POST | `/api/domains/` | Список/создание доменов |
| GET/POST | `/api/criteria/` | Список/создание критериев |
| GET/POST | `/api/evaluation-sessions/` | Сессии оценки |
| GET | `/api/evaluation-sessions/{id}/get_overall_maturity_index/` | Индекс зрелости |
| GET | `/api/evaluation-sessions/{id}/get_domain_scores/` | Оценки по доменам |
| GET | `/api/evaluation-sessions/{id}/generate_maturity_passport/` | PDF паспорт |
| GET/POST | `/api/assigned-criteria/` | Назначенные критерии |
| GET/POST | `/api/evaluation-answers/` | Ответы на оценку |

## 📈 Расчёт индекса зрелости

```
Индекс домена = Σ(оценка_критерия × вес_критерия) / Σ(веса_критериев)

Общий индекс = Σ(индекс_домена × вес_домена) / Σ(веса_доменов)
```

**Уровни зрелости:**
- 🌟 **Превосходный** (8-10)
- ⭐ **Высокий** (6-8)
- 💫 **Средний** (4-6)
- ⚠️ **Низкий** (2-4)
- ❌ **Критический** (0-2)

## 📄 Лицензия

MIT License

## 👨‍💻 Автор

Система разработана для оценки зрелости цифровых продуктов региона.
