import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function EvaluationSessionList() {
  const [sessions, setSessions] = useState([]);
  const [products, setProducts] = useState({});
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    in_progress: 0,
    pending: 0
  });

  useEffect(() => {
    // Загружаем сессии
    axios.get('/api/evaluation-sessions/')
      .then(response => {
        setSessions(response.data);
        
        // Подсчитываем статистику
        const statsData = {
          total: response.data.length,
          completed: response.data.filter(s => s.status === 'completed').length,
          in_progress: response.data.filter(s => s.status === 'in_progress').length,
          pending: response.data.filter(s => s.status === 'pending').length
        };
        setStats(statsData);
      })
      .catch(error => {
        console.error('Ошибка при загрузке сессий оценки:', error);
      });

    // Загружаем продукты для отображения названий
    axios.get('/api/products/')
      .then(response => {
        const productsMap = {};
        response.data.forEach(product => {
          productsMap[product.id] = product.name;
        });
        setProducts(productsMap);
        setLoading(false);
      })
      .catch(error => {
        console.error('Ошибка при загрузке продуктов:', error);
        setLoading(false);
      });
  }, []);

  const getStatusText = (status) => {
    const statuses = {
      'pending': 'В ожидании',
      'in_progress': 'В процессе',
      'completed': 'Завершено',
      'archived': 'В архиве'
    };
    return statuses[status] || status;
  };

  if (loading) {
    return <div className="loading">⏳ Загрузка сессий оценки...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>📊 Сессии оценки</h1>
        <Link to="/start-evaluation">
          <button>➕ Начать новую оценку</button>
        </Link>
      </div>

      {/* Статистика */}
      <div className="stats-dashboard">
        <div className="stat-card stat-total">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Всего оценок</div>
          </div>
        </div>
        
        <div className="stat-card stat-completed">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-value">{stats.completed}</div>
            <div className="stat-label">Завершено</div>
          </div>
        </div>
        
        <div className="stat-card stat-progress">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <div className="stat-value">{stats.in_progress}</div>
            <div className="stat-label">В процессе</div>
          </div>
        </div>
        
        <div className="stat-card stat-pending">
          <div className="stat-icon">⏸️</div>
          <div className="stat-content">
            <div className="stat-value">{stats.pending}</div>
            <div className="stat-label">В ожидании</div>
          </div>
        </div>
      </div>

      {sessions.length === 0 ? (
        <div className="empty-state">
          <p>Пока нет сессий оценки</p>
          <Link to="/start-evaluation">
            <button>➕ Создать первую оценку</button>
          </Link>
        </div>
      ) : (
        <div className="sessions-list">
          {sessions.map(session => (
            <div key={session.id} className="session-card">
              <div className="session-header">
                <h3>{products[session.product] || `Продукт #${session.product}`}</h3>
                <span className={`status-badge status-${session.status}`}>
                  {getStatusText(session.status)}
                </span>
              </div>
              
              <div className="session-body">
                <div className="session-info">
                  <div className="info-row">
                    <span className="info-label">📅 Дата начала:</span>
                    <span className="info-value">
                      {new Date(session.start_date).toLocaleDateString('ru-RU')}
                    </span>
                  </div>
                  
                  {session.end_date && (
                    <div className="info-row">
                      <span className="info-label">📅 Дата окончания:</span>
                      <span className="info-value">
                        {new Date(session.end_date).toLocaleDateString('ru-RU')}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="session-footer">
                <Link to={`/evaluation-session/${session.id}`}>
                  <button className="secondary-btn">📝 Оценить</button>
                </Link>
                {session.status === 'completed' && (
                  <Link to={`/evaluation-session/${session.id}/results`}>
                    <button>📊 Результаты</button>
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default EvaluationSessionList;
