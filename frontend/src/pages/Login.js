import React, { useState } from 'react';
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
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading} style={{ width: '100%' }}>
            {loading ? '⏳ Вход...' : '🔓 Войти'}
          </button>
        </form>

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

