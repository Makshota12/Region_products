# 🗄️ БАЗА ДАННЫХ - КРАТКАЯ СПРАВКА

## 📌 ОСНОВНАЯ ИНФОРМАЦИЯ

**База данных:** PostgreSQL  
**Язык:** Python (Django ORM)  
**Файл моделей:** `backend/.../core/models.py`  
**Всего таблиц:** 10

---

## 🎨 ВИЗУАЛЬНАЯ СХЕМА

```
┌─────────────────────────────────────────────────────────────┐
│                  🏢 СИСТЕМА ОЦЕНКИ ЗРЕЛОСТИ                 │
│               ЦИФРОВЫХ ПРОДУКТОВ РЕГИОНА                    │
└─────────────────────────────────────────────────────────────┘

ПОЛЬЗОВАТЕЛИ                 ПРОДУКТЫ                ОЦЕНКА
───────────────              ──────────              ───────

👤 User                      📦 Product              🎯 Domain
   │                            │                        │
   │                            │                        │
   ├─ Profile (1:1)            │                        │
   │    └─ Role (N:1)          │                        └─ Criterion (1:N)
   │                            │                             │
   │                            └─ EvaluationSession (1:N)    │
   │                                     │                     │
   │                                     │                     │
   └───────────────────┬─────────────────┴─────────────────────┘
                       │
              AssignedCriterion (сессия + критерий)
                       │
                       │
              EvaluationAnswer (ответы)


РОЛИ:                   СТАТУСЫ СЕССИИ:          БАЛЛЫ:
• 👑 Администратор      • ⏳ В ожидании          • 1-10
• 🔍 Эксперт            • 🔄 В процессе          • Описание для каждого
• 📦 Владелец           • ✅ Завершено           • RatingScale
• 👀 Наблюдатель        • 🗄️ В архиве
```

---

## 📋 ТАБЛИЦЫ (10 шт)

### 1️⃣ **auth_user** - Пользователи Django
```
• id, username, email, password
• Встроенная таблица аутентификации
```

### 2️⃣ **core_role** - Роли (4 роли)
```
• id, name
• admin, expert, owner, observer
```

### 3️⃣ **core_profile** - Профили
```
• id, user_id (1:1), role_id (N:1)
• Расширение пользователя
```

### 4️⃣ **core_product** - Цифровые продукты
```
• id, name, description
• department_owner, product_link
• launch_date, is_archived
```

### 5️⃣ **core_domain** - Домены оценки (4 домена)
```
• id, name (UK), description, weight (%)
• Технологии, UX/UI, Безопасность, Аналитика
```

### 6️⃣ **core_criterion** - Критерии (11 критериев)
```
• id, domain_id (N:1), name, description, weight (%)
• UK: (domain_id, name)
```

### 7️⃣ **core_ratingscale** - Шкалы оценки
```
• id, criterion_id (N:1), score (1-10), description
• UK: (criterion_id, score)
• 5 баллов на критерий (1,3,5,7,10)
```

### 8️⃣ **core_evaluationsession** - Сессии оценки
```
• id, product_id (N:1), start_date, end_date
• status, created_by (N:1 → User)
```

### 9️⃣ **core_assignedcriterion** - Назначенные критерии
```
• id, evaluation_session_id (N:1)
• criterion_id (N:1), assigned_to (N:1 → User)
• is_verified
• UK: (evaluation_session_id, criterion_id) ← НЕТ ДУБЛИКАТОВ!
```

### 🔟 **core_evaluationanswer** - Ответы на критерии
```
• id, assigned_criterion_id (1:1)
• score_value (1-10), metric_value
• file_evidence, comment, submitted_at
```

---

## 🔗 СВЯЗИ

```
User ─────1:1───── Profile ─────N:1───── Role
  │
  │ created_by
  └───────N:1───── EvaluationSession
                         │
                         │ 1:N
                         │
Product ────1:N───── EvaluationSession ────1:N───── AssignedCriterion ────1:1───── EvaluationAnswer
                                                           │
                                                           │ N:1
Domain ────1:N───── Criterion ────1:N───── RatingScale    │
                         │                                 │
                         └─────────────────N:1─────────────┘
```

---

## 🎯 КЛЮЧЕВЫЕ МОМЕНТЫ

### ✅ Защита от дубликатов:
```sql
UNIQUE (evaluation_session_id, criterion_id)
```
**Гарантия:** Один критерий = одна запись в сессии

### 📊 Текущие данные:
```
Продуктов:     4
Доменов:       4
Критериев:     11
Сессий:        7
Критериев×Сессий: 77 (7 × 11 = 77)
```

### 🔄 Жизненный цикл:
```
1. Создать продукт
2. Создать сессию оценки
3. Автоматически создаются 11 критериев (AssignedCriterion)
4. Заполняются ответы (EvaluationAnswer)
5. Расчет результатов:
   • Балл по домену
   • Общий индекс зрелости (1-10)
```

---

## 💡 ФОРМУЛЫ РАСЧЕТА

### Балл по домену:
```
Балл_домена = Σ(Балл_критерия × Вес_критерия) / Σ(Вес_критериев)
```

### Общий индекс зрелости:
```
Индекс = Σ(Балл_домена × Вес_домена) / Σ(Вес_доменов)
```

**Результат:** Число от 1 до 10

**Интерпретация:**
- 8-10: 🏆 Превосходный
- 6-8: 🥇 Высокий
- 4-6: 🥈 Средний
- 2-4: 🥉 Низкий
- 0-2: ⚠️ Критический

---

## 🛠️ КОМАНДЫ DJANGO

### Миграции:
```bash
python manage.py makemigrations  # Создать миграции
python manage.py migrate         # Применить миграции
```

### Данные:
```bash
python manage.py dumpdata > backup.json  # Экспорт
python manage.py loaddata backup.json    # Импорт
```

### Проверка:
```bash
python manage.py dbshell  # Подключиться к БД
```

---

## 📊 SQL ПРИМЕРЫ

### Получить все сессии продукта:
```sql
SELECT * FROM core_evaluationsession
WHERE product_id = 1;
```

### Получить критерии сессии с ответами:
```sql
SELECT 
    ac.id,
    c.name AS criterion_name,
    ea.score_value
FROM core_assignedcriterion ac
JOIN core_criterion c ON ac.criterion_id = c.id
LEFT JOIN core_evaluationanswer ea ON ac.id = ea.assigned_criterion_id
WHERE ac.evaluation_session_id = 1;
```

### Проверить дубликаты:
```sql
SELECT 
    evaluation_session_id,
    criterion_id,
    COUNT(*)
FROM core_assignedcriterion
GROUP BY evaluation_session_id, criterion_id
HAVING COUNT(*) > 1;
```

---

## 🎨 СТРУКТУРА ФАЙЛОВ

```
backend/
└── digital_product_maturity_project/
    ├── digital_product_maturity/
    │   ├── core/
    │   │   ├── models.py         ← 📌 МОДЕЛИ (ЗДЕСЬ!)
    │   │   ├── views.py
    │   │   ├── serializers.py
    │   │   ├── urls.py
    │   │   └── signals.py
    │   └── settings.py
    └── db.sqlite3                ← База данных (если SQLite)
```

---

## 🔍 ДИАГНОСТИКА

### Проверка количества записей:
```bash
cd backend/digital_product_maturity_project
python clean_duplicates.py
```

### Ожидаемые результаты:
```
Сессий: N
Критериев в системе: 11
Ожидается AssignedCriterion: N × 11
Фактически: N × 11
[OK] Дубликаты не найдены!
```

---

## 📚 ПОЛНАЯ ДОКУМЕНТАЦИЯ

Подробная документация: **`DATABASE_STRUCTURE.md`**

Содержит:
- Детальное описание всех полей
- ER-диаграмму
- Примеры запросов
- Объяснение связей
- Формулы расчета

---

## 🎯 БЫСТРЫЙ СТАРТ

### 1. Создать администратора:
```bash
python manage.py createsuperuser
```

### 2. Заполнить базовые данные:
```bash
python create_superuser.py
python populate_db.py
```

### 3. Открыть админку:
```
http://127.0.0.1:8000/admin/
Логин: admin
Пароль: admin123
```

---

**📖 Для детального изучения откройте: `DATABASE_STRUCTURE.md`**

