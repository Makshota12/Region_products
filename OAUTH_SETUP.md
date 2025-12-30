# Настройка OAuth авторизации

## 🎉 Что уже сделано:

✅ **Красивый современный дизайн** с градиентами и анимациями  
✅ **Навигация на русском языке**  
✅ **Кликабельные карточки продуктов** с переходом на детальную страницу  
✅ **Детальная карточка продукта** с информацией и историей оценок  
✅ **Страницы регистрации и входа** с красивым UI  
✅ **JWT авторизация** через username/password  
✅ **Базовая интеграция Google и Telegram OAuth** (требует настройки)  

---

## 🔐 Авторизация

### 1. Обычная авторизация (username/password)

**Уже работает!** Просто перейдите на страницу `/login` или `/register`.

**Тестовый аккаунт:**
- Логин: `admin`
- Пароль: `admin123`

### 2. Настройка Google OAuth

#### Шаг 1: Создайте проект в Google Cloud

1. Перейдите на https://console.cloud.google.com/
2. Создайте новый проект или выберите существующий
3. Включите **Google+ API**

#### Шаг 2: Создайте OAuth 2.0 credentials

1. Перейдите в **APIs & Services** → **Credentials**
2. Нажмите **Create Credentials** → **OAuth client ID**
3. Выберите **Web application**
4. Добавьте Authorized redirect URIs:
   ```
   http://localhost:8000/api/auth/google/callback/
   http://127.0.0.1:8000/api/auth/google/callback/
   ```
5. Сохраните **Client ID** и **Client Secret**

#### Шаг 3: Настройте в Django Admin

1. Перейдите на http://127.0.0.1:8000/admin/
2. Войдите как `admin` / `admin123`
3. Найдите **Social applications** → **Add**
4. Заполните:
   - **Provider:** Google
   - **Name:** Google OAuth
   - **Client id:** (ваш Client ID из Google)
   - **Secret key:** (ваш Client Secret из Google)
   - **Sites:** Выберите `example.com`
5. Сохраните

#### Шаг 4: Тестирование

Перейдите на `/login` и нажмите **"Войти через Google"**

---

### 3. Настройка Telegram OAuth

#### Шаг 1: Создайте Telegram бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте `/newbot`
3. Следуйте инструкциям (придумайте имя и username для бота)
4. Сохраните **API Token** (например: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

#### Шаг 2: Настройте Web App для бота

1. Отправьте `/setdomain` в BotFather
2. Выберите своего бота
3. Укажите домен: `localhost:3000` (для разработки)

#### Шаг 3: Обновите настройки Django

Откройте файл:
```
backend/digital_product_maturity_project/digital_product_maturity/settings.py
```

Найдите и замените:
```python
'telegram': {
    'TOKEN': 'YOUR_TELEGRAM_BOT_TOKEN_HERE',  # Вставьте ваш токен
}
```

#### Шаг 4: Обновите компонент Login.js

Откройте файл:
```
frontend/src/pages/Login.js
```

Найдите и замените:
```javascript
const telegramBotUsername = 'YourBotUsername'; // Замените на username вашего бота
```

#### Шаг 5: Настройте в Django Admin

1. Перейдите на http://127.0.0.1:8000/admin/
2. Найдите **Social applications** → **Add**
3. Заполните:
   - **Provider:** Telegram
   - **Name:** Telegram OAuth
   - **Client id:** (username вашего бота без @)
   - **Secret key:** (ваш Bot Token)
   - **Sites:** Выберите `example.com`
4. Сохраните

---

## 📱 Использование приложения

### Главная страница
- **Просмотр продуктов:** Красивые карточки с информацией
- **Клик на карточку:** Открывает детальную страницу продукта

### Детальная страница продукта
- **Основная информация:** Название, описание, владелец, дата запуска, ссылка
- **История оценок:** Все проведенные оценки с статусами
- **Действия:**
  - ✏️ Редактировать продукт
  - 📥 Архивировать/восстановить
  - 🗑️ Удалить
  - ➕ Создать новую оценку

### Страницы авторизации
- **Регистрация:** `/register` - создание нового аккаунта
- **Вход:** `/login` - вход через username/password, Google или Telegram
- **Выход:** Автоматический при выходе из системы

---

## 🎨 Новый дизайн

### Цветовая схема:
- **Основной градиент:** Фиолетовый → Синий (#667eea → #764ba2)
- **Акцент:** Зеленый для успешных действий
- **Красный:** Для удаления/ошибок

### Элементы:
- ✨ Плавные анимации при наведении
- 📱 Адаптивный дизайн
- 💳 Красивые карточки с тенями
- 🎯 Интерактивные кнопки
- 🌈 Градиентная навигация

---

## 🚀 Быстрый старт

### Запуск серверов:

**Backend:**
```bash
cd backend\digital_product_maturity_project
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm start
```

**Или используйте:**
```bash
start_local.bat
```

### Доступ:
- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8000/api/
- **Django Admin:** http://127.0.0.1:8000/admin/

---

## 📝 API Endpoints для авторизации

```
POST /api/auth/register/        - Регистрация нового пользователя
POST /api/auth/login/           - Вход (получение JWT токенов)
POST /api/auth/logout/          - Выход (blacklist токена)
GET  /api/auth/user/            - Информация о текущем пользователе

# Google OAuth
GET  /api/auth/google/login/    - Начало авторизации через Google
GET  /api/auth/google/callback/ - Callback после авторизации Google

# Telegram OAuth
GET  /api/auth/telegram/login/  - Начало авторизации через Telegram
```

---

## 🔧 Troubleshooting

### Google OAuth не работает:
1. Проверьте, что redirect URI точно совпадает
2. Убедитесь, что Google+ API включен
3. Проверьте настройки в Django Admin

### Telegram OAuth не работает:
1. Проверьте, что токен бота правильный
2. Убедитесь, что бот активирован (/start)
3. Проверьте домен в настройках бота

### Ошибки миграций:
```bash
cd backend\digital_product_maturity_project
python manage.py migrate
```

### Ошибки компиляции React:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## 💡 Дополнительные возможности

- Все страницы переведены на русский язык
- Карточки продуктов кликабельны
- Детальная информация о продукте
- История оценок продукта
- Красивая форма авторизации
- Поддержка социальных сетей (Google, Telegram)
- JWT токены для безопасности
- Автоматическое создание профилей пользователей

---

**Готово! Приложение полностью настроено и готово к использованию! 🎉**

