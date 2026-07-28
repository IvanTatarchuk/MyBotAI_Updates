import React, { useState } from 'react';

type Analysis = {
  filename: string;
  analysis: {
    filename: string;
    size_bytes: number;
    sha256: string;
    insight: string;
  }
}

export const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Analysis | null>(null);

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const apiKey = import.meta.env.VITE_API_KEY || 'dev-secret-key';

  const onSubmit: React.FormEventHandler<HTMLFormElement> = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!file) {
      setError('Please select a file');
      return;
    }
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch(`${apiUrl}/api/upload`, {
        method: 'POST',
        headers: {
          'x-api-key': apiKey
        },
        body: formData
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `Request failed with ${response.status}`);
      }
      const data = await response.json();
      setResult(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      maxWidth: 720,
      margin: '2rem auto',
      fontFamily: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial, "Apple Color Emoji", "Segoe UI Emoji"'
    }}>
      <h1>Million App</h1>
      <p>Upload a document to get instant insights.</p>
      <form onSubmit={onSubmit}>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          accept="*/*"
        />
        <button type="submit" disabled={loading} style={{ marginLeft: '0.5rem' }}>
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
      </form>
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      {result && (
        <div style={{ marginTop: '1rem', padding: '1rem', border: '1px solid #ddd', borderRadius: 8 }}>
          <h2>Result</h2>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
      <footer style={{ marginTop: '2rem', color: '#666' }}>
        <small>Backend: {apiUrl}</small>
      </footer>
    </div>
  );
};

