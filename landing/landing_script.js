// Load tools from JSON and render with proper design matching existing tools
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
        const loadedTools = data.tools || data || [];
        
        console.log(`✅ Loaded ${loadedTools.length} tools from GitHub`);
        
        // Replace the global tools array with loaded data
        window.tools = loadedTools;
        
        // Re-render with new tools
        renderTools(window.tools);
        updateStats(window.tools);
        
    } catch (error) {
        console.error('Error loading tools from GitHub:', error);
        console.log('📦 Using tools already in HTML (39 default tools)');
        // Tools are already in HTML, no need to change
    }
}

// Enhanced renderTools function that matches the existing design
function renderTools(toolsToRender = window.tools) {
    const grid = document.getElementById('toolsGrid');
    if (!grid) {
        console.error('❌ toolsGrid not found!');
        return;
    }
    
    grid.innerHTML = toolsToRender.map(tool => {
        // Ensure tool has an ID
        const toolId = tool.id || tool.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
        
        return `
            <div class="tool-card" onclick="openModal('${toolId}')">
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
    
    console.log(`✅ Rendered ${toolsToRender.length} tools`);
}

// Enhanced openModal to handle both embedded and loaded tools
function openModal(toolId) {
    // Find the tool in window.tools array
    let tool = window.tools.find(t => (t.id === toolId) || (t.name.toLowerCase().replace(/\s+/g, '-') === toolId));
    
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

    // Vision & Ability Scores with bars
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

    // Buzz Score if available
    if (tool.buzz_score) {
        modalBody += `
            <div class="modal-section">
                <h4>Buzz Score</h4>
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span class="score-label">Market Buzz</span>
                    <span class="score-value" style="font-size: 16px;">${tool.buzz_score}/100</span>
                </div>
                <div class="score-bar">
                    <div class="score-bar-fill" style="width: ${tool.buzz_score}%"></div>
                </div>
            </div>
        `;
    }

    // Pricing
    if (tool.pricing) {
        modalBody += `
            <div class="modal-section">
                <h4>💰 Pricing</h4>
                <p>${tool.pricing}</p>
            </div>
        `;
    }

    // About/Description
    modalBody += `
        <div class="modal-section">
            <h4>About</h4>
            <p>${tool.description || tool.about || 'AI Tool'}</p>
        </div>
    `;

    // Key Features
    if (tool.features && tool.features.length > 0) {
        modalBody += `
            <div class="modal-section">
                <h4>✨ Key Features</h4>
                <ul>
                    ${tool.features.map(f => `<li style="padding-left: 20px;">• ${f}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Strengths
    if (tool.strengths && tool.strengths.length > 0) {
        modalBody += `
            <div class="modal-section">
                <h4>💪 Strengths</h4>
                <ul>
                    ${tool.strengths.map(s => `<li class="strength">${s}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Limitations
    if (tool.limitations && tool.limitations.length > 0) {
        modalBody += `
            <div class="modal-section">
                <h4>⚠️ Limitations</h4>
                <ul>
                    ${tool.limitations.map(l => `<li class="limitation">${l}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Integrations
    if (tool.integrations) {
        modalBody += `
            <div class="modal-section">
                <h4>🔗 Integrations</h4>
                <p>${tool.integrations}</p>
            </div>
        `;
    }

    // Changelog
    if (tool.changelog && tool.changelog.length > 0) {
        modalBody += `
            <div class="modal-section">
                <h4>📝 Recent Updates</h4>
                <ul>
                    ${tool.changelog.map(c => `<li style="padding-left: 20px;">• ${c}</li>`).join('')}
                </ul>
            </div>
        `;
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
        modalBody += `
            <div class="modal-section">
                <h4>Status</h4>
                <p style="color: ${statusColors[tool.status.toLowerCase()] || 'var(--color-text)'}; font-weight: 600;">${tool.status}</p>
            </div>
        `;
    }

    // Footer with link
    const toolUrl = tool.official_url || tool.url || tool.website || '#';
    modalBody += `
        <div class="modal-section">
            <a href="${toolUrl}" target="_blank" class="cta-button" style="display: inline-block;">Visit Official Website →</a>
        </div>
    `;

    document.getElementById('modalBody').innerHTML = modalBody;
    document.getElementById('toolModal').classList.add('active');
}

// Update stats (if exists)
function updateStats(tools) {
    const toolsCount = tools ? tools.length : 0;
    const statElements = document.querySelectorAll(".stat-count, .tool-count");
    statElements.forEach(el => {
        el.textContent = toolsCount;
    });
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", function() {
    console.log('🚀 Landing page initializing...');
    loadTools();
});

console.log('✅ landing_script.js loaded - ready to load tools from JSON!');