import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate, Link } from 'react-router-dom';

function ProductForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    department_owner: '',
    product_link: '',
    launch_date: '',
    is_archived: false,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (id) {
      // Загружаем данные продукта для редактирования
      axios.get(`/api/products/${id}/`)
        .then(response => {
          setFormData(response.data);
        })
        .catch(error => {
          console.error('Ошибка при загрузке продукта:', error);
        });
    }
  }, [id]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);

    const request = id
      ? axios.put(`/api/products/${id}/`, formData)
      : axios.post('/api/products/', formData);

    request
      .then(response => {
        alert(id ? ' Продукт успешно обновлен!' : ' Продукт успешно создан!');
        navigate('/');
      })
      .catch(error => {
        console.error('Ошибка при сохранении продукта:', error);
        alert(' Ошибка при сохранении продукта');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/" style={{ color: '#1f2937', textDecoration: 'none' }}>
          ← Назад к списку продуктов
        </Link>
      </div>

      <h1>{id ? ' Редактирование продукта' : ' Добавление продукта'}</h1>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label> Наименование продукта:</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Введите название цифрового продукта"
            required
          />
        </div>

        <div>
          <label> Описание:</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Опишите цифровой продукт, его назначение и функциональность"
            rows="4"
          />
        </div>

        <div>
          <label> Ответственное ведомство/владелец:</label>
          <input
            type="text"
            name="department_owner"
            value={formData.department_owner}
            onChange={handleChange}
            placeholder="Например: Министерство цифрового развития"
            required
          />
        </div>

        <div>
          <label> Ссылка на продукт:</label>
          <input
            type="url"
            name="product_link"
            value={formData.product_link}
            onChange={handleChange}
            placeholder="https://example.com"
          />
        </div>

        <div>
          <label> Дата запуска:</label>
          <input
            type="date"
            name="launch_date"
            value={formData.launch_date}
            onChange={handleChange}
          />
        </div>

        {id && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <input
              type="checkbox"
              name="is_archived"
              checked={formData.is_archived}
              onChange={handleChange}
              id="is_archived"
            />
            <label htmlFor="is_archived" style={{ margin: 0 }}>
               Отправить в архив
            </label>
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', marginTop: '30px' }}>
          <button type="submit" disabled={loading}>
            {loading ? ' Сохранение...' : (id ? ' Сохранить изменения' : ' Создать продукт')}
          </button>
          <Link to="/">
            <button type="button" className="secondary-btn">
               Отмена
            </button>
          </Link>
        </div>
      </form>
    </div>
  );
}

export default ProductForm;
