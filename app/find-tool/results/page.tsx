'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useState, Suspense } from 'react';
import Link from 'next/link';
import { matchToolsToQuery } from '@/app/lib/usecase-matcher';

interface Tool {
  name: string;
  description?: string;
  category: string;
  url?: string;
  gartner_quadrant?: string;
  vision?: number;
  ability?: number;
  key_features?: string[];
  pricing?: string;
  publisher?: string;
}

interface ToolMatch {
  tool: Tool;
  matchScore: number;
  matchReasons: string[];
}

function ResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get('q') || '';
  const [matches, setMatches] = useState<ToolMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadResults() {
      if (!query) {
        router.push('/find-tool');
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const results = await matchToolsToQuery(query);
        setMatches(results);
      } catch (err) {
        console.error('Error matching tools:', err);
        setError('Failed to load tool recommendations. Please try again.');
      } finally {
        setLoading(false);
      }
    }

    loadResults();
  }, [query, router]);

  const quadrantColors = {
    'Leader': '#32b8c6',
    'Visionary': '#4c8bf5',
    'Challenger': '#f59e0b',
    'Niche Player': '#10b981'
  };

  if (loading) {
    return (
      <div className="results-page">
        <div className="results-container">
          <div className="loading">
            <div className="spinner"></div>
            <p>Finding the best AI tools for you...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-page">
        <div className="results-container">
          <div className="error">
            <p>{error}</p>
            <Link href="/find-tool" className="back-button">Try Again</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="results-page">
      <div className="results-container">
        <Link href="/" className="back-link">← Back to Home</Link>

        <div className="results-header">
          <h1>🎯 Recommended Tools</h1>
          <p className="query-display">For: "{query}"</p>
          <p className="results-count">{matches.length} tools found</p>
        </div>

        {matches.length === 0 ? (
          <div className="no-results">
            <p>No tools found matching your query. Try a different search!</p>
            <Link href="/find-tool" className="back-button">Try Again</Link>
          </div>
        ) : (
          <div className="results-grid">
            {matches.map((match, idx) => (
              <div key={idx} className="tool-card">
                <div className="tool-card-header">
                  <div>
                    <h3>{match.tool.name}</h3>
                    {match.tool.publisher && (
                      <p className="publisher">by {match.tool.publisher}</p>
                    )}
                  </div>
                  <div className="badges">
                    {match.tool.gartner_quadrant && (
                      <span
                        className="quadrant-badge"
                        style={{
                          backgroundColor: quadrantColors[match.tool.gartner_quadrant as keyof typeof quadrantColors] || '#6b7280'
                        }}
                      >
                        {match.tool.gartner_quadrant}
                      </span>
                    )}
                    <span className="match-score">
                      {Math.round(match.matchScore)}% match
                    </span>
                  </div>
                </div>

                {match.tool.description && (
                  <p className="description">{match.tool.description}</p>
                )}

                {match.matchReasons.length > 0 && (
                  <div className="match-reasons">
                    <p className="reasons-title">Why this matches:</p>
                    <ul>
                      {match.matchReasons.slice(0, 3).map((reason, i) => (
                        <li key={i}>{reason}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {match.tool.key_features && match.tool.key_features.length > 0 && (
                  <div className="features">
                    <p className="features-title">Key Features:</p>
                    <ul>
                      {match.tool.key_features.slice(0, 3).map((feature, i) => (
                        <li key={i}>{feature}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="tool-card-footer">
                  {match.tool.pricing && (
                    <span className="pricing">{match.tool.pricing}</span>
                  )}
                  {match.tool.url && (
                    <a
                      href={match.tool.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="visit-button"
                    >
                      Visit →
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <style jsx>{`
        .results-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #1a1f2e 0%, #252b3b 100%);
          padding: 40px 20px;
        }
        .results-container {
          max-width: 1200px;
          margin: 0 auto;
        }
        .back-link {
          display: inline-block;
          color: var(--color-primary);
          text-decoration: none;
          margin-bottom: 32px;
          font-size: 16px;
          font-weight: 500;
        }
        .back-link:hover {
          text-decoration: underline;
        }
        .results-header {
          text-align: center;
          margin-bottom: 48px;
        }
        .results-header h1 {
          font-size: 42px;
          margin: 0 0 16px 0;
          color: #ffffff;
        }
        .query-display {
          font-size: 18px;
          color: #d1d5db;
          margin: 0 0 8px 0;
        }
        .results-count {
          color: var(--color-primary);
          font-size: 16px;
          font-weight: 600;
          margin: 0;
        }
        .loading, .error, .no-results {
          text-align: center;
          padding: 60px 20px;
        }
        .spinner {
          width: 48px;
          height: 48px;
          border: 4px solid rgba(50, 184, 198, 0.2);
          border-top-color: var(--color-primary);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 16px auto;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .back-button {
          display: inline-block;
          padding: 12px 24px;
          background: var(--color-primary);
          color: white;
          border-radius: 8px;
          text-decoration: none;
          margin-top: 16px;
        }
        .results-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 24px;
        }
        .tool-card {
          background: rgba(42, 48, 60, 0.8);
          border: 1px solid rgba(100, 116, 139, 0.3);
          border-radius: 12px;
          padding: 24px;
          display: flex;
          flex-direction: column;
          gap: 16px;
          transition: all 0.3s;
          backdrop-filter: blur(10px);
        }
        .tool-card:hover {
          border-color: var(--color-primary);
          transform: translateY(-4px);
          box-shadow: 0 12px 32px rgba(50, 184, 198, 0.3);
          background: rgba(48, 54, 66, 0.9);
        }
        .tool-card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 16px;
        }
        .tool-card-header h3 {
          margin: 0;
          font-size: 22px;
          font-weight: 700;
          color: #ffffff;
        }
        .publisher {
          font-size: 14px;
          color: #9ca3af;
          margin: 4px 0 0 0;
        }
        .badges {
          display: flex;
          flex-direction: column;
          gap: 8px;
          align-items: flex-end;
        }
        .quadrant-badge {
          padding: 4px 12px;
          border-radius: 999px;
          font-size: 12px;
          color: white;
          font-weight: 600;
        }
        .match-score {
          padding: 4px 12px;
          border-radius: 999px;
          font-size: 12px;
          background: rgba(50, 184, 198, 0.2);
          color: var(--color-primary);
          font-weight: 600;
        }
        .description {
          color: #d1d5db;
          line-height: 1.7;
          margin: 0;
          font-size: 15px;
        }
        .match-reasons, .features {
          margin: 0;
        }
        .reasons-title, .features-title {
          font-size: 14px;
          color: var(--color-primary);
          margin: 0 0 12px 0;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .match-reasons ul, .features ul {
          margin: 0;
          padding-left: 20px;
          color: #e5e7eb;
          font-size: 14px;
          line-height: 1.6;
        }
        .match-reasons li, .features li {
          margin-bottom: 6px;
        }
        .tool-card-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: auto;
          padding-top: 16px;
          border-top: 1px solid var(--color-border);
        }
        .pricing {
          font-size: 14px;
          color: #9ca3af;
          font-weight: 500;
        }
        .visit-button {
          padding: 12px 24px;
          background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-teal-400) 100%);
          color: white;
          border-radius: 8px;
          text-decoration: none;
          font-weight: 700;
          font-size: 14px;
          transition: all 0.2s;
          box-shadow: 0 2px 8px rgba(50, 184, 198, 0.2);
        }
        .visit-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(50, 184, 198, 0.4);
        }
      `}</style>
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={
      <div className="results-page">
        <div className="results-container">
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading...</p>
          </div>
        </div>
      </div>
    }>
      <ResultsContent />
    </Suspense>
  );
}
