'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function FindToolPage() {
  const [query, setQuery] = useState('');
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/find-tool/results?q=${encodeURIComponent(query)}`);
    }
  };

  return (
    <div className="find-tool-page">
      <div className="find-tool-container">
        <Link href="/" className="back-link">← Back to Home</Link>

        <div className="find-tool-header">
          <h1>🔍 Find Your Perfect AI Tool</h1>
          <p className="subtitle">
            Describe what you want to do, and we'll recommend the best AI tools for your needs
          </p>
        </div>

        <form onSubmit={handleSubmit} className="search-form">
          <div className="search-input-wrapper">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="E.g., Create a business presentation with data visualization..."
              className="search-input"
              autoFocus
            />
            <button type="submit" className="search-button" disabled={!query.trim()}>
              Find Tools →
            </button>
          </div>
        </form>

        <div className="examples">
          <p>Try asking:</p>
          <div className="example-chips">
            <button onClick={() => setQuery("Create marketing content for social media")}>
              Create marketing content
            </button>
            <button onClick={() => setQuery("Analyze customer feedback and sentiment")}>
              Analyze customer feedback
            </button>
            <button onClick={() => setQuery("Generate code for a web application")}>
              Generate code
            </button>
            <button onClick={() => setQuery("Design a logo and brand identity")}>
              Design a logo
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        .find-tool-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
          padding: 40px 20px;
        }
        .find-tool-container {
          max-width: 800px;
          margin: 0 auto;
        }
        .back-link {
          display: inline-block;
          color: var(--color-primary);
          text-decoration: none;
          margin-bottom: 32px;
          font-size: 14px;
        }
        .back-link:hover {
          text-decoration: underline;
        }
        .find-tool-header {
          text-align: center;
          margin-bottom: 48px;
        }
        .find-tool-header h1 {
          font-size: 48px;
          margin: 0 0 16px 0;
          background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-teal-400) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .subtitle {
          font-size: 18px;
          color: var(--color-text-secondary);
          margin: 0;
        }
        .search-form {
          margin-bottom: 48px;
        }
        .search-input-wrapper {
          display: flex;
          gap: 12px;
          flex-direction: column;
        }
        .search-input {
          flex: 1;
          padding: 20px 24px;
          background: var(--color-charcoal-800);
          border: 2px solid var(--color-border);
          border-radius: 12px;
          color: var(--color-text);
          font-size: 16px;
          transition: all 0.3s;
        }
        .search-input:focus {
          outline: none;
          border-color: var(--color-primary);
          box-shadow: 0 0 0 3px rgba(50, 184, 198, 0.1);
        }
        .search-button {
          padding: 20px 32px;
          background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-teal-400) 100%);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s;
        }
        .search-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(50, 184, 198, 0.3);
        }
        .search-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .examples {
          text-align: center;
        }
        .examples p {
          color: var(--color-text-secondary);
          margin-bottom: 16px;
        }
        .example-chips {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          justify-content: center;
        }
        .example-chips button {
          padding: 12px 20px;
          background: rgba(50, 184, 198, 0.1);
          border: 1px solid var(--color-primary);
          border-radius: 999px;
          color: var(--color-primary);
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s;
        }
        .example-chips button:hover {
          background: rgba(50, 184, 198, 0.2);
          transform: translateY(-2px);
        }
        @media (min-width: 640px) {
          .search-input-wrapper {
            flex-direction: row;
          }
          .search-button {
            white-space: nowrap;
          }
        }
      `}</style>
    </div>
  );
}
