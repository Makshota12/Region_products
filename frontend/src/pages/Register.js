import React, { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showPassword2, setShowPassword2] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.password2) {
      setError('Пароли не совпадают');
      return;
    }

    if (formData.password.length < 6) {
      setError('Пароль должен содержать минимум 6 символов');
      return;
    }

    setLoading(true);

    try {
      await axios.post('/api/auth/register/', {
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      alert('Регистрация успешна! Теперь вы можете войти.');
      navigate('/login');
    } catch (error) {
      if (error.response?.data) {
        const errorMsg = Object.values(error.response.data).flat().join(' ');
        setError(errorMsg);
      } else {
        setError('Ошибка при регистрации. Попробуйте позже.');
      }
      console.error('Ошибка регистрации:', error);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>📝 Регистрация</h1>
        <p className="auth-subtitle">Создайте аккаунт для доступа к системе</p>

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
              placeholder="Придумайте имя пользователя"
              minLength="3"
            />
          </div>

          <div>
            <label>Email:</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Введите ваш email"
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
                placeholder="Придумайте пароль (минимум 6 символов)"
                minLength="6"
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

          <div>
            <label>Подтвердите пароль:</label>
            <div className="password-input-wrapper">
              <input
                type={showPassword2 ? "text" : "password"}
                name="password2"
                value={formData.password2}
                onChange={handleChange}
                required
                placeholder="Введите пароль еще раз"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword2(!showPassword2)}
              >
                {showPassword2 ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading} style={{ width: '100%' }}>
            {loading ? '⏳ Регистрация...' : '✅ Зарегистрироваться'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Уже есть аккаунт? <Link to="/login">Войти</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Register;

