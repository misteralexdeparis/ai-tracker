'use client';

interface Tool {
  name: string;
  category: string;
  gartner_quadrant?: string;
  vision?: number;
  ability?: number;
  credibility?: number;
  buzz_score?: number;
  adoption?: number;
  final_score?: number;
  description?: string;
  features?: string[];
  key_features?: string[];
  pricing?: string;
  url?: string;
  official_url?: string;
  founding_year?: number;
  founded_year?: number;
  free_tier?: string;
  publisher?: string;
  last_known_version?: string;
  version?: string;
  tags?: string[];
  docs_url?: string;
  release_notes_url?: string;
}

interface ToolModalProps {
  tool: Tool | null;
  onClose: () => void;
}

export default function ToolModal({ tool, onClose }: ToolModalProps) {
  if (!tool) return null;

  const quadrantColors = {
    'Leader': '#32b8c6',
    'Visionary': '#4c8bf5',
    'Challenger': '#f59e0b',
    'Niche Player': '#10b981'
  };

  const quadrantColor = quadrantColors[tool.gartner_quadrant as keyof typeof quadrantColors] || '#6b7280';

  return (
    <div className="tool-modal-overlay" onClick={onClose}>
      <div className="tool-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="tool-modal-header">
          <div>
            <h2>{tool.name}</h2>
            <div className="tool-modal-badges">
              <span className="tool-category-badge">{tool.category}</span>
              {tool.gartner_quadrant && (
                <span
                  className="tool-quadrant-badge"
                  style={{ backgroundColor: quadrantColor }}
                >
                  {tool.gartner_quadrant}
                </span>
              )}
              {tool.free_tier && tool.free_tier.toLowerCase() !== 'no' && (
                <span className="tool-free-badge">Free Tier</span>
              )}
            </div>
          </div>
          <button className="tool-modal-close" onClick={onClose}>&times;</button>
        </div>

        <div className="tool-modal-body">
          {tool.description && (
            <section className="tool-modal-section">
              <p className="tool-description">{tool.description}</p>
            </section>
          )}

          {/* Tool Info Section */}
          {(tool.publisher || tool.founding_year || tool.last_known_version || tool.pricing) && (
            <section className="tool-modal-section">
              <h3>ℹ️ Information</h3>
              <div className="tool-info-grid">
                {tool.publisher && (
                  <div className="tool-info-item">
                    <span className="tool-info-label">Publisher:</span>
                    <span className="tool-info-value">{tool.publisher}</span>
                  </div>
                )}
                {tool.founding_year && (
                  <div className="tool-info-item">
                    <span className="tool-info-label">Founded:</span>
                    <span className="tool-info-value">{tool.founding_year}</span>
                  </div>
                )}
                {tool.last_known_version && (
                  <div className="tool-info-item">
                    <span className="tool-info-label">Version:</span>
                    <span className="tool-info-value">{tool.last_known_version}</span>
                  </div>
                )}
                {tool.pricing && (
                  <div className="tool-info-item">
                    <span className="tool-info-label">Pricing:</span>
                    <span className="tool-info-value">{tool.pricing}</span>
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Tags Section */}
          {tool.tags && tool.tags.length > 0 && (
            <section className="tool-modal-section">
              <h3>🏷️ Tags</h3>
              <div className="tool-tags">
                {tool.tags.map((tag, idx) => (
                  <span key={idx} className="tool-tag">{tag}</span>
                ))}
              </div>
            </section>
          )}

          {/* Key Features */}
          {((tool.features && tool.features.length > 0) || (tool.key_features && tool.key_features.length > 0)) && (
            <section className="tool-modal-section">
              <h3>⭐ Key Features</h3>
              <ul className="tool-features-list">
                {(tool.key_features || tool.features || []).slice(0, 5).map((feature, idx) => (
                  <li key={idx}>{feature}</li>
                ))}
              </ul>
            </section>
          )}

          {/* Scores Section */}
          <section className="tool-modal-section">
            <h3>📊 Performance Scores</h3>
            <div className="tool-scores-grid">
              {tool.vision !== undefined && (
                <div className="tool-score-item">
                  <div className="tool-score-label">Vision</div>
                  <div className="tool-score-value">{Math.round(tool.vision)}</div>
                </div>
              )}
              {tool.ability !== undefined && (
                <div className="tool-score-item">
                  <div className="tool-score-label">Ability</div>
                  <div className="tool-score-value">{Math.round(tool.ability)}</div>
                </div>
              )}
              {tool.buzz_score !== undefined && (
                <div className="tool-score-item">
                  <div className="tool-score-label">Buzz</div>
                  <div className="tool-score-value">{Math.round(tool.buzz_score)}</div>
                </div>
              )}
              {tool.credibility !== undefined && (
                <div className="tool-score-item">
                  <div className="tool-score-label">Credibility</div>
                  <div className="tool-score-value">{Math.round(tool.credibility)}</div>
                </div>
              )}
              {tool.adoption !== undefined && (
                <div className="tool-score-item">
                  <div className="tool-score-label">Adoption</div>
                  <div className="tool-score-value">{Math.round(tool.adoption)}</div>
                </div>
              )}
            </div>
          </section>

          {/* Links Section */}
          {(tool.docs_url || tool.release_notes_url) && (
            <section className="tool-modal-section">
              <h3>🔗 Resources</h3>
              <div className="tool-links">
                {tool.docs_url && (
                  <a href={tool.docs_url} target="_blank" rel="noopener noreferrer" className="tool-link">
                    📚 Documentation
                  </a>
                )}
                {tool.release_notes_url && (
                  <a href={tool.release_notes_url} target="_blank" rel="noopener noreferrer" className="tool-link">
                    📝 Release Notes
                  </a>
                )}
              </div>
            </section>
          )}
        </div>

        <div className="tool-modal-footer">
          {tool.url && (
            <a
              href={tool.url}
              target="_blank"
              rel="noopener noreferrer"
              className="tool-visit-button"
            >
              Visit {tool.name} →
            </a>
          )}
          <button className="tool-close-button" onClick={onClose}>Close</button>
        </div>
      </div>

      <style jsx global>{`
        .tool-modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.6);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 3000;
          padding: 20px;
          backdrop-filter: blur(4px);
        }
        .tool-modal-content {
          background: var(--color-charcoal-800);
          border-radius: 16px;
          max-width: 600px;
          width: 100%;
          max-height: 90vh;
          display: flex;
          flex-direction: column;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          animation: slideIn 0.3s ease-out;
          border: 1px solid var(--color-border);
        }
        .tool-modal-header {
          padding: 24px;
          border-bottom: 1px solid var(--color-border);
          display: flex;
          justify-content: space-between;
        }
        .tool-modal-header h2 {
          margin: 0 0 12px 0;
          font-size: 24px;
        }
        .tool-modal-badges {
          display: flex;
          gap: 8px;
        }
        .tool-category-badge, .tool-quadrant-badge, .tool-free-badge {
          padding: 4px 12px;
          border-radius: 999px;
          font-size: 12px;
        }
        .tool-category-badge {
          background: rgba(50, 184, 198, 0.2);
          color: var(--color-primary);
          border: 1px solid var(--color-primary);
        }
        .tool-quadrant-badge {
          color: white;
        }
        .tool-free-badge {
          background: rgba(16, 185, 129, 0.2);
          color: #10b981;
        }
        .tool-modal-close {
          background: none;
          border: none;
          font-size: 28px;
          cursor: pointer;
          color: var(--color-text);
        }
        .tool-modal-body {
          padding: 24px;
          overflow-y: auto;
          flex: 1;
        }
        .tool-modal-section {
          margin-bottom: 24px;
        }
        .tool-modal-section h3 {
          font-size: 18px;
          margin: 0 0 12px 0;
        }
        .tool-scores-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
          gap: 12px;
        }
        .tool-score-item {
          text-align: center;
          padding: 16px;
          background: rgba(50, 184, 198, 0.05);
          border-radius: 8px;
          border: 1px solid var(--color-border);
        }
        .tool-score-label {
          font-size: 12px;
          color: var(--color-text-secondary);
          margin-bottom: 4px;
        }
        .tool-score-value {
          font-size: 24px;
          font-weight: bold;
          color: var(--color-primary);
        }
        .tool-features-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        .tool-features-list li {
          padding: 8px 12px;
          margin-bottom: 8px;
          background: rgba(50, 184, 198, 0.05);
          border-left: 3px solid var(--color-primary);
          border-radius: 4px;
        }
        .tool-modal-footer {
          padding: 16px 24px;
          border-top: 1px solid var(--color-border);
          display: flex;
          justify-content: space-between;
          gap: 12px;
        }
        .tool-visit-button {
          flex: 1;
          padding: 12px 24px;
          background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-teal-400) 100%);
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          text-decoration: none;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s;
        }
        .tool-visit-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(50, 184, 198, 0.3);
        }
        .tool-close-button {
          padding: 12px 24px;
          background: var(--color-charcoal-700);
          border: 1px solid var(--color-border);
          border-radius: 8px;
          cursor: pointer;
          color: var(--color-text);
        }
        .tool-info-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
        }
        .tool-info-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
          padding: 12px;
          background: rgba(50, 184, 198, 0.05);
          border-radius: 8px;
          border: 1px solid var(--color-border);
        }
        .tool-info-label {
          font-size: 12px;
          color: var(--color-text-secondary);
          font-weight: 600;
        }
        .tool-info-value {
          font-size: 14px;
          color: var(--color-text);
        }
        .tool-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .tool-tag {
          padding: 6px 12px;
          background: rgba(50, 184, 198, 0.1);
          border: 1px solid var(--color-primary);
          border-radius: 999px;
          font-size: 12px;
          color: var(--color-primary);
          font-weight: 500;
        }
        .tool-links {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .tool-link {
          padding: 12px 16px;
          background: rgba(50, 184, 198, 0.05);
          border: 1px solid var(--color-border);
          border-radius: 8px;
          color: var(--color-primary);
          text-decoration: none;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .tool-link:hover {
          background: rgba(50, 184, 198, 0.1);
          border-color: var(--color-primary);
          transform: translateX(4px);
        }
        .tool-description {
          margin: 0;
          line-height: 1.6;
          color: var(--color-text);
        }
        @media (max-width: 640px) {
          .tool-info-grid {
            grid-template-columns: 1fr;
          }
          .tool-scores-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }
      `}</style>
    </div>
  );
}
