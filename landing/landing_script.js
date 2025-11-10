let tools = [];

// Load tools from GitHub with cache busting
async function loadTools() {
    try {
        const timestamp = Date.now();
        const cacheBreaker = Math.random().toString(36).substring(7);
        const url = `https://raw.githubusercontent.com/misteralexdeparis/ai-tracker/main/public/ai_tracker_enhanced.json?t=${timestamp}&cb=${cacheBreaker}`;
        
        const response = await fetch(url, {
            cache: 'no-store',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch: ${response.status}`);
        }

        const data = await response.json();
        tools = data.tools || data || [];
        
        console.log(`✅ Loaded ${tools.length} tools from GitHub`);
        renderTools(tools);
    } catch (error) {
        console.error('Error loading tools from GitHub:', error);
        // Fallback to sample data if fetch fails
        loadSampleTools();
    }
}

// Sample fallback data
function loadSampleTools() {
    tools = [
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
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", function() {
    loadTools();
    updateStats();
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
function updateStats() {
    const toolsCount = tools.length;
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
    let filtered = tools;

    if (category && category !== "all") {
        filtered = tools.filter(tool => {
            const cats = Array.isArray(tool.category) ? tool.category : [tool.category];
            return cats.some(c => c.toLowerCase() === category.toLowerCase());
        });
    }

    renderTools(filtered);
}

// Filter by use case
function filterByUseCase(usecase) {
    if (!usecase) {
        renderTools(tools);
        return;
    }

    const filtered = tools.filter(tool => {
        const name = (tool.name || "").toLowerCase();
        const dev = (tool.developer || "").toLowerCase();
        const cats = Array.isArray(tool.category) 
            ? tool.category.join(" ").toLowerCase() 
            : (tool.category || "").toLowerCase();

        return name.includes(usecase.toLowerCase()) ||
               dev.includes(usecase.toLowerCase()) ||
               cats.includes(usecase.toLowerCase());
    });

    renderTools(filtered);
}

// Category pill click handler
document.addEventListener("click", function(e) {
    if (e.target.classList.contains("pill")) {
        // Remove active class from all pills
        document.querySelectorAll(".pill").forEach(pill => {
            pill.classList.remove("active");
        });
        // Add active class to clicked pill
        e.target.classList.add("active");
        // Filter by category
        const category = e.target.getAttribute("data-category");
        filterByCategory(category);
    }
});

// Use case input handler
const usecaseInput = document.getElementById("usecase");
if (usecaseInput) {
    usecaseInput.addEventListener("input", function(e) {
        filterByUseCase(e.target.value);
    });
}

// Recommendation system
function getRecommendations(category) {
    const filtered = tools.filter(tool => {
        const cats = Array.isArray(tool.category) ? tool.category : [tool.category];
        return cats.some(c => c.toLowerCase() === category.toLowerCase());
    });

    const sorted = filtered.sort((a, b) => (b.vision + b.ability) - (a.vision + a.ability));

    if (document.getElementById("recommendations")) {
        const container = document.getElementById("recommendations");
        container.innerHTML = "";

        sorted.slice(0, 3).forEach(tool => {
            const card = document.createElement("div");
            card.className = "tool-card";
            card.innerHTML = `
                <h3>${tool.name}</h3>
                <p class="developer">${tool.developer}</p>
                <span class="badge">${tool.quadrant}</span>
                <p>Vision: ${tool.vision} | Ability: ${tool.ability}</p>
                ${tool.official_url ? `<a href="${tool.official_url}" target="_blank" class="btn">Visit</a>` : ''}
            `;
            container.appendChild(card);
        });
    }
}