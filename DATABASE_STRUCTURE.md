# 🗄️ СТРУКТУРА БАЗЫ ДАННЫХ

## 📌 Общая информация

**СУБД:** PostgreSQL (рекомендуется) или SQLite (для разработки)  
**ORM:** Django ORM (Python)  
**Язык определения моделей:** Python (Django Models)  
**Файл моделей:** `backend/.../core/models.py`

---

## 📊 СХЕМА БАЗЫ ДАННЫХ

```
┌─────────────────────────────────────────────────────────────┐
│                    СИСТЕМА ОЦЕНКИ ЗРЕЛОСТИ                  │
│                    ЦИФРОВЫХ ПРОДУКТОВ                       │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   auth_user      │  ← Встроенная таблица Django
│  (Django User)   │
├──────────────────┤
│ id (PK)          │
│ username         │
│ email            │
│ password         │
│ ...              │
└────────┬─────────┘
         │
         │ 1:1
         │
┌────────▼─────────┐       ┌──────────────┐
│   core_profile   │ N:1   │  core_role   │
├──────────────────┤◄──────┤──────────────┤
│ id (PK)          │       │ id (PK)      │
│ user_id (FK)     │       │ name (UK)    │
│ role_id (FK)     │       └──────────────┘
└────────┬─────────┘
         │
         │ 1:N (created_by)
         │
┌────────▼─────────────────┐      ┌──────────────────┐
│   core_product           │      │   core_domain    │
├──────────────────────────┤      ├──────────────────┤
│ id (PK)                  │      │ id (PK)          │
│ name                     │      │ name (UK)        │
│ description              │      │ description      │
│ department_owner         │      │ weight (%)       │
│ product_link             │      └────────┬─────────┘
│ launch_date              │               │
│ is_archived              │               │ 1:N
└────────┬─────────────────┘               │
         │                         ┌───────▼──────────┐
         │ 1:N                     │  core_criterion  │
         │                         ├──────────────────┤
┌────────▼──────────────────┐     │ id (PK)          │
│ core_evaluationsession    │     │ domain_id (FK)   │
├───────────────────────────┤     │ name             │
│ id (PK)                   │     │ description      │
│ product_id (FK)           │     │ weight (%)       │
│ start_date                │     └────────┬─────────┘
│ end_date                  │              │
│ status                    │              │ 1:N
│ created_by (FK → User)    │              │
└────────┬──────────────────┘     ┌────────▼───────────────┐
         │                        │ core_ratingscale       │
         │ 1:N                    ├────────────────────────┤
         │                        │ id (PK)                │
┌────────▼─────────────────┐     │ criterion_id (FK)      │
│ core_assignedcriterion   │◄────┤ score (1-10)           │
├──────────────────────────┤  N:1│ description            │
│ id (PK)                  │     └────────────────────────┘
│ evaluation_session_id(FK)│
│ criterion_id (FK)        │
│ assigned_to (FK → User)  │
│ is_verified              │
│ [UK: session + criterion]│
└────────┬─────────────────┘
         │
         │ 1:1
         │
┌────────▼─────────────────┐
│ core_evaluationanswer    │
├──────────────────────────┤
│ id (PK)                  │
│ assigned_criterion_id(FK)│
│ score_value (1-10)       │
│ metric_value             │
│ file_evidence            │
│ comment                  │
│ submitted_at             │
└──────────────────────────┘
```

---

## 📋 ТАБЛИЦЫ (10 основных)

### 1. 👤 **auth_user** (Django User)
**Назначение:** Встроенная таблица Django для аутентификации

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Первичный ключ |
| username | String (150) | Имя пользователя (уникальное) |
| email | String (254) | Email пользователя |
| password | String (128) | Хэшированный пароль |
| first_name | String (150) | Имя |
| last_name | String (150) | Фамилия |
| is_staff | Boolean | Доступ к админ-панели |
| is_active | Boolean | Активен ли пользователь |
| date_joined | DateTime | Дата регистрации |

---

### 2. 🎭 **core_role**
**Назначение:** Роли пользователей в системе

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Первичный ключ |
| name | String (50) | Название роли (уникальное) |

**Возможные значения:**
- `admin` - Администратор системы
- `expert` - Эксперт/Аудитор
- `owner` - Владелец продукта
- `observer` - Наблюдатель

---

### 3. 👨‍💼 **core_profile**
**Назначение:** Профили пользователей с дополнительной информацией

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Первичный ключ |
| user_id | Integer (FK) | → auth_user (1:1) |
| role_id | Integer (FK) | → core_role (N:1) |

**Связи:**
- **1:1** с `auth_user` (у каждого пользователя один профиль)
- **N:1** с `core_role` (много профилей → одна роль)

---

### 4. 📦 **core_product**
**Назначение:** Цифровые продукты региона

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Первичный ключ |
| name | String (255) | Наименование продукта |
| description | Text | Описание продукта |
| department_owner | String (255) | Ответственное ведомство |
| product_link | URL | Ссылка на продукт |
| launch_date | Date | Дата запуска |
| is_archived | Boolean | В архиве (по умолчанию False) |

**Индексы:**
- По полю `name` (для сортировки)

---

### 5. 🎯 **core_domain**
**Назначение:** Домены оценки (области зрелости)

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Первичный ключ |
| name | String (255) | Название домена (уникальное) |
| description | Text | Описание домена |
| weight | Decimal (5,2) | Вес в индексе зрелости (0.01-100.00%) |

**Примеры доменов:**
- Технологическая зрелость (30%)
- UX/UI и доступность (25%)
- Безопасность и надежность (25%)
- Аналитика и управление данными (20%)

**Ограничения:**
- `name` должен быть уникальным
- `weight`: 0.01 ≤ weight ≤ 100.00

---

### 6. ✅ **core_criterion**
**Назначение:** Критерии оценки в рамках доменов

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Первичный ключ |
| domain_id | Integer (FK) | → core_domain (N:1) |
| name | String (255) | Название критерия |
| description | Text | Описание критерия |
| weight | Decimal (5,2) | Вес в домене (0.01-100.00%) |

**Примеры критериев:**
- Современность стека технологий
- Архитектура и масштабируемость
- Удобство интерфейса (UX)
- Защита данных

**Ограничения:**
- **UNIQUE**: (domain_id, name) - уникальная пара
- `weight`: 0.01 ≤ weight ≤ 100.00

**Связи:**
- **N:1** с `core_domain` (много критериев → один домен)

---

### 7. 📊 **core_ratingscale**
**Назначение:** Шкалы оценки с описаниями для каждого балла

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Первичный ключ |
| criterion_id | Integer (FK) | → core_criterion (N:1) |
| score | Integer | Балл (1-10) |
| description | Text | Дескриптор балла (описание) |

**Пример:**
```
Критерий: "Современность стека технологий"
├─ Балл 1: "Устаревшие технологии, нет поддержки"
├─ Балл 3: "Технологии требуют обновления"
├─ Балл 5: "Актуальные, но не передовые"
├─ Балл 7: "Современный стек, активная поддержка"
└─ Балл 10: "Передовые технологии, инновационные решения"
```

**Ограничения:**
- **UNIQUE**: (criterion_id, score) - уникальная пара
- `score`: 1 ≤ score ≤ 10

**Связи:**
- **N:1** с `core_criterion` (много шкал → один критерий)

---

### 8. 🎪 **core_evaluationsession**
**Назначение:** Сессии оценки продуктов

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Первичный ключ |
| product_id | Integer (FK) | → core_product (N:1) |
| start_date | Date | Дата начала (автоматически) |
| end_date | Date | Дата окончания |
| status | String (50) | Статус сессии |
| created_by | Integer (FK) | → auth_user (N:1) |

**Статусы:**
- `pending` - В ожидании
- `in_progress` - В процессе
- `completed` - Завершено
- `archived` - В архиве

**Связи:**
- **N:1** с `core_product` (много сессий → один продукт)
- **N:1** с `auth_user` (много сессий → один создатель)
- **1:N** с `core_assignedcriterion` (одна сессия → много критериев)

**Методы (в коде):**
- `get_domain_score(domain_id)` - расчет балла по домену
- `get_overall_maturity_index()` - расчет общего индекса зрелости

---

### 9. 📝 **core_assignedcriterion**
**Назначение:** Связь сессии оценки с критериями (назначение критериев)

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Первичный ключ |
| evaluation_session_id | Integer (FK) | → core_evaluationsession (N:1) |
| criterion_id | Integer (FK) | → core_criterion (N:1) |
| assigned_to | Integer (FK) | → auth_user (N:1) |
| is_verified | Boolean | Верифицировано (по умолчанию False) |

**Ограничения:**
- **UNIQUE**: (evaluation_session_id, criterion_id) 
  - Гарантирует отсутствие дубликатов
  - Один критерий = одна запись в сессии

**Связи:**
- **N:1** с `core_evaluationsession`
- **N:1** с `core_criterion`
- **N:1** с `auth_user` (назначено кому)
- **1:1** с `core_evaluationanswer` (один критерий → один ответ)

**Логика создания:**
- При создании сессии автоматически создаются для ВСЕХ критериев
- Гарантируется ровно 11 записей на сессию (при 11 критериях)

---

### 10. ✍️ **core_evaluationanswer**
**Назначение:** Ответы на критерии (результаты оценки)

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Первичный ключ |
| assigned_criterion_id | Integer (FK) | → core_assignedcriterion (1:1) |
| score_value | Integer | Балл по шкале (1-10) |
| metric_value | Decimal (10,2) | Числовое значение метрики |
| file_evidence | File | Файл-доказательство |
| comment | Text | Комментарий |
| submitted_at | DateTime | Дата отправки (автоматически) |

**Ограничения:**
- `score_value`: 1 ≤ score ≤ 10 (опционально)
- `assigned_criterion_id` - уникальный (1:1 связь)

**Связи:**
- **1:1** с `core_assignedcriterion` (один критерий → один ответ)

---

## 🔗 СВЯЗИ МЕЖДУ ТАБЛИЦАМИ

### Тип связей:

1. **1:1 (Один к одному):**
   - `auth_user` ↔ `core_profile`
   - `core_assignedcriterion` ↔ `core_evaluationanswer`

2. **1:N (Один ко многим):**
   - `core_role` → `core_profile` (одна роль → много профилей)
   - `core_product` → `core_evaluationsession` (один продукт → много сессий)
   - `core_domain` → `core_criterion` (один домен → много критериев)
   - `core_criterion` → `core_ratingscale` (один критерий → много шкал)
   - `core_evaluationsession` → `core_assignedcriterion` (одна сессия → много критериев)
   - `auth_user` → `core_evaluationsession` (один пользователь → много созданных сессий)
   - `auth_user` → `core_assignedcriterion` (один пользователь → много назначенных критериев)

3. **N:M (Многие ко многим) через промежуточную таблицу:**
   - `core_evaluationsession` ↔ `core_criterion` через `core_assignedcriterion`

---

## 📐 НОРМАЛИЗАЦИЯ

База данных находится в **3NF (Третьей нормальной форме):**

✅ **1NF** - Все поля атомарны, нет повторяющихся групп  
✅ **2NF** - Нет частичной зависимости от ключа  
✅ **3NF** - Нет транзитивных зависимостей

**Пример нормализации:**
- Роли вынесены в отдельную таблицу `core_role`
- Домены отделены от критериев
- Оценочные сессии отделены от ответов

---

## 🔒 ОГРАНИЧЕНИЯ И ИНДЕКСЫ

### Уникальные ограничения (UNIQUE):

1. **core_domain.name** - название домена
2. **core_criterion (domain_id, name)** - критерий уникален в домене
3. **core_ratingscale (criterion_id, score)** - балл уникален для критерия
4. **core_assignedcriterion (evaluation_session_id, criterion_id)** - критерий уникален в сессии
5. **core_role.name** - название роли
6. **auth_user.username** - имя пользователя

### Внешние ключи (FOREIGN KEY):

**Всего: 14 внешних ключей**

**С каскадным удалением (CASCADE):**
- `core_criterion.domain_id`
- `core_ratingscale.criterion_id`
- `core_evaluationsession.product_id`
- `core_assignedcriterion.evaluation_session_id`
- `core_assignedcriterion.criterion_id`
- `core_evaluationanswer.assigned_criterion_id`
- `core_profile.user_id`

**С установкой NULL (SET_NULL):**
- `core_evaluationsession.created_by`
- `core_assignedcriterion.assigned_to`
- `core_profile.role_id`

### Индексы:

**Автоматические индексы:**
- Все первичные ключи (PK)
- Все внешние ключи (FK)
- Все уникальные поля (UNIQUE)

**Дополнительные индексы (ordering):**
- `core_product.name`
- `core_domain.name`
- `core_criterion (domain, name)`
- `core_evaluationsession.start_date`

---

## 💾 РАЗМЕР И ХРАНЕНИЕ

### Текущие объемы (пример):

```
Таблица                      | Записей | Размер
-----------------------------|---------|--------
auth_user                    | 1       | ~1 KB
core_role                    | 4       | <1 KB
core_profile                 | 1       | <1 KB
core_product                 | 4       | ~2 KB
core_domain                  | 4       | ~1 KB
core_criterion               | 11      | ~5 KB
core_ratingscale             | 55      | ~10 KB
core_evaluationsession       | 7       | ~2 KB
core_assignedcriterion       | 77      | ~5 KB
core_evaluationanswer        | 30      | ~10 KB
-----------------------------|---------|--------
ИТОГО                        | 194     | ~37 KB
```

### Ожидаемый рост:

**При 100 продуктах и 10 сессиях на продукт:**
```
core_product:              100 записей
core_evaluationsession:    1,000 сессий
core_assignedcriterion:    11,000 записей (11 критериев × 1,000)
core_evaluationanswer:     11,000 ответов

Ожидаемый размер: ~50-100 MB
```

**Масштабируемость:** До 1000+ продуктов без проблем

---

## 🔄 ЖИЗНЕННЫЙ ЦИКЛ ДАННЫХ

### Создание оценки:

```
1. Создается продукт (core_product)
   ↓
2. Создается сессия оценки (core_evaluationsession)
   ↓
3. Автоматически создаются назначенные критерии (core_assignedcriterion)
   ├─ Для КАЖДОГО критерия из core_criterion
   ├─ Ровно 11 записей (если 11 критериев)
   └─ Связь: session + criterion (уникальная)
   ↓
4. Заполняются ответы (core_evaluationanswer)
   ├─ По мере оценки
   ├─ Связь 1:1 с core_assignedcriterion
   └─ Можно сохранять частично
   ↓
5. Расчет результатов
   ├─ Балл по домену = Σ(балл × вес критерия) / Σ(вес)
   └─ Общий индекс = Σ(балл домена × вес домена) / Σ(вес доменов)
```

### Удаление:

**Каскадное удаление:**
- Удаление продукта → удаляются все сессии → все критерии → все ответы
- Удаление домена → удаляются все критерии → все шкалы
- Удаление пользователя → профиль удаляется, сессии обнуляются (SET_NULL)

---

## 🛠️ ТЕХНИЧЕСКИЕ ДЕТАЛИ

### Django ORM:

**Язык:** Python  
**Фреймворк:** Django 5.2.9  
**ORM:** Django ORM (встроенный)

**Преимущества Django ORM:**
- ✅ Автоматическая миграция схемы
- ✅ Защита от SQL-инъекций
- ✅ Поддержка множества СУБД
- ✅ Встроенная админ-панель
- ✅ Сигналы для автоматизации
- ✅ Валидация на уровне моделей

### Миграции:

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Просмотр SQL миграций
python manage.py sqlmigrate core 0001
```

### Типы полей Django → SQL:

| Django Field | PostgreSQL | SQLite |
|--------------|------------|--------|
| CharField | VARCHAR(n) | TEXT |
| TextField | TEXT | TEXT |
| IntegerField | INTEGER | INTEGER |
| DecimalField | NUMERIC(m,d) | REAL |
| DateField | DATE | TEXT |
| DateTimeField | TIMESTAMP | TEXT |
| BooleanField | BOOLEAN | INTEGER |
| URLField | VARCHAR(200) | TEXT |
| FileField | VARCHAR(100) | TEXT |

---

## 📊 ПРИМЕРЫ ЗАПРОСОВ

### SQL-эквиваленты Django ORM:

**1. Получить все продукты:**
```python
# Django ORM
Product.objects.all()

# SQL
SELECT * FROM core_product;
```

**2. Получить сессии для продукта:**
```python
# Django ORM
EvaluationSession.objects.filter(product_id=1)

# SQL
SELECT * FROM core_evaluationsession 
WHERE product_id = 1;
```

**3. Получить критерии с доменами:**
```python
# Django ORM
Criterion.objects.select_related('domain')

# SQL
SELECT c.*, d.*
FROM core_criterion c
INNER JOIN core_domain d ON c.domain_id = d.id;
```

**4. Получить ответы для сессии:**
```python
# Django ORM
AssignedCriterion.objects.filter(
    evaluation_session_id=1
).select_related('answer', 'criterion')

# SQL
SELECT ac.*, ea.*, cr.*
FROM core_assignedcriterion ac
LEFT JOIN core_evaluationanswer ea ON ac.id = ea.assigned_criterion_id
INNER JOIN core_criterion cr ON ac.criterion_id = cr.id
WHERE ac.evaluation_session_id = 1;
```

---

## 🎯 ИТОГОВАЯ ИНФОРМАЦИЯ

**Всего таблиц:** 10  
**Всего полей:** ~50  
**Всего связей:** 14  
**Уникальных ограничений:** 6  
**Индексов:** ~20  

**Язык определения:** Python (Django Models)  
**СУБД:** PostgreSQL / SQLite  
**ORM:** Django ORM  
**Нормализация:** 3NF  

**Файл моделей:** `backend/digital_product_maturity_project/digital_product_maturity/core/models.py`

---

## 📚 ДОПОЛНИТЕЛЬНО

### Визуализация схемы:

Для генерации ER-диаграммы используйте:

```bash
# Установка
pip install django-extensions pygraphviz

# Добавьте в INSTALLED_APPS: 'django_extensions'

# Генерация диаграммы
python manage.py graph_models core -o database_schema.png
```

### Экспорт данных:

```bash
# Экспорт всей БД в JSON
python manage.py dumpdata > database_backup.json

# Экспорт конкретной таблицы
python manage.py dumpdata core.Product > products.json

# Импорт
python manage.py loaddata database_backup.json
```

### Админ-панель:

Доступ к управлению БД через Django Admin:
- URL: http://127.0.0.1:8000/admin/
- Логин: `admin`
- Пароль: `admin123`

---

**📖 Этот документ описывает полную структуру базы данных системы оценки зрелости цифровых продуктов.**

