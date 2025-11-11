// Working version - Load from GitHub + render in correct container
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
        const tools = data.tools || data || [];
        
        console.log(`✅ Loaded ${tools.length} tools from GitHub`);
        renderToolsGrid(tools);
        updateStats(tools);
    } catch (error) {
        console.error('Error loading tools from GitHub:', error);
        console.log('📦 Loading embedded sample data...');
        loadSampleTools();
    }
}

// Embedded sample data with SUNO
function loadSampleTools() {
    const tools = [
        {"name":"GPT-5 Pro","official_url":"https://openai.com/gpt-5","category":"LLM","vision":92,"ability":91,"buzz_score":92,"quadrant":"Leader"},
        {"name":"GPT-5","official_url":"https://openai.com/gpt-5","category":"LLM","vision":88,"ability":86,"buzz_score":87,"quadrant":"Leader"},
        {"name":"Claude 4.5","official_url":"https://claude.ai","category":"LLM","vision":85,"ability":87,"buzz_score":86,"quadrant":"Leader"},
        {"name":"Sora 2","official_url":"https://openai.com/sora","category":"Video Generation","vision":85,"ability":62,"buzz_score":74,"quadrant":"Leader"},
        {"name":"SUNO","official_url":"https://suno.ai","category":"Audio/Music","vision":75,"ability":72,"buzz_score":74,"quadrant":"Leader"},
        {"name":"Midjourney v7","official_url":"https://www.midjourney.com","category":"Image Generation","vision":78,"ability":84,"buzz_score":81,"quadrant":"Leader"},
        {"name":"Lovable","official_url":"https://lovable.dev","category":"AI Coding","vision":79,"ability":79,"buzz_score":79,"quadrant":"Leader"}
    ];
    
    console.log(`✅ Loaded ${tools.length} sample tools (including SUNO!)`);
    renderToolsGrid(tools);
    updateStats(tools);
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", function() {
    console.log('🚀 AI Tracker Landing initializing...');
    loadTools();
});

// Render tools in the grid - look for both possible containers
function renderToolsGrid(toolsToRender) {
    // Try to find the tools container (could be #tools section)
    let gridContainer = document.querySelector('#tools .tool-grid') || 
                       document.querySelector('#tools .tools-grid') ||
                       document.querySelector('#tools [class*="grid"]') ||
                       document.querySelector('[class*="tools-container"]');
    
    // If not found, look for any section that might hold tools
    if (!gridContainer) {
        gridContainer = document.querySelector('#tools');
    }
    
    if (!gridContainer) {
        console.error('❌ Tools grid container not found. Looking for alternatives...');
        console.log('Available IDs:', Array.from(document.querySelectorAll('[id]')).map(el => el.id));
        return;
    }

    console.log('✅ Found grid container:', gridContainer.id || gridContainer.className);

    // Clear previous tools but keep category buttons
    const existingCards = gridContainer.querySelectorAll('[data-tool-card]');
    existingCards.forEach(card => card.remove());

    if (!toolsToRender || toolsToRender.length === 0) {
        const msg = document.createElement('p');
        msg.textContent = 'No tools found';
        msg.style.padding = '20px';
        gridContainer.appendChild(msg);
        return;
    }

    // Create a container for cards if needed
    let cardsContainer = gridContainer.querySelector('.tools-cards-container');
    if (!cardsContainer) {
        cardsContainer = document.createElement('div');
        cardsContainer.className = 'tools-cards-container';
        cardsContainer.style.display = 'grid';
        cardsContainer.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
        cardsContainer.style.gap = '20px';
        cardsContainer.style.marginTop = '30px';
        gridContainer.appendChild(cardsContainer);
    }

    // Render each tool
    toolsToRender.forEach(tool => {
        const card = document.createElement("div");
        card.setAttribute('data-tool-card', 'true');
        card.setAttribute('data-category', tool.category);
        
        const quadrantClass = tool.quadrant ? tool.quadrant.toLowerCase().replace(/\s+/g, '-') : "niche";
        card.className = `tool-card ${quadrantClass}`;
        card.style.cssText = `
            padding: 20px;
            border-radius: 8px;
            background: #f5f5f5;
            border: 1px solid #ddd;
            cursor: pointer;
            transition: all 0.3s ease;
        `;

        const categories = Array.isArray(tool.category) 
            ? tool.category.join(", ") 
            : (tool.category || "Other");

        card.innerHTML = `
            <h3 style="margin-top: 0;">${tool.name || "Unknown"}</h3>
            <p style="color: #666; font-size: 0.9em;">${tool.developer || ""}</p>
            <span style="display: inline-block; padding: 4px 8px; background: #e0e0e0; border-radius: 4px; font-size: 0.8em;">${tool.quadrant || "Niche"}</span>
            <p style="margin: 10px 0; font-size: 0.9em;"><strong>Vision:</strong> ${tool.vision || 0} | <strong>Ability:</strong> ${tool.ability || 0}</p>
            <p style="color: #888; font-size: 0.85em;">${categories}</p>
            ${tool.official_url ? `<a href="${tool.official_url}" target="_blank" style="display: inline-block; padding: 8px 16px; background: #007bff; color: white; border-radius: 4px; text-decoration: none; margin-top: 10px;">Visit</a>` : ''}
        `;

        cardsContainer.appendChild(card);
    });
    
    console.log(`✅ Rendered ${toolsToRender.length} tools in grid`);
}

// Update stats
function updateStats(tools) {
    const toolsCount = tools ? tools.length : 0;
    
    const statElements = document.querySelectorAll(".stat-count");
    statElements.forEach(el => {
        el.textContent = toolsCount;
    });

    const countElements = document.querySelectorAll(".tool-count");
    countElements.forEach(el => {
        el.textContent = toolsCount;
    });

    const now = new Date();
    const dateStr = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    const dateElements = document.querySelectorAll(".last-updated-date");
    dateElements.forEach(el => {
        el.textContent = dateStr;
    });
}

// Filter by category - fixed version
function filterByCategory(category) {
    const cards = document.querySelectorAll('[data-tool-card]');
    
    cards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        if (category === "all" || (cardCategory && cardCategory.toLowerCase().includes(category.toLowerCase()))) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
    
    console.log(`📊 Filtered by category: ${category}`);
}

// Category pill click handler
document.addEventListener("click", function(e) {
    if (e.target.classList.contains("category-pill")) {
        document.querySelectorAll(".category-pill").forEach(pill => {
            pill.classList.remove("active");
        });
        e.target.classList.add("active");
        const category = e.target.getAttribute("data-category");
        filterByCategory(category);
    }
});

console.log('✅ landing_script.js loaded successfully - ready to load tools!');