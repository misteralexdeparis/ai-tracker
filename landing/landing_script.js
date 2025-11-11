// AI Tracker Landing Script - Dynamic Gartner Matrix
(function() {
    'use strict';
    
    // Avoid duplicate declarations
    if (window.aiTrackerLoaded) {
        console.log('⚠️ AI Tracker already loaded, skipping...');
        return;
    }
    window.aiTrackerLoaded = true;
    
    // Module-scoped variables (no conflicts!)
    const state = {
        allTools: [],
        filteredTools: [],
        currentFilter: 'all'
    };

    // Load tools from JSON
    async function loadTools() {
        try {
            const timestamp = Date.now();
            const url = `https://raw.githubusercontent.com/misteralexdeparis/ai-tracker/main/public/ai_tracker_enhanced.json?t=${timestamp}`;
            
            const response = await fetch(url, {
                method: 'GET',
                mode: 'cors',
                cache: 'no-cache'
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch: ${response.status}`);
            }

            const data = await response.json();
            state.allTools = data.tools || data || [];
            window.tools = state.allTools;
            
            console.log(`✅ Loaded ${state.allTools.length} tools from GitHub`);
            console.log('Tools:', state.allTools.map(t => `${t.name} (Vision: ${t.vision}, Ability: ${t.ability})`));
            
            // Render everything
            renderTools(state.allTools);
            updateCategoryCounts();
            
            // Force render matrix with delay to ensure DOM is ready
            setTimeout(() => {
                console.log('🎯 Rendering Gartner Matrix...');
                renderGartnerMatrix(state.allTools);
            }, 100);
            
            updateStats(state.allTools);
            
        } catch (error) {
            console.error('❌ Error loading tools:', error);
        }
    }

    // Get category counts
    function getCategoryCounts() {
        const counts = {};
        let total = 0;
        
        state.allTools.forEach(tool => {
            const category = tool.category || 'Other';
            counts[category] = (counts[category] || 0) + 1;
            total++;
        });
        
        return { counts, total };
    }

    // Update category counts dynamically
    function updateCategoryCounts() {
        const { counts, total } = getCategoryCounts();
        
        console.log('📊 Category counts:', counts);
        
        // Update matrix categories
        const matrixCategories = document.querySelectorAll('#matrixCategories .category-pill');
        matrixCategories.forEach(pill => {
            const category = pill.getAttribute('data-category');
            const countSpan = pill.querySelector('.category-count');
            
            if (countSpan) {
                if (category === 'all') {
                    countSpan.textContent = `(${total})`;
                } else {
                    const count = counts[category] || 0;
                    countSpan.textContent = `(${count})`;
                }
            }
        });
        
        // Update tools categories
        const toolsCategories = document.querySelectorAll('#categories .category-pill');
        toolsCategories.forEach(pill => {
            const category = pill.getAttribute('data-category');
            const countSpan = pill.querySelector('.category-count');
            
            if (countSpan) {
                if (category === 'all') {
                    countSpan.textContent = `(${total})`;
                } else {
                    const count = counts[category] || 0;
                    countSpan.textContent = `(${count})`;
                }
            }
        });
    }

    // Render tools grid
    function renderTools(toolsToRender = state.allTools) {
        const grid = document.getElementById('toolsGrid');
        if (!grid) {
            console.warn('⚠️ toolsGrid not found!');
            return;
        }
        
        console.log(`📦 Rendering ${toolsToRender.length} tools in grid`);
        
        grid.innerHTML = toolsToRender.map(tool => {
            const toolId = tool.id || tool.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
            
            return `
                <div class="tool-card" onclick="window.aiTracker.openModal('${toolId}')">
                    <div class="tool-header">
                        <div>
                            <div class="tool-name">${tool.name || 'Unknown'}</div>
                            <div class="tool-developer">${tool.developer || tool.twitter_handle || ''}</div>
                        </div>
                    </div>
                    <div class="tool-category">${tool.category || 'Other'}</div>
                    <div class="quadrant-badge ${(tool.quadrant || 'niche').toLowerCase()}">
                        ${tool.quadrant || 'Niche'}
                    </div>
                    <div class="tool-about">${tool.description || tool.about || 'AI Tool'}</div>
                    <div class="tool-scores">
                        <div class="score">
                            <div class="score-label">Vision</div>
                            <div class="score-value">${tool.vision || 0}</div>
                        </div>
                        <div class="score">
                            <div class="score-label">Ability</div>
                            <div class="score-value">${tool.ability || 0}</div>
                        </div>
                    </div>
                    <button class="btn-secondary">View Details</button>
                </div>
            `;
        }).join('');
    }

    // Render Gartner Matrix
    function renderGartnerMatrix(toolsToRender = state.allTools) {
        const canvas = document.getElementById('matrixCanvas');
        if (!canvas) {
            console.error('❌ matrixCanvas not found!');
            console.log('Available elements:', {
                toolsGrid: !!document.getElementById('toolsGrid'),
                matrixCanvas: !!document.getElementById('matrixCanvas'),
                matrixCategories: !!document.getElementById('matrixCategories')
            });
            return;
        }
        
        console.log(`🎯 Rendering ${toolsToRender.length} tools on matrix`);
        
        // // Remove existing tool dots
        // const existingDots = canvas.querySelectorAll('.tool-dot');
        // console.log(`Removing ${existingDots.length} existing dots`);
        // existingDots.forEach(dot => dot.remove());
        
        // if (!toolsToRender || toolsToRender.length === 0) {
        //     console.warn('⚠️ No tools to render');
        //     return;
        // }
        
        // Render each tool as a dot
        toolsToRender.forEach(tool => {
            const dot = document.createElement('div');
            dot.className = `tool-dot ${(tool.quadrant || 'niche').toLowerCase()}`;
            
            const xPercent = (tool.vision || 50);
            const yPercent = (tool.ability || 50);
            
            dot.style.left = `${xPercent}%`;
            dot.style.bottom = `${yPercent}%`;
            dot.title = `${tool.name}\nVision: ${tool.vision} | Ability: ${tool.ability}`;
            
            dot.onclick = () => window.aiTracker.openModal(tool.id || tool.name.toLowerCase().replace(/\s+/g, '-'));
            
            canvas.appendChild(dot);
        });
        
        console.log(`✅ Rendered ${toolsToRender.length} tools on matrix`);
    }

    // Filter matrix by category
    function filterMatrix(category) {
        state.currentFilter = category;
        
        // Update active pill
        document.querySelectorAll('#matrixCategories .category-pill').forEach(pill => {
            pill.classList.remove('active');
        });
        event.target.closest('.category-pill').classList.add('active');
        
        // Filter tools
        if (category === 'all') {
            state.filteredTools = state.allTools;
        } else {
            state.filteredTools = state.allTools.filter(tool => tool.category === category);
        }
        
        // Update status
        const statusEl = document.getElementById('matrixFilterStatus');
        if (statusEl) {
            statusEl.textContent = `Showing ${state.filteredTools.length} tools${category !== 'all' ? ` in ${category}` : ''}`;
        }
        
        // Re-render
        renderGartnerMatrix(state.filteredTools);
    }

    // Filter by quadrant (legacy support)
    function filterByQuadrant(quadrant) {
        if (quadrant === 'all') {
            state.filteredTools = state.allTools;
        } else {
            state.filteredTools = state.allTools.filter(tool => (tool.quadrant || 'niche').toLowerCase() === quadrant.toLowerCase());
        }
        renderGartnerMatrix(state.filteredTools);
    }

    // Open modal with tool details
    function openModal(toolId) {
        let tool = state.allTools.find(t => (t.id === toolId) || (t.name.toLowerCase().replace(/\s+/g, '-') === toolId));
        
        if (!tool) {
            console.error('Tool not found:', toolId);
            return;
        }

        document.getElementById('modalTitle').textContent = tool.name;
        document.getElementById('modalSubtitle').textContent = tool.developer || tool.twitter_handle || 'AI Tool';
        
        let modalBody = `
            <div class="modal-section">
                <div class="tool-category">${tool.category || 'Other'}</div>
                <div class="quadrant-badge ${(tool.quadrant || 'niche').toLowerCase()}" style="margin-top: 8px;">${tool.quadrant || 'Niche'}</div>
            </div>
        `;

        // Gartner Scores
        modalBody += `
            <div class="modal-section">
                <h4>Gartner Scores</h4>
                <div style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span class="score-label">Completeness of Vision</span>
                        <span class="score-value" style="font-size: 16px;">${tool.vision || 0}/100</span>
                    </div>
                    <div class="score-bar">
                        <div class="score-bar-fill" style="width: ${tool.vision || 0}%"></div>
                    </div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span class="score-label">Ability to Execute</span>
                        <span class="score-value" style="font-size: 16px;">${tool.ability || 0}/100</span>
                    </div>
                    <div class="score-bar">
                        <div class="score-bar-fill" style="width: ${tool.ability || 0}%"></div>
                    </div>
                </div>
            </div>
        `;

        // Buzz Score
        if (tool.buzz_score) {
            modalBody += `
                <div class="modal-section">
                    <h4>Market Buzz Score</h4>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span class="score-label">Buzz Score</span>
                        <span class="score-value" style="font-size: 16px;">${tool.buzz_score}/100</span>
                    </div>
                    <div class="score-bar">
                        <div class="score-bar-fill" style="width: ${tool.buzz_score}%"></div>
                    </div>
                </div>
            `;
        }

        // Description
        if (tool.description) {
            modalBody += `<div class="modal-section"><h4>Description</h4><p>${tool.description}</p></div>`;
        }

        // Features
        if (tool.features && tool.features.length > 0) {
            modalBody += `<div class="modal-section"><h4>✨ Key Features</h4><ul>${tool.features.map(f => `<li style="padding-left: 20px;">• ${f}</li>`).join('')}</ul></div>`;
        }

        // Strengths
        if (tool.strengths && tool.strengths.length > 0) {
            modalBody += `<div class="modal-section"><h4>💪 Strengths</h4><ul>${tool.strengths.map(s => `<li class="strength">• ${s}</li>`).join('')}</ul></div>`;
        }

        // Limitations
        if (tool.limitations && tool.limitations.length > 0) {
            modalBody += `<div class="modal-section"><h4>⚠️ Limitations</h4><ul>${tool.limitations.map(l => `<li class="limitation">• ${l}</li>`).join('')}</ul></div>`;
        }

        // Pricing
        if (tool.pricing) {
            modalBody += `<div class="modal-section"><h4>💰 Pricing</h4><p>${tool.pricing}</p></div>`;
        }

        // Integrations
        if (tool.integrations) {
            modalBody += `<div class="modal-section"><h4>🔗 Integrations</h4><p>${tool.integrations}</p></div>`;
        }

        // Changelog
        if (tool.changelog && tool.changelog.length > 0) {
            modalBody += `<div class="modal-section"><h4>📝 Recent Updates</h4><ul>${tool.changelog.map(c => `<li style="padding-left: 20px;">• ${c}</li>`).join('')}</ul></div>`;
        }

        // Status
        if (tool.status) {
            const statusColors = {
                'live': 'var(--color-teal-300)',
                'active': 'var(--color-teal-300)',
                'beta': 'var(--color-orange-400)',
                'legacy': 'var(--color-gray-400)',
                'research': 'var(--color-slate-500)'
            };
            modalBody += `<div class="modal-section"><h4>Status</h4><p style="color: ${statusColors[tool.status.toLowerCase()] || 'var(--color-text)'}; font-weight: 600;">🟢 ${tool.status}</p></div>`;
        }

        // Social Links
        modalBody += `
            <div class="modal-section">
                <h4>Connect</h4>
                <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                    ${tool.official_url ? `<a href="${tool.official_url}" target="_blank" class="cta-button" style="display: inline-block;">Visit Website →</a>` : ''}
                    ${tool.twitter_handle ? `<a href="https://twitter.com/${tool.twitter_handle.replace('@', '')}" target="_blank" style="display: inline-block; padding: 8px 16px; background: #1DA1F2; color: white; border-radius: 4px; text-decoration: none;">Twitter</a>` : ''}
                    ${tool.discord_server ? `<a href="${tool.discord_server}" target="_blank" style="display: inline-block; padding: 8px 16px; background: #5865F2; color: white; border-radius: 4px; text-decoration: none;">Discord</a>` : ''}
                    ${tool.reddit ? `<a href="https://reddit.com/${tool.reddit}" target="_blank" style="display: inline-block; padding: 8px 16px; background: #FF4500; color: white; border-radius: 4px; text-decoration: none;">Reddit</a>` : ''}
                </div>
            </div>
        `;

        document.getElementById('modalBody').innerHTML = modalBody;
        document.getElementById('toolModal').classList.add('active');
    }

    // Update stats
    function updateStats(tools) {
        const toolsCount = tools ? tools.length : 0;
        const statElements = document.querySelectorAll(".stat-count, .tool-count");
        statElements.forEach(el => {
            el.textContent = toolsCount;
        });
    }

    // Expose public API
    window.aiTracker = {
        openModal,
        filterMatrix,
        filterByQuadrant,
        loadTools,
        renderGartnerMatrix
    };

    // Initialize on DOM ready
    document.addEventListener("DOMContentLoaded", function() {
        console.log('🚀 AI Tracker Landing initializing...');
        loadTools();
        
        // Also try immediate render after a tiny delay
        setTimeout(() => {
            if (state.allTools.length > 0 && document.getElementById('matrixCanvas')) {
                console.log('🔄 Force rendering matrix...');
                renderGartnerMatrix(state.allTools);
            }
        }, 200);
    });

})();

console.log('✅ AI Tracker script loaded successfully!');