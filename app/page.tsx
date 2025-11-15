'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import GartnerMatrix from './components/GartnerMatrix';
import AllTools from './components/AllTools';
import AboutDataModal from './components/AboutDataModal';
import ToolModal from './components/ToolModal';
import {
  parseUserInput,
  buildUserRequirements,
  matchToolsToUserNeeds,
  type ToolMatch,
  type Tool,
  type ToolEnrichment,
} from './lib/usecase-matcher';

type ViewMode = 'discover' | 'gartner' | 'all-tools';

export default function Home() {
  const router = useRouter();
  const [viewMode, setViewMode] = useState<ViewMode>('discover');
  const [searchText, setSearchText] = useState('');
  const [codingLevel, setCodingLevel] = useState<string>('');
  const [budget, setBudget] = useState<string>('');
  const [experienceLevel, setExperienceLevel] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  const [detectedUseCases, setDetectedUseCases] = useState<string[]>([]);
  const [showAboutData, setShowAboutData] = useState(false);
  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [selectedTool, setSelectedTool] = useState<any>(null);

  // Update detected use cases as user types
  useEffect(() => {
    if (searchText.length > 3) {
      const detected = parseUserInput(searchText);
      setDetectedUseCases(detected);
    } else {
      setDetectedUseCases([]);
    }
  }, [searchText]);

  const handleSearch = () => {
    // Build query params
    const params = new URLSearchParams();
    params.set('q', searchText);
    if (codingLevel) params.set('coding_level', codingLevel);
    if (budget) params.set('budget', budget);
    if (experienceLevel) params.set('experience', experienceLevel);

    // Navigate to results page
    router.push(`/find-tool/results?${params.toString()}`);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && searchText.trim()) {
      handleSearch();
    }
  };

  const exampleSearches = [
    "Create a business presentation with data",
    "Build a full-stack web application",
    "Analyze multiple research documents",
    "Generate marketing copy for social media",
    "Create images for my blog",
  ];

  return (
    <>
      <style jsx global>{`
        :root {
          --color-white: rgba(255, 255, 255, 1);
          --color-gray-200: rgba(245, 245, 245, 1);
          --color-gray-300: rgba(167, 169, 169, 1);
          --color-gray-400: rgba(119, 124, 124, 1);
          --color-slate-500: rgba(98, 108, 113, 1);
          --color-charcoal-700: rgba(31, 33, 33, 1);
          --color-charcoal-800: rgba(38, 40, 40, 1);
          --color-slate-900: rgba(19, 52, 59, 1);
          --color-teal-300: rgba(50, 184, 198, 1);
          --color-teal-400: rgba(45, 166, 178, 1);
          --color-text: var(--color-gray-200);
          --color-text-secondary: rgba(167, 169, 169, 0.7);
          --color-primary: var(--color-teal-300);
          --color-primary-hover: var(--color-teal-400);
          --color-border: rgba(119, 124, 124, 0.3);
          --font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          --font-size-sm: 12px;
          --font-size-base: 14px;
          --font-size-lg: 16px;
          --font-size-xl: 18px;
          --font-size-2xl: 20px;
          --font-size-3xl: 24px;
          --font-size-4xl: 30px;
          --font-size-6xl: 48px;
          --font-weight-normal: 400;
          --font-weight-medium: 500;
          --font-weight-bold: 600;
          --space-4: 4px;
          --space-8: 8px;
          --space-12: 12px;
          --space-16: 16px;
          --space-24: 24px;
          --space-32: 32px;
          --space-40: 40px;
          --space-48: 48px;
          --space-64: 64px;
          --radius-sm: 6px;
          --radius-base: 8px;
          --radius-lg: 12px;
          --radius-xl: 16px;
          --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);
          --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.16);
          --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.2);
        }

        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: var(--font-family-base);
          background: linear-gradient(135deg, #1a1d2e 0%, #0f1117 100%);
          color: var(--color-text);
          line-height: 1.6;
        }

        .header {
          position: sticky;
          top: 0;
          background: rgba(31, 33, 33, 0.95);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid var(--color-border);
          z-index: 1000;
          padding: var(--space-16) 0;
        }

        .header-container {
          max-width: 1280px;
          margin: 0 auto;
          padding: 0 var(--space-24);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .logo {
          font-size: var(--font-size-xl);
          font-weight: var(--font-weight-bold);
          color: var(--color-primary);
        }

        .view-toggle {
          display: flex;
          gap: var(--space-8);
          background: var(--color-charcoal-800);
          padding: var(--space-4);
          border-radius: var(--radius-base);
          border: 1px solid var(--color-border);
        }

        .view-toggle-btn {
          padding: var(--space-8) var(--space-24);
          border: none;
          background: transparent;
          color: var(--color-text);
          cursor: pointer;
          border-radius: var(--radius-sm);
          font-size: var(--font-size-base);
          font-weight: var(--font-weight-medium);
          transition: all 0.3s;
        }

        .view-toggle-btn.active {
          background: var(--color-primary);
          color: var(--color-slate-900);
        }

        .view-toggle-btn:hover:not(.active) {
          background: rgba(50, 184, 198, 0.1);
          color: var(--color-primary);
        }

        .about-data-btn {
          background: rgba(50, 184, 198, 0.2);
          color: var(--color-primary);
          border: 1px solid var(--color-primary);
          padding: var(--space-8) var(--space-16);
          border-radius: var(--radius-base);
          cursor: pointer;
          font-weight: var(--font-weight-medium);
          transition: all 0.3s;
          font-size: var(--font-size-base);
        }

        .about-data-btn:hover {
          background: rgba(50, 184, 198, 0.3);
          transform: translateY(-2px);
        }

        .hero {
          padding: var(--space-64) var(--space-24);
          text-align: center;
          background: linear-gradient(135deg, rgba(50, 184, 198, 0.1) 0%, rgba(19, 52, 59, 0.1) 100%);
        }

        .hero h1 {
          font-size: var(--font-size-6xl);
          font-weight: var(--font-weight-bold);
          margin-bottom: var(--space-16);
          background: linear-gradient(135deg, var(--color-primary) 0%, #ffffff 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .hero p {
          font-size: var(--font-size-xl);
          color: var(--color-text-secondary);
          margin-bottom: var(--space-32);
          max-width: 700px;
          margin-left: auto;
          margin-right: auto;
        }

        .search-container {
          max-width: 800px;
          margin: 0 auto;
          padding: var(--space-32);
          background: var(--color-charcoal-800);
          border-radius: var(--radius-xl);
          border: 1px solid var(--color-border);
          box-shadow: var(--shadow-lg);
        }

        .search-input {
          width: 100%;
          padding: var(--space-16);
          font-size: var(--font-size-lg);
          background: var(--color-charcoal-700);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-base);
          color: var(--color-text);
          margin-bottom: var(--space-16);
        }

        .search-input:focus {
          outline: none;
          border-color: var(--color-primary);
          box-shadow: 0 0 0 3px rgba(50, 184, 198, 0.1);
        }

        .search-input::placeholder {
          color: var(--color-text-secondary);
        }

        .detected-tags {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-8);
          margin-bottom: var(--space-16);
          min-height: 24px;
        }

        .tag {
          padding: var(--space-4) var(--space-12);
          background: rgba(50, 184, 198, 0.2);
          border-radius: var(--radius-sm);
          color: var(--color-primary);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
        }

        .search-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: var(--space-16);
        }

        .filters-toggle {
          padding: var(--space-8) var(--space-16);
          background: transparent;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-base);
          color: var(--color-text);
          cursor: pointer;
          font-size: var(--font-size-base);
          transition: all 0.3s;
        }

        .filters-toggle:hover {
          border-color: var(--color-primary);
          color: var(--color-primary);
        }

        .cta-button {
          padding: var(--space-12) var(--space-32);
          background: var(--color-primary);
          color: var(--color-slate-900);
          border: none;
          border-radius: var(--radius-base);
          font-size: var(--font-size-lg);
          font-weight: var(--font-weight-bold);
          cursor: pointer;
          transition: all 0.3s;
        }

        .cta-button:hover {
          background: var(--color-primary-hover);
          transform: translateY(-2px);
          box-shadow: var(--shadow-lg);
        }

        .cta-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
        }

        .filters-panel {
          margin-top: var(--space-24);
          padding-top: var(--space-24);
          border-top: 1px solid var(--color-border);
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: var(--space-16);
        }

        .filter-group {
          display: flex;
          flex-direction: column;
          gap: var(--space-8);
        }

        .filter-label {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          font-weight: var(--font-weight-medium);
        }

        .filter-select {
          padding: var(--space-8) var(--space-12);
          background: var(--color-charcoal-700);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-base);
          color: var(--color-text);
          font-size: var(--font-size-base);
          cursor: pointer;
        }

        .filter-select:focus {
          outline: none;
          border-color: var(--color-primary);
        }

        .examples-section {
          max-width: 1280px;
          margin: var(--space-48) auto;
          padding: 0 var(--space-24);
        }

        .examples-title {
          font-size: var(--font-size-base);
          color: var(--color-text-secondary);
          margin-bottom: var(--space-16);
          text-align: center;
        }

        .examples-grid {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-12);
          justify-content: center;
        }

        .example-chip {
          padding: var(--space-8) var(--space-16);
          background: var(--color-charcoal-800);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-base);
          color: var(--color-text);
          cursor: pointer;
          font-size: var(--font-size-sm);
          transition: all 0.3s;
        }

        .example-chip:hover {
          background: rgba(50, 184, 198, 0.2);
          color: var(--color-primary);
          border-color: var(--color-primary);
          transform: translateY(-2px);
        }

        .how-it-works {
          max-width: 1280px;
          margin: var(--space-64) auto;
          padding: var(--space-48) var(--space-24);
          background: var(--color-charcoal-800);
          border-radius: var(--radius-xl);
          border: 1px solid var(--color-border);
        }

        .how-it-works h2 {
          font-size: var(--font-size-4xl);
          text-align: center;
          margin-bottom: var(--space-48);
          color: var(--color-primary);
        }

        .steps-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: var(--space-32);
        }

        .step {
          text-align: center;
        }

        .step-number {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-teal-400) 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto var(--space-16);
          color: var(--color-slate-900);
          font-size: var(--font-size-3xl);
          font-weight: var(--font-weight-bold);
        }

        .step h3 {
          font-size: var(--font-size-xl);
          margin-bottom: var(--space-8);
        }

        .step p {
          color: var(--color-text-secondary);
          font-size: var(--font-size-base);
        }

        .content-section {
          max-width: 1280px;
          margin: var(--space-64) auto;
          padding: 0 var(--space-24);
        }

        /* Gartner Matrix Styles */
        .gartner-section {
          max-width: 1280px;
          margin: var(--space-64) auto;
          padding: 0 var(--space-24);
        }

        .section-title {
          font-size: var(--font-size-4xl);
          font-weight: var(--font-weight-bold);
          margin-bottom: var(--space-16);
          text-align: center;
        }

        .section-subtitle {
          font-size: var(--font-size-lg);
          color: var(--color-text-secondary);
          text-align: center;
          margin-bottom: var(--space-48);
          max-width: 700px;
          margin-left: auto;
          margin-right: auto;
        }

        .categories {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-12);
          justify-content: center;
          margin-bottom: var(--space-32);
        }

        .category-pill {
          padding: var(--space-12) var(--space-24);
          background: var(--color-charcoal-800);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          color: var(--color-text);
          cursor: pointer;
          transition: all 0.3s;
          font-size: var(--font-size-base);
        }

        .category-pill:hover,
        .category-pill.active {
          background: var(--color-primary);
          color: var(--color-slate-900);
          border-color: var(--color-primary);
        }

        .matrix-filter-status {
          text-align: center;
          color: var(--color-text-secondary);
          margin-bottom: var(--space-16);
          font-size: var(--font-size-base);
        }

        .legend {
          display: flex;
          justify-content: center;
          gap: var(--space-24);
          margin-bottom: var(--space-24);
          flex-wrap: wrap;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: var(--space-8);
        }

        .legend-dot {
          width: 16px;
          height: 16px;
          border-radius: 50%;
        }

        .legend-dot.leader {
          background: #2563eb;
        }

        .legend-dot.visionary {
          background: #10b981;
        }

        .legend-dot.challenger {
          background: #8b5cf6;
        }

        .legend-dot.niche {
          background: #f59e0b;
        }

        .legend-item span {
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .gartner-matrix-container {
          width: 100%;
          height: 600px;
          background: var(--color-charcoal-800);
          border-radius: var(--radius-lg);
          border: 1px solid var(--color-border);
          padding: var(--space-32);
          padding-left: 100px;
          padding-bottom: 60px;
          position: relative;
          margin-bottom: var(--space-32);
        }

        .matrix-canvas {
          width: 100%;
          height: 100%;
          position: relative;
          border-left: 2px solid var(--color-border);
          border-bottom: 2px solid var(--color-border);
        }

        .matrix-quadrant {
          position: absolute;
          width: 50%;
          height: 50%;
          display: flex;
          align-items: flex-start;
          justify-content: flex-start;
          padding: var(--space-16);
          font-size: var(--font-size-lg);
          font-weight: var(--font-weight-bold);
          opacity: 0.6;
        }

        .matrix-quadrant.top-left {
          top: 0;
          left: 0;
          background: rgba(139, 92, 246, 0.05);
          color: #8b5cf6;
        }

        .matrix-quadrant.top-right {
          top: 0;
          right: 0;
          background: rgba(37, 99, 235, 0.05);
          color: #2563eb;
        }

        .matrix-quadrant.bottom-left {
          bottom: 0;
          left: 0;
          background: rgba(245, 158, 11, 0.05);
          color: #f59e0b;
        }

        .matrix-quadrant.bottom-right {
          bottom: 0;
          right: 0;
          background: rgba(16, 185, 129, 0.05);
          color: #10b981;
        }

        .matrix-tool-dot {
          position: absolute;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          cursor: pointer;
          transition: all 0.3s ease;
          border: 2px solid;
          z-index: 10;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          transform: translate(-50%, -50%);
        }

        .matrix-tool-dot:hover {
          transform: translate(-50%, -50%) scale(2.5);
          z-index: 20;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }

        .matrix-tool-dot.leader {
          background: #2563eb;
          border-color: #2563eb;
        }

        .matrix-tool-dot.visionary {
          background: #10b981;
          border-color: #10b981;
        }

        .matrix-tool-dot.challenger {
          background: #8b5cf6;
          border-color: #8b5cf6;
        }

        .matrix-tool-dot.niche-player {
          background: #f59e0b;
          border-color: #f59e0b;
        }

        .matrix-axis-label {
          position: absolute;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
          font-weight: var(--font-weight-medium);
        }

        .matrix-axis-label.x-axis {
          bottom: var(--space-8);
          left: 50%;
          transform: translateX(-50%);
        }

        .matrix-axis-label.y-axis {
          left: -80px;
          top: 50%;
          transform: translateY(-50%) rotate(-90deg);
          transform-origin: center;
          white-space: nowrap;
        }

        /* Community Section */
        .community-section {
          max-width: 1280px;
          margin: var(--space-64) auto;
          padding: 0 var(--space-24);
        }

        .community-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: var(--space-32);
        }

        .community-card {
          background: var(--color-charcoal-800);
          padding: var(--space-40);
          border-radius: var(--radius-xl);
          border: 1px solid var(--color-border);
          text-align: center;
          transition: all 0.3s;
        }

        .community-card:hover {
          transform: translateY(-8px);
          box-shadow: var(--shadow-lg);
          border-color: var(--color-primary);
        }

        .community-icon {
          font-size: 48px;
          margin-bottom: var(--space-24);
        }

        .community-card h3 {
          font-size: var(--font-size-2xl);
          margin-bottom: var(--space-12);
        }

        .community-card p {
          color: var(--color-text-secondary);
          margin-bottom: var(--space-24);
          line-height: 1.6;
        }

        /* Newsletter Section */
        .newsletter-section {
          background: var(--color-charcoal-800);
          padding: var(--space-64) var(--space-24);
          text-align: center;
          border-top: 1px solid var(--color-border);
          border-bottom: 1px solid var(--color-border);
          margin: var(--space-64) 0;
        }

        .newsletter-section h2 {
          font-size: var(--font-size-4xl);
          margin-bottom: var(--space-16);
        }

        .newsletter-section p {
          color: var(--color-text-secondary);
          margin-bottom: var(--space-32);
          font-size: var(--font-size-lg);
        }

        .newsletter-form {
          max-width: 500px;
          margin: 0 auto;
          display: flex;
          gap: var(--space-12);
        }

        .newsletter-form input {
          flex: 1;
          padding: var(--space-16);
          background: var(--color-charcoal-700);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-base);
          color: var(--color-text);
          font-size: var(--font-size-base);
        }

        .newsletter-form input:focus {
          outline: none;
          border-color: var(--color-primary);
          box-shadow: 0 0 0 3px rgba(50, 184, 198, 0.1);
        }
      `}</style>

      <header className="header">
        <div className="header-container">
          <div className="logo">🤖 AI Tools Tracker</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-24)' }}>
            <div className="view-toggle">
              <button
                className={`view-toggle-btn ${viewMode === 'discover' ? 'active' : ''}`}
                onClick={() => setViewMode('discover')}
              >
                🎯 Discover Your AI Tool
              </button>
              <button
                className={`view-toggle-btn ${viewMode === 'gartner' ? 'active' : ''}`}
                onClick={() => setViewMode('gartner')}
              >
                📊 Gartner Matrix
              </button>
              <button
                className={`view-toggle-btn ${viewMode === 'all-tools' ? 'active' : ''}`}
                onClick={() => setViewMode('all-tools')}
              >
                📋 All Tools
              </button>
            </div>
            <button className="about-data-btn" onClick={() => setShowAboutData(true)}>
              📊 About Data
            </button>
          </div>
        </div>
      </header>

      {viewMode === 'discover' ? (
        <>
          <section className="hero">
            <h1>Discover Your Perfect AI Tool</h1>
            <p>
              Describe what you want to accomplish in plain language, and we'll match you with the best AI tools from our curated database of 61 leading solutions.
            </p>
          </section>

          <div className="search-container" style={{ maxWidth: '800px', margin: '-40px auto 0', position: 'relative', zIndex: 10 }}>
            <input
              type="text"
              className="search-input"
              placeholder="e.g., Create a business presentation with financial data..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onKeyPress={handleKeyPress}
            />

            {detectedUseCases.length > 0 && (
              <div className="detected-tags">
                <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                  Detected:
                </span>
                {detectedUseCases.map((uc, idx) => (
                  <span key={idx} className="tag">
                    {uc.replace(/-/g, ' ')}
                  </span>
                ))}
              </div>
            )}

            <div className="search-actions">
              <button
                className="filters-toggle"
                onClick={() => setShowFilters(!showFilters)}
              >
                {showFilters ? '▼' : '▶'} {showFilters ? 'Hide' : 'Show'} Filters
              </button>
              <button
                className="cta-button"
                onClick={handleSearch}
                disabled={!searchText.trim()}
              >
                Find My Tool
              </button>
            </div>

            {showFilters && (
              <div className="filters-panel">
                <div className="filter-group">
                  <label className="filter-label">Coding Level</label>
                  <select
                    className="filter-select"
                    value={codingLevel}
                    onChange={(e) => setCodingLevel(e.target.value)}
                  >
                    <option value="">Any</option>
                    <option value="no-code">No Coding</option>
                    <option value="low-code">Low Code</option>
                    <option value="developer">Developer</option>
                    <option value="expert">Expert</option>
                  </select>
                </div>

                <div className="filter-group">
                  <label className="filter-label">Budget</label>
                  <select
                    className="filter-select"
                    value={budget}
                    onChange={(e) => setBudget(e.target.value)}
                  >
                    <option value="">Any</option>
                    <option value="free">Free Tier Only</option>
                    <option value="paid">Paid OK</option>
                  </select>
                </div>

                <div className="filter-group">
                  <label className="filter-label">Experience</label>
                  <select
                    className="filter-select"
                    value={experienceLevel}
                    onChange={(e) => setExperienceLevel(e.target.value)}
                  >
                    <option value="">Any</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="expert">Expert</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          <div className="examples-section">
            <p className="examples-title">Try these examples:</p>
            <div className="examples-grid">
              {exampleSearches.map((example, idx) => (
                <button
                  key={idx}
                  className="example-chip"
                  onClick={() => setSearchText(example)}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          <div className="how-it-works">
            <h2>How It Works</h2>
            <div className="steps-grid">
              <div className="step">
                <div className="step-number">1</div>
                <h3>Describe Your Need</h3>
                <p>Tell us what you want to accomplish in plain language</p>
              </div>
              <div className="step">
                <div className="step-number">2</div>
                <h3>AI-Powered Matching</h3>
                <p>Our algorithm analyzes 61 tools and finds the best matches for your use case</p>
              </div>
              <div className="step">
                <div className="step-number">3</div>
                <h3>Get Recommendations</h3>
                <p>See compatibility scores, strengths, limitations, and pricing for each match</p>
              </div>
            </div>
          </div>
        </>
      ) : viewMode === 'gartner' ? (
        <div className="content-section">
          <GartnerMatrix onToolClick={setSelectedTool} />
        </div>
      ) : (
        <div className="content-section">
          <AllTools onToolClick={setSelectedTool} />
        </div>
      )}

      {/* Community Footer */}
      <section className="community-section">
        <div className="community-grid">
          <div className="community-card">
            <div className="community-icon">💬</div>
            <h3>Discord Server</h3>
            <p>Real-time chat, feedback, and discussions with the community</p>
            <a href="https://discord.gg/rMWTpNQVBD" target="_blank" rel="noopener noreferrer" className="cta-button">
              Join Discord
            </a>
          </div>
          <div className="community-card">
            <div className="community-icon">🐙</div>
            <h3>GitHub Discussions</h3>
            <p>Feature requests, bug reports, and contribute to the project</p>
            <a href="https://github.com/misteralexdeparis/ai-tracker" target="_blank" rel="noopener noreferrer" className="cta-button">
              View on GitHub
            </a>
          </div>
          <div className="community-card">
            <div className="community-icon">📬</div>
            <h3>Newsletter</h3>
            <p>Weekly AI tool updates delivered to your inbox</p>
            <button className="cta-button" onClick={() => document.getElementById('newsletter-section')?.scrollIntoView({ behavior: 'smooth' })}>
              Subscribe Now
            </button>
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="newsletter-section" id="newsletter-section">
        <h2>Stay Updated</h2>
        <p>Get notified when new AI tools are added to our tracker</p>
        <form className="newsletter-form" onSubmit={(e) => {
          e.preventDefault();
          if (newsletterEmail) {
            window.location.href = `/api/newsletter/subscribe?email=${encodeURIComponent(newsletterEmail)}`;
          }
        }}>
          <input
            type="email"
            placeholder="your@email.com"
            value={newsletterEmail}
            onChange={(e) => setNewsletterEmail(e.target.value)}
            required
          />
          <button type="submit" className="cta-button">Subscribe</button>
        </form>
      </section>

      {/* Modals */}
      <AboutDataModal isOpen={showAboutData} onClose={() => setShowAboutData(false)} />
      <ToolModal tool={selectedTool} onClose={() => setSelectedTool(null)} />
    </>
  );
}
