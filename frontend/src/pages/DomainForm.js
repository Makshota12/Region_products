import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams, Link } from 'react-router-dom';

function DomainForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    weight: 25.00
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (id) {
      axios.get(`/api/domains/${id}/`)
        .then(response => {
          setFormData(response.data);
        })
        .catch(error => {
          console.error('Ошибка при загрузке домена:', error);
        });
    }
  }, [id]);

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
      ? axios.put(`/api/domains/${id}/`, formData)
      : axios.post('/api/domains/', formData);

    request
      .then(response => {
        alert(id ? ' Домен успешно обновлен!' : ' Домен успешно создан!');
        navigate('/domains');
      })
      .catch(error => {
        console.error('Ошибка при сохранении домена:', error);
        alert(' Ошибка при сохранении домена');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/domains" style={{ color: '#1f2937', textDecoration: 'none' }}>
          ← Назад к доменам
        </Link>
      </div>

      <h1>{id ? ' Редактирование домена' : ' Добавление домена'}</h1>
      
      <p style={{ color: '#666', marginBottom: '30px' }}>
        {id 
          ? 'Измените параметры домена оценки'
          : 'Создайте новый домен для модели оценки зрелости продуктов'
        }
      </p>

      <form onSubmit={handleSubmit}>
        <div>
          <label> Название домена:</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Например: Технологическая зрелость"
            required
          />
        </div>

        <div>
          <label> Описание:</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Опишите, что оценивается в этом домене..."
            rows="4"
          />
        </div>

        <div>
          <label> Вес в общей оценке (%):</label>
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
            Укажите, какой процент этот домен занимает в общем индексе зрелости
          </small>
        </div>

        <div style={{ display: 'flex', gap: '10px', marginTop: '30px' }}>
          <button type="submit" disabled={loading}>
            {loading ? ' Сохранение...' : (id ? ' Сохранить изменения' : ' Создать домен')}
          </button>
          <Link to="/domains">
            <button type="button" className="secondary-btn">
               Отмена
            </button>
          </Link>
        </div>
      </form>
    </div>
  );
}

export default DomainForm;
