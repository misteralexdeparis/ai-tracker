'use client';

import { useEffect, useState, useRef } from 'react';

interface Tool {
  name: string;
  category: string;
  gartner_quadrant?: string;
  vision?: number;
  ability?: number;
  [key: string]: any;
}

interface GartnerMatrixProps {
  onToolClick?: (tool: Tool) => void;
}

export default function GartnerMatrix({ onToolClick }: GartnerMatrixProps = {}) {
  const [tools, setTools] = useState<Tool[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const canvasRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load tools data
    fetch('/ai_tracker_enhanced.json')
      .then(res => res.json())
      .then(data => {
        setTools(data.tools);
        // Extract unique categories
        const cats = Array.from(new Set(data.tools.map((t: Tool) => t.category)));
        setCategories(['all', ...cats]);
      });
  }, []);

  useEffect(() => {
    if (!canvasRef.current || tools.length === 0) return;

    const canvas = canvasRef.current;
    canvas.innerHTML = `
      <div class="matrix-quadrant top-left">Challengers</div>
      <div class="matrix-quadrant top-right">Leaders</div>
      <div class="matrix-quadrant bottom-left">Niche Players</div>
      <div class="matrix-quadrant bottom-right">Visionaries</div>
      <div class="matrix-axis-label x-axis">Completeness of Vision →</div>
      <div class="matrix-axis-label y-axis">Ability to Execute</div>
    `;

    const filteredTools = selectedCategory === 'all'
      ? tools
      : tools.filter(t => t.category === selectedCategory);

    filteredTools.forEach(tool => {
      if (!tool.vision || !tool.ability) return;

      const dot = document.createElement('div');
      dot.className = `matrix-tool-dot ${tool.gartner_quadrant?.toLowerCase().replace(' ', '-') || ''}`;
      dot.style.left = `${tool.vision}%`;
      dot.style.bottom = `${tool.ability}%`;
      dot.title = `${tool.name}\nVision: ${tool.vision} | Ability: ${tool.ability}`;

      // Add click handler
      if (onToolClick) {
        dot.style.cursor = 'pointer';
        dot.addEventListener('click', () => onToolClick(tool));
      }

      canvas.appendChild(dot);
    });
  }, [tools, selectedCategory, onToolClick]);

  const filterStatus = selectedCategory === 'all'
    ? 'Showing all tools'
    : `Showing ${selectedCategory} tools`;

  return (
    <section className="gartner-section section">
      <h2 className="section-title">Interactive Gartner Magic Quadrant</h2>
      <p className="section-subtitle">Explore innovation vs execution across the AI landscape</p>

      <div className="categories">
        {categories.map(cat => (
          <button
            key={cat}
            className={`category-pill ${selectedCategory === cat ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {cat === 'all' ? 'All Tools' : cat}
          </button>
        ))}
      </div>

      <p className="matrix-filter-status">{filterStatus}</p>

      <div className="legend">
        <div className="legend-item">
          <div className="legend-dot leader"></div>
          <span>Leaders</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot visionary"></div>
          <span>Visionaries</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot challenger"></div>
          <span>Challengers</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot niche"></div>
          <span>Niche Players</span>
        </div>
      </div>

      <div className="gartner-matrix-container">
        <div className="matrix-canvas" ref={canvasRef}></div>
      </div>
    </section>
  );
}
