import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/api/products/')
      .then(response => {
        setProducts(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Ошибка при загрузке продуктов:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="loading">⏳ Загрузка продуктов...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>📦 Цифровые продукты региона</h1>
        <Link to="/add-product">
          <button>➕ Добавить продукт</button>
        </Link>
      </div>

      {products.length === 0 ? (
        <div className="empty-state">
          <p>Пока нет добавленных продуктов</p>
          <Link to="/add-product">
            <button>➕ Добавить первый продукт</button>
          </Link>
        </div>
      ) : (
        <div className="products-grid">
          {products.map(product => (
            <Link to={`/product/${product.id}`} key={product.id} style={{ textDecoration: 'none', color: 'inherit' }}>
              <div className="product-card">
                <div className="product-card-header">
                  <h3>{product.name}</h3>
                  {product.is_archived && (
                    <span className="status-badge status-archived">Архив</span>
                  )}
                </div>
                <div className="product-card-body">
                  <p className="product-description">
                    {product.description || 'Описание отсутствует'}
                  </p>
                  <div className="product-meta">
                    <div className="meta-item">
                      <span className="meta-label">🏢 Владелец:</span>
                      <span className="meta-value">{product.department_owner}</span>
                    </div>
                    {product.launch_date && (
                      <div className="meta-item">
                        <span className="meta-label">📅 Запуск:</span>
                        <span className="meta-value">
                          {new Date(product.launch_date).toLocaleDateString('ru-RU')}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="product-card-footer">
                  <span className="card-link">Подробнее →</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default ProductList;
