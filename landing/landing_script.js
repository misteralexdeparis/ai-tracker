// Ultimate working version - Load from GitHub directly (no CORS issues with proper headers)
async function loadTools() {
    try {
        const timestamp = Date.now();
        // Use GitHub Pages or raw content with proper CORS
        const url = `https://raw.githubusercontent.com/misteralexdeparis/ai-tracker/main/public/ai_tracker_enhanced.json?t=${timestamp}`;
        
        const response = await fetch(url, {
            method: 'GET',
            mode: 'cors',
            cache: 'no-cache'
        });

        if (!response.ok) {
            console.warn('⚠️ GitHub fetch failed, trying fallback...');
            throw new Error(`Failed to fetch: ${response.status}`);
        }

        const data = await response.json();
        const tools = data.tools || data || [];
        
        console.log(`✅ Loaded ${tools.length} tools from GitHub`);
        renderTools(tools);
        updateStats(tools);
    } catch (error) {
        console.error('Error loading tools from GitHub:', error);
        // Fallback: load embedded sample data
        console.log('📦 Loading embedded sample data...');
        loadSampleTools();
    }
}

// Embedded sample data (will be replaced with real data once fetch works)
function loadSampleTools() {
    const tools = [
        {"name":"GPT-5 Pro","official_url":"https://openai.com/gpt-5","category":"LLM","vision":92,"ability":91,"quadrant":"Leader"},
        {"name":"GPT-5","official_url":"https://openai.com/gpt-5","category":"LLM","vision":88,"ability":86,"quadrant":"Leader"},
        {"name":"Claude 4.5","official_url":"https://claude.ai","category":"LLM","vision":85,"ability":87,"quadrant":"Leader"},
        {"name":"Sora 2","official_url":"https://openai.com/sora","category":"Video Generation","vision":85,"ability":62,"quadrant":"Leader"},
        {"name":"SUNO","official_url":"https://suno.ai","category":"Audio/Music","vision":75,"ability":72,"quadrant":"Leader"},
        {"name":"Midjourney v7","official_url":"https://www.midjourney.com","category":"Image Generation","vision":78,"ability":84,"quadrant":"Leader"},
        {"name":"Lovable","official_url":"https://lovable.dev","category":"AI Coding","vision":79,"ability":79,"quadrant":"Leader"}
    ];
    
    console.log(`✅ Loaded ${tools.length} sample tools`);
    renderTools(tools);
    updateStats(tools);
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", function() {
    console.log('🚀 AI Tracker initializing...');
    loadTools();
});

// Render tools grid
function renderTools(toolsToRender) {
    const grid = document.getElementById("tools-grid");
    if (!grid) {
        console.error('❌ tools-grid element not found');
        return;
    }

    grid.innerHTML = "";

    if (!toolsToRender || toolsToRender.length === 0) {
        grid.innerHTML = "<p>No tools found</p>";
        return;
    }

    toolsToRender.forEach(tool => {
        const card = document.createElement("div");
        const quadrantClass = tool.quadrant ? tool.quadrant.toLowerCase() : "niche";
        card.className = `tool-card ${quadrantClass}`;

        const categories = Array.isArray(tool.category) 
            ? tool.category.join(", ") 
            : (tool.category || "Other");

        card.innerHTML = `
            <h3>${tool.name || "Unknown"}</h3>
            <p class="developer">${tool.developer || ""}</p>
            <span class="badge">${tool.quadrant || "Niche"}</span>
            <p class="scores">Vision: <strong>${tool.vision || 0}</strong> | Ability: <strong>${tool.ability || 0}</strong></p>
            <p class="category">${categories}</p>
            ${tool.official_url ? `<a href="${tool.official_url}" target="_blank" class="btn">Visit</a>` : ''}
        `;

        grid.appendChild(card);
    });
    
    console.log(`✅ Rendered ${toolsToRender.length} tools`);
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

// Filter by category
function filterByCategory(category) {
    const grid = document.getElementById("tools-grid");
    if (!grid) return;
    
    const cards = Array.from(grid.children);
    cards.forEach(card => {
        if (category === "all" || card.classList.contains(category.toLowerCase())) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

// Category pill click handler
document.addEventListener("click", function(e) {
    if (e.target.classList.contains("pill")) {
        document.querySelectorAll(".pill").forEach(pill => {
            pill.classList.remove("active");
        });
        e.target.classList.add("active");
        const category = e.target.getAttribute("data-category");
        filterByCategory(category);
    }
});

console.log('✅ landing_script.js loaded successfully');