'use client';

import { useEffect, useState } from 'react';

interface Tool {
  name: string;
  category: string;
  gartner_quadrant?: string;
  vision?: number;
  ability?: number;
  final_score?: number;
  description?: string;
  free_tier?: string;
  [key: string]: any;
}

interface AllToolsProps {
  onToolClick: (tool: Tool) => void;
}

export default function AllTools({ onToolClick }: AllToolsProps) {
  const [tools, setTools] = useState<Tool[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  useEffect(() => {
    fetch('/ai_tracker_enhanced.json')
      .then(res => res.json())
      .then(data => {
        setTools(data.tools);
        const cats = Array.from(new Set(data.tools.map((t: Tool) => t.category)));
        setCategories(['All', ...cats.sort()]);
      });
  }, []);

  const filteredTools = selectedCategory === 'All'
    ? tools
    : tools.filter(t => t.category === selectedCategory);

  const quadrantColors = {
    'Leader': '#32b8c6',
    'Visionary': '#4c8bf5',
    'Challenger': '#f59e0b',
    'Niche Player': '#10b981'
  };

  return (
    <>
      <section className="all-tools-section section">
        <h2 className="section-title">All AI Tools</h2>
        <p className="section-subtitle">Browse our complete collection of {tools.length} AI tools</p>

      <div className="categories">
        {categories.map(cat => (
          <button
            key={cat}
            className={`category-pill ${selectedCategory === cat ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      <p className="all-tools-count">
        Showing {filteredTools.length} {filteredTools.length === 1 ? 'tool' : 'tools'}
      </p>

      <div className="all-tools-grid">
        {filteredTools.map(tool => {
          const quadrantColor = quadrantColors[tool.gartner_quadrant as keyof typeof quadrantColors] || '#6b7280';
          
          return (
            <div
              key={tool.name}
              className="tool-card"
              onClick={() => onToolClick(tool)}
            >
              <div className="tool-card-header">
                <h3>{tool.name}</h3>
                <div className="tool-card-badges">
                  <span className="tool-card-category-badge">{tool.category}</span>
                  {tool.gartner_quadrant && (
                    <span
                      className="tool-card-quadrant-badge"
                      style={{ backgroundColor: quadrantColor }}
                    >
                      {tool.gartner_quadrant}
                    </span>
                  )}
                </div>
              </div>

              {tool.description && (
                <p className="tool-card-description">
                  {tool.description.substring(0, 120)}
                  {tool.description.length > 120 ? '...' : ''}
                </p>
              )}

              <div className="tool-card-scores">
                {tool.vision !== undefined && tool.ability !== undefined && (
                  <div className="tool-card-score-item">
                    <span className="tool-card-score-label">Vision / Ability:</span>
                    <span className="tool-card-score-value">{tool.vision} / {tool.ability}</span>
                  </div>
                )}
                {tool.final_score !== undefined && (
                  <div className="tool-card-score-item">
                    <span className="tool-card-score-label">Final Score:</span>
                    <span className="tool-card-score-value final">{tool.final_score}</span>
                  </div>
                )}
              </div>

              {tool.free_tier && tool.free_tier.toLowerCase() !== 'no' && (
                <div className="tool-card-free-tier">✓ Free Tier Available</div>
              )}
            </div>
          );
        })}
      </div>
    </section>

      <style jsx global>{`
        .all-tools-section {
          padding: 48px 24px;
        }

        .all-tools-count {
          text-align: center;
          color: var(--color-text-secondary);
          margin: 24px 0;
          font-size: 14px;
        }

        .all-tools-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 24px;
          max-width: 1280px;
          margin: 0 auto;
        }

        .tool-card {
          background: var(--color-charcoal-800);
          border: 1px solid var(--color-border);
          border-radius: 12px;
          padding: 24px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .tool-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 24px rgba(50, 184, 198, 0.2);
          border-color: var(--color-primary);
        }

        .tool-card-header {
          margin-bottom: 16px;
        }

        .tool-card-header h3 {
          margin: 0 0 12px 0;
          font-size: 20px;
          font-weight: 600;
          color: var(--color-text);
        }

        .tool-card-badges {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .tool-card-category-badge,
        .tool-card-quadrant-badge {
          padding: 4px 12px;
          border-radius: 999px;
          font-size: 11px;
          font-weight: 500;
        }

        .tool-card-category-badge {
          background: rgba(50, 184, 198, 0.15);
          color: var(--color-primary);
          border: 1px solid var(--color-primary);
        }

        .tool-card-quadrant-badge {
          color: white;
        }

        .tool-card-description {
          color: var(--color-text-secondary);
          font-size: 14px;
          line-height: 1.6;
          margin: 0 0 16px 0;
        }

        .tool-card-scores {
          display: flex;
          flex-direction: column;
          gap: 8px;
          padding: 12px;
          background: rgba(50, 184, 198, 0.05);
          border-radius: 8px;
          margin-bottom: 12px;
        }

        .tool-card-score-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .tool-card-score-label {
          font-size: 12px;
          color: var(--color-text-secondary);
          font-weight: 500;
        }

        .tool-card-score-value {
          font-size: 14px;
          font-weight: 600;
          color: var(--color-primary);
        }

        .tool-card-score-value.final {
          font-size: 16px;
        }

        .tool-card-free-tier {
          font-size: 12px;
          color: #10b981;
          font-weight: 500;
          padding: 8px;
          background: rgba(16, 185, 129, 0.1);
          border-radius: 6px;
          text-align: center;
        }

        @media (max-width: 768px) {
          .all-tools-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </>
  );
}
