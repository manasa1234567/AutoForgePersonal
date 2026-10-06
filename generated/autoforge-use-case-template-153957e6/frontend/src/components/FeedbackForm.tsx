import React, { useState } from 'react';
import '../styles/feedbackForm.css';

interface FeedbackFormProps {
  programId: string;
  onClose: () => void;
  onSubmitted: () => void;
}

interface FeedbackFormData {
  rating: number | null;
  comments: string;
}

interface FeedbackFormErrors {
  rating?: string;
}

export default function FeedbackForm({ programId, onClose, onSubmitted }: FeedbackFormProps) {
  const [formData, setFormData] = useState<FeedbackFormData>({ rating: null, comments: '' });
  const [errors, setErrors] = useState<FeedbackFormErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const validate = (): boolean => {
    const newErrors: FeedbackFormErrors = {};
    if (formData.rating === null) {
      newErrors.rating = 'Rating is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: name === 'rating' ? Number(value) : value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) {
      return;
    }
    setSubmitting(true);
    setSubmitError(null);
    try {
      const response = await fetch(`/api/programs/${programId}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }
      onSubmitted();
    } catch (err) {
      setSubmitError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="feedback-form-dialog" role="dialog" aria-modal="true" aria-labelledby="feedback-form-title">
      <h2 id="feedback-form-title">Submit Feedback</h2>
      <form onSubmit={handleSubmit} noValidate>
        <label htmlFor="rating">Rating (1 to 5):</label>
        <input
          id="rating"
          name="rating"
          type="number"
          min={1}
          max={5}
          value={formData.rating ?? ''}
          onChange={handleChange}
          aria-invalid={errors.rating ? 'true' : 'false'}
          aria-describedby={errors.rating ? 'rating-error' : undefined}
          required
        />
        {errors.rating && <span id="rating-error" className="error-message">{errors.rating}</span>}

        <label htmlFor="comments">Comments (optional):</label>
        <textarea
          id="comments"
          name="comments"
          value={formData.comments}
          onChange={handleChange}
          rows={4}
        ></textarea>

        {submitError && <p className="error-message" role="alert">{submitError}</p>}

        <div className="feedback-form-actions">
          <button type="submit" disabled={submitting} aria-busy={submitting}>Submit</button>
          <button type="button" onClick={onClose} disabled={submitting}>Cancel</button>
        </div>
      </form>
    </div>
  );
}
