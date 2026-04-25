import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, Link, useNavigate } from 'react-router-dom';

function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Загружаем данные о продукте
    axios.get(`/api/products/${id}/`)
      .then(response => {
        setProduct(response.data);
      })
      .catch(error => {
        console.error('Ошибка при загрузке продукта:', error);
      });

    // Загружаем оценки продукта
    axios.get(`/api/evaluation-sessions/?product=${id}`)
      .then(response => {
        setEvaluations(response.data.filter(session => session.product === parseInt(id)));
      })
      .catch(error => {
        console.error('Ошибка при загрузке оценок:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [id]);

  const handleDelete = () => {
    if (window.confirm('Вы уверены, что хотите удалить этот продукт?')) {
      axios.delete(`/api/products/${id}/`)
        .then(() => {
          alert('Продукт успешно удален');
          navigate('/');
        })
        .catch(error => {
          console.error('Ошибка при удалении:', error);
          alert('Не удалось удалить продукт');
        });
    }
  };

  const handleArchive = () => {
    axios.patch(`/api/products/${id}/`, { is_archived: !product.is_archived })
      .then(response => {
        setProduct(response.data);
        alert(product.is_archived ? 'Продукт восстановлен из архива' : 'Продукт отправлен в архив');
      })
      .catch(error => {
        console.error('Ошибка при архивировании:', error);
      });
  };

  if (loading) {
    return <div className="loading">⏳ Загрузка...</div>;
  }

  if (!product) {
    return <div className="error">❌ Продукт не найден</div>;
  }

  return (
    <div className="product-detail">
      <div style={{ marginBottom: '20px' }}>
        <Link to="/" style={{ color: '#1f2937', textDecoration: 'none' }}>← Назад к списку</Link>
      </div>

      <div className="product-header">
        <h1>{product.name}</h1>
        {product.is_archived && (
          <span className="status-badge status-archived">В архиве</span>
        )}
      </div>

      <div className="product-info-card">
        <div className="info-section">
          <h2>📋 Основная информация</h2>
          <div className="info-grid">
            <div className="info-item">
              <strong>Наименование:</strong>
              <p>{product.name}</p>
            </div>
            <div className="info-item">
              <strong>Описание:</strong>
              <p>{product.description || 'Нет описания'}</p>
            </div>
            <div className="info-item">
              <strong>Ответственное ведомство:</strong>
              <p>{product.department_owner}</p>
            </div>
            <div className="info-item">
              <strong>Дата запуска:</strong>
              <p>{product.launch_date || 'Не указана'}</p>
            </div>
            {product.product_link && (
              <div className="info-item">
                <strong>Ссылка:</strong>
                <p>
                  <a href={product.product_link} target="_blank" rel="noopener noreferrer">
                    {product.product_link} 🔗
                  </a>
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="info-section">
          <h2>📊 История оценок</h2>
          {evaluations.length > 0 ? (
            <div className="evaluations-list">
              {evaluations.map(evaluation => (
                <div key={evaluation.id} className="evaluation-card">
                  <div className="evaluation-header">
                    <span className="evaluation-date">
                      📅 {new Date(evaluation.start_date).toLocaleDateString('ru-RU')}
                    </span>
                    <span className={`status-badge status-${evaluation.status}`}>
                      {evaluation.status === 'pending' && 'В ожидании'}
                      {evaluation.status === 'in_progress' && 'В процессе'}
                      {evaluation.status === 'completed' && 'Завершено'}
                      {evaluation.status === 'archived' && 'В архиве'}
                    </span>
                  </div>
                  <div className="evaluation-actions">
                    <Link to={`/evaluation-session/${evaluation.id}`}>
                      <button className="secondary-btn">Просмотреть</button>
                    </Link>
                    {evaluation.status === 'completed' && (
                      <Link to={`/evaluation-session/${evaluation.id}/results`}>
                        <button>Результаты</button>
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>Пока нет оценок для этого продукта</p>
          )}
          <div style={{ marginTop: '20px' }}>
            <Link to="/start-evaluation">
              <button>➕ Создать новую оценку</button>
            </Link>
          </div>
        </div>

        <div className="action-buttons">
          <Link to={`/edit-product/${id}`}>
            <button>✏️ Редактировать</button>
          </Link>
          <button onClick={handleArchive} className="secondary-btn">
            {product.is_archived ? '📤 Восстановить' : '📥 Архивировать'}
          </button>
          <button onClick={handleDelete} className="delete-btn">
            🗑️ Удалить
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProductDetail;

