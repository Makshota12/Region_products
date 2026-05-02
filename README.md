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
- Интерактивные дашборды (радарный, столбчатый, круговой графики)

### Отчётность
- PDF-паспорт зрелости продукта (на русском языке)
- Сводный отчёт по портфелю продуктов

### Пользователи и роли
- Регистрация и авторизация
- Профили пользователей
- Роли: Администратор, Эксперт, Владелец продукта, Наблюдатель

---

## 🏗 Архитектура приложения

### 🧱 Стиль архитектуры — Modular Monolith + SPA frontend

Приложение спроектировано как **монолитный backend** на Django + REST API и **отдельный SPA-фронтенд** на React. В литературе такой стиль называют **«headless monolith»** или **«decoupled monolith»** — это **не микросервисы**, а «толстый» монолит, у которого UI вынесен в отдельное JS-приложение и общается с ядром только по REST/JSON.

**Почему именно монолит, а не микросервисы:**

| Критерий | Решение и обоснование |
|---|---|
| **Масштаб команды** | 1–2 разработчика — микросервисы дают больше операционных издержек, чем выгод. |
| **Нагрузка** | Внутренний инструмент оценки (десятки–сотни оценок в день) — одного процесса Django более чем достаточно. |
| **Транзакционность** | Расчёт интегральных индексов и сохранение ответов должны быть в одной транзакции БД — в монолите это бесплатно, в микросервисах потребовало бы Saga / 2PC. |
| **Стоимость инфраструктуры** | Один контейнер backend + один контейнер БД vs. 5–7 сервисов + брокер сообщений + service mesh. |
| **Скорость релизов** | Один `docker compose up` — никаких распределённых деплоев. |
| **Целостность модели данных** | Все доменные сущности (Product, Domain, Criterion, Session, Answer, User) ссылаются друг на друга через FK — единая БД упрощает целостность. |

**Состав системы (фактический):**

- **Backend** — один Django-проект `digital_product_maturity_project` с одним Django-приложением `core`, в котором размещены **все** доменные модули: каталог продуктов, конструктор модели оценки, проведение сессий, расчёт индексов, генерация PDF, аутентификация, RBAC, аудит. Один процесс — одна БД (PostgreSQL/SQLite).
- **Frontend** — React SPA (`frontend/`), общающийся с backend через `axios` по REST + JWT.
- **БД** — PostgreSQL (prod) или SQLite (dev), общая для всего домена.
- **Внешние сервисы** — только Google OAuth 2.0 для социального логина.

**Применённые архитектурные паттерны внутри монолита:**

- **MVC / MVT** — стандартный Django-паттерн (Model–View–Template, в нашем случае Template = DRF Serializer).
- **Repository через ORM** — доступ к данным только через Django ORM, никаких сырых SQL.
- **DTO через DRF Serializers** — внешний контракт API изолирован от моделей.
- **RBAC через Permission classes** — `CatalogPermission`, `ProductPermission`, `EvaluationPermission` (см. `core/views.py`).
- **Signals** для побочных эффектов (создание `Profile` при создании `User`).

**Готовность к эволюции (если когда-то понадобятся микросервисы):**

Сейчас всё бизнес-приложение лежит в одной Django-app `core`. Чтобы превратить его в **модульный монолит** (промежуточный шаг перед микросервисами), достаточно разнести `core` на 5 Django-apps:

```text
core/  →  products/        (каталог)
          model_builder/   (домены, критерии, шкалы)
          evaluations/     (сессии, ответы, расчёт индексов)
          reporting/       (PDF, графики, дашборд)
          accounts/        (User, Profile, RBAC, Google OAuth)
```

После такого разделения границы доменов становятся явными, и в будущем любой модуль (например, `reporting` с `matplotlib` и Celery) можно вынести в самостоятельный сервис без переписывания остального кода.

```mermaid
%%{init: {'theme':'default'}}%%
flowchart LR
    classDef ext fill:#cfe8ff,stroke:#3a7bd5,stroke-width:2px,color:#0b3d91
    classDef mono fill:#d4f7d4,stroke:#1e8449,stroke-width:2.5px,color:#0e3d1e
    classDef db fill:#f0f0f0,stroke:#4a4a4a,stroke-width:1.5px,color:#1f2937
    classDef svc fill:#fde2e4,stroke:#c0392b,stroke-width:2px,color:#7a1d12

    User["👤 Пользователь<br/>(браузер)"]:::ext
    SPA["⚛️ React SPA<br/>(frontend)"]:::ext
    Mono["🧱 Django Monolith<br/>(один процесс, app: core)<br/>—————————————<br/>products • model_builder<br/>evaluations • reporting<br/>accounts"]:::mono
    DB[("🗄 PostgreSQL<br/>(одна БД)")]:::db
    Google["🔐 Google OAuth"]:::svc

    User <--> SPA
    SPA -- "REST + JWT" --> Mono
    Mono -- "JSON" --> SPA
    Mono <--> DB
    Mono -- "id_token verify" --> Google
```

**Вывод:** для текущего масштаба и команды — **монолит — правильный выбор**. Архитектура спроектирована так, чтобы при росте нагрузки её можно было плавно превратить в модульный монолит, а затем — точечно вынести нужные модули в сервисы, не переписывая всё.

---

### Общая схема архитектуры

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              КЛИЕНТ (Браузер)                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         React Frontend                               │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ProductList│ │DomainList│ │Evaluation│ │ Results  │ │ Profile  │  │   │
│  │  │          │ │          │ │  Input   │ │Dashboard │ │          │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  │                              │                                       │   │
│  │                    ┌─────────▼─────────┐                            │   │
│  │                    │   React Router    │                            │   │
│  │                    │    + Axios        │                            │   │
│  │                    └─────────┬─────────┘                            │   │
│  └──────────────────────────────┼──────────────────────────────────────┘   │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │ HTTP/REST API
                                  │ JSON
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                              СЕРВЕР                                         │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Django Backend                                  │   │
│  │                                                                      │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │   │
│  │  │   URL Router   │  │   Views/API    │  │  Serializers   │        │   │
│  │  │   (urls.py)    │──│  (views.py)    │──│(serializers.py)│        │   │
│  │  └────────────────┘  └───────┬────────┘  └────────────────┘        │   │
│  │                              │                                       │   │
│  │  ┌────────────────┐  ┌───────▼────────┐  ┌────────────────┐        │   │
│  │  │   Auth Views   │  │    Models      │  │    Signals     │        │   │
│  │  │(auth_views.py) │  │  (models.py)   │  │  (signals.py)  │        │   │
│  │  └────────────────┘  └───────┬────────┘  └────────────────┘        │   │
│  │                              │                                       │   │
│  │  ┌────────────────┐  ┌───────▼────────┐  ┌────────────────┐        │   │
│  │  │  PDF Generator │  │  Django ORM    │  │   Migrations   │        │   │
│  │  │  (ReportLab)   │  │                │  │                │        │   │
│  │  └────────────────┘  └───────┬────────┘  └────────────────┘        │   │
│  └──────────────────────────────┼──────────────────────────────────────┘   │
│                                 │                                           │
│  ┌──────────────────────────────▼──────────────────────────────────────┐   │
│  │                        База данных                                   │   │
│  │                  SQLite / PostgreSQL                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Архитектура компонентов

```
┌───────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                               │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   Pages (Страницы)              Components (Компоненты)               │
│   ├── ProductList.js            ├── App.js (главный)                 │
│   ├── ProductForm.js            ├── App.css (стили)                  │
│   ├── ProductDetail.js          └── setupProxy.js                    │
│   ├── DomainList.js                                                  │
│   ├── DomainForm.js             Services (Сервисы)                   │
│   ├── CriterionList.js          └── Axios (HTTP клиент)              │
│   ├── CriterionForm.js                                               │
│   ├── EvaluationSessionList.js  Visualization (Визуализация)         │
│   ├── EvaluationSessionForm.js  └── Chart.js (графики)               │
│   ├── EvaluationInput.js                                             │
│   ├── EvaluationResults.js                                           │
│   ├── Login.js                                                       │
│   ├── Register.js                                                    │
│   └── Profile.js                                                     │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                        BACKEND (Django)                               │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   Core App                      Settings                              │
│   ├── models.py (8 моделей)     ├── settings.py                      │
│   ├── views.py (ViewSets)       ├── urls.py                          │
│   ├── serializers.py            └── wsgi.py / asgi.py                │
│   ├── urls.py (API routes)                                           │
│   ├── signals.py                Utils                                 │
│   ├── auth_views.py             ├── create_superuser.py              │
│   ├── admin.py                  ├── populate_db.py                   │
│   └── apps.py                   └── check_data.py                    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

### Паттерн взаимодействия (Request Flow)

```
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│ Browser│───▶│ React  │───▶│ Axios  │───▶│ Django │───▶│  DB    │
│        │    │  App   │    │ HTTP   │    │  API   │    │        │
└────────┘    └────────┘    └────────┘    └────────┘    └────────┘
     ▲                                          │
     │              JSON Response               │
     └──────────────────────────────────────────┘
```

### Архитектура приложения (Mermaid)

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'background':'#ffffff','mainBkg':'#ffffff','secondBkg':'#ffffff','tertiaryColor':'#ffffff','lineColor':'#1f2937','textColor':'#111111'}}}%%
graph TB
    subgraph Browser["🌐 Браузер (Клиент)"]
        UI[React SPA]
        Router[React Router]
        HTTP[Axios HTTP Client]
        UI --> Router
        Router --> HTTP
    end
    
    subgraph Backend["🖥️ Django Backend"]
        URLConf[URL Router]
        Views[ViewSets & API Views]
        Serializers[DRF Serializers]
        Models[Django Models]
        Auth[JWT Auth + Google OAuth]
        Permissions[Role-Based Permissions]
        ORM[Django ORM]
        PDF[ReportLab PDF Generator]
        
        URLConf --> Views
        Views --> Serializers
        Views --> Auth
        Views --> Permissions
        Serializers --> Models
        Models --> ORM
        Views --> PDF
    end
    
    subgraph Storage["💾 Хранилище"]
        DB[(SQLite/PostgreSQL)]
        Media[Media Files]
    end
    
    HTTP -->|REST API<br/>JSON| URLConf
    Views -->|Query/Save| ORM
    ORM --> DB
    Views -->|Upload/Retrieve| Media
    Views -.->|JSON Response| HTTP
    
    style Browser fill:#e3f2fd
    style Backend fill:#fff3e0
    style Storage fill:#f3e5f5
    style UI fill:#667eea,color:#fff
    style Views fill:#764ba2,color:#fff
    style DB fill:#27ae60,color:#fff
```

### Поток запроса (Sequence Diagram)

```mermaid
%%{init: {'theme':'default', 'themeVariables': {'background':'#ffffff'}}}%%
sequenceDiagram
    participant U as 👤 Пользователь
    participant R as React App
    participant A as Axios
    participant D as Django API
    participant DB as База данных
    
    U->>R: Открывает страницу /products
    R->>A: GET /api/products/
    A->>A: Добавляет JWT токен<br/>из localStorage
    A->>D: HTTP Request + Authorization
    D->>D: Проверка JWT
    D->>D: Проверка прав доступа
    D->>DB: SELECT * FROM products
    DB-->>D: Данные продуктов
    D->>D: Сериализация (JSON)
    D-->>A: HTTP 200 + JSON
    A-->>R: Response data
    R->>R: Рендер компонента
    R-->>U: Отображение списка
    
    U->>R: Нажимает "Создать продукт"
    R->>A: POST /api/products/
    A->>D: HTTP Request + JWT + данные
    D->>D: Проверка роли (IsAdminRoleOrReadOnly)
    alt Пользователь - Admin
        D->>DB: INSERT INTO products
        DB-->>D: Success
        D-->>A: HTTP 201 Created
        A-->>R: Success
        R-->>U: ✅ Продукт создан
    else Пользователь - Observer
        D-->>A: HTTP 403 Forbidden
        A-->>R: Error
        R-->>U: ❌ Доступ запрещён
    end
```

### Архитектура компонентов (Mermaid)

```mermaid
%%{init: {'theme':'default', 'themeVariables': {'background':'#ffffff'}}}%%
graph LR
    subgraph Frontend["Frontend (React)"]
        direction TB
        Pages[Pages]
        Components[Components]
        Services[Services]
        
        Pages --> |ProductList<br/>DomainList<br/>EvaluationInput<br/>Profile<br/>Login| Components
        Components --> |App.js<br/>App.css<br/>Router| Services
        Services --> |Axios<br/>setupProxy| API
    end
    
    subgraph Backend["Backend (Django)"]
        direction TB
        Core[Core App]
        Settings[Settings]
        Utils[Utils]
        
        Core --> |models.py<br/>views.py<br/>serializers.py<br/>auth_views.py<br/>admin.py| Settings
        Settings --> |settings.py<br/>urls.py<br/>wsgi.py| Utils
        Utils --> |create_superuser<br/>populate_db<br/>check_data| DB
    end
    
    subgraph Data["Data Layer"]
        DB[(Database)]
        Media[Media Storage]
    end
    
    API[REST API<br/>JSON]
    
    Frontend -->|HTTP/HTTPS| API
    API -->|DRF ViewSets| Backend
    Backend -->|ORM| Data
    
    style Frontend fill:#e3f2fd
    style Backend fill:#fff3e0
    style Data fill:#f3e5f5
    style Pages fill:#667eea,color:#fff
    style Core fill:#764ba2,color:#fff
    style DB fill:#27ae60,color:#fff
```

---

## 🗄 Структура базы данных

### ER-диаграмма (сущность-связь)

```
Продукт (1) --------------------< (N) СессияОценки >-------------------- (1) Пользователь [created_by, SET_NULL]
  id PK                               id PK                                         id PK
  name                                product_id FK -> Product.id                  username, email, ...
  description                         created_by_id FK -> User.id (nullable)
  department_owner                    start_date, end_date, status
  product_link
  launch_date
  is_archived

Домен (1) ---------------------< (N) Критерий (1) ------------------------< (N) ШкалаОценки
  id PK                               id PK                                       id PK
  name                                domain_id FK -> Domain.id                   criterion_id FK -> Criterion.id
  description                         name, description, weight                   score (1..10), description
  weight

СессияОценки (1) ----------< (N) НазначенныйКритерий >------------------- (1) Критерий
                                    id PK                                         id PK
                                    evaluation_session_id FK -> EvaluationSession.id
                                    criterion_id FK -> Criterion.id
                                    assigned_to_id FK -> User.id (nullable, SET_NULL)
                                    is_verified
                                    UNIQUE(evaluation_session_id, criterion_id)

НазначенныйКритерий (1) ---------- (1) ОтветОценки
                                   id PK
                                   assigned_criterion_id FK UNIQUE -> AssignedCriterion.id
                                   score_value, metric_value, file_evidence, comment, submitted_at

Пользователь (1) ------------------------ (1) Профиль >------------------------------ (N) Роль
  id PK                              id PK                                        id PK
  username, email, ...               user_id FK UNIQUE -> User.id                 name (admin|expert|owner|observer)
                                    role_id FK -> Role.id (nullable, SET_NULL)
```

### ER-диаграмма (Mermaid)

```mermaid
%%{init: {'theme':'default', 'themeVariables': {'background':'#ffffff'}}}%%
erDiagram
    ПРОДУКТ ||--o{ СЕССИЯ_ОЦЕНКИ : "имеет сессии"
    ДОМЕН ||--o{ КРИТЕРИЙ : "содержит критерии"
    КРИТЕРИЙ ||--o{ ШКАЛА_ОЦЕНКИ : "определяет шкалу"
    СЕССИЯ_ОЦЕНКИ ||--o{ НАЗНАЧЕННЫЙ_КРИТЕРИЙ : "включает назначения"
    КРИТЕРИЙ ||--o{ НАЗНАЧЕННЫЙ_КРИТЕРИЙ : "назначается как"
    НАЗНАЧЕННЫЙ_КРИТЕРИЙ ||--|| ОТВЕТ_ОЦЕНКИ : "имеет ответ"
    ПОЛЬЗОВАТЕЛЬ ||--o{ СЕССИЯ_ОЦЕНКИ : "создает"
    ПОЛЬЗОВАТЕЛЬ ||--o{ НАЗНАЧЕННЫЙ_КРИТЕРИЙ : "назначен на"
    ПОЛЬЗОВАТЕЛЬ ||--|| ПРОФИЛЬ : "имеет профиль"
    РОЛЬ ||--o{ ПРОФИЛЬ : "назначается в профиль"

    ПРОДУКТ {
        int идентификатор PK "id"
        string название "name"
        text описание "description"
        string владелец_ведомство "department_owner"
        string ссылка_на_продукт "product_link"
        date дата_запуска "launch_date"
        bool в_архиве "is_archived"
    }

    ДОМЕН {
        int идентификатор PK "id"
        string название "name"
        text описание "description"
        decimal вес "weight"
    }

    КРИТЕРИЙ {
        int идентификатор PK "id"
        int домен_id FK "domain_id"
        string название "name"
        text описание "description"
        decimal вес "weight"
    }

    ШКАЛА_ОЦЕНКИ {
        int идентификатор PK "id"
        int критерий_id FK "criterion_id"
        int балл "score"
        text описание "description"
    }

    СЕССИЯ_ОЦЕНКИ {
        int идентификатор PK "id"
        int продукт_id FK "product_id"
        int создано_пользователем_id FK "created_by_id"
        date дата_начала "start_date"
        date дата_завершения "end_date"
        string статус "status"
    }

    НАЗНАЧЕННЫЙ_КРИТЕРИЙ {
        int идентификатор PK "id"
        int сессия_оценки_id FK "evaluation_session_id"
        int критерий_id FK "criterion_id"
        int назначено_пользователю_id FK "assigned_to_id"
        bool подтверждено "is_verified"
    }

    ОТВЕТ_ОЦЕНКИ {
        int идентификатор PK "id"
        int назначенный_критерий_id FK "assigned_criterion_id"
        int значение_балла "score_value"
        decimal значение_метрики "metric_value"
        string файл_доказательство "file_evidence"
        text комментарий "comment"
        datetime отправлено_в "submitted_at"
    }

    ПОЛЬЗОВАТЕЛЬ {
        int идентификатор PK "id"
        string логин "username"
        string email "email"
    }

    ПРОФИЛЬ {
        int идентификатор PK "id"
        int пользователь_id FK "user_id"
        int роль_id FK "role_id"
    }

    РОЛЬ {
        int идентификатор PK "id"
        string название "name"
    }
```

### Кардинальности и правила связей

- `Продукт 1:N СессияОценки` — у продукта может быть много сессий оценки.
- `Домен 1:N Критерий` — каждый критерий принадлежит ровно одному домену.
- `Критерий 1:N ШкалаОценки` — у критерия несколько уровней шкалы.
- `СессияОценки N:M Критерий` реализовано через `НазначенныйКритерий`.
- `НазначенныйКритерий 1:1 ОтветОценки` — на один назначенный критерий максимум один ответ.
- `Пользователь 1:N СессияОценки` через `created_by` (`SET_NULL` при удалении пользователя).
- `Пользователь 1:N НазначенныйКритерий` через `assigned_to` (`SET_NULL` при удалении пользователя).
- `Пользователь 1:1 Профиль` — профиль создается для каждого пользователя.
- `Роль 1:N Профиль` — роль может быть назначена многим пользователям; роль в профиле может быть `NULL`.

### Описание таблиц

#### Продукт (`Product`)
| Поле | Тип | Описание |
|------|-----|----------|
| идентификатор (`id`) | INTEGER | Первичный ключ (AUTO) |
| название (`name`) | VARCHAR(255) | Название продукта |
| описание (`description`) | TEXT | Описание продукта |
| владелец_ведомство (`department_owner`) | VARCHAR(255) | Владелец/ведомство |
| ссылка_на_продукт (`product_link`) | URL | Ссылка на продукт |
| дата_запуска (`launch_date`) | DATE | Дата запуска |
| в_архиве (`is_archived`) | BOOLEAN | Флаг архивации |

#### Домен оценки (`Domain`)
| Поле | Тип | Описание |
|------|-----|----------|
| идентификатор (`id`) | INTEGER | Первичный ключ (AUTO) |
| название (`name`) | VARCHAR(255) | Название домена (уникальное) |
| описание (`description`) | TEXT | Описание домена |
| вес (`weight`) | DECIMAL(5,2) | Вес в общем индексе (0.01-100%) |

#### Критерий оценки (`Criterion`)
| Поле | Тип | Описание |
|------|-----|----------|
| идентификатор (`id`) | INTEGER | Первичный ключ (AUTO) |
| домен_id (`domain_id`) | FK → Domain | Внешний ключ на домен |
| название (`name`) | VARCHAR(255) | Название критерия |
| описание (`description`) | TEXT | Описание критерия |
| вес (`weight`) | DECIMAL(5,2) | Вес в домене (0.01-100%) |

#### Шкала оценки (`RatingScale`)
| Поле | Тип | Описание |
|------|-----|----------|
| идентификатор (`id`) | INTEGER | Первичный ключ (AUTO) |
| критерий_id (`criterion_id`) | FK → Criterion | Внешний ключ на критерий |
| балл (`score`) | INTEGER | Балл (1-10) |
| описание (`description`) | TEXT | Текстовое описание балла |

#### Сессия оценки (`EvaluationSession`)
| Поле | Тип | Описание |
|------|-----|----------|
| идентификатор (`id`) | INTEGER | Первичный ключ (AUTO) |
| продукт_id (`product_id`) | FK → Product | Оцениваемый продукт |
| создано_пользователем (`created_by`) | FK → User | Создатель сессии |
| дата_начала (`start_date`) | DATE | Дата начала (AUTO) |
| дата_завершения (`end_date`) | DATE | Дата завершения |
| статус (`status`) | VARCHAR(50) | ожидает/в_процессе/завершена/в_архиве |

#### Назначенный критерий (`AssignedCriterion`)
| Поле | Тип | Описание |
|------|-----|----------|
| идентификатор (`id`) | INTEGER | Первичный ключ (AUTO) |
| сессия_оценки_id (`evaluation_session_id`) | FK → EvaluationSession | Сессия оценки |
| критерий_id (`criterion_id`) | FK → Criterion | Критерий |
| назначено_пользователю (`assigned_to`) | FK → User | Ответственный |
| подтверждено (`is_verified`) | BOOLEAN | Флаг верификации |

#### Ответ на оценку (`EvaluationAnswer`)
| Поле | Тип | Описание |
|------|-----|----------|
| идентификатор (`id`) | INTEGER | Первичный ключ (AUTO) |
| назначенный_критерий_id (`assigned_criterion_id`) | FK → AssignedCriterion | Назначенный критерий (1:1) |
| значение_балла (`score_value`) | INTEGER | Балл (1-10) |
| значение_метрики (`metric_value`) | DECIMAL(10,2) | Числовая метрика |
| файл_доказательство (`file_evidence`) | FILE | Файл-доказательство |
| комментарий (`comment`) | TEXT | Комментарий |
| отправлено_в (`submitted_at`) | DATETIME | Дата отправки (AUTO) |

#### Роль пользователя (`Role`)
| Поле | Тип | Описание |
|------|-----|----------|
| идентификатор (`id`) | INTEGER | Первичный ключ (AUTO) |
| название (`name`) | VARCHAR(50) | администратор/эксперт/владелец/наблюдатель |

#### Профиль пользователя (`Profile`)
| Поле | Тип | Описание |
|------|-----|----------|
| идентификатор (`id`) | INTEGER | Первичный ключ (AUTO) |
| пользователь_id (`user_id`) | FK → User | Пользователь Django (1:1) |
| роль_id (`role_id`) | FK → Role | Роль пользователя |

### Где строить физическую модель БД

Физическую модель на основе вашей логической модели лучше строить в двух местах:

1. **В коде проекта (основной источник истины)** — через `Django models` и миграции (`python manage.py makemigrations && python manage.py migrate`).
2. **В PostgreSQL-клиенте для визуальной проверки** — например, в pgAdmin 4 (ERD Tool), DBeaver или DataGrip, подключившись к вашей БД и проверив фактические таблицы/индексы/ограничения.

Для текущего проекта:

- **Production БД:** `PostgreSQL` (основная целевая физическая модель).
- **Development БД:** `SQLite` (локальная разработка и быстрый старт).

### Full SQL for Physical Database Model (PostgreSQL, DBeaver visualization)

> Below is a standalone DDL script for visualization in DBeaver with fully English table names, columns, relations, and indexes.  
> Use this script to build an English ERD in a separate PostgreSQL database.

```sql
-- Recommended for PostgreSQL 15+
BEGIN;

-- =========================================================
-- 1) Users and reference entities
-- =========================================================

CREATE TABLE IF NOT EXISTS role (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS app_user (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS profile (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE
        REFERENCES app_user(id) ON DELETE CASCADE,
    role_id BIGINT
        REFERENCES role(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS product (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    department_owner VARCHAR(255),
    product_link TEXT,
    launch_date DATE,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS domain (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    weight NUMERIC(5,2) NOT NULL CHECK (weight > 0 AND weight <= 100)
);

-- =========================================================
-- 2) Criteria and scales
-- =========================================================

CREATE TABLE IF NOT EXISTS criterion (
    id BIGSERIAL PRIMARY KEY,
    domain_id BIGINT NOT NULL
        REFERENCES domain(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    weight NUMERIC(5,2) NOT NULL CHECK (weight > 0 AND weight <= 100),
    CONSTRAINT uq_criterion_domain_name
        UNIQUE (domain_id, name)
);

CREATE TABLE IF NOT EXISTS rating_scale (
    id BIGSERIAL PRIMARY KEY,
    criterion_id BIGINT NOT NULL
        REFERENCES criterion(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score BETWEEN 1 AND 10),
    description TEXT NOT NULL,
    CONSTRAINT uq_rating_scale_criterion_score
        UNIQUE (criterion_id, score)
);

-- =========================================================
-- 3) Evaluation sessions and assignments
-- =========================================================

CREATE TABLE IF NOT EXISTS evaluation_session (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL
        REFERENCES product(id) ON DELETE CASCADE,
    created_by_id BIGINT
        REFERENCES app_user(id) ON DELETE SET NULL,
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    CONSTRAINT chk_evaluation_status
        CHECK (status IN ('pending', 'in_progress', 'completed', 'archived')),
    CONSTRAINT chk_session_dates
        CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS assigned_criterion (
    id BIGSERIAL PRIMARY KEY,
    evaluation_session_id BIGINT NOT NULL
        REFERENCES evaluation_session(id) ON DELETE CASCADE,
    criterion_id BIGINT NOT NULL
        REFERENCES criterion(id) ON DELETE CASCADE,
    assigned_to_id BIGINT
        REFERENCES app_user(id) ON DELETE SET NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_assigned_criterion
        UNIQUE (evaluation_session_id, criterion_id)
);

CREATE TABLE IF NOT EXISTS evaluation_answer (
    id BIGSERIAL PRIMARY KEY,
    assigned_criterion_id BIGINT NOT NULL UNIQUE
        REFERENCES assigned_criterion(id) ON DELETE CASCADE,
    score_value INTEGER CHECK (score_value BETWEEN 1 AND 10),
    metric_value NUMERIC(10,2),
    file_evidence TEXT,
    comment TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- 4) Indexes for frequent queries
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_criterion_domain_id
    ON criterion(domain_id);

CREATE INDEX IF NOT EXISTS idx_rating_scale_criterion_id
    ON rating_scale(criterion_id);

CREATE INDEX IF NOT EXISTS idx_eval_session_product_id
    ON evaluation_session(product_id);

CREATE INDEX IF NOT EXISTS idx_eval_session_created_by_id
    ON evaluation_session(created_by_id);

CREATE INDEX IF NOT EXISTS idx_assigned_criterion_session_id
    ON assigned_criterion(evaluation_session_id);

CREATE INDEX IF NOT EXISTS idx_assigned_criterion_criterion_id
    ON assigned_criterion(criterion_id);

CREATE INDEX IF NOT EXISTS idx_assigned_criterion_assigned_to_id
    ON assigned_criterion(assigned_to_id);

CREATE INDEX IF NOT EXISTS idx_profile_role_id
    ON profile(role_id);

COMMIT;
```

### Полный SQL-код физической модели БД (PostgreSQL, боевой вариант для Django)

> Ниже — вариант с английскими именами таблиц/полей, совместимый с текущей backend-моделью Django.  
> Используйте его для production-окружения или когда нужна схема, максимально близкая к коду приложения.

```sql
BEGIN;

-- =========================================================
-- 1) Справочники и базовые сущности
-- =========================================================

CREATE TABLE IF NOT EXISTS role (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS domain (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    weight NUMERIC(5,2) NOT NULL CHECK (weight > 0 AND weight <= 100)
);

CREATE TABLE IF NOT EXISTS product (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    department_owner VARCHAR(255),
    product_link TEXT,
    launch_date DATE,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE
);

-- =========================================================
-- 2) Критерии и шкалы
-- =========================================================

CREATE TABLE IF NOT EXISTS criterion (
    id BIGSERIAL PRIMARY KEY,
    domain_id BIGINT NOT NULL REFERENCES domain(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    weight NUMERIC(5,2) NOT NULL CHECK (weight > 0 AND weight <= 100),
    CONSTRAINT uq_criterion_domain_name UNIQUE (domain_id, name)
);

CREATE TABLE IF NOT EXISTS rating_scale (
    id BIGSERIAL PRIMARY KEY,
    criterion_id BIGINT NOT NULL REFERENCES criterion(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score BETWEEN 1 AND 10),
    description TEXT NOT NULL,
    CONSTRAINT uq_rating_scale_criterion_score UNIQUE (criterion_id, score)
);

-- =========================================================
-- 3) Сессии оценки и назначения
-- =========================================================

CREATE TABLE IF NOT EXISTS evaluation_session (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    CONSTRAINT chk_evaluation_status
        CHECK (status IN ('pending', 'in_progress', 'completed', 'archived')),
    CONSTRAINT chk_session_dates
        CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS assigned_criterion (
    id BIGSERIAL PRIMARY KEY,
    evaluation_session_id BIGINT NOT NULL REFERENCES evaluation_session(id) ON DELETE CASCADE,
    criterion_id BIGINT NOT NULL REFERENCES criterion(id) ON DELETE CASCADE,
    assigned_to_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_assigned_criterion UNIQUE (evaluation_session_id, criterion_id)
);

CREATE TABLE IF NOT EXISTS evaluation_answer (
    id BIGSERIAL PRIMARY KEY,
    assigned_criterion_id BIGINT NOT NULL UNIQUE REFERENCES assigned_criterion(id) ON DELETE CASCADE,
    score_value INTEGER CHECK (score_value BETWEEN 1 AND 10),
    metric_value NUMERIC(10,2),
    file_evidence TEXT,
    comment TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- 4) Профили пользователей (расширение auth_user)
-- =========================================================

CREATE TABLE IF NOT EXISTS profile (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
    role_id BIGINT REFERENCES role(id) ON DELETE SET NULL
);

-- =========================================================
-- 5) Индексы для ускорения типовых запросов
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_criterion_domain_id
    ON criterion(domain_id);

CREATE INDEX IF NOT EXISTS idx_rating_scale_criterion_id
    ON rating_scale(criterion_id);

CREATE INDEX IF NOT EXISTS idx_eval_session_product_id
    ON evaluation_session(product_id);

CREATE INDEX IF NOT EXISTS idx_eval_session_created_by_id
    ON evaluation_session(created_by_id);

CREATE INDEX IF NOT EXISTS idx_assigned_criterion_session_id
    ON assigned_criterion(evaluation_session_id);

CREATE INDEX IF NOT EXISTS idx_assigned_criterion_criterion_id
    ON assigned_criterion(criterion_id);

CREATE INDEX IF NOT EXISTS idx_assigned_criterion_assigned_to_id
    ON assigned_criterion(assigned_to_id);

CREATE INDEX IF NOT EXISTS idx_profile_role_id
    ON profile(role_id);

COMMIT;
```

### Tabular Description of the Physical Model (report format)

Below is the table description in the format: **Attribute / Data Type / Key Type / NOT NULL**.

#### Table 4.1 - Description of table `role`
| Attribute | Data Type | Key Type | NOT NULL |
|---|---|---|---|
| id | BIGSERIAL | PK | + |
| name | VARCHAR(50) | UQ | + |

#### Table 4.2 - Description of table `app_user`
| Attribute | Data Type | Key Type | NOT NULL |
|---|---|---|---|
| id | BIGSERIAL | PK | + |
| username | VARCHAR(150) | UQ | + |
| email | VARCHAR(254) | - | - |
| created_at | TIMESTAMPTZ | - | + |

#### Table 4.3 - Description of table `profile`
| Attribute | Data Type | Key Type | NOT NULL |
|---|---|---|---|
| id | BIGSERIAL | PK | + |
| user_id | BIGINT | FK, UQ | + |
| role_id | BIGINT | FK | - |

#### Table 4.4 - Description of table `product`
| Attribute | Data Type | Key Type | NOT NULL |
|---|---|---|---|
| id | BIGSERIAL | PK | + |
| name | VARCHAR(255) | - | + |
| description | TEXT | - | - |
| department_owner | VARCHAR(255) | - | - |
| product_link | TEXT | - | - |
| launch_date | DATE | - | - |
| is_archived | BOOLEAN | - | + |

#### Table 4.5 - Description of table `domain`
| Attribute | Data Type | Key Type | NOT NULL |
|---|---|---|---|
| id | BIGSERIAL | PK | + |
| name | VARCHAR(255) | UQ | + |
| description | TEXT | - | - |
| weight | NUMERIC(5,2) | CHECK | + |

#### Table 4.6 - Description of table `criterion`
| Attribute | Data Type | Key Type | NOT NULL |
|---|---|---|---|
| id | BIGSERIAL | PK | + |
| domain_id | BIGINT | FK | + |
| name | VARCHAR(255) | UQ* | + |
| description | TEXT | - | - |
| weight | NUMERIC(5,2) | CHECK | + |

\* Unique as a pair (`domain_id`, `name`).

#### Table 4.7 - Description of table `rating_scale`
| Attribute | Data Type | Key Type | NOT NULL |
|---|---|---|---|
| id | BIGSERIAL | PK | + |
| criterion_id | BIGINT | FK | + |
| score | INTEGER | UQ*, CHECK | + |
| description | TEXT | - | + |

\* Unique as a pair (`criterion_id`, `score`).

#### Table 4.8 - Description of table `evaluation_session`
| Attribute | Data Type | Key Type | NOT NULL |
|---|---|---|---|
| id | BIGSERIAL | PK | + |
| product_id | BIGINT | FK | + |
| created_by_id | BIGINT | FK | - |
| start_date | DATE | - | + |
| end_date | DATE | CHECK | - |
| status | VARCHAR(50) | CHECK | + |

#### Table 4.9 - Description of table `assigned_criterion`
| Attribute | Data Type | Key Type | NOT NULL |
|---|---|---|---|
| id | BIGSERIAL | PK | + |
| evaluation_session_id | BIGINT | FK, UQ* | + |
| criterion_id | BIGINT | FK, UQ* | + |
| assigned_to_id | BIGINT | FK | - |
| is_verified | BOOLEAN | - | + |

\* Unique as a pair (`evaluation_session_id`, `criterion_id`).

#### Table 4.10 - Description of table `evaluation_answer`
| Attribute | Data Type | Key Type | NOT NULL |
|---|---|---|---|
| id | BIGSERIAL | PK | + |
| assigned_criterion_id | BIGINT | FK, UQ | + |
| score_value | INTEGER | CHECK | - |
| metric_value | NUMERIC(10,2) | - | - |
| file_evidence | TEXT | - | - |
| comment | TEXT | - | - |
| submitted_at | TIMESTAMPTZ | - | + |

### Пояснительная записка: типы ключей и типы данных

#### Что означает тип ключа

| Обозначение | Расшифровка | Что означает на практике |
|---|---|---|
| PK | Primary Key (первичный ключ) | Уникальный идентификатор строки в таблице. Не повторяется и не может быть `NULL`. |
| FK | Foreign Key (внешний ключ) | Ссылка на запись в другой таблице. Обеспечивает целостность связей между таблицами. |
| UQ | Unique (уникальное ограничение) | Значения в колонке (или комбинации колонок) не должны повторяться. |
| CHECK | Проверочное ограничение | Ограничивает допустимые значения по условию (например, диапазон балла, допустимые статусы). |

#### Что означает тип данных

| Тип данных | Что хранит | Пример |
|---|---|---|
| BIGSERIAL | Большое автоинкрементное целое число (обычно для `id`) | 1, 2, 3, ... |
| BIGINT | Большое целое число | 1250 |
| INTEGER | Целое число | 10 |
| VARCHAR(50), VARCHAR(150), VARCHAR(255) | Строка фиксированной максимальной длины | `администратор`, `product_owner` |
| TEXT | Текст произвольной длины | Развернутое описание или комментарий |
| NUMERIC(5,2) | Точное десятичное число: всего 5 знаков, из них 2 после запятой | `75.50` |
| NUMERIC(10,2) | Точное десятичное число: всего 10 знаков, из них 2 после запятой | `123456.78` |
| DATE | Календарная дата без времени | `2026-04-29` |
| BOOLEAN | Логическое значение | `TRUE` / `FALSE` |
| TIMESTAMPTZ | Дата и время с часовым поясом | `2026-04-29 19:05:00+03` |

#### Дополнительно по колонке `NOT NULL`

- `+` означает, что поле обязательно к заполнению (значение `NULL` запрещено).
- `-` означает, что поле может быть пустым (`NULL` разрешен).

---

## 🛠 Стек технологий

### Backend

| Технология | Версия | Назначение |
|------------|--------|------------|
| **Python** | 3.11+ | Язык программирования |
| **Django** | 4.2+ | Web-фреймворк |
| **Django REST Framework** | 3.14+ | REST API |
| **djangorestframework-simplejwt** | 5.3+ | JWT аутентификация |
| **django-cors-headers** | 4.3+ | CORS для API |
| **django-allauth** | 0.58+ | Расширенная аутентификация |
| **dj-rest-auth** | 5.0+ | REST API для auth |
| **ReportLab** | 4.0+ | Генерация PDF |
| **SQLite** | 3 | БД для разработки |
| **PostgreSQL** | 15+ | БД для production |
| **Gunicorn** | 21+ | WSGI сервер |

### Frontend

| Технология | Версия | Назначение |
|------------|--------|------------|
| **React** | 18+ | UI библиотека |
| **React Router DOM** | 6+ | Маршрутизация SPA |
| **Axios** | 1.6+ | HTTP клиент |
| **Chart.js** | 4+ | Библиотека графиков |
| **react-chartjs-2** | 5+ | React обёртка для Chart.js |
| **Font Awesome** | 6+ | Иконки |
| **CSS3** | - | Стилизация (градиенты, анимации) |

### DevOps / Инфраструктура

| Технология | Назначение |
|------------|------------|
| **Docker** | Контейнеризация |
| **Docker Compose** | Оркестрация контейнеров |
| **Git** | Контроль версий |
| **GitHub** | Хостинг репозитория |
| **npm** | Пакетный менеджер (frontend) |
| **pip** | Пакетный менеджер (backend) |

### Архитектурные паттерны

| Паттерн | Применение |
|---------|------------|
| **MVC/MVT** | Django (Model-View-Template) |
| **REST API** | Взаимодействие frontend-backend |
| **SPA** | Single Page Application (React) |
| **JWT** | Stateless аутентификация |
| **ORM** | Django ORM для работы с БД |
| **Signals** | Django signals для событий |
| **ViewSet** | DRF ViewSets для CRUD API |

---

## 📁 Структура проекта

```
digital_product_maturity_system/
├── backend/
│   ├── digital_product_maturity_project/
│   │   ├── digital_product_maturity/
│   │   │   ├── core/                    # Основное приложение
│   │   │   │   ├── migrations/          # Миграции БД
│   │   │   │   ├── __init__.py
│   │   │   │   ├── admin.py             # Django Admin
│   │   │   │   ├── apps.py              # Конфигурация приложения
│   │   │   │   ├── auth_views.py        # Аутентификация API
│   │   │   │   ├── models.py            # Модели данных (8 моделей)
│   │   │   │   ├── serializers.py       # DRF сериализаторы
│   │   │   │   ├── signals.py           # Django signals
│   │   │   │   ├── urls.py              # URL маршруты API
│   │   │   │   └── views.py             # ViewSets и actions
│   │   │   ├── __init__.py
│   │   │   ├── asgi.py
│   │   │   ├── settings.py              # Настройки Django
│   │   │   ├── urls.py                  # Главные URL
│   │   │   └── wsgi.py
│   │   ├── manage.py
│   │   ├── create_superuser.py          # Создание админа
│   │   ├── populate_db.py               # Наполнение тестовыми данными
│   │   └── check_data.py                # Проверка данных
│   ├── requirements.txt                 # Python зависимости
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── pages/                       # Страницы приложения
│   │   │   ├── ProductList.js           # Список продуктов
│   │   │   ├── ProductForm.js           # Форма продукта
│   │   │   ├── ProductDetail.js         # Детали продукта
│   │   │   ├── DomainList.js            # Список доменов
│   │   │   ├── DomainForm.js            # Форма домена
│   │   │   ├── CriterionList.js         # Список критериев
│   │   │   ├── CriterionForm.js         # Форма критерия
│   │   │   ├── EvaluationSessionList.js # Список сессий
│   │   │   ├── EvaluationSessionForm.js # Создание сессии
│   │   │   ├── EvaluationInput.js       # Ввод оценок
│   │   │   ├── EvaluationResults.js     # Результаты + графики
│   │   │   ├── Login.js                 # Вход
│   │   │   ├── Register.js              # Регистрация
│   │   │   └── Profile.js               # Профиль
│   │   ├── components/
│   │   │   └── RatingScaleForm.js
│   │   ├── App.js                       # Главный компонент
│   │   ├── App.css                      # Глобальные стили
│   │   ├── index.js                     # Точка входа
│   │   └── setupProxy.js                # Proxy для API
│   ├── package.json
│   ├── Dockerfile
│   └── .dockerignore
├── docker-compose.yml                   # Docker конфигурация
├── start_local.bat                      # Скрипт локального запуска
├── .gitignore
└── README.md
```

---

## 🔌 API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET/POST | `/api/products/` | Список/создание продуктов |
| GET/PUT/DELETE | `/api/products/{id}/` | Операции с продуктом |
| GET/POST | `/api/domains/` | Список/создание доменов |
| GET/POST | `/api/criteria/` | Список/создание критериев |
| GET/POST | `/api/rating-scales/` | Шкалы оценки |
| GET/POST | `/api/evaluation-sessions/` | Сессии оценки |
| GET | `/api/evaluation-sessions/{id}/get_overall_maturity_index/` | Индекс зрелости |
| GET | `/api/evaluation-sessions/{id}/get_domain_scores/` | Оценки по доменам |
| GET | `/api/evaluation-sessions/compare_products/?product_ids=1,2,3` | Сравнение последних индексов по продуктам |
| GET | `/api/evaluation-sessions/product_history/?product_id={id}` | История индекса зрелости по продукту |
| GET | `/api/evaluation-sessions/{id}/generate_maturity_passport/` | PDF паспорт |
| GET/POST | `/api/assigned-criteria/` | Назначенные критерии |
| POST | `/api/assigned-criteria/{id}/verify/` | Подтвердить критерий (верификатор) |
| POST | `/api/assigned-criteria/{id}/request_changes/` | Запросить уточнения (верификатор) |
| GET/POST | `/api/evaluation-answers/` | Ответы на оценку |
| POST | `/api/auth/login/` | Вход |
| POST | `/api/auth/register/` | Регистрация |
| GET | `/api/auth/user/` | Текущий пользователь |

### API импорта/экспорта для интеграции с реестрами

| Назначение | Body | Ответ |
|---|---|---|
| `POST /api/products/import/csv` — импорт списка продуктов из CSV-файла ведомственного реестра | `multipart/form-data`: `file` (обязательно), `delimiter` (опц.), `dry_run` (опц.) | JSON со статистикой импорта: `created`, `updated`, `skipped`, `errors[]` |
| `POST /api/products/import/json` — импорт списка продуктов через JSON (например, после REST-запроса к внешней системе) | JSON: `{"products":[{"name":"...","description":"...","department_owner":"...","product_link":"...","launch_date":"YYYY-MM-DD"}], "dry_run": false}` | JSON со статистикой: `created`, `updated`, `errors[]` |
| `POST /api/integrations/registry/sync` — запуск синхронизации с внешним ведомственным REST API | JSON: `{"source":"registry_a","since":"YYYY-MM-DDTHH:MM:SSZ","full_sync":false}` | JSON: `{"job_id":"...","status":"pending"}` |
| `GET /api/products/import/jobs/{job_id}` — проверка статуса асинхронного импорта | Не требуется | JSON: `{"job_id":"...","status":"pending|running|success|failed","progress":0-100,"errors":[]}` |
| `GET /api/products/import/template/csv` — скачать шаблон CSV для корректной загрузки | Не требуется | Файл CSV (шаблон с колонками продукта) |
| `GET /api/reports/portfolio/export/json` — синхронный экспорт сводного отчета по портфелю в JSON | Query params: `date_from`, `date_to`, `include_domains=true|false`, `include_history=true|false` | JSON-отчет по портфелю для загрузки в аналитическую платформу |
| `POST /api/reports/portfolio/export/json` — запуск асинхронной выгрузки сводного JSON-отчета | JSON: `{"date_from":"YYYY-MM-DD","date_to":"YYYY-MM-DD","include_domains":true,"include_history":true}` | JSON: `{"export_id":"...","status":"pending"}` |
| `GET /api/reports/exports/{export_id}` — статус асинхронной выгрузки отчета | Не требуется | JSON: `{"export_id":"...","status":"pending|running|ready|failed","progress":0-100}` |
| `GET /api/reports/exports/{export_id}/download` — загрузка готового JSON-отчета | Не требуется | Файл JSON отчета |

---

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

---

## 🔄 Бизнес-процесс оценки зрелости

Ниже представлены две модели одного и того же цикла: **AS-IS** (ручной процесс) и **TO-BE** (процесс с применением разработанной системы оценки зрелости).  
Для наглядности сохранён одинаковый каркас из 6 этапов, но в TO-BE каждый этап оптимизирован средствами продукта.

### 📜 AS-IS (до автоматизации): расширенный список процессов

1. **Планирование и подготовка оценки**
   - 1.1 Утвердить план оценки.
   - 1.2 Согласовать состав участников (владельцы, эксперты, координатор).
   - 1.3 Составить список продуктов и проверить актуальность карточек.
   - 1.4 Подготовить оценочные анкеты в Word/Excel.
   - 1.5 Согласовать методику и шкалы вручную.
2. **Сбор исходных данных**
   - 2.1 Разослать анкеты владельцам по e-mail.
   - 2.2 Получить подтверждение о получении анкеты.
   - 2.3 Собрать заполненные анкеты.
   - 2.4 Проверить полноту данных.
   - 2.5 При неполноте — вернуть на доработку и повторить сбор.
3. **Обработка и анализ данных**
   - 3.1 Перенести данные из анкет в Excel вручную.
   - 3.2 Проверить корректность переносов (контрольные сверки).
   - 3.3 Рассчитать показатели вручную формулами.
   - 3.4 Построить графики и диаграммы.
   - 3.5 При обнаружении ошибок — повторить перерасчёт.
4. **Подготовка отчетности**
   - 4.1 Составить текстовый отчёт.
   - 4.2 Создать презентацию.
   - 4.3 Сформулировать рекомендации.
   - 4.4 Подготовить версии документов для согласования.
5. **Согласование и утверждение**
   - 5.1 Провести рабочее совещание.
   - 5.2 Зафиксировать замечания.
   - 5.3 Внести корректировки.
   - 5.4 Утвердить финальный отчёт.
   - 5.5 При отклонении — вернуться к этапу анализа/отчётности.
6. **Распространение и архивация**
   - 6.1 Разослать отчёты участникам.
   - 6.2 Подтвердить получение.
   - 6.3 Архивировать материалы в сетевой папке.
   - 6.4 Закрыть цикл оценки.

### BPMN (AS-IS, расширенная)

```mermaid
%%{init: {'theme':'default', 'themeVariables': {'background':'#ffffff'}}}%%
flowchart TD
    classDef event fill:#cfe8ff,stroke:#3a7bd5,stroke-width:2px,color:#0b3d91
    classDef task fill:#ffffff,stroke:#4a4a4a,stroke-width:1.5px,color:#1f2937
    classDef gw fill:#fff4c2,stroke:#c69500,stroke-width:1.5px,color:#5b4400
    classDef pain fill:#ffd6d6,stroke:#c0392b,stroke-width:2px,color:#7a1d12,stroke-dasharray: 4 3

    Start((Старт цикла)):::event
    A11[1.1 Утвердить план]:::task
    A12[1.2 Согласовать участников]:::task
    A13[1.3 Список продуктов]:::task
    A14[1.4 Подготовить анкеты]:::task
    A15[1.5 Согласовать методику]:::task

    B21[2.1 Разослать анкеты]:::task
    B22[2.2 Подтверждение получения]:::task
    B23[2.3 Собрать анкеты]:::task
    B24[2.4 Проверить полноту]:::task
    G2{Все анкеты\nполные?}:::gw
    B25[2.5 Вернуть на доработку]:::task

    C31[3.1 Перенос в Excel]:::task
    C32[3.2 Контроль сверки]:::task
    C33[3.3 Ручной расчёт]:::task
    C34[3.4 Графики/диаграммы]:::task
    G3{Ошибки\nв расчётах?}:::gw
    Pain1[/Риск ошибок при копировании и формулах/]:::pain

    D41[4.1 Текстовый отчёт]:::task
    D42[4.2 Презентация]:::task
    D43[4.3 Рекомендации]:::task
    D44[4.4 Версии на согласование]:::task

    E51[5.1 Рабочее совещание]:::task
    E52[5.2 Зафиксировать замечания]:::task
    E53[5.3 Внести корректировки]:::task
    G5{Отчёт\nутверждён?}:::gw

    F61[6.1 Разослать отчёты]:::task
    F62[6.2 Подтвердить получение]:::task
    F63[6.3 Архивировать материалы]:::task
    End((Завершение цикла)):::event

    Start --> A11 --> A12 --> A13 --> A14 --> A15 --> B21 --> B22 --> B23 --> B24 --> G2
    G2 -- Нет --> B25 --> B23
    G2 -- Да --> C31 --> C32 --> C33 --> C34 --> G3
    G3 -- Да --> C31
    G3 -- Нет --> Pain1 --> D41 --> D42 --> D43 --> D44 --> E51 --> E52 --> E53 --> G5
    G5 -- Нет --> C33
    G5 -- Да --> F61 --> F62 --> F63 --> End
```

---

### 🚀 TO-BE (с применением продукта): тот же список этапов, но оптимизированный

1. **Планирование и подготовка оценки**
   - 1.1 Создать цикл оценки в системе.
   - 1.2 Импортировать/актуализировать список продуктов из реестров.
   - 1.3 Назначить роли участников (Администратор, Эксперт, Владелец, Наблюдатель).
   - 1.4 Выбрать модель зрелости (домены/критерии/веса) из конструктора.
   - 1.5 Автоматически сформировать цифровые анкеты.
2. **Сбор исходных данных**
   - 2.1 Автоматически разослать задания и ссылки на формы.
   - 2.2 Владельцы заполняют формы онлайн, система валидирует поля.
   - 2.3 Система контролирует полноту и сроки заполнения.
   - 2.4 При неполноте — автонапоминание и эскалация.
   - 2.5 Эксперт верифицирует ответы и при необходимости запрашивает уточнение.
3. **Обработка и анализ данных**
   - 3.1 Данные сохраняются в БД без ручного переноса.
   - 3.2 Индексы пересчитываются автоматически при каждом изменении.
   - 3.3 Строятся интерактивные графики и история индекса.
   - 3.4 Выполняется сравнение нескольких продуктов в один клик.
4. **Подготовка отчетности**
   - 4.1 Сформировать паспорт зрелости (PDF) по шаблону.
   - 4.2 Сформировать сводный отчёт по портфелю.
   - 4.3 Сгенерировать рекомендации по слабым доменам.
   - 4.4 Подготовить JSON-выгрузку для внешней аналитической платформы.
5. **Согласование и утверждение**
   - 5.1 Провести цифровое согласование внутри системы.
   - 5.2 Фиксировать замечания в карточке сессии.
   - 5.3 Вносить корректировки по задачам.
   - 5.4 Утверждать финальный отчёт электронной фиксацией статуса.
   - 5.5 Вести аудит действий и версий изменений.
6. **Распространение и архивация**
   - 6.1 Публиковать результаты в role-based дашборде.
   - 6.2 Автоматически рассылать уведомления об утверждении.
   - 6.3 Архивировать цикл в централизованном хранилище.
   - 6.4 Оставлять данные доступными для последующего сравнения периодов.

### BPMN (TO-BE, с оптимизацией системой)

```mermaid
%%{init: {'theme':'default', 'themeVariables': {'background':'#ffffff'}}}%%
flowchart TD
    classDef event fill:#cfe8ff,stroke:#3a7bd5,stroke-width:2px,color:#0b3d91
    classDef task fill:#ffffff,stroke:#4a4a4a,stroke-width:1.5px,color:#1f2937
    classDef auto fill:#d4f7d4,stroke:#1e8449,stroke-width:1.5px,color:#0e3d1e
    classDef gw fill:#fff4c2,stroke:#c69500,stroke-width:1.5px,color:#5b4400
    classDef store fill:#f0f0f0,stroke:#4a4a4a,stroke-width:1.5px,color:#1f2937

    Start((Старт цикла)):::event
    P11[1.1 Создать цикл в системе]:::task
    P12[1.2 Импорт каталога продуктов]:::auto
    P13[1.3 Назначить роли]:::task
    P14[1.4 Выбрать модель зрелости]:::task
    P15[1.5 Автогенерация анкет]:::auto

    Q21[2.1 Авторассылка заданий]:::auto
    Q22[2.2 Онлайн-заполнение анкет]:::task
    Q23[2.3 Автопроверка полноты]:::auto
    G2{Анкеты\nполные и\nв срок?}:::gw
    Q24[2.4 Напоминание/эскалация]:::auto
    Q25[2.5 Верификация экспертом]:::task
    G25{Нужны\nуточнения?}:::gw
    Q26[Запрос уточнений владельцу]:::task

    R31[3.1 Автосохранение в БД]:::auto
    R32[3.2 Автопересчёт индексов]:::auto
    R33[3.3 Дашборды и динамика]:::auto
    R34[3.4 Сравнение продуктов]:::auto
    DB[(PostgreSQL/SQLite)]:::store

    S41[4.1 PDF-паспорт]:::auto
    S42[4.2 Портфельный отчёт]:::auto
    S43[4.3 Рекомендации]:::auto
    S44[4.4 JSON-экспорт]:::auto

    T51[5.1 Цифровое согласование]:::task
    T52[5.2 Замечания в сессии]:::task
    T53[5.3 Корректировки]:::task
    G5{Отчёт\nутверждён?}:::gw
    T54[5.4 Электронное утверждение]:::auto
    T55[5.5 Аудит-лог версий]:::auto

    U61[6.1 Публикация в дашборде]:::auto
    U62[6.2 Автоуведомления]:::auto
    U63[6.3 Централизованная архивация]:::auto
    U64[6.4 Доступ для сравнения периодов]:::auto
    End((Цикл завершён)):::event

    Start --> P11 --> P12 --> P13 --> P14 --> P15 --> Q21 --> Q22 --> Q23 --> G2
    G2 -- Нет --> Q24 --> Q22
    G2 -- Да --> Q25 --> G25
    G25 -- Да --> Q26 --> Q22
    G25 -- Нет --> R31 --> DB --> R32 --> R33 --> R34
    R34 --> S41 --> S42 --> S43 --> S44 --> T51 --> T52 --> T53 --> G5
    G5 -- Нет --> T53
    G5 -- Да --> T54 --> T55 --> U61 --> U62 --> U63 --> U64 --> End
```

---

### 📊 Ключевой эффект перехода AS-IS → TO-BE

- Исключён ручной перенос данных и повторный ввод.
- Сокращены циклы согласования за счёт цифрового workflow.
- Добавлена верификация и аудит действий по ролям.
- Отчётность и визуализация формируются автоматически.
- Обеспечено сравнение периодов и выгрузка данных во внешние аналитические контуры.

---

## 📡 Информационное обеспечение бизнес-процессов

В этом разделе показано, какими данными обмениваются участники процесса и где эти данные хранятся. Все диаграммы выполнены на Mermaid и отрисовываются прямо в GitHub.

Условные обозначения (приближены к нотации Гейна-Сарсона / Йордона):

- **Прямоугольник** `[Внешняя сущность]` — источник или приёмник данных вне системы (роль, внешний сервис).
- **Скруглённый блок** `(Процесс)` — обработчик данных внутри системы.
- **Цилиндр** `[(Хранилище данных)]` — таблица БД или физическое хранилище.
- **Стрелки с подписью** — поток данных и его содержание.

---

### 🌐 Контекстная диаграмма (DFD Level 0)

Система оценки зрелости показана одним процессом, взаимодействующим с пользователями и внешними сервисами. Видно «what goes in / what goes out».

**Описание потоков данных:**
1. **От Владельца продукта в систему:** анкетные данные, числовые метрики, файлы-доказательства.
2. **От системы к Владельцу:** уведомления о необходимости заполнения, запросы на уточнение, паспорт зрелости.
3. **От Эксперта:** решения о верификации, комментарии, запросы изменений.
4. **От системы к Эксперту:** список сессий на проверку, данные ответов.
5. **От Администратора:** настройки модели (домены, критерии, веса), реестр продуктов.
6. **От системы к Администратору:** отчёты о ходе оценки, статистика.
7. **От системы к Руководству:** сводные дашборды, аналитические отчёты.
8. **Обмен с внешними системами:** импорт метрик доступности, DAU, обратной связи.

```mermaid
%%{init: {'theme':'default', 'themeVariables': {'background':'#ffffff'}}}%%
flowchart LR
    classDef ext fill:#cfe8ff,stroke:#3a7bd5,stroke-width:2px,color:#0b3d91
    classDef sys fill:#d4f7d4,stroke:#1e8449,stroke-width:2.5px,color:#0e3d1e
    classDef svc fill:#fde2e4,stroke:#c0392b,stroke-width:2px,color:#7a1d12

    Admin["👑 Администратор системы"]:::ext
    Expert["🔍 Эксперт / Аудитор"]:::ext
    Owner["📦 Владелец продукта"]:::ext
    Observer["👀 Наблюдатель"]:::ext
    Google["🔐 Google OAuth 2.0"]:::svc

    System(("Система оценки зрелости<br/>цифровых продуктов")):::sys

    Admin -- "управление: продукты,<br/>домены, критерии, роли" --> System
    System -- "интерфейс администратора,<br/>отчёты, журнал аудита" --> Admin

    Expert -- "оценки, комментарии,<br/>верификация ответов" --> System
    System -- "анкеты, графики,<br/>паспорт зрелости (PDF)" --> Expert

    Owner -- "данные о продукте,<br/>заполненная анкета" --> System
    System -- "уведомления, индексы,<br/>рекомендации" --> Owner

    Observer -- "запрос на просмотр" --> System
    System -- "только чтение:<br/>дашборд, отчёты" --> Observer

    System -- "id_token (JWT)" --> Google
    Google -- "верификация e-mail<br/>+ профиль пользователя" --> System
```

---

### 🧭 DFD Level 1 — декомпозиция системы

Диаграмма DFD уровня 1 детализирует основные процессы, хранилища данных и потоки внутри системы. Показано, какие потоки идут между процессами и какие данные читаются/пишутся в БД.

**Выделены следующие процессы:**
- **Процесс 1 «Управление реестром продуктов»** – добавление, редактирование, архивация цифровых продуктов.
- **Процесс 2 «Настройка модели оценки»** – создание доменов, критериев, шкал и весов.
- **Процесс 3 «Инициация и проведение оценки»** – создание сессии, назначение ответственных, заполнение анкет.
- **Процесс 4 «Верификация результатов»** – проверка данных экспертом, утверждение или отправка на доработку.
- **Процесс 5 «Расчёт индексов и визуализация»** – автоматический расчёт баллов, интегральных показателей, построение дашбордов.
- **Процесс 6 «Генерация отчётности»** – формирование PDF-паспортов и сводных отчётов.

**Основные хранилища данных (сущности):**
- **D1** – Реестр продуктов
- **D2** – Модель зрелости (домены, критерии, шкалы)
- **D3** – Данные оценочных сессий
- **D4** – Ответы по критериям
- **D5** – Отчёты

**Пример потока:** Владелец продукта → (заполненная анкета) → Процесс 3 → (сохранение ответов) → D4. Затем Эксперт → (запрос на верификацию) → Процесс 4 → (чтение из D4) → Процесс 4 → (утверждённые данные) → Процесс 5 → (расчёт) → D5 → Процесс 6 → (отчёт) → Руководство.

```mermaid
%%{init: {'theme':'default', 'themeVariables': {'background':'#ffffff'}}}%%
flowchart TB
    classDef ext fill:#cfe8ff,stroke:#3a7bd5,stroke-width:2px,color:#0b3d91
    classDef proc fill:#fff4c2,stroke:#c69500,stroke-width:1.5px,color:#5b4400
    classDef store fill:#f0f0f0,stroke:#4a4a4a,stroke-width:1.5px,color:#1f2937
    classDef svc fill:#fde2e4,stroke:#c0392b,stroke-width:2px,color:#7a1d12

    Admin["👑 Админ"]:::ext
    Expert["🔍 Эксперт"]:::ext
    Owner["📦 Владелец"]:::ext
    Observer["👀 Наблюдатель"]:::ext
    Google["🔐 Google OAuth"]:::svc

    P0(("P0<br/>Аутентификация<br/>и авторизация")):::proc
    P1(("P1<br/>Управление<br/>каталогом продуктов")):::proc
    P2(("P2<br/>Конструктор модели<br/>оценки")):::proc
    P3(("P3<br/>Проведение<br/>сессии оценки")):::proc
    P4(("P4<br/>Расчёт интегральных<br/>индексов")):::proc
    P5(("P5<br/>Генерация отчётности<br/>и графиков")):::proc
    P6(("P6<br/>Управление<br/>пользователями и ролями")):::proc

    D1[("D1: Products")]:::store
    D2[("D2: Domains, Criteria,<br/>RatingScale")]:::store
    D3[("D3: EvaluationSession,<br/>AssignedCriterion")]:::store
    D4[("D4: EvaluationAnswer")]:::store
    D5[("D5: User, Profile, Role")]:::store

    %% Аутентификация
    Admin -- "учётные данные / Google" --> P0
    Expert -- "учётные данные / Google" --> P0
    Owner -- "учётные данные / Google" --> P0
    Observer -- "учётные данные / Google" --> P0
    P0 <-- "id_token" --> Google
    P0 -- "проверка роли" --> D5
    P0 -- "JWT access / refresh" --> Admin
    P0 -- "JWT" --> Expert
    P0 -- "JWT" --> Owner
    P0 -- "JWT" --> Observer

    %% Каталог продуктов
    Admin -- "CRUD продукта" --> P1
    Owner -- "CRUD своих продуктов" --> P1
    P1 <-- "запись / чтение" --> D1
    P1 -- "карточка продукта" --> Expert
    P1 -- "карточка продукта" --> Observer

    %% Конструктор модели
    Admin -- "домены, критерии,<br/>веса, шкалы" --> P2
    P2 <-- "запись / чтение" --> D2

    %% Сессии оценки
    Admin -- "создать сессию,<br/>назначить критерии" --> P3
    Expert -- "ответы и оценки" --> P3
    Owner -- "ответы по своему продукту" --> P3
    P3 -- "конфигурация сессии" --> D3
    P3 -- "answer_value, comment" --> D4
    P2 -- "набор критериев" --> P3
    D1 -- "продукт сессии" --> P3

    %% Расчёт индексов
    P3 -- "событие 'ответ сохранён'" --> P4
    D4 -- "ответы" --> P4
    D2 -- "веса доменов и критериев" --> P4
    P4 -- "доменные оценки,<br/>интегральный индекс" --> D3
    P4 -- "уровень зрелости" --> P5

    %% Отчётность
    Expert -- "запрос отчёта" --> P5
    Admin -- "запрос отчёта" --> P5
    Owner -- "запрос отчёта" --> P5
    Observer -- "просмотр отчёта" --> P5
    P5 -- "чтение результатов" --> D3
    P5 -- "чтение ответов" --> D4
    P5 -- "PDF паспорт зрелости<br/>+ графики" --> Expert
    P5 -- "PDF + дашборд" --> Admin
    P5 -- "PDF + рекомендации" --> Owner
    P5 -- "только-чтение дашборд" --> Observer

    %% Управление пользователями
    Admin -- "создать пользователя,<br/>назначить роль" --> P6
    P6 <-- "запись / чтение" --> D5
    P6 -- "роли и профили" --> P0
```

---

### 🔁 Контекстная диаграмма потоков данных по ролям

Удобный «срез» — те же потоки, но сгруппированные с точки зрения каждой роли. Хорошо видно, что наблюдатель только читает, а админ имеет полный двунаправленный обмен.

```mermaid
%%{init: {'theme':'default', 'themeVariables': {'background':'#ffffff'}}}%%
flowchart LR
    classDef ext fill:#cfe8ff,stroke:#3a7bd5,stroke-width:2px,color:#0b3d91
    classDef sys fill:#d4f7d4,stroke:#1e8449,stroke-width:2.5px,color:#0e3d1e

    Admin["👑 Администратор"]:::ext
    Expert["🔍 Эксперт"]:::ext
    Owner["📦 Владелец"]:::ext
    Observer["👀 Наблюдатель"]:::ext

    Sys(("Платформа оценки<br/>зрелости")):::sys

    Admin -- "продукты, домены, критерии, шкалы,<br/>сессии, пользователи, роли" --> Sys
    Sys -- "журнал аудита, отчёты,<br/>статусы пользователей" --> Admin

    Expert -- "ответы по критериям, комментарии,<br/>верификация" --> Sys
    Sys -- "анкеты, продукт, графики,<br/>PDF паспорт зрелости" --> Expert

    Owner -- "карточки своих продуктов,<br/>ответы на анкеты" --> Sys
    Sys -- "уведомления, рекомендации,<br/>динамика индекса" --> Owner

    Observer -- "только запросы на чтение" --> Sys
    Sys -- "дашборд и отчёты (read-only)" --> Observer
```

---

### 🛤 Диаграмма workflow одной сессии оценки (процесса координации)

Для описания логики взаимодействия участников при проведении оценки разработана диаграмма workflow, отражающая состояния сессии и переходы между ними. Жизненный цикл одного экземпляра «сессия оценки продукта» — от создания до архивации. Workflow построен на основе ролевой модели (ФТ-07). Полезно для понимания, в каком состоянии данные доступны для чтения/записи.

**Состояния сессии:**
1. **«Черновик»** – сессия создана администратором, назначены ответственные, но данные не введены.
2. **«Ожидает заполнения»** – владельцу продукта отправлено уведомление, он может вносить ответы.
3. **«На верификации»** – владелец завершил заполнение (отправил на проверку). Эксперт получает задание.
4. **«Запрос изменений»** – эксперт обнаружил несоответствия и отправил сессию на доработку владельцу.
5. **«Завершена»** – эксперт утвердил все ответы, система рассчитала индексы и сгенерировала отчёты.

**Переходы:**
- Администратор → инициация → Черновик
- Черновик → назначение ответственных → Ожидает заполнения
- Ожидает заполнения → владелец заполнил → На верификации
- На верификации → эксперт отклонил → Запрос изменений
- Запрос изменений → владелец исправил → На верификации
- На верификации → эксперт утвердил → Завершена

Для каждого перехода в системе предусмотрены автоматические уведомления (электронная почта, внутрисистемные оповещения) и логирование действий.

```mermaid
%%{init: {'theme':'default', 'themeVariables': {'background':'#ffffff'}}}%%
stateDiagram-v2
    [*] --> Черновик : Админ создал сессию,<br/>назначил продукт и критерии

    Черновик --> Активная : Старт сессии<br/>(уведомления участникам)
    Черновик --> Архивная : Отмена

    Активная --> Активная : Эксперт/Владелец<br/>сохраняют ответы<br/>(автоперерасчёт индекса)
    Активная --> НаПроверке : Все ответы заполнены,<br/>отправлено на проверку
    Активная --> Архивная : Преждевременная отмена

    НаПроверке --> Активная : Эксперт/Админ<br/>вернул на доработку<br/>с замечаниями
    НаПроверке --> Утверждена : Электронное<br/>утверждение отчёта

    Утверждена --> Опубликована : Публикация в дашборд<br/>(виден Наблюдателям)
    Опубликована --> Архивная : По истечении периода<br/>оценки

    Архивная --> [*]
```

---

### 📥 Сводная таблица потоков данных (Data Dictionary, кратко)

| # | Поток данных | От | К | Содержимое | Хранилище |
|---|---|---|---|---|---|
| F1 | Учётные данные | Любая роль | P0 Auth | `username`, `password` или `id_token` | — |
| F2 | JWT-токен | P0 Auth | Любая роль | `access_token`, `refresh_token` | — |
| F3 | CRUD продукта | Admin / Owner | P1 | `name`, `description`, `department_owner`, `link` | D1: Products |
| F4 | Карточка продукта | P1 | Все роли | Атрибуты Product + список сессий | D1 |
| F5 | Модель оценки | Admin | P2 | Домены (с весами), критерии (с весами), шкалы | D2 |
| F6 | Конфигурация сессии | Admin | P3 | `product_id`, `start_date`, набор `AssignedCriterion` | D3 |
| F7 | Ответ на критерий | Expert / Owner | P3 | `assigned_criterion_id`, `metric_value (0-100)`, `comment` | D4 |
| F8 | Доменные оценки | P4 | P3 / P5 | `{domain → score}`, `overall_index` | D3 (расчётно) |
| F9 | PDF паспорт зрелости | P5 | Любая роль | 3 страницы: титул + графики + детализация | — (стрим) |
| F10 | Аудит | Все процессы | D5 / журнал | `who`, `when`, `what`, `before/after` | D5 |

---

## 📅 Диаграмма Ганта (план дипломного проекта)

```mermaid
gantt
    title План разработки и опытной эксплуатации системы
    dateFormat  YYYY-MM-DD
    axisFormat  %d.%m

    section Аналитика и проектирование
    Сбор требований и согласование критериев зрелости :done, a1, 2026-01-10, 14d
    Проектирование архитектуры и модели данных        :done, a2, after a1, 14d
    Подготовка ER-диаграммы и API-контрактов          :done, a3, after a2, 10d

    section Реализация backend
    Реализация Django API и RBAC                      :done, b1, 2026-02-10, 20d
    Реализация модуля сессий и расчетов индекса       :done, b2, after b1, 20d
    Реализация генерации PDF-отчетов                  :done, b3, after b2, 12d

    section Реализация frontend
    UI-макеты и маршрутизация React                   :done, c1, 2026-03-01, 14d
    Формы оценки, дашборды и визуализация             :done, c2, after c1, 20d
    Интеграция аутентификации (JWT + Google OAuth)    :active, c3, after c2, 12d

    section Тестирование и внедрение
    Интеграционное тестирование                       :d1, 2026-04-10, 10d
    Подготовка Docker-окружения                       :d2, after d1, 7d
    Опытная эксплуатация и сбор метрик                :d3, after d2, 14d
    Финальная доработка и подготовка к защите         :d4, after d3, 10d
```

## 📈 Мониторинг и централизованное логирование (опытная эксплуатация)

На этапе опытной эксплуатации используется стек:

- **Prometheus + Grafana** — сбор и визуализация метрик серверов и приложения.
- **ELK Stack (Elasticsearch + Logstash + Kibana)** — централизованный сбор и анализ логов.

Состав контейнеров в `docker-compose.yml`:

- Метрики: `prometheus`, `grafana`, `node-exporter`, `cadvisor`, `postgres-exporter`
- Логи: `elasticsearch`, `logstash`, `filebeat`, `kibana`

### Точки доступа

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api/`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (`admin` / `admin`)
- Elasticsearch: `http://localhost:9200`
- Kibana: `http://localhost:5601`

### Готовые дашборды после запуска

- **Grafana (автоматически):**
  - datasource `Prometheus` создается автоматически;
  - dashboard `Diploma Project - System Overview` появляется в папке `Diploma Monitoring`.
- **Kibana (автоматически):**
  - создается Data View `app-logs-*` (название `Application Logs`);
  - можно сразу открыть Discover и строить визуализации/дашборды по логам.

### Запуск полного стенда (приложение + мониторинг + ELK)

```bash
docker-compose up --build
```

После запуска:

1. В Grafana добавьте datasource `Prometheus` с URL `http://prometheus:9090`.
2. В Kibana создайте data view для индексов `app-logs-*`.
3. Проверьте endpoint метрик приложения: `http://localhost:8000/metrics`.

---

### Резервное копирование БД (ежесуточно)

В `docker-compose.yml` добавлен сервис `db-backup`, который:

- создает дамп PostgreSQL в `./backups` каждые 24 часа;
- хранит резервные копии с ротацией (по умолчанию 7 дней).

Основные параметры:

- `BACKUP_INTERVAL_SECONDS=86400`
- `RETENTION_DAYS=7`

Пример ручного восстановления:

```bash
gunzip -c backups/digital_product_maturity_YYYYMMDD_HHMMSS.sql.gz | \
docker exec -i <postgres_container_name> psql -U postgres -d digital_product_maturity
```

---

### Базовые production-настройки безопасности

Настройки читаются из `.env`:

- `DEBUG=false`
- `ALLOWED_HOSTS=example.ru,api.example.ru`
- `CORS_ALLOW_ALL_ORIGINS=false`
- `CORS_ALLOWED_ORIGINS=https://example.ru,https://app.example.ru`
- `CSRF_TRUSTED_ORIGINS=https://example.ru,https://app.example.ru`
- `SECURE_SSL_REDIRECT=true`
- `SESSION_COOKIE_SECURE=true`
- `CSRF_COOKIE_SECURE=true`

---

### Проверка требований производительности (k6)

Добавлен smoke/performance-сценарий: `tests/performance/k6-smoke.js`.

Пример запуска (50 виртуальных пользователей, 60 сек):

```bash
k6 run tests/performance/k6-smoke.js
```

Критерии в сценарии:

- `p(95) < 3000ms` для HTTP-запросов;
- доля ошибок `< 5%`.

---

## 3.3 Тестирование системы

Апробация разработанного прототипа системы оценки зрелости цифровых продуктов выполнялась в локальной среде развертывания. Использовались два режима запуска:

- локальный запуск (`Django + React`);
- контейнерный запуск (`Docker Compose`, включая `backend`, `frontend`, `db` и наблюдаемость).

Для проверки API применялись `Postman` и встроенная документация DRF-endpoints, для проверки пользовательских сценариев - браузерное тестирование интерфейса. Автоматизированная проверка выполнялась в CI (`GitHub Actions`) и дополнительно локальными тестами (`npm test`, `python manage.py test`, `k6`).

### Методика тестирования

В ходе апробации использовались следующие виды тестирования:

1. **Модульное тестирование**  
   Проверка корректности отдельных компонентов: базовые frontend-тесты (`Jest/React Testing Library`), backend-тесты (`Django test runner`), проверка валидации и ролевых ограничений в API-методах.

2. **Интеграционное тестирование**  
   Проверка сквозного сценария от создания сущностей до получения итоговой аналитики:  
   `Авторизация -> создание продукта -> запуск сессии -> ввод ответов -> верификация -> расчеты -> PDF`.

3. **Функциональное тестирование интерфейса**  
   Ручное прохождение пользовательских сценариев в браузере с контролем ожидаемого результата и HTTP-статусов API.

4. **Нагрузочное тестирование**  
   Проверка НФТ-01 с использованием `k6` (`tests/performance/k6-smoke.js`) при профиле до 50 виртуальных пользователей.

5. **Проверка безопасности и доступа**  
   Проверка авторизации, ограничений по ролям, корректной реакции системы на неавторизованные и запрещенные запросы (`401/403`).

Критерий успешности тестов: совпадение фактического результата с ожидаемым и отсутствие критических дефектов, блокирующих целевые сценарии работы.

### Функциональное тестирование

Функциональные проверки выполнялись по тест-кейсам для ключевых модулей системы.

#### Таблица 3.6 - Тестирование модуля аутентификации и авторизации

| Проверяемая функция | Входные данные | Ожидаемый результат | Фактический результат | Статус |
|---|---|---|---|---|
| Регистрация пользователя | `POST /api/auth/register/` с валидными `username/email/password` | Код `201`, учетная запись создана | Код `201`, пользователь создан | Пройден |
| Вход в систему | `POST /api/auth/login/` с корректными учетными данными | Код `200`, возвращается JWT-токен | Код `200`, токен получен | Пройден |
| Запрос без токена | `GET /api/products/` без `Authorization` | Код `401` | Код `401` | Пройден |
| Доступ без достаточной роли | Попытка изменения справочников ролью без прав | Код `403` | Код `403` | Пройден |

На **Рисунке 3.17** представлен результат запроса к защищенному endpoint без передачи токена авторизации. Сервер вернул код `401` и сообщение `Authentication credentials were not provided`, что подтверждает корректную работу механизма ограничения доступа для неаутентифицированных запросов.

На **Рисунке 3.18** представлен результат успешного входа в систему. Сервер вернул код `200` и объект с JWT-параметрами (`token`, `refresh`), а также данными пользователя. Полученный токен используется для авторизации последующих запросов через заголовок `Authorization`.

На **Рисунке 3.19** представлен результат запроса `GET /api/auth/user/` с валидным Bearer-токеном. Сервер вернул код `200` и карточку текущего пользователя (`id`, `username`, `email`, `role`, `is_staff`), что подтверждает корректность аутентификации и декодирования JWT.

#### Таблица 3.7 - Тестирование модуля управления реестром и моделью оценки

| Проверяемая функция | Входные данные | Ожидаемый результат | Фактический результат | Статус |
|---|---|---|---|---|
| Получение списка продуктов | `GET /api/products/` с токеном | Код `200`, список продуктов | Код `200`, список возвращается | Пройден |
| Создание продукта | `POST /api/products/` с обязательными полями | Код `201`, запись создана | Код `201`, продукт создан | Пройден |
| Создание домена и критерия | `POST /api/domains/`, `POST /api/criteria/` | Код `201`, сущности созданы | Код `201`, данные созданы | Пройден |
| Валидация обязательных полей | Запрос без обязательных полей | Код `400/422`, ошибка валидации | Ошибка валидации возвращена | Пройден |

#### Таблица 3.8 - Тестирование модуля оценочных сессий и верификации

| Проверяемая функция | Входные данные | Ожидаемый результат | Фактический результат | Статус |
|---|---|---|---|---|
| Создание сессии оценки | `POST /api/evaluation-sessions/` | Код `201`, сессия создана, критерии назначены | Код `201`, сессия создана | Пройден |
| Сохранение ответа по критерию | `POST/PATCH /api/evaluation-answers/` | Код `200/201`, ответ сохранен | Код `200/201`, ответ сохранен | Пройден |
| Верификация экспертом | `POST /api/assigned-criteria/{id}/verify/` | Статус верификации обновлен | Статус обновляется корректно | Пройден |
| Запрос уточнений | `POST /api/assigned-criteria/{id}/request_changes/` | Комментарий верификатора сохраняется | Комментарий и статус сохранены | Пройден |

#### Таблица 3.9 - Тестирование аналитики и отчетности

| Проверяемая функция | Входные данные | Ожидаемый результат | Фактический результат | Статус |
|---|---|---|---|---|
| Расчет общего индекса | `GET /api/evaluation-sessions/{id}/get_overall_maturity_index/` | Код `200`, возвращается индекс зрелости | Код `200`, индекс возвращен | Пройден |
| Расчет доменных оценок | `GET /api/evaluation-sessions/{id}/get_domain_scores/` | Код `200`, возвращается словарь оценок по доменам | Код `200`, данные возвращены | Пройден |
| Сравнение продуктов | `GET /api/evaluation-sessions/compare_products/` | Код `200`, сравнение по последним индексам | Код `200`, данные доступны | Пройден |
| Генерация PDF-паспорта | `GET /api/evaluation-sessions/{id}/generate_maturity_passport/` | Код `200`, PDF формируется | Код `200`, файл выгружается | Пройден |

На **Рисунке 3.20** представлен результат успешного создания карточки цифрового продукта. Сервер вернул код `201` и JSON-объект созданной записи, включая идентификатор продукта, что подтверждает корректность обработки `POST /api/products/`.

На **Рисунке 3.21** представлен результат создания сессии оценки. Сервер вернул код `201` и данные новой сессии (`id`, `product`, `status`, `start_date`), что подтверждает работоспособность модуля инициации оценки.

На **Рисунке 3.22** представлен результат расчета интегрального показателя через endpoint `get_overall_maturity_index`. В ответе (`200`) возвращается числовое значение `overall_index`, что подтверждает корректную работу расчетного блока.

На **Рисунке 3.23** представлен результат получения оценок по доменам через endpoint `get_domain_scores`. Сервер вернул код `200` и структуру `domain_scores`, используемую далее для построения диаграмм и сравнительного анализа.

На **Рисунке 3.24** представлен результат генерации паспорта зрелости в формате PDF. Сервер возвращает код `200`, после чего документ доступен для загрузки/просмотра, что подтверждает корректную работу подсистемы отчетности.

### Интеграционное тестирование (сквозной сценарий)

В интеграционном тестировании выполнялся полный бизнес-сценарий:

1. Администратор создает продукт и сессию оценки.  
2. Владелец продукта заполняет ответы по критериям, прикладывает комментарии и файлы-доказательства.  
3. Эксперт проверяет ответы, запрашивает уточнение по отдельному критерию, затем подтверждает данные.  
4. Система автоматически пересчитывает индексы зрелости и формирует итоговый PDF-отчет.  
5. Результаты отображаются в аналитическом интерфейсе (динамика и сравнение продуктов).

Результат интеграционного теста: критических ошибок не выявлено, сквозной процесс выполняется в соответствии с целевой логикой TO-BE.

### Нагрузочное тестирование (k6)

Нагрузочная проверка выполнялась скриптом `tests/performance/k6-smoke.js`.

Параметры профиля:

- `vus`: до 50 виртуальных пользователей;
- `duration`: 60 секунд;
- пороги: `http_req_duration p(95) < 3000ms`, `http_req_failed < 5%`.

Результат: на тестовом профиле ключевые пороги выдерживаются; деградации, препятствующей базовым сценариям эксплуатации, не зафиксировано.

### Оценка эффективности

По результатам апробации подтверждены качественные эффекты автоматизации:

- сокращение доли ручных операций при проведении оценки;
- повышение прозрачности процесса за счет ролевого workflow и статусов верификации;
- воспроизводимость расчетов индексов по единым формулам;
- ускорение подготовки отчетности за счет автоматической генерации PDF и встроенной визуализации.

### Какие скриншоты включить в пояснительную записку

Для раздела 3.3 рекомендуется включить следующий набор иллюстраций:

1. `Postman`: регистрация/вход (`201/200`) и получение JWT.  
2. `Postman`: пример `401` без токена и `403` при недостаточных правах.  
3. UI: создание продукта и запуск сессии оценки.  
4. UI: ввод оценок и блок верификации (подтверждение / запрос уточнений).  
5. UI: итоговый дашборд с индексом и графиками.  
6. UI/API: генерация и скачивание PDF-паспорта.  
7. Терминал/отчет: запуск `k6` с итоговыми метриками.  
8. CI: успешный прогон `GitHub Actions` (lint + tests + docker build).

### Пошаговый гайд по подготовке скриншотов в Postman

Ниже приведен практический сценарий, который можно выполнить последовательно и получить готовый набор скриншотов для раздела тестирования.

#### Шаг 1. Настройка окружения в Postman

1. Создайте environment `local`.
2. Добавьте переменные:
   - `base_url = http://localhost:8000`
   - `token =` (пустое значение на старте)
3. Убедитесь, что environment `local` выбран в правом верхнем углу Postman.

#### Шаг 2. Базовая коллекция запросов

Создайте коллекцию `Diploma Testing` и добавьте запросы в следующем порядке.

1) **Проверка без авторизации (скрин для 401)**

- Method: `GET`
- URL: `{{base_url}}/api/products/`
- Без заголовка `Authorization`
- Ожидаемо: `401 Authentication credentials were not provided`

2) **Вход и получение JWT**

- Method: `POST`
- URL: `{{base_url}}/api/auth/login/`
- Body -> raw -> JSON:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

- Ожидаемо: `200`, в ответе есть поле `token`
- Скопируйте значение `token` в переменную environment `token`

3) **Проверка авторизованного запроса (скрин для 200)**

- Method: `GET`
- URL: `{{base_url}}/api/auth/user/`
- Authorization -> `Bearer Token` -> `{{token}}`
- Ожидаемо: `200`, JSON с `id`, `username`, `email`, `role`, `is_staff`

4) **Создание продукта**

- Method: `POST`
- URL: `{{base_url}}/api/products/`
- Authorization: `Bearer {{token}}`
- Body -> raw -> JSON:

```json
{
  "name": "Мобильное приложение Умный регион",
  "description": "Тестовый продукт для раздела 3.3",
  "department_owner": "Минцифры региона",
  "product_link": "https://example.com",
  "launch_date": "2024-01-15",
  "is_archived": false
}
```

- Ожидаемо: `201`, в ответе есть `id` продукта (сохраните его как `product_id`)

5) **Создание сессии оценки**

- Method: `POST`
- URL: `{{base_url}}/api/evaluation-sessions/`
- Authorization: `Bearer {{token}}`
- Body -> raw -> JSON:

```json
{
  "product": 1,
  "status": "pending"
}
```

> Если `product` не равен `1`, подставьте `id` из предыдущего шага.

- Ожидаемо: `201`, в ответе есть `id` сессии (сохраните как `session_id`)

6) **Проверка расчетного endpoint**

- Method: `GET`
- URL: `{{base_url}}/api/evaluation-sessions/{session_id}/get_overall_maturity_index/`
- Authorization: `Bearer {{token}}`
- Ожидаемо: `200`, JSON с полем `overall_index`

7) **Проверка доменных оценок**

- Method: `GET`
- URL: `{{base_url}}/api/evaluation-sessions/{session_id}/get_domain_scores/`
- Authorization: `Bearer {{token}}`
- Ожидаемо: `200`, JSON с `domain_scores`

8) **Генерация PDF-паспорта**

- Method: `GET`
- URL: `{{base_url}}/api/evaluation-sessions/{session_id}/generate_maturity_passport/`
- Authorization: `Bearer {{token}}`
- Ожидаемо: `200`, файл PDF скачивается/открывается

#### Шаг 3. Как правильно делать скриншоты

На каждом скриншоте должны быть видны:

- метод и URL запроса;
- вкладка `Body` запроса (если есть payload);
- HTTP-статус ответа (`200/201/401/403`);
- JSON-ответ (или факт загрузки PDF);
- время выполнения и размер ответа (желательно).

#### Шаг 4. Рекомендуемое именование файлов

- `fig-3-17-auth-401-no-token.png`
- `fig-3-18-auth-login-jwt-200.png`
- `fig-3-19-auth-user-200.png`
- `fig-3-20-create-product-201.png`
- `fig-3-21-create-session-201.png`
- `fig-3-22-overall-index-200.png`
- `fig-3-23-domain-scores-200.png`
- `fig-3-24-pdf-passport-200.png`

### Рекомендации по дальнейшему развитию

1. Расширить автоматизацию тестирования полноценными e2e-сценариями (`Playwright`/`Selenium`) для критических пользовательских путей.  
2. Добавить в CI статический анализ безопасности (`Bandit` для backend, `npm audit`/SAST для frontend).  
3. Выполнять регулярные нагрузочные тесты с профилями длительной и пиковой нагрузки, хранить исторические SLA-отчеты.  
4. Внедрить формализованные UAT-чек-листы для ролей (Администратор, Эксперт, Владелец, Наблюдатель).  
5. Расширить аналитическую часть отчетности метриками стабильности релизов и временем закрытия замечаний верификации.

---

## 🚀 Быстрый старт

### Локальный запуск

```bash
# Backend
cd backend/digital_product_maturity_project
pip install -r ../requirements.txt
python manage.py migrate
python create_superuser.py
python populate_db.py
python manage.py runserver

# Frontend (в другом терминале)
cd frontend
npm install
npm start
```

### Docker Compose

```bash
docker-compose up --build
```

**Доступ:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Логин: `admin` / Пароль: `admin123`

---

## 📄 Лицензия

MIT License

## 👨‍💻 Автор

Система разработана для оценки зрелости цифровых продуктов региона.

---

## ✅ Матрица покрытия требований

### Функциональные требования

| Требование | Статус | Как покрыто |
|---|---|---|
| ФТ-01 Реестр продуктов | ✅ Выполнено | CRUD + архивация (`Product`, `/api/products/`) |
| ФТ-02 Конструктор критериев | ✅ Выполнено | `Domain`, `Criterion`, `RatingScale` + API |
| ФТ-03 Оценочные сессии | ✅ Выполнено | `EvaluationSession`, автоназначение `AssignedCriterion` |
| ФТ-04 Ввод и верификация | ✅ Выполнено | `EvaluationAnswer` (балл/метрика/файл/коммент) + `verify/request_changes` |
| ФТ-05 Расчет и визуализация | ✅ Выполнено | Индексы, графики, сравнение продуктов, история индекса |
| ФТ-06 Отчетность | ✅ Выполнено | Паспорт зрелости PDF + портфельный отчет |
| ФТ-07 Роли и доступ | ✅ Выполнено | `Role`, `Profile`, permission-классы RBAC |

### Нефункциональные требования

| Требование | Статус | Как покрыто |
|---|---|---|
| НФТ-01 Производительность | 🟡 Частично | k6 smoke добавлен, требуется регулярный запуск и фиксация SLA-отчетов |
| НФТ-02 Usability | 🟡 Частично | адаптивный web-интерфейс, статусы и подтверждения; нужны UX-тесты с пользователями |
| НФТ-03 Надежность и безопасность | 🟡 Частично | HTTPS/secure cookies/env hardening, JWT, хэш-пароли, backup; требуется production TLS-контур и аудит OWASP |
| НФТ-04 Техническая реализация | ✅ Выполнено | клиент-сервер, Django+React+PostgreSQL, Docker Compose |
| НФТ-05 Масштабируемость | 🟡 Частично | подготовлен модульный монолит и контейнеризация; автоскейлинг не внедрен |

### Ограничения прототипа

- SLA (3 сек при 50 одновременных пользователях и PDF до 30 сек) подтверждается нагрузочным тестом и инфраструктурой эксплуатации.
- Полный security hardening (WAF, централизованный секрет-менеджмент, регулярный pentest) относится к production-контуру региона.
