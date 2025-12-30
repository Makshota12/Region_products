# Digital Product Maturity Assessment System

Информационная система для оценки зрелости цифровых продуктов региона.

## Описание

Система предназначена для управления реестром цифровых продуктов, проведения оценочных сессий по различным критериям, визуализации результатов и генерации отчетов о зрелости продуктов.

### Основные функции:

- **FR-01:** Управление реестром цифровых продуктов
- **FR-02:** Конструктор моделей оценки (домены и критерии)
- **FR-03:** Проведение оценочных сессий
- **FR-04:** Ввод и верификация оценочных данных
- **FR-05:** Расчет и визуализация результатов
- **FR-06:** Генерация отчетов (Паспорт зрелости продукта, сводный отчет)
- **FR-07:** Управление пользователями и ролями

## Технологический стек

- **Backend:** Django 4.2.7, Django REST Framework
- **Frontend:** React 19.2.3
- **Database:** PostgreSQL 15 (для Docker) / SQLite (для локальной разработки)
- **Deployment:** Docker Compose

## Установка и запуск

### Вариант 1: Запуск с Docker Compose (рекомендуется)

#### Требования:
- Docker Desktop (Windows/Mac) или Docker + Docker Compose (Linux)

#### Шаги:

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd digital_product_maturity_system
```

2. Запустите все сервисы:
```bash
docker-compose up --build
```

3. Приложение будет доступно по адресам:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Django Admin: http://localhost:8000/admin/

4. Для создания суперпользователя (администратора):
```bash
docker-compose exec backend sh -c "cd digital_product_maturity_project && python manage.py createsuperuser"
```

5. Для остановки:
```bash
docker-compose down
```

### Вариант 2: Локальный запуск (для разработки)

#### Требования:
- Python 3.11+
- Node.js 18+
- npm или yarn

#### Backend:

1. Перейдите в директорию backend:
```bash
cd backend
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Перейдите в директорию проекта Django:
```bash
cd digital_product_maturity_project
```

4. Выполните миграции:
```bash
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустите сервер:
```bash
python manage.py runserver
```

Backend будет доступен по адресу: http://127.0.0.1:8000/

#### Frontend:

1. Откройте новый терминал и перейдите в директорию frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите development сервер:
```bash
npm start
```

Frontend будет доступен по адресу: http://localhost:3000/

## Структура проекта

```
digital_product_maturity_system/
├── backend/
│   ├── digital_product_maturity_project/
│   │   ├── digital_product_maturity/
│   │   │   ├── core/            # Основное приложение
│   │   │   │   ├── models.py    # Модели данных
│   │   │   │   ├── views.py     # API endpoints
│   │   │   │   ├── serializers.py
│   │   │   │   └── urls.py
│   │   │   ├── settings.py      # Настройки Django
│   │   │   └── urls.py
│   │   └── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/               # Страницы приложения
│   │   ├── components/          # React компоненты
│   │   └── App.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Продукты
- `GET/POST /api/products/` - Список/создание продуктов
- `GET/PUT/DELETE /api/products/{id}/` - Детали/обновление/удаление продукта

### Домены оценки
- `GET/POST /api/domains/` - Список/создание доменов
- `GET/PUT/DELETE /api/domains/{id}/` - Детали/обновление/удаление домена

### Критерии
- `GET/POST /api/criteria/` - Список/создание критериев
- `GET/PUT/DELETE /api/criteria/{id}/` - Детали/обновление/удаление критерия

### Оценочные сессии
- `GET/POST /api/evaluation-sessions/` - Список/создание сессий
- `GET /api/evaluation-sessions/{id}/get_overall_maturity_index/` - Общий индекс зрелости
- `GET /api/evaluation-sessions/{id}/get_domain_scores/` - Оценки по доменам
- `GET /api/evaluation-sessions/{id}/generate_maturity_passport/` - Генерация паспорта зрелости (PDF)

### Отчеты
- `GET /api/portfolio-report/` - Сводный отчет по портфелю (PDF)

### Пользователи и роли
- `GET/POST /api/users/` - Управление пользователями
- `GET/POST /api/roles/` - Управление ролями
- `GET/POST /api/profiles/` - Управление профилями

## Роли пользователей

- **Администратор системы** - Полный доступ ко всем функциям
- **Эксперт/Аудитор** - Проведение оценок и верификация
- **Владелец продукта** - Управление продуктом и ввод данных
- **Наблюдатель** - Просмотр данных (только чтение)

## Безопасность

- Аутентификация пользователей
- Хэширование паролей
- HTTPS (в продакшене)
- CORS настройки
- Защита от OWASP Top 10

## Лицензия

Proprietary - все права защищены.

## Контакты

Для вопросов и поддержки обращайтесь к администратору системы.

