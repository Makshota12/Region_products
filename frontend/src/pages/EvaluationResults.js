import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';
import { Radar, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement
);

function EvaluationResults() {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [product, setProduct] = useState(null);
  const [domainScores, setDomainScores] = useState({});
  const [overallIndex, setOverallIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Загружаем сессию
    axios.get(`/api/evaluation-sessions/${sessionId}/`)
      .then(response => {
        setSession(response.data);
        // Загружаем продукт
        return axios.get(`/api/products/${response.data.product}/`);
      })
      .then(response => {
        setProduct(response.data);
      })
      .catch(error => console.error('Ошибка при загрузке сессии:', error));

    // Загружаем оценки по доменам
    axios.get(`/api/evaluation-sessions/${sessionId}/get_domain_scores/`)
      .then(response => {
        setDomainScores(response.data.domain_scores);
      })
      .catch(error => console.error('Ошибка при загрузке оценок доменов:', error));

    // Загружаем общий индекс зрелости
    axios.get(`/api/evaluation-sessions/${sessionId}/get_overall_maturity_index/`)
      .then(response => {
        setOverallIndex(response.data.overall_index);
        setLoading(false);
      })
      .catch(error => {
        console.error('Ошибка при загрузке индекса зрелости:', error);
        setLoading(false);
      });
  }, [sessionId]);

  const getMaturityLevel = (index) => {
    if (index >= 8) return { level: 'Превосходный', color: '#38ef7d', emoji: '🌟' };
    if (index >= 6) return { level: 'Высокий', color: '#4facfe', emoji: '⭐' };
    if (index >= 4) return { level: 'Средний', color: '#f7b731', emoji: '💫' };
    if (index >= 2) return { level: 'Низкий', color: '#f7797d', emoji: '⚠️' };
    return { level: 'Критический', color: '#eb3349', emoji: '❌' };
  };

  const maturityInfo = getMaturityLevel(overallIndex);

  // Данные для радарного графика
  const radarData = {
    labels: Object.keys(domainScores),
    datasets: [
      {
        label: 'Оценки по доменам',
        data: Object.values(domainScores),
        backgroundColor: 'rgba(102, 126, 234, 0.2)',
        borderColor: 'rgba(102, 126, 234, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(102, 126, 234, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(102, 126, 234, 1)',
      },
    ],
  };

  // Данные для столбчатого графика
  const barData = {
    labels: Object.keys(domainScores),
    datasets: [
      {
        label: 'Оценка',
        data: Object.values(domainScores),
        backgroundColor: [
          'rgba(102, 126, 234, 0.8)',
          'rgba(118, 75, 162, 0.8)',
          'rgba(56, 239, 125, 0.8)',
          'rgba(247, 183, 49, 0.8)',
        ],
        borderColor: [
          'rgba(102, 126, 234, 1)',
          'rgba(118, 75, 162, 1)',
          'rgba(56, 239, 125, 1)',
          'rgba(247, 183, 49, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  // Данные для круговой диаграммы (процент заполненности)
  const completionPercentage = overallIndex * 10; // Преобразуем из 10-балльной в процент
  const doughnutData = {
    labels: ['Достигнуто', 'Потенциал'],
    datasets: [
      {
        data: [completionPercentage, 100 - completionPercentage],
        backgroundColor: [
          maturityInfo.color,
          '#e9ecef',
        ],
        borderWidth: 0,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 14,
            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
          }
        }
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 10,
        ticks: {
          stepSize: 2
        }
      }
    }
  };

  const handleDownloadPDF = () => {
    window.open(`/api/evaluation-sessions/${sessionId}/generate_maturity_passport/`, '_blank');
  };

  if (loading) {
    return <div className="loading">⏳ Загрузка результатов оценки...</div>;
  }

  if (!session) {
    return <div className="error">❌ Сессия не найдена</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/evaluation-sessions" style={{ color: '#667eea', textDecoration: 'none' }}>
          ← Назад к сессиям
        </Link>
      </div>

      <h1>📊 Результаты оценки зрелости</h1>

      {product && (
        <div className="product-info-banner">
          <h2>📦 {product.name}</h2>
          <p>{product.description}</p>
        </div>
      )}

      {/* Общий индекс зрелости */}
      <div className="maturity-index-card" style={{ backgroundColor: `${maturityInfo.color}20`, borderColor: maturityInfo.color }}>
        <div className="maturity-icon">{maturityInfo.emoji}</div>
        <div className="maturity-content">
          <h2>Общий индекс зрелости</h2>
          <div className="maturity-score">{overallIndex.toFixed(2)}</div>
          <div className="maturity-level" style={{ color: maturityInfo.color }}>
            {maturityInfo.level} уровень
          </div>
        </div>
      </div>

      {/* Статистика по доменам */}
      <div className="domains-stats">
        <h2>📈 Оценки по доменам</h2>
        <div className="domains-grid">
          {Object.entries(domainScores).map(([domain, score], index) => {
            const domainInfo = getMaturityLevel(score);
            return (
              <div key={index} className="domain-stat-card" style={{ borderLeftColor: domainInfo.color }}>
                <div className="domain-stat-header">
                  <span className="domain-emoji">{domainInfo.emoji}</span>
                  <span className="domain-name">{domain}</span>
                </div>
                <div className="domain-score" style={{ color: domainInfo.color }}>
                  {score.toFixed(2)}
                </div>
                <div className="domain-level">{domainInfo.level}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Графики */}
      <div className="charts-container">
        <div className="chart-card">
          <h3>🕸️ Радарный график</h3>
          <div style={{ maxHeight: '400px', padding: '20px' }}>
            <Radar data={radarData} options={chartOptions} />
          </div>
        </div>

        <div className="chart-card">
          <h3>📊 Столбчатая диаграмма</h3>
          <div style={{ maxHeight: '400px', padding: '20px' }}>
            <Bar data={barData} options={{ ...chartOptions, scales: { y: { beginAtZero: true, max: 10 } } }} />
          </div>
        </div>

        <div className="chart-card">
          <h3>🎯 Процент достижения</h3>
          <div style={{ maxHeight: '300px', maxWidth: '300px', margin: '0 auto', padding: '20px' }}>
            <Doughnut data={doughnutData} />
          </div>
          <div style={{ textAlign: 'center', marginTop: '15px', fontSize: '18px', fontWeight: '700', color: maturityInfo.color }}>
            {completionPercentage.toFixed(1)}% от максимума
          </div>
        </div>
      </div>

      {/* Кнопки действий */}
      <div className="action-buttons">
        <button onClick={handleDownloadPDF} className="pdf-button">
          📄 Скачать паспорт зрелости (PDF)
        </button>
        <Link to={`/evaluation-session/${sessionId}`}>
          <button className="secondary-btn">✏️ Редактировать оценки</button>
        </Link>
      </div>
    </div>
  );
}

export default EvaluationResults;
