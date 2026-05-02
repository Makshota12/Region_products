import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';

function Profile() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [usernameInput, setUsernameInput] = useState('');
  const [avatarFile, setAvatarFile] = useState(null);

  useEffect(() => {
    // Проверяем, есть ли токен
    const token = localStorage.getItem('token');

    if (!token) {
      alert('Вы не авторизованы');
      navigate('/login');
      return;
    }

    // Загружаем информацию о пользователе
    axios.get('/api/auth/user/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(response => {
        setUser(response.data);
        setUsernameInput(response.data.username || '');
        // Обновляем username в localStorage с актуальными данными сервера
        localStorage.setItem('username', response.data.username);
        setLoading(false);
      })
      .catch(error => {
        console.error('Ошибка при загрузке профиля:', error);
        // Если ошибка авторизации - перенаправляем на вход
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('username');
          alert('Сессия истекла. Войдите снова.');
          navigate('/login');
        } else {
          setLoading(false);
        }
      });
  }, [navigate]);

  const handleLogout = () => {
    if (window.confirm('Вы уверены, что хотите выйти?')) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      alert('Вы успешно вышли из системы');
      navigate('/login');
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const formData = new FormData();
      formData.append('username', usernameInput.trim());
      if (avatarFile) {
        formData.append('avatar', avatarFile);
      }

      const response = await axios.patch('/api/auth/user/update/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setUser(response.data);
      localStorage.setItem('username', response.data.username);
      setAvatarFile(null);
      setEditing(false);
      alert('Профиль обновлен');
    } catch (error) {
      console.error('Ошибка при обновлении профиля:', error);
      alert(error.response?.data?.error || 'Не удалось обновить профиль');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="loading">Загрузка профиля...</div>;
  }

  if (!user) {
    return (
      <div className="error">
        Не удалось загрузить профиль
        <br />
        <Link to="/login">
          <button style={{ marginTop: '20px' }}>Войти</button>
        </Link>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <h1>Мой профиль</h1>

      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar">
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt="Аватар профиля"
                style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }}
              />
            ) : (
              user.username?.[0]?.toUpperCase() || 'U'
            )}
          </div>
          <div className="profile-title">
            <h2>{user.username}</h2>
            <span className="profile-role">{user.role || 'Роль не назначена'}</span>
          </div>
        </div>

        <div className="profile-section">
          <h3>Редактирование профиля</h3>
          {!editing ? (
            <button onClick={() => setEditing(true)}>Изменить имя и фото</button>
          ) : (
            <form onSubmit={handleSaveProfile}>
              <div className="info-grid">
                <div className="info-item">
                  <strong>Новое имя пользователя</strong>
                  <input
                    type="text"
                    value={usernameInput}
                    onChange={(e) => setUsernameInput(e.target.value)}
                    required
                    maxLength={150}
                    placeholder="Введите имя пользователя"
                  />
                </div>
                <div className="info-item">
                  <strong>Фото профиля</strong>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setAvatarFile(e.target.files?.[0] || null)}
                  />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
                <button type="submit" disabled={saving}>
                  {saving ? 'Сохранение...' : 'Сохранить'}
                </button>
                <button
                  type="button"
                  className="secondary-btn"
                  onClick={() => {
                    setEditing(false);
                    setUsernameInput(user.username || '');
                    setAvatarFile(null);
                  }}
                >
                  Отмена
                </button>
              </div>
            </form>
          )}
        </div>

        <div className="profile-info">
          <div className="profile-section">
            <h3>Контактная информация</h3>
            <div className="info-grid">
              <div className="info-item">
                <strong>Имя пользователя:</strong>
                <p>{user.username}</p>
              </div>
              <div className="info-item">
                <strong>Email:</strong>
                <p>{user.email || 'Не указан'}</p>
              </div>
            </div>
          </div>

          <div className="profile-section">
            <h3>Права доступа</h3>
            <div className="info-grid">
              <div className="info-item">
                <strong>Роль в системе:</strong>
                <p>{user.role || 'Наблюдатель'}</p>
              </div>
              <div className="info-item">
                <strong>Статус:</strong>
                <p>
                  {user.is_staff ? (
                    <span className="status-badge status-completed">Администратор</span>
                  ) : (
                    <span className="status-badge status-in-progress">Пользователь</span>
                  )}
                </p>
              </div>
            </div>
          </div>

          <div className="profile-section">
            <h3>Описание роли</h3>
            <div className="role-description">
              {user.role === 'Администратор системы' && (
                <p>Полный доступ ко всем функциям системы: управление пользователями, настройка модели оценки, создание и редактирование продуктов, проведение оценок.</p>
              )}
              {user.role === 'Эксперт/Аудитор' && (
                <p>Проведение оценок зрелости продуктов, верификация данных, просмотр результатов, генерация отчетов.</p>
              )}
              {user.role === 'Владелец продукта' && (
                <p>Управление своими продуктами, заполнение оценок, просмотр результатов своих продуктов.</p>
              )}
              {(user.role === 'Наблюдатель' || !user.role) && (
                <p>Просмотр списка продуктов и результатов оценок. Доступ только для чтения.</p>
              )}
            </div>
          </div>
        </div>

        <div className="profile-actions">
          <Link to="/">
            <button className="secondary-btn">
              На главную
            </button>
          </Link>
          <button onClick={handleLogout} className="delete-btn">
            Выйти
          </button>
        </div>
      </div>

      <div className="quick-links">
        <h3>Быстрые действия</h3>
        <div className="links-grid">
          <Link to="/" className="quick-link-card">
            <div className="link-icon"></div>
            <div className="link-title">Продукты</div>
            <div className="link-desc">Список цифровых продуктов</div>
          </Link>

          <Link to="/domains" className="quick-link-card">
            <div className="link-icon"></div>
            <div className="link-title">Модель оценки</div>
            <div className="link-desc">Домены и критерии</div>
          </Link>

          <Link to="/evaluation-sessions" className="quick-link-card">
            <div className="link-icon"></div>
            <div className="link-title">Сессии оценки</div>
            <div className="link-desc">Проведение оценок</div>
          </Link>

          {user.is_staff && (
            <a href="http://127.0.0.1:8000/admin/" target="_blank" rel="noopener noreferrer" className="quick-link-card">
              <div className="link-icon"></div>
              <div className="link-title">Админ-панель</div>
              <div className="link-desc">Django Admin</div>
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

export default Profile;

