// Load tools from /public (simple and works everywhere)
async function loadTools() {
    try {
        const timestamp = Date.now();
        const cacheBreaker = Math.random().toString(36).substring(7);
        // Load from public folder
        const url = `/ai_tracker_enhanced.json?t=${timestamp}&cb=${cacheBreaker}`;
        
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Failed to fetch: ${response.status}`);
        }

        const data = await response.json();
        const tools = data.tools || data || [];
        
        console.log(`✅ Loaded ${tools.length} tools from /public`);
        renderTools(tools);
        updateStats(tools);
    } catch (error) {
        console.error('Error loading tools:', error);
        // Fallback to sample data if fetch fails
        loadSampleTools();
    }
}

// Sample fallback data
function loadSampleTools() {
    console.log('⚠️ Using fallback data');
    const tools = [
        {
            id: "gpt-5-pro",
            name: "GPT-5 Pro",
            developer: "OpenAI",
            category: ["LLM"],
            quadrant: "Leader",
            vision: 92,
            ability: 91,
            official_url: "https://openai.com"
        },
        {
            id: "gpt-5",
            name: "GPT-5",
            developer: "OpenAI",
            category: ["LLM"],
            quadrant: "Leader",
            vision: 88,
            ability: 86,
            official_url: "https://openai.com"
        },
        {
            id: "claude-4-5",
            name: "Claude 4.5",
            developer: "Anthropic",
            category: ["LLM"],
            quadrant: "Leader",
            vision: 85,
            ability: 87,
            official_url: "https://claude.ai"
        }
    ];
    renderTools(tools);
    updateStats(tools);
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", function() {
    loadTools();
});

// Render tools grid
function renderTools(toolsToRender) {
    const grid = document.getElementById("tools-grid");
    if (!grid) return;

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
}

// Update stats
function updateStats(tools) {
    const toolsCount = tools ? tools.length : 0;
    const statElements = document.querySelectorAll(".stat-count");
    statElements.forEach(el => {
        el.textContent = toolsCount;
    });

    // Update tool count display
    const countElements = document.querySelectorAll(".tool-count");
    countElements.forEach(el => {
        el.textContent = toolsCount;
    });

    // Update last updated date
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