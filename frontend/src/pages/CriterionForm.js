import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams, Link } from 'react-router-dom';
import RatingScaleForm from '../components/RatingScaleForm';

function CriterionForm() {
  const { domainId, id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    domain: domainId || '',
    name: '',
    description: '',
    weight: 25.00,
  });
  const [domains, setDomains] = useState([]);
  const [currentDomain, setCurrentDomain] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Загружаем список доменов
    axios.get('/api/domains/')
      .then(response => {
        setDomains(response.data);
      })
      .catch(error => {
        console.error('Ошибка при загрузке доменов:', error);
      });

    // Загружаем информацию о текущем домене
    if (domainId) {
      axios.get(`/api/domains/${domainId}/`)
        .then(response => {
          setCurrentDomain(response.data);
        })
        .catch(error => {
          console.error('Ошибка при загрузке домена:', error);
        });
    }

    // Если редактирование - загружаем критерий
    if (id) {
      axios.get(`/api/criteria/${id}/`)
        .then(response => {
          setFormData(response.data);
        })
        .catch(error => {
          console.error('Ошибка при загрузке критерия:', error);
        });
    }
  }, [id, domainId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);

    const request = id
      ? axios.put(`/api/criteria/${id}/`, formData)
      : axios.post('/api/criteria/', formData);

    request
      .then(response => {
        alert(id ? '✅ Критерий успешно обновлен!' : '✅ Критерий успешно создан!');
        if (domainId) {
          navigate(`/domains/${domainId}/criteria`);
        } else {
          navigate('/domains');
        }
      })
      .catch(error => {
        console.error('Ошибка при сохранении критерия:', error);
        alert('❌ Ошибка при сохранении критерия');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const backUrl = domainId ? `/domains/${domainId}/criteria` : '/domains';

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <Link to={backUrl} style={{ color: '#1f2937', textDecoration: 'none' }}>
          ← Назад к критериям
        </Link>
      </div>

      <h1>{id ? '✏️ Редактирование критерия' : '➕ Добавление критерия'}</h1>
      
      {currentDomain && (
        <div className="info-banner" style={{ marginBottom: '30px', padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
          <strong>Домен:</strong> {currentDomain.name} ({currentDomain.weight}% в общей оценке)
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {!domainId && (
          <div>
            <label>📊 Выберите домен:</label>
            <select
              name="domain"
              value={formData.domain}
              onChange={handleChange}
              required
            >
              <option value="">-- Выберите домен --</option>
              {domains.map(domain => (
                <option key={domain.id} value={domain.id}>
                  {domain.name}
                </option>
              ))}
            </select>
          </div>
        )}

        <div>
          <label>📝 Название критерия:</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Например: Современность технологического стека"
            required
          />
        </div>

        <div>
          <label>📄 Описание критерия:</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Опишите, что оценивается в этом критерии..."
            rows="4"
          />
        </div>

        <div>
          <label>⚖️ Вес в домене (%):</label>
          <input
            type="number"
            name="weight"
            value={formData.weight}
            onChange={handleChange}
            min="0.01"
            max="100"
            step="0.01"
            required
            placeholder="25.00"
          />
          <small style={{ display: 'block', marginTop: '5px', color: '#666' }}>
            Укажите, какой процент этот критерий занимает в оценке домена
          </small>
        </div>

        <div style={{ display: 'flex', gap: '10px', marginTop: '30px' }}>
          <button type="submit" disabled={loading}>
            {loading ? '💾 Сохранение...' : (id ? '💾 Сохранить изменения' : '➕ Создать критерий')}
          </button>
          <Link to={backUrl}>
            <button type="button" className="secondary-btn">
              ❌ Отмена
            </button>
          </Link>
        </div>
      </form>

      {id && (
        <div style={{ marginTop: '40px' }}>
          <RatingScaleForm criterionId={id} />
        </div>
      )}
    </div>
  );
}

export default CriterionForm;
