import React, { useCallback, useEffect, useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [googleReady, setGoogleReady] = useState(false);
  const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post('/api/auth/login/', formData);
      // Сохраняем токен в localStorage
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('username', formData.username);
      alert(`✅ Добро пожаловать, ${formData.username}!`);
      navigate('/profile');
    } catch (error) {
      setError('Неверное имя пользователя или пароль');
      console.error('Ошибка входа:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleCredential = useCallback(async (response) => {
    if (!response?.credential) {
      setError('Не удалось получить токен Google');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const apiResponse = await axios.post('/api/auth/google/', {
        id_token: response.credential
      });

      localStorage.setItem('token', apiResponse.data.token);
      localStorage.setItem('username', apiResponse.data.username);
      alert(`✅ Добро пожаловать, ${apiResponse.data.username}!`);
      navigate('/profile');
    } catch (err) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      const backendError = err?.response?.data?.error;
      setError(
        backendError
          ? `Google OAuth: ${backendError}`
          : 'Не удалось войти через Google. Проверьте настройки OAuth.'
      );
      console.error('Google login error:', err);
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    if (!googleClientId) {
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => {
      if (!window.google || !window.google.accounts || !window.google.accounts.id) {
        return;
      }

      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: handleGoogleCredential
      });

      const googleButtonContainer = document.getElementById('google-signin-button');
      if (googleButtonContainer) {
        googleButtonContainer.innerHTML = '';
        window.google.accounts.id.renderButton(googleButtonContainer, {
          theme: 'outline',
          size: 'large',
          width: '320',
          text: 'continue_with'
        });
      }
      setGoogleReady(true);
    };
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, [googleClientId, handleGoogleCredential]);


  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>🔐 Вход в систему</h1>
        <p className="auth-subtitle">Войдите для доступа к системе оценки зрелости продуктов</p>

        {error && (
          <div className="error">
            ❌ {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div>
            <label>Имя пользователя:</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="Введите имя пользователя"
            />
          </div>

          <div>
            <label>Пароль:</label>
            <div className="password-input-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Введите пароль"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Скрыть пароль' : 'Показать пароль'}
                title={showPassword ? 'Скрыть пароль' : 'Показать пароль'}
              >
                {showPassword ? '🙈' : '👁'}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading} style={{ width: '100%' }}>
            {loading ? '⏳ Вход...' : '🔓 Войти'}
          </button>
        </form>

        <div style={{ marginTop: '16px', textAlign: 'center' }}>
          <p style={{ marginBottom: '8px' }}>или</p>
          {!googleClientId && (
            <div className="error" style={{ marginBottom: '8px' }}>
              Укажите REACT_APP_GOOGLE_CLIENT_ID для входа через Google
            </div>
          )}
          <div id="google-signin-button" />
          {googleClientId && !googleReady && <p>Подключение Google входа...</p>}
        </div>

        <div className="auth-footer">
          <p>
            Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
          </p>
        </div>
      </div>

      <div className="auth-info">
        <h3>💡 Тестовый доступ</h3>
        <div className="test-credentials">
          <p><strong>Логин:</strong> admin</p>
          <p><strong>Пароль:</strong> admin123</p>
        </div>
      </div>
    </div>
  );
}

export default Login;

