import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ProgramCreationPage() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Program title is required');
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const response = await fetch('/api/programs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description }),
      });
      if (!response.ok) {
        throw new Error('Failed to create program');
      }
      navigate('/');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main>
      <h1>Create New Training Program</h1>
      <form onSubmit={handleSubmit} noValidate>
        <label htmlFor="title">Program Title *</label>
        <input
          id="title"
          name="title"
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          required
        />

        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          name="description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          rows={4}
        />

        {error && <p role="alert" className="error-message">{error}</p>}

        <button type="submit" disabled={submitting} aria-busy={submitting}>Create Program</button>
      </form>
    </main>
  );
}
