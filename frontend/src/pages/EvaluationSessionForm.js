import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function EvaluationSessionForm() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('');

  useEffect(() => {
    axios.get('/api/products/')
      .then(response => {
        setProducts(response.data);
      })
      .catch(error => {
        console.error('Error fetching products:', error);
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('/api/evaluation-sessions/', { product: selectedProduct })
      .then(response => {
        console.log('Evaluation session created:', response.data);
        navigate(`/evaluation-session/${response.data.id}`);
      })
      .catch(error => {
        console.error('Error creating evaluation session:', error);
      });
  };

  return (
    <div>
      <h1> Начать новую оценку</h1>
      <p style={{ color: '#666', marginBottom: '30px' }}>
        Выберите продукт для проведения оценки зрелости
      </p>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label> Выберите продукт:</label>
          <select value={selectedProduct} onChange={(e) => setSelectedProduct(e.target.value)} required>
            <option value="">-- Выберите продукт --</option>
            {products.map(product => (
              <option key={product.id} value={product.id}>{product.name}</option>
            ))}
          </select>
        </div>
        <button type="submit"> Начать оценку</button>
      </form>
    </div>
  );
}

export default EvaluationSessionForm;
