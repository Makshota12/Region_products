import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function DomainList() {
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/api/domains/')
      .then(response => {
        setDomains(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Ошибка при загрузке доменов:', error);
        setLoading(false);
      });
  }, []);

  const handleDelete = (id, name) => {
    if (window.confirm(`Вы уверены, что хотите удалить домен "${name}"?`)) {
      axios.delete(`/api/domains/${id}/`)
        .then(() => {
          alert('✅ Домен успешно удален');
          setDomains(domains.filter(d => d.id !== id));
        })
        .catch(error => {
          console.error('Ошибка при удалении домена:', error);
          alert('❌ Не удалось удалить домен');
        });
    }
  };

  if (loading) {
    return <div className="loading">⏳ Загрузка доменов оценки...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>⚙️ Модель оценки - Домены</h1>
        <Link to="/add-domain">
          <button>➕ Добавить домен</button>
        </Link>
      </div>

      <p style={{ color: '#666', marginBottom: '30px' }}>
        Домены - это основные области оценки цифрового продукта. Для каждого домена можно настроить критерии оценки.
      </p>

      {domains.length === 0 ? (
        <div className="empty-state">
          <p>Пока нет доменов оценки</p>
          <Link to="/add-domain">
            <button>➕ Создать первый домен</button>
          </Link>
        </div>
      ) : (
        <div className="domains-list">
          {domains.map(domain => (
            <div key={domain.id} className="domain-card">
              <div className="domain-card-header">
                <h3>📊 {domain.name}</h3>
                <span className="domain-weight-badge">Вес: {domain.weight}%</span>
              </div>
              
              <div className="domain-card-body">
                {domain.description && (
                  <p className="domain-description">{domain.description}</p>
                )}
              </div>
              
              <div className="domain-card-footer">
                <Link to={`/domains/${domain.id}/criteria`}>
                  <button className="view-btn">
                    📋 Критерии
                  </button>
                </Link>
                <Link to={`/edit-domain/${domain.id}`}>
                  <button className="edit-btn">
                    ✏️ Редактировать
                  </button>
                </Link>
                <button 
                  onClick={() => handleDelete(domain.id, domain.name)} 
                  className="delete-btn"
                >
                  🗑️ Удалить
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DomainList;
