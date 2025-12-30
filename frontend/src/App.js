import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import ProductList from './pages/ProductList';
import ProductForm from './pages/ProductForm';
import DomainList from './pages/DomainList';
import DomainForm from './pages/DomainForm';
import CriterionList from './pages/CriterionList';
import CriterionForm from './pages/CriterionForm';
import EvaluationSessionList from './pages/EvaluationSessionList';
import EvaluationSessionForm from './pages/EvaluationSessionForm';
import EvaluationInput from './pages/EvaluationInput';
import EvaluationResults from './pages/EvaluationResults';
import Login from './pages/Login';
import Register from './pages/Register';
import ProductDetail from './pages/ProductDetail';
import Profile from './pages/Profile';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = React.useState(false);
  const [username, setUsername] = React.useState('');

  React.useEffect(() => {
    // Функция для проверки авторизации
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      const savedUsername = localStorage.getItem('username');
      if (token) {
        setIsLoggedIn(true);
        setUsername(savedUsername || 'Пользователь');
      } else {
        setIsLoggedIn(false);
        setUsername('');
      }
    };

    // Проверяем при загрузке
    checkAuth();

    // Слушаем изменения в localStorage
    const handleStorageChange = (e) => {
      if (e.key === 'username' || e.key === 'token') {
        checkAuth();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Также проверяем периодически (на случай изменений в том же окне)
    const interval = setInterval(checkAuth, 1000);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, []);

  return (
    <Router>
      <div className="App">
        <nav>
          <ul>
            <li>
              <Link to="/">📦 Продукты</Link>
            </li>
            <li>
              <Link to="/add-product">➕ Добавить продукт</Link>
            </li>
            <li>
              <Link to="/domains">⚙️ Модель оценки</Link>
            </li>
            <li>
              <Link to="/evaluation-sessions">📊 Сессии оценки</Link>
            </li>
            <li>
              {isLoggedIn ? (
                <Link to="/profile">👤 {username}</Link>
              ) : (
                <Link to="/login">🔐 Вход</Link>
              )}
            </li>
          </ul>
        </nav>
        <div className="content">
          <Routes>
            <Route path="/" element={<ProductList />} />
            <Route path="/product/:id" element={<ProductDetail />} />
            <Route path="/add-product" element={<ProductForm />} />
            <Route path="/edit-product/:id" element={<ProductForm />} />

            <Route path="/domains" element={<DomainList />} />
            <Route path="/add-domain" element={<DomainForm />} />
            <Route path="/edit-domain/:id" element={<DomainForm />} />
            <Route path="/domains/:domainId/criteria" element={<CriterionList />} />
            <Route path="/domains/:domainId/add-criterion" element={<CriterionForm />} />
            <Route path="/edit-criterion/:id" element={<CriterionForm />} />

            <Route path="/evaluation-sessions" element={<EvaluationSessionList />} />
            <Route path="/start-evaluation" element={<EvaluationSessionForm />} />
            <Route path="/evaluation-session/:sessionId" element={<EvaluationInput />} />
            <Route path="/evaluation-session/:sessionId/results" element={<EvaluationResults />} />
            
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
