import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate, Link } from 'react-router-dom';

function EvaluationInput() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [product, setProduct] = useState(null);
  const [assignedCriteria, setAssignedCriteria] = useState([]);
  const [criteria, setCriteria] = useState({});
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [progress, setProgress] = useState({ completed: 0, total: 0, percentage: 0 });

  useEffect(() => {
    const loadData = async () => {
      try {
        // Загружаем сессию
        const sessionResponse = await axios.get(`/api/evaluation-sessions/${sessionId}/`);
        setSession(sessionResponse.data);
        
        // Загружаем продукт
        const productResponse = await axios.get(`/api/products/${sessionResponse.data.product}/`);
        setProduct(productResponse.data);
        
        // Загружаем назначенные критерии с ответами (теперь сервер возвращает все данные)
        const criteriaResponse = await axios.get(`/api/assigned-criteria/?evaluation_session=${sessionId}`);
        
        console.log('Загружены критерии:', criteriaResponse.data);
        
        setAssignedCriteria(criteriaResponse.data);
        
        // Инициализируем ответы из загруженных данных
        const initialAnswers = {};
        let completedCount = 0;
        
        criteriaResponse.data.forEach(ac => {
          // Проверяем, есть ли уже ответ
          if (ac.answer && ac.answer.score_value) {
            initialAnswers[ac.id] = {
              score_value: ac.answer.score_value,
              metric_value: ac.answer.metric_value || '',
              comment: ac.answer.comment || '',
              answerId: ac.answer.id, // Сохраняем ID для обновления
            };
            completedCount++;
          } else {
            initialAnswers[ac.id] = {
              score_value: '',
              metric_value: '',
              comment: '',
              answerId: ac.answer?.id || null,
            };
          }
        });
        
        console.log('Инициализированные ответы:', initialAnswers);
        console.log('Заполнено критериев:', completedCount);
        
        setAnswers(initialAnswers);
        setProgress({
          completed: completedCount,
          total: criteriaResponse.data.length,
          percentage: criteriaResponse.data.length > 0 ? Math.round((completedCount / criteriaResponse.data.length) * 100) : 0
        });
        
        setLoading(false);
      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
        setLoading(false);
      }
    };
    
    loadData();
  }, [sessionId]);

  const handleAnswerChange = (assignedCriterionId, field, value) => {
    setAnswers(prevAnswers => {
      const newAnswers = {
        ...prevAnswers,
        [assignedCriterionId]: {
          ...prevAnswers[assignedCriterionId],
          [field]: value,
        },
      };
      
      // Пересчитываем прогресс
      let completedCount = 0;
      Object.keys(newAnswers).forEach(key => {
        if (newAnswers[key].score_value) completedCount++;
      });
      
      setProgress({
        completed: completedCount,
        total: assignedCriteria.length,
        percentage: assignedCriteria.length > 0 ? Math.round((completedCount / assignedCriteria.length) * 100) : 0
      });
      
      return newAnswers;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      let savedCount = 0;
      const errors = [];

      for (const ac of assignedCriteria) {
        const answerData = answers[ac.id];
        
        // Проверяем, что хотя бы оценка заполнена
        if (!answerData?.score_value) {
          console.log(`Пропускаем критерий ${ac.id} - нет оценки`);
          continue;
        }

        // Подготавливаем данные для отправки
        const dataToSend = {
          assigned_criterion: ac.id,
          score_value: parseInt(answerData.score_value),
          metric_value: answerData.metric_value || null,
          comment: answerData.comment || ''
        };

        try {
          // Проверяем, есть ли уже ответ (из состояния или из данных сервера)
          const existingAnswerId = answerData.answerId || (ac.answer && ac.answer.id);
          
          if (existingAnswerId) {
            // Обновляем существующий ответ
            console.log(`Обновляем ответ ${existingAnswerId} для критерия ${ac.id}`);
            await axios.put(`/api/evaluation-answers/${existingAnswerId}/`, dataToSend);
          } else {
            // Создаем новый ответ
            console.log(`Создаем новый ответ для критерия ${ac.id}`);
            const response = await axios.post(`/api/evaluation-answers/`, dataToSend);
            // Сохраняем ID нового ответа
            answerData.answerId = response.data.id;
          }
          savedCount++;
        } catch (err) {
          console.error(`Ошибка при сохранении критерия ${ac.id}:`, err);
          errors.push(`Критерий ${ac.criterion_name || ac.criterion}: ${err.response?.data ? JSON.stringify(err.response.data) : err.message}`);
        }
      }

      if (errors.length > 0) {
        alert(`⚠️ Сохранено ${savedCount} оценок, но были ошибки:\n${errors.join('\n')}`);
      } else if (savedCount === 0) {
        alert('⚠️ Нет оценок для сохранения. Заполните хотя бы одну оценку.');
        return;
      } else {
        // Проверяем, все ли критерии заполнены
        const filledCount = Object.values(answers).filter(a => a.score_value).length;
        const totalCount = assignedCriteria.length;
        const allFilled = filledCount === totalCount;
        
        // Определяем новый статус
        let newStatus = 'in_progress'; // По умолчанию "В процессе"
        if (allFilled) {
          newStatus = 'completed'; // Если все заполнены - "Завершено"
        }
        
        // Обновляем статус сессии
        try {
          await axios.patch(`/api/evaluation-sessions/${sessionId}/`, {
            status: newStatus
          });
          
          if (allFilled) {
            alert(`✅ Все ${savedCount} оценок сохранены! Оценка завершена.`);
          } else {
            alert(`✅ Сохранено ${savedCount} из ${totalCount} оценок. Статус: В процессе`);
          }
        } catch (err) {
          console.error('Ошибка обновления статуса:', err);
          alert(`✅ Успешно сохранено ${savedCount} оценок!`);
        }
        
        // Перезагружаем данные
        window.location.reload();
      }
    } catch (error) {
      console.error('Общая ошибка при сохранении:', error);
      alert('❌ Критическая ошибка при сохранении оценок');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="loading">⏳ Загрузка оценочной сессии...</div>;
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

      <h1>📝 Оценка продукта</h1>
      
      {product && (
        <div className="product-info-banner">
          <h2>📦 {product.name}</h2>
          <p>{product.description}</p>
        </div>
      )}

      {/* Прогресс выполнения */}
      <div className="progress-card">
        <div className="progress-header">
          <h3>📊 Прогресс оценки</h3>
          <span className="progress-text">
            {progress.completed} из {progress.total} критериев оценено
          </span>
        </div>
        <div className="progress-bar-container">
          <div 
            className="progress-bar-fill" 
            style={{ width: `${progress.percentage}%` }}
          >
            <span className="progress-percentage">{progress.percentage}%</span>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        {assignedCriteria.length === 0 ? (
          <div className="empty-state">
            <p>❌ Нет критериев для оценки</p>
            <p style={{ fontSize: '14px', color: '#666' }}>
              Сначала настройте модель оценки и назначьте критерии
            </p>
          </div>
        ) : (
          assignedCriteria.map(ac => {
            // Используем данные напрямую из ac (из нового сериализатора)
            const hasAnswer = answers[ac.id]?.score_value;

            return (
              <div key={ac.id} className={`criterion-card ${hasAnswer ? 'criterion-completed' : ''}`}>
                <div className="criterion-header">
                  <h3>
                    {hasAnswer && <span style={{color: '#27ae60'}}>✅ </span>}
                    {ac.criterion_name || 'Критерий'}
                  </h3>
                  <div className="criterion-meta">
                    <span className="criterion-domain">{ac.domain_name}</span>
                    <span className="criterion-weight">Вес: {ac.criterion_weight}%</span>
                  </div>
                </div>
                
                {ac.criterion_description && (
                  <p className="criterion-description">{ac.criterion_description}</p>
                )}

                <div className="answer-inputs">
                  <div className="input-group">
                    <label>⭐ Оценка (1-10):</label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={answers[ac.id]?.score_value || ''}
                      onChange={(e) => handleAnswerChange(ac.id, 'score_value', e.target.value)}
                      placeholder="Выберите оценку от 1 до 10"
                    />
                  </div>

                  <div className="input-group">
                    <label>📈 Числовая метрика (опционально):</label>
                    <input
                      type="number"
                      step="0.01"
                      value={answers[ac.id]?.metric_value || ''}
                      onChange={(e) => handleAnswerChange(ac.id, 'metric_value', e.target.value)}
                      placeholder="Например: 95.5"
                    />
                  </div>

                  <div className="input-group">
                    <label>💬 Комментарий:</label>
                    <textarea
                      value={answers[ac.id]?.comment || ''}
                      onChange={(e) => handleAnswerChange(ac.id, 'comment', e.target.value)}
                      placeholder="Добавьте комментарий к оценке..."
                      rows="3"
                    />
                  </div>
                </div>
              </div>
            );
          })
        )}

        {assignedCriteria.length > 0 && (
          <div style={{ marginTop: '30px', display: 'flex', gap: '10px' }}>
            <button type="submit" disabled={saving || progress.percentage === 0}>
              {saving ? '💾 Сохранение...' : '💾 Сохранить оценки'}
            </button>
            <Link to={`/evaluation-session/${sessionId}/results`}>
              <button type="button" className="secondary-btn">
                📊 Посмотреть результаты
              </button>
            </Link>
          </div>
        )}
      </form>
    </div>
  );
}

export default EvaluationInput;
