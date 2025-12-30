# 📁 Структура проекта

## 🎯 Общая структура

```
digital_product_maturity_system/
├── 📂 backend/                          # Django Backend
│   ├── 📂 digital_product_maturity_project/
│   │   ├── 📂 digital_product_maturity/   # Основной проект
│   │   │   ├── 📂 core/                   # Главное приложение
│   │   │   │   ├── 📄 models.py          # Модели данных
│   │   │   │   ├── 📄 views.py           # API endpoints
│   │   │   │   ├── 📄 serializers.py     # REST serializers
│   │   │   │   ├── 📄 urls.py            # URL маршруты
│   │   │   │   ├── 📄 auth_views.py      # Авторизация API
│   │   │   │   ├── 📄 signals.py         # Автоматические действия
│   │   │   │   └── 📄 apps.py            # Конфигурация приложения
│   │   │   ├── 📄 settings.py            # Настройки Django
│   │   │   ├── 📄 urls.py                # Главные URL
│   │   │   └── 📄 wsgi.py                # WSGI конфигурация
│   │   ├── 📄 manage.py                  # Django команды
│   │   ├── 📄 create_superuser.py        # Создание администратора
│   │   └── 📄 populate_db.py             # Заполнение БД данными
│   ├── 📄 requirements.txt               # Python зависимости
│   ├── 📄 Dockerfile                     # Docker образ backend
│   └── 📄 .dockerignore                  # Игнорируемые файлы
│
├── 📂 frontend/                         # React Frontend
│   ├── 📂 src/
│   │   ├── 📂 pages/                    # Страницы приложения
│   │   │   ├── 📄 ProductList.js       # 📦 Список продуктов
│   │   │   ├── 📄 ProductForm.js       # ➕ Форма продукта
│   │   │   ├── 📄 ProductDetail.js     # 📋 Детали продукта
│   │   │   ├── 📄 DomainList.js        # ⚙️ Список доменов
│   │   │   ├── 📄 DomainForm.js        # ➕ Форма домена
│   │   │   ├── 📄 CriterionList.js     # 📝 Список критериев
│   │   │   ├── 📄 CriterionForm.js     # ➕ Форма критерия
│   │   │   ├── 📄 EvaluationSessionList.js  # 📊 Список сессий
│   │   │   ├── 📄 EvaluationSessionForm.js  # 🚀 Создание сессии
│   │   │   ├── 📄 EvaluationInput.js   # ✏️ Ввод оценок
│   │   │   ├── 📄 EvaluationResults.js # 📈 Результаты оценки
│   │   │   ├── 📄 Login.js             # 🔐 Вход
│   │   │   └── 📄 Register.js          # 📝 Регистрация
│   │   ├── 📂 components/              # React компоненты
│   │   │   └── 📄 RatingScaleForm.js  # Шкалы оценки
│   │   ├── 📄 App.js                   # Главный компонент
│   │   ├── 📄 App.css                  # Стили приложения
│   │   ├── 📄 setupProxy.js            # Прокси настройки
│   │   └── 📄 index.js                 # Точка входа
│   ├── 📂 public/
│   │   └── 📄 index.html               # HTML шаблон
│   ├── 📄 package.json                 # NPM зависимости
│   ├── 📄 Dockerfile                   # Docker образ frontend
│   └── 📄 .dockerignore                # Игнорируемые файлы
│
├── 📄 docker-compose.yml               # Docker Compose конфигурация
├── 📄 start_local.bat                  # Скрипт запуска (Windows)
├── 📄 README.md                        # Основная документация
├── 📄 QUICK_START.md                   # Быстрый старт
├── 📄 CHANGELOG.md                     # История изменений
├── 📄 OAUTH_SETUP.md                   # Настройка OAuth
└── 📄 PROJECT_STRUCTURE.md             # Этот файл
```

---

## 📦 Backend - Django REST API

### Модели данных (models.py)

**Product** - Цифровые продукты
- name, description, department_owner
- product_link, launch_date, is_archived

**Domain** - Домены оценки
- name, description, weight (вес в общей оценке)

**Criterion** - Критерии оценки
- domain, name, description, weight (вес в домене)

**RatingScale** - Шкалы оценки
- criterion, score (1-10), description

**EvaluationSession** - Сессии оценки
- product, start_date, end_date, status, created_by

**AssignedCriterion** - Назначенные критерии
- evaluation_session, criterion, assigned_to, is_verified

**EvaluationAnswer** - Ответы на оценку
- assigned_criterion, score_value, metric_value, comment, file_evidence

**Role & Profile** - Роли и профили пользователей
- admin, expert, owner, observer

### API Endpoints (urls.py)

**Продукты:**
- `/api/products/` - GET, POST
- `/api/products/{id}/` - GET, PUT, DELETE

**Домены:**
- `/api/domains/` - GET, POST
- `/api/domains/{id}/` - GET, PUT, DELETE

**Критерии:**
- `/api/criteria/` - GET, POST
- `/api/criteria/{id}/` - GET, PUT, DELETE

**Сессии оценки:**
- `/api/evaluation-sessions/` - GET, POST
- `/api/evaluation-sessions/{id}/get_domain_scores/` - GET
- `/api/evaluation-sessions/{id}/get_overall_maturity_index/` - GET
- `/api/evaluation-sessions/{id}/generate_maturity_passport/` - GET (PDF)

**Авторизация:**
- `/api/auth/register/` - POST
- `/api/auth/login/` - POST
- `/api/auth/logout/` - POST
- `/api/auth/user/` - GET

---

## 🎨 Frontend - React SPA

### Страницы (pages/)

**Управление продуктами:**
- `ProductList.js` - Карточки продуктов с кликабельностью
- `ProductForm.js` - Создание/редактирование продукта
- `ProductDetail.js` - Детальная информация о продукте

**Модель оценки:**
- `DomainList.js` - Список доменов с весами
- `DomainForm.js` - Создание/редактирование домена
- `CriterionList.js` - Критерии для домена
- `CriterionForm.js` - Создание/редактирование критерия

**Оценка продуктов:**
- `EvaluationSessionList.js` - Дашборд с статистикой сессий
- `EvaluationSessionForm.js` - Создание новой сессии
- `EvaluationInput.js` - Ввод оценок с прогресс-баром
- `EvaluationResults.js` - Графики и визуализация результатов

**Авторизация:**
- `Login.js` - Вход с показом/скрытием пароля
- `Register.js` - Регистрация с проверкой паролей

### Навигация (App.js)

```javascript
📦 Продукты           → /
➕ Добавить продукт   → /add-product
⚙️ Модель оценки      → /domains
📊 Сессии оценки      → /evaluation-sessions
🔐 Вход               → /login
```

### Стили (App.css)

**Компоненты:**
- Навигация (градиентная)
- Карточки (продуктов, доменов, критериев)
- Формы (с валидацией)
- Кнопки (цветные с эффектами)
- Прогресс-бары (анимированные)
- Графики (Chart.js)
- Дашборды (статистика)

---

## 🔄 Автоматизация

### Signals (signals.py)

**create_assigned_criteria** - При создании сессии:
- Автоматически создаются назначенные критерии
- Все критерии из модели назначаются создателю
- Статус: не верифицирован

**create_user_profile** - При регистрации:
- Автоматически создается профиль
- Роль по умолчанию: observer
- Привязка к пользователю

---

## 🎯 Ключевые функции

### Backend
✅ REST API с полным CRUD
✅ JWT авторизация
✅ Автоматический расчет индекса зрелости
✅ PDF генерация паспорта зрелости
✅ Сигналы для автоматизации
✅ Профили пользователей с ролями

### Frontend
✅ Адаптивный дизайн
✅ Кликабельные карточки
✅ Прогресс-бары
✅ Графики (Radar, Bar, Doughnut)
✅ Дашборды с статистикой
✅ Показ/скрытие пароля
✅ Русский язык во всем интерфейсе

---

## 🚀 Запуск проекта

### Локально:
```bash
# Backend
cd backend\digital_product_maturity_project
python manage.py runserver

# Frontend (новое окно)
cd frontend
npm start
```

### Docker:
```bash
docker-compose up --build
```

### Быстрый запуск (Windows):
```bash
start_local.bat
```

---

## 📊 База данных

**SQLite** (по умолчанию для разработки)
- Файл: `backend/digital_product_maturity_project/db.sqlite3`
- Миграции: автоматические

**PostgreSQL** (для Docker и продакшена)
- Хост: db
- База: digital_product_maturity
- Порт: 5432

---

## 🎨 Цветовая схема

**Основной градиент:**
- #667eea → #764ba2 (фиолетовый → синий)

**Акценты:**
- 🟢 Зеленый (#38ef7d) - успех, завершено
- 🔵 Синий (#4facfe) - информация
- 🟡 Желтый (#f7b731) - предупреждение, редактирование
- 🔴 Красный (#eb3349) - ошибка, удаление

**Уровни зрелости:**
- 🌟 Превосходный (8-10): #38ef7d
- ⭐ Высокий (6-8): #4facfe
- 💫 Средний (4-6): #f7b731
- ⚠️ Низкий (2-4): #f7797d
- ❌ Критический (0-2): #eb3349

---

## 📝 Чек-лист готовности

✅ Backend запущен на порту 8000
✅ Frontend запущен на порту 3000
✅ База данных заполнена тестовыми данными
✅ Суперпользователь создан (admin/admin123)
✅ Все интерфейсы переведены на русский
✅ Дашборды и графики работают
✅ Автоматизация настроена (signals)
✅ Стили и анимации применены
✅ Формы с валидацией
✅ Показ/скрытие паролей
✅ Кликабельные карточки
✅ PDF генерация работает

---

**🎉 Проект готов к использованию!**

