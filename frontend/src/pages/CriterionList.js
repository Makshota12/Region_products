import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useParams } from 'react-router-dom';

function CriterionList() {
  const { domainId } = useParams();
  const [domain, setDomain] = useState(null);
  const [criteria, setCriteria] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`/api/domains/${domainId}/`)
      .then(response => setDomain(response.data))
      .catch(error => console.error('Ошибка при загрузке домена:', error));

    axios.get(`/api/criteria/?domain=${domainId}`)
      .then(response => {
        setCriteria(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Ошибка при загрузке критериев:', error);
        setLoading(false);
      });
  }, [domainId]);

  const handleDelete = (id, name) => {
    if (window.confirm(`Вы уверены, что хотите удалить критерий "${name}"?`)) {
      axios.delete(`/api/criteria/${id}/`)
        .then(() => {
          alert('✅ Критерий успешно удален');
          setCriteria(criteria.filter(c => c.id !== id));
        })
        .catch(error => {
          console.error('Ошибка при удалении критерия:', error);
          alert('❌ Не удалось удалить критерий');
        });
    }
  };

  if (loading) {
    return <div className="loading">⏳ Загрузка критериев...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/domains" style={{ color: '#667eea', textDecoration: 'none' }}>
          ← Назад к доменам
        </Link>
      </div>

      {domain && (
        <>
          <h1>📋 Критерии домена: {domain.name}</h1>
          <div className="domain-info-banner" style={{ marginBottom: '30px' }}>
            <p style={{ margin: 0 }}>
              <strong>Описание:</strong> {domain.description || 'Нет описания'}
            </p>
            <p style={{ margin: '10px 0 0 0' }}>
              <strong>Вес в общей оценке:</strong> {domain.weight}%
            </p>
          </div>
        </>
      )}

      <div style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
        <Link to={`/domains/${domainId}/add-criterion`}>
          <button>➕ Добавить критерий</button>
        </Link>
      </div>

      {criteria.length === 0 ? (
        <div className="empty-state">
          <p>Пока нет критериев для этого домена</p>
          <Link to={`/domains/${domainId}/add-criterion`}>
            <button>➕ Создать первый критерий</button>
          </Link>
        </div>
      ) : (
        <div className="criteria-list">
          {criteria.map(criterion => (
            <div key={criterion.id} className="criterion-card">
              <div className="criterion-header">
                <h3>{criterion.name}</h3>
                <span className="criterion-weight">Вес: {criterion.weight}%</span>
              </div>
              
              {criterion.description && (
                <p className="criterion-description">{criterion.description}</p>
              )}
              
              <div className="criterion-footer">
                <Link to={`/edit-criterion/${criterion.id}`}>
                  <button className="edit-btn">
                    ✏️ Редактировать
                  </button>
                </Link>
                <button 
                  onClick={() => handleDelete(criterion.id, criterion.name)} 
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

export default CriterionList;
