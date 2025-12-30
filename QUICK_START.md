# Быстрый старт

## ✅ Исправленные ошибки

1. **Синтаксическая ошибка в models.py** - исправлена переменная `criteri-in_domain` → `criteria_in_domain`
2. **Отсутствующие сериализаторы** - добавлен `UserSerializer`
3. **Отсутствующие ViewSet** - добавлен `UserViewSet`
4. **Неполная регистрация URL** - добавлены эндпоинты для ролей, профилей и пользователей
5. **Настройки базы данных** - добавлена поддержка PostgreSQL для Docker
6. **MEDIA файлы** - настроены MEDIA_URL и MEDIA_ROOT для загрузки файлов

## 🚀 Способы запуска приложения

### Вариант 1: Docker Compose (рекомендуется для продакшена)

```bash
# Запуск всех сервисов (база данных + backend + frontend)
docker-compose up --build

# В другом терминале создайте суперпользователя:
docker-compose exec backend sh -c "cd digital_product_maturity_project && python manage.py createsuperuser"

# Остановка:
docker-compose down
```

**Доступ:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin панель: http://localhost:8000/admin/

### Вариант 2: Локальный запуск (для разработки)

#### Простой способ (Windows):
Запустите файл `start_local.bat` - он автоматически откроет два окна командной строки для backend и frontend.

#### Ручной способ:

**Терминал 1 - Backend:**
```bash
cd backend\digital_product_maturity_project
python manage.py migrate
python manage.py createsuperuser  # при первом запуске
python manage.py runserver
```

**Терминал 2 - Frontend:**
```bash
cd frontend
npm install  # при первом запуске
npm start
```

**Доступ:**
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000/api/
- Admin панель: http://127.0.0.1:8000/admin/

## 📋 Проверка работоспособности

### Backend проверки:

```bash
cd backend\digital_product_maturity_project

# Проверка на ошибки конфигурации
python manage.py check

# Проверка миграций
python manage.py showmigrations

# Запуск тестов (если есть)
python manage.py test
```

### Frontend проверки:

```bash
cd frontend

# Проверка на ошибки
npm run build

# Запуск тестов
npm test
```

## 🗂️ Структура API

### Основные эндпоинты:

**Продукты:**
- `GET /api/products/` - список продуктов
- `POST /api/products/` - создать продукт
- `GET /api/products/{id}/` - детали продукта
- `PUT /api/products/{id}/` - обновить продукт
- `DELETE /api/products/{id}/` - удалить продукт

**Домены оценки:**
- `GET /api/domains/` - список доменов
- `POST /api/domains/` - создать домен
- `GET /api/domains/{id}/` - детали домена

**Критерии:**
- `GET /api/criteria/` - список критериев
- `POST /api/criteria/` - создать критерий
- `GET /api/criteria/{id}/` - детали критерия

**Оценочные сессии:**
- `GET /api/evaluation-sessions/` - список сессий
- `POST /api/evaluation-sessions/` - создать сессию
- `GET /api/evaluation-sessions/{id}/` - детали сессии
- `GET /api/evaluation-sessions/{id}/get_overall_maturity_index/` - получить общий индекс зрелости
- `GET /api/evaluation-sessions/{id}/get_domain_scores/` - получить оценки по доменам
- `GET /api/evaluation-sessions/{id}/generate_maturity_passport/` - скачать PDF паспорт

**Назначенные критерии:**
- `GET /api/assigned-criteria/` - список назначенных критериев
- `POST /api/assigned-criteria/` - назначить критерий

**Ответы на оценку:**
- `GET /api/evaluation-answers/` - список ответов
- `POST /api/evaluation-answers/` - создать ответ
- `PUT /api/evaluation-answers/{id}/` - обновить ответ

**Пользователи и роли:**
- `GET /api/users/` - список пользователей
- `GET /api/roles/` - список ролей
- `GET /api/profiles/` - список профилей

**Отчеты:**
- `GET /api/portfolio-report/` - скачать сводный отчет по портфелю (PDF)

## 🔐 Роли пользователей

При создании нового пользователя автоматически назначается роль **"Наблюдатель"**.

Доступные роли:
- **admin** - Администратор системы (полный доступ)
- **expert** - Эксперт/Аудитор (проведение оценок)
- **owner** - Владелец продукта (управление своими продуктами)
- **observer** - Наблюдатель (только просмотр)

## 📊 Пример использования

### 1. Создание модели оценки:

1. Войдите в систему как администратор
2. Перейдите в "Evaluation Model"
3. Создайте домены (например: "Технологии", "UX/UI", "Безопасность")
4. Для каждого домена создайте критерии с весами
5. Для каждого критерия задайте шкалы оценки (1-10 баллов с описанием)

### 2. Добавление продуктов:

1. Перейдите в "Product List"
2. Нажмите "Add Product"
3. Заполните информацию о продукте
4. Сохраните

### 3. Проведение оценки:

1. Перейдите в "Evaluation Sessions"
2. Нажмите "Start New Evaluation"
3. Выберите продукт
4. Система создаст динамическую анкету на основе модели оценки
5. Заполните оценки по каждому критерию
6. Сохраните ответы

### 4. Просмотр результатов:

1. Перейдите в "Evaluation Results"
2. Выберите сессию оценки
3. Просмотрите визуализации (графики, диаграммы)
4. Скачайте PDF-отчет "Паспорт зрелости продукта"

### 5. Генерация сводного отчета:

Перейдите по URL: `http://127.0.0.1:8000/api/portfolio-report/` для скачивания PDF-отчета по всему портфелю продуктов.

## ⚙️ Дополнительные настройки

### Изменение базы данных на PostgreSQL (локально):

1. Установите PostgreSQL
2. Создайте базу данных:
```sql
CREATE DATABASE digital_product_maturity;
```

3. Установите переменные окружения:
```bash
set DB_NAME=digital_product_maturity
set DB_USER=postgres
set DB_PASSWORD=ваш_пароль
set DB_HOST=localhost
set DB_PORT=5432
```

4. Запустите миграции:
```bash
python manage.py migrate
```

### Настройка для продакшена:

1. Измените `DEBUG = False` в settings.py
2. Настройте `ALLOWED_HOSTS`
3. Используйте реальный `SECRET_KEY`
4. Настройте HTTPS
5. Используйте PostgreSQL вместо SQLite
6. Настройте статические файлы (collectstatic)

## 🛠️ Устранение проблем

### Backend не запускается:

```bash
# Проверьте Python версию (должна быть 3.11+)
python --version

# Переустановите зависимости
pip install -r requirements.txt

# Проверьте миграции
python manage.py showmigrations
python manage.py migrate

# Проверьте на ошибки
python manage.py check
```

### Frontend не запускается:

```bash
# Проверьте Node.js версию (должна быть 18+)
node --version

# Очистите кэш и переустановите
rm -rf node_modules package-lock.json
npm install

# Проверьте на ошибки
npm run build
```

### Docker проблемы:

```bash
# Остановите все контейнеры
docker-compose down

# Удалите volumes (ОСТОРОЖНО: удалит данные БД)
docker-compose down -v

# Пересоберите образы
docker-compose build --no-cache

# Запустите снова
docker-compose up
```

## ✅ Все задачи выполнены!

Все функциональные требования реализованы:
- ✅ FR-01: Управление реестром цифровых продуктов
- ✅ FR-02: Конструктор моделей оценки
- ✅ FR-03: Проведение оценочных сессий
- ✅ FR-04: Ввод и верификация данных
- ✅ FR-05: Расчет и визуализация результатов
- ✅ FR-06: Генерация PDF-отчетов
- ✅ FR-07: Управление пользователями и ролями
- ✅ Docker Compose для развертывания

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи серверов в терминалах
2. Убедитесь, что все зависимости установлены
3. Проверьте, что порты 3000 и 8000 свободны
4. Обратитесь к документации Django и React

