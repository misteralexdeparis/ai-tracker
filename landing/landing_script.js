// AI Tracker Landing Script - ULTRA DEBUG VERSION
(function() {
    'use strict';
    
    if (window.aiTrackerLoaded) {
        console.log('⚠️ AI Tracker already loaded');
        return;
    }
    window.aiTrackerLoaded = true;
    
    const state = {
        allTools: [],
        filteredTools: [],
        currentFilter: 'all'
    };

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
            
            console.log(`✅ Loaded ${state.allTools.length} tools`);
            
            renderTools(state.allTools);
            updateCategoryCounts();
            
            setTimeout(() => {
                console.log('🎯 FORCING MATRIX RENDER');
                renderGartnerMatrix(state.allTools);
            }, 100);
            
            updateStats(state.allTools);
            
        } catch (error) {
            console.error('❌ Error:', error);
        }
    }

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

    function updateCategoryCounts() {
        const { counts, total } = getCategoryCounts();
        
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
    }

    function renderTools(toolsToRender = state.allTools) {
        const grid = document.getElementById('toolsGrid');
        if (!grid) return;
        
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

    function renderGartnerMatrix(toolsToRender = state.allTools) {
        console.log('🔍 renderGartnerMatrix called with', toolsToRender.length, 'tools');
        
        const canvas = document.getElementById('matrixCanvas');
        console.log('🔍 Canvas element:', canvas);
        console.log('🔍 Canvas type:', canvas?.tagName, 'ID:', canvas?.id);
        
        if (!canvas) {
            console.error('❌ matrixCanvas NOT found!');
            console.log('🔍 Searching for all divs:');
            document.querySelectorAll('div').forEach((d, i) => {
                if (d.id || d.className) {
                    console.log(`  Div ${i}: id="${d.id}" class="${d.className}"`);
                }
            });
            return;
        }
        
        console.log('✅ Canvas found! Clearing old dots...');
        const existingDots = canvas.querySelectorAll('.tool-dot');
        console.log(`🔍 Found ${existingDots.length} existing dots`);
        existingDots.forEach(dot => dot.remove());
        
        if (!toolsToRender || toolsToRender.length === 0) {
            console.warn('⚠️ No tools to render');
            return;
        }
        
        console.log(`🎯 Starting to add ${toolsToRender.length} dots...`);
        
        let dotsAdded = 0;
        toolsToRender.forEach((tool, index) => {
            try {
                const dot = document.createElement('div');
                const quadrant = (tool.quadrant || 'niche').toLowerCase();
                dot.className = `tool-dot ${quadrant}`;
                
                const xPercent = (tool.vision || 50);
                const yPercent = (tool.ability || 50);
                
                dot.style.left = `${xPercent}%`;
                dot.style.bottom = `${yPercent}%`;
                dot.title = `${tool.name}\nVision: ${tool.vision} | Ability: ${tool.ability}`;
                dot.onclick = () => window.aiTracker.openModal(tool.id || tool.name.toLowerCase().replace(/\s+/g, '-'));
                
                canvas.appendChild(dot);
                dotsAdded++;
                
                if (index === 0 || index === toolsToRender.length - 1) {
                    console.log(`✅ Dot ${index}: ${tool.name} @ ${xPercent}% left, ${yPercent}% bottom, quadrant: ${quadrant}`);
                }
            } catch (e) {
                console.error(`❌ Error adding dot ${index}:`, e);
            }
        });
        
        console.log(`✅ Total dots added: ${dotsAdded}`);
        console.log('🔍 Canvas now has:', canvas.querySelectorAll('.tool-dot').length, 'dots');
        console.log('🔍 Canvas innerHTML length:', canvas.innerHTML.length);
    }

    function filterMatrix(category) {
        state.currentFilter = category;
        
        document.querySelectorAll('#matrixCategories .category-pill').forEach(pill => {
            pill.classList.remove('active');
        });
        event.target.closest('.category-pill').classList.add('active');
        
        if (category === 'all') {
            state.filteredTools = state.allTools;
        } else {
            state.filteredTools = state.allTools.filter(tool => tool.category === category);
        }
        
        const statusEl = document.getElementById('matrixFilterStatus');
        if (statusEl) {
            statusEl.textContent = `Showing ${state.filteredTools.length} tools${category !== 'all' ? ` in ${category}` : ''}`;
        }
        
        renderGartnerMatrix(state.filteredTools);
    }

    function filterByQuadrant(quadrant) {
        if (quadrant === 'all') {
            state.filteredTools = state.allTools;
        } else {
            state.filteredTools = state.allTools.filter(tool => (tool.quadrant || 'niche').toLowerCase() === quadrant.toLowerCase());
        }
        renderGartnerMatrix(state.filteredTools);
    }

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

        if (tool.vision !== undefined && tool.ability !== undefined) {
            modalBody += `
                <div class="modal-section">
                    <h4>Gartner Scores</h4>
                    <div style="margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span class="score-label">Vision</span>
                            <span class="score-value">${tool.vision}/100</span>
                        </div>
                        <div class="score-bar">
                            <div class="score-bar-fill" style="width: ${tool.vision}%"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span class="score-label">Ability</span>
                            <span class="score-value">${tool.ability}/100</span>
                        </div>
                        <div class="score-bar">
                            <div class="score-bar-fill" style="width: ${tool.ability}%"></div>
                        </div>
                    </div>
                </div>
            `;
        }

        if (tool.buzz_score) {
            modalBody += `
                <div class="modal-section">
                    <h4>Buzz Score</h4>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span class="score-label">Buzz</span>
                        <span class="score-value">${tool.buzz_score}/100</span>
                    </div>
                    <div class="score-bar">
                        <div class="score-bar-fill" style="width: ${tool.buzz_score}%"></div>
                    </div>
                </div>
            `;
        }

        if (tool.description) {
            modalBody += `<div class="modal-section"><h4>Description</h4><p>${tool.description}</p></div>`;
        }

        if (tool.features && tool.features.length > 0) {
            modalBody += `<div class="modal-section"><h4>✨ Features</h4><ul>${tool.features.map(f => `<li>• ${f}</li>`).join('')}</ul></div>`;
        }

        if (tool.strengths && tool.strengths.length > 0) {
            modalBody += `<div class="modal-section"><h4>💪 Strengths</h4><ul>${tool.strengths.map(s => `<li>• ${s}</li>`).join('')}</ul></div>`;
        }

        if (tool.limitations && tool.limitations.length > 0) {
            modalBody += `<div class="modal-section"><h4>⚠️ Limitations</h4><ul>${tool.limitations.map(l => `<li>• ${l}</li>`).join('')}</ul></div>`;
        }

        if (tool.pricing) {
            modalBody += `<div class="modal-section"><h4>💰 Pricing</h4><p>${tool.pricing}</p></div>`;
        }

        if (tool.integrations) {
            modalBody += `<div class="modal-section"><h4>🔗 Integrations</h4><p>${tool.integrations}</p></div>`;
        }

        if (tool.changelog && tool.changelog.length > 0) {
            modalBody += `<div class="modal-section"><h4>📝 Updates</h4><ul>${tool.changelog.map(c => `<li>• ${c}</li>`).join('')}</ul></div>`;
        }

        if (tool.status) {
            modalBody += `<div class="modal-section"><h4>Status</h4><p>🟢 ${tool.status}</p></div>`;
        }

        modalBody += `
            <div class="modal-section">
                <h4>Links</h4>
                <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                    ${tool.official_url ? `<a href="${tool.official_url}" target="_blank" class="cta-button">Website</a>` : ''}
                </div>
            </div>
        `;

        document.getElementById('modalBody').innerHTML = modalBody;
        document.getElementById('toolModal').classList.add('active');
    }

    function updateStats(tools) {
        const toolsCount = tools ? tools.length : 0;
        document.querySelectorAll(".stat-count, .tool-count").forEach(el => {
            el.textContent = toolsCount;
        });
    }

    window.aiTracker = {
        openModal,
        filterMatrix,
        filterByQuadrant,
        loadTools,
        renderGartnerMatrix
    };

    document.addEventListener("DOMContentLoaded", function() {
        console.log('🚀 Loading tools...');
        loadTools();
        
        setTimeout(() => {
            console.log('🔄 Second render attempt...');
            renderGartnerMatrix(state.allTools);
        }, 500);
    });

})();

console.log('✅ Script loaded');