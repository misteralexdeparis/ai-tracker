'use client';

interface AboutDataModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AboutDataModal({ isOpen, onClose }: AboutDataModalProps) {
  if (!isOpen) return null;

  // Calculate dates
  const lastUpdated = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  const nextUpdate = "Dec 1, 2025";

  return (
    <div className="about-data-modal-overlay" onClick={onClose}>
      <div className="about-data-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="about-data-modal-header">
          <h2>📊 About Our Data</h2>
          <button className="about-data-modal-close" onClick={onClose}>&times;</button>
        </div>

        <div className="about-data-modal-body">
          {/* Data Freshness */}
          <section className="about-data-modal-section">
            <h3>🔄 Data Freshness</h3>
            <div className="about-data-info-box">
              <div className="about-data-info-row">
                <span className="about-data-info-label">Last Updated:</span>
                <span className="about-data-info-value">{lastUpdated}</span>
              </div>
              <div className="about-data-info-row">
                <span className="about-data-info-label">Next Update:</span>
                <span className="about-data-info-value">{nextUpdate}</span>
              </div>
              <div className="about-data-info-row">
                <span className="about-data-info-label">Update Frequency:</span>
                <span className="about-data-info-value">Every 15 days (1st & 15th)</span>
              </div>
            </div>
          </section>

          {/* Methodology */}
          <section className="about-data-modal-section">
            <h3>🔬 How We Gather Data</h3>
            <div className="about-data-methodology">
              <div className="about-data-step">
                <div className="about-data-step-number">1</div>
                <div className="about-data-step-content">
                  <h4>📋 Tool Tracking</h4>
                  <p>We maintain a curated list of 61+ AI tools across multiple categories (LLMs, Image Generation, Video, Coding, etc.)</p>
                </div>
              </div>
              <div className="about-data-step">
                <div className="about-data-step-number">2</div>
                <div className="about-data-step-content">
                  <h4>🌐 Web Scraping</h4>
                  <p>Our automated scraper discovers new tools from official websites, Product Hunt, Twitter, and developer communities</p>
                </div>
              </div>
              <div className="about-data-step">
                <div className="about-data-step-number">3</div>
                <div className="about-data-step-content">
                  <h4>🤖 AI Enrichment</h4>
                  <p>We use Claude API to enrich tool data with descriptions, pricing models, features, use cases, and more</p>
                </div>
              </div>
              <div className="about-data-step">
                <div className="about-data-step-number">4</div>
                <div className="about-data-step-content">
                  <h4>✅ Quality Assurance</h4>
                  <p>All new tools are vetted against quality thresholds (Vision ≥ 40, Ability ≥ 40, Buzz ≥ 40) before inclusion</p>
                </div>
              </div>
              <div className="about-data-step">
                <div className="about-data-step-number">5</div>
                <div className="about-data-step-content">
                  <h4>📊 Smart Versioning</h4>
                  <p>We track major and minor updates, detect quadrant changes, and maintain a complete changelog for each tool</p>
                </div>
              </div>
            </div>
          </section>

          {/* Data Points */}
          <section className="about-data-modal-section">
            <h3>📈 Data Included Per Tool</h3>
            <div className="about-data-data-grid">
              <div className="about-data-data-item"><span className="about-data-data-emoji">📝</span><span>Description</span></div>
              <div className="about-data-data-item"><span className="about-data-data-emoji">💰</span><span>Pricing Model</span></div>
              <div className="about-data-data-item"><span className="about-data-data-emoji">⭐</span><span>Features</span></div>
              <div className="about-data-data-item"><span className="about-data-data-emoji">📅</span><span>Founding Year</span></div>
              <div className="about-data-data-item"><span className="about-data-data-emoji">📊</span><span>Gartner Scores</span></div>
              <div className="about-data-data-item"><span className="about-data-data-emoji">🔄</span><span>Version History</span></div>
              <div className="about-data-data-item"><span className="about-data-data-emoji">📢</span><span>Changelog</span></div>
              <div className="about-data-data-item"><span className="about-data-data-emoji">🔗</span><span>Official Links</span></div>
            </div>
          </section>

          {/* Tech Stack */}
          <section className="about-data-modal-section">
            <h3>⚙️ Technical Stack</h3>
            <div className="about-data-tech-stack">
              <div className="about-data-tech-item"><strong>Scraping:</strong> Python + GitHub Actions</div>
              <div className="about-data-tech-item"><strong>Enrichment:</strong> Claude AI API</div>
              <div className="about-data-tech-item"><strong>Data Processing:</strong> Smart versioning + deduplication</div>
              <div className="about-data-tech-item"><strong>Storage:</strong> JSON + GitHub</div>
              <div className="about-data-tech-item"><strong>Updates:</strong> Automated bi-weekly (1st & 15th)</div>
              <div className="about-data-tech-item"><strong>Cost:</strong> ~$2/month (highly optimized)</div>
            </div>
          </section>

          {/* Transparency */}
          <section className="about-data-modal-section">
            <h3>🤝 Transparency</h3>
            <div className="about-data-transparency-box">
              <p>✅ <strong>No biased rankings</strong> - We provide objective data from multiple sources</p>
              <p>✅ <strong>Open methodology</strong> - All scraping & enrichment logic is documented</p>
              <p>✅ <strong>Version tracking</strong> - Major/minor updates are tracked and logged</p>
              <p>✅ <strong>Quality gates</strong> - New tools must meet minimum quality thresholds</p>
              <p>✅ <strong>Regular updates</strong> - Data refreshed every 15 days automatically</p>
            </div>
          </section>

          {/* Statistics */}
          <section className="about-data-modal-section">
            <h3>📊 Current Statistics</h3>
            <div className="about-data-stats-grid">
              <div className="about-data-stat">
                <div className="about-data-stat-value">61</div>
                <div className="about-data-stat-label">Tools Tracked</div>
              </div>
              <div className="about-data-stat">
                <div className="about-data-stat-value">8</div>
                <div className="about-data-stat-label">Categories</div>
              </div>
              <div className="about-data-stat">
                <div className="about-data-stat-value">41</div>
                <div className="about-data-stat-label">Enriched</div>
              </div>
            </div>
          </section>
        </div>

        <div className="about-data-modal-footer">
          <button className="about-data-close-button" onClick={onClose}>Close</button>
        </div>
      </div>

      <style jsx global>{`
        .about-data-modal-overlay {
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
          padding: var(--space-20);
          backdrop-filter: blur(4px);
        }

        .about-data-modal-content {
          background: var(--color-charcoal-800);
          border-radius: var(--radius-xl);
          max-width: 700px;
          width: 100%;
          max-height: 90vh;
          display: flex;
          flex-direction: column;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          animation: slideIn 0.3s ease-out;
          border: 1px solid var(--color-border);
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .about-data-modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--space-24);
          border-bottom: 1px solid var(--color-border);
          background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-teal-400) 100%);
          color: white;
          border-radius: var(--radius-xl) var(--radius-xl) 0 0;
        }

        .about-data-modal-header h2 {
          margin: 0;
          font-size: var(--font-size-2xl);
          font-weight: var(--font-weight-semibold);
        }

        .about-data-modal-close {
          background: none;
          border: none;
          cursor: pointer;
          color: white;
          font-size: 28px;
          padding: 0;
          transition: opacity 0.2s;
        }

        .about-data-modal-close:hover {
          opacity: 0.8;
        }

        .about-data-modal-body {
          overflow-y: auto;
          padding: var(--space-24);
          flex: 1;
        }

        .about-data-modal-section {
          margin-bottom: var(--space-32);
        }

        .about-data-modal-section h3 {
          font-size: var(--font-size-lg);
          font-weight: var(--font-weight-semibold);
          margin: 0 0 var(--space-16) 0;
          color: var(--color-text);
        }

        .about-data-info-box {
          background: rgba(50, 184, 198, 0.1);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-large);
          padding: var(--space-16);
        }

        .about-data-info-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--space-8) 0;
          border-bottom: 1px solid var(--color-border);
        }

        .about-data-info-row:last-child {
          border-bottom: none;
        }

        .about-data-info-label {
          font-weight: var(--font-weight-semibold);
          color: var(--color-text);
        }

        .about-data-info-value {
          color: var(--color-primary);
          font-weight: var(--font-weight-medium);
        }

        .about-data-methodology {
          display: flex;
          flex-direction: column;
          gap: var(--space-16);
        }

        .about-data-step {
          display: flex;
          gap: var(--space-16);
          padding: var(--space-16);
          background: rgba(50, 184, 198, 0.05);
          border-left: 4px solid var(--color-primary);
          border-radius: var(--radius-base);
        }

        .about-data-step-number {
          min-width: 40px;
          width: 40px;
          height: 40px;
          background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-teal-400) 100%);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: var(--font-weight-semibold);
          flex-shrink: 0;
        }

        .about-data-step-content h4 {
          margin: 0 0 var(--space-8) 0;
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-semibold);
          color: var(--color-text);
        }

        .about-data-step-content p {
          margin: 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          line-height: 1.5;
        }

        .about-data-data-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
          gap: var(--space-12);
        }

        .about-data-data-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: var(--space-8);
          padding: var(--space-16);
          background: rgba(50, 184, 198, 0.05);
          border-radius: var(--radius-base);
          text-align: center;
        }

        .about-data-data-emoji {
          font-size: var(--font-size-2xl);
        }

        .about-data-data-item span:last-child {
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-medium);
          color: var(--color-text);
        }

        .about-data-tech-stack {
          display: flex;
          flex-direction: column;
          gap: var(--space-12);
        }

        .about-data-tech-item {
          padding: var(--space-12);
          background: rgba(50, 184, 198, 0.05);
          border-left: 3px solid var(--color-primary);
          border-radius: var(--radius-sm);
          font-size: var(--font-size-sm);
          color: var(--color-text);
        }

        .about-data-tech-item strong {
          color: var(--color-text);
        }

        .about-data-transparency-box {
          background: rgba(50, 184, 198, 0.1);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-base);
          padding: var(--space-16);
        }

        .about-data-transparency-box p {
          margin: var(--space-8) 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          line-height: 1.6;
        }

        .about-data-transparency-box p:first-child {
          margin-top: 0;
        }

        .about-data-transparency-box p:last-child {
          margin-bottom: 0;
        }

        .about-data-stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: var(--space-16);
        }

        .about-data-stat {
          text-align: center;
          padding: var(--space-16);
          background: rgba(50, 184, 198, 0.05);
          border-radius: var(--radius-base);
          border: 1px solid var(--color-border);
        }

        .about-data-stat-value {
          font-size: var(--font-size-4xl);
          font-weight: var(--font-weight-bold);
          color: var(--color-primary);
          margin-bottom: var(--space-4);
        }

        .about-data-stat-label {
          font-size: var(--font-size-xs);
          color: var(--color-text-secondary);
          font-weight: var(--font-weight-medium);
        }

        .about-data-modal-footer {
          padding: var(--space-16) var(--space-24);
          border-top: 1px solid var(--color-border);
          background: rgba(50, 184, 198, 0.05);
          border-radius: 0 0 var(--radius-xl) var(--radius-xl);
          display: flex;
          justify-content: flex-end;
        }

        .about-data-close-button {
          padding: var(--space-8) var(--space-24);
          background: var(--color-charcoal-700);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-base);
          cursor: pointer;
          font-weight: var(--font-weight-medium);
          font-size: var(--font-size-sm);
          color: var(--color-text);
          transition: all 0.2s;
        }

        .about-data-close-button:hover {
          background: var(--color-charcoal-700);
          border-color: var(--color-primary);
        }
      `}</style>
    </div>
  );
}
