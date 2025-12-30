import React, { useState, useEffect } from 'react';
import axios from 'axios';

function RatingScaleForm({ criterionId, ratingScale, onSuccess }) {
  const [formData, setFormData] = useState({
    criterion: criterionId,
    score: ratingScale?.score || '',
    description: ratingScale?.description || '',
  });

  useEffect(() => {
    if (ratingScale) {
      setFormData(ratingScale);
    }
  }, [ratingScale]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (ratingScale) {
      axios.put(`/api/rating-scales/${ratingScale.id}/`, formData)
        .then(response => {
          console.log('Rating Scale updated:', response.data);
          onSuccess();
        })
        .catch(error => {
          console.error('Error updating rating scale:', error);
        });
    } else {
      axios.post('/api/rating-scales/', formData)
        .then(response => {
          console.log('Rating Scale created:', response.data);
          onSuccess();
        })
        .catch(error => {
          console.error('Error creating rating scale:', error);
        });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Score:</label>
        <input type="number" name="score" value={formData.score} onChange={handleChange} required min="1" max="10"/>
      </div>
      <div>
        <label>Description:</label>
        <textarea name="description" value={formData.description} onChange={handleChange} required></textarea>
      </div>
      <button type="submit">{ratingScale ? 'Update' : 'Add'} Rating Scale</button>
    </form>
  );
}

export default RatingScaleForm;

