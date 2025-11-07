let tools = [];

// Load tools from JSON
async function loadTools() {
    try {
        const response = await fetch('../public/ai_tracker_enhanced.json');
        tools = await response.json();
        renderTools(tools);
    } catch (error) {
        console.error('Error loading tools:', error);
        // Fallback to sample data if JSON fails
        loadSampleTools();
    }
}

// Sample fallback data
function loadSampleTools() {
    tools = [
        { id: "gpt-5-pro", name: "GPT-5 Pro", developer: "OpenAI", category: ["LLM"], quadrant: "Leader", vision: 92, ability: 91 },
        { id: "gpt-5", name: "GPT-5", developer: "OpenAI", category: ["LLM"], quadrant: "Leader", vision: 88, ability: 86 },
        { id: "claude-4-5", name: "Claude 4.5", developer: "Anthropic", category: ["LLM"], quadrant: "Leader", vision: 85, ability: 87 },
        { id: "gemini-2-5-pro", name: "Gemini 2.5 Pro", developer: "Google", category: ["LLM"], quadrant: "Leader", vision: 82, ability: 81 },
        { id: "midjourney-v7", name: "Midjourney v7", developer: "Midjourney", category: ["Image Generation"], quadrant: "Leader", vision: 78, ability: 84 },
        { id: "lovable", name: "Lovable", developer: "Lovable", category: ["Vibe Coding"], quadrant: "Leader", vision: 79, ability: 79 },
        { id: "github-copilot", name: "GitHub Copilot", developer: "GitHub", category: ["Vibe Coding"], quadrant: "Leader", vision: 68, ability: 83 },
        { id: "bolt-new", name: "Bolt.new", developer: "StackBlitz", category: ["Vibe Coding"], quadrant: "Leader", vision: 73, ability: 77 },
        { id: "sora-2", name: "Sora 2", developer: "OpenAI", category: ["Video Generation"], quadrant: "Leader", vision: 85, ability: 62 },
        { id: "dalle-3", name: "DALL-E 3", developer: "OpenAI", category: ["Image Generation"], quadrant: "Leader", vision: 70, ability: 79 },
    ];
    renderTools(tools);
}

// Initialize
document.addEventListener("DOMContentLoaded", function() {
    loadTools();
    updateStats();
});

// Render tools grid
function renderTools(toolsToRender) {
    const grid = document.getElementById("tools-grid");
    grid.innerHTML = "";
    
    if (!toolsToRender || toolsToRender.length === 0) {
        grid.innerHTML = "<p>No tools found</p>";
        return;
    }
    
    toolsToRender.forEach(tool => {
        const card = document.createElement("div");
        const quadrantClass = tool.quadrant ? tool.quadrant.toLowerCase() : "niche";
        card.className = `tool-card ${quadrantClass}`;
        
        const categories = Array.isArray(tool.category) ? tool.category.join(", ") : tool.category;
        
        card.innerHTML = `
            <h3>${tool.name}</h3>
            <div class="developer">${tool.developer}</div>
            <span class="badge">${categories}</span>
            <span class="badge quadrant-badge">${tool.quadrant}</span>
            <div class="scores">
                <div>Vision: ${tool.vision}</div>
                <div>Ability: ${tool.ability}</div>
            </div>
            <button class="btn" onclick="openToolDetail('${tool.id}')">Learn More</button>
        `;
        grid.appendChild(card);
    });
}

// Open tool detail modal (placeholder)
function openToolDetail(toolId) {
    const tool = tools.find(t => t.id === toolId);
    if (tool) {
        alert(`${tool.name}\n\nDeveloper: ${tool.developer}\nVision: ${tool.vision}\nAbility: ${tool.ability}\n\nMore details at: ${tool.url}`);
    }
}

// Filter by category
function filterByCategory(category) {
    const pills = document.querySelectorAll(".pill");
    pills.forEach(p => p.classList.remove("active"));
    event.target.classList.add("active");
    
    if (category === "all") {
        renderTools(tools);
    } else {
        const filtered = tools.filter(t => {
            const cats = Array.isArray(t.category) ? t.category : [t.category];
            return cats.some(c => c.includes(category));
        });
        renderTools(filtered);
    }
}

// Filter by use case
function filterTools() {
    const usecase = document.getElementById("usecase").value;
    const rec = document.getElementById("recommendations");
    rec.innerHTML = "";
    
    if (!usecase) return;
    
    let categoryMap = {
        "code": ["Vibe Coding"],
        "video": ["Video Generation"],
        "image": ["Image Generation"],
        "search": ["LLM", "AI Search"],
        "audio": ["Audio"]
    };
    
    const filtered = tools.filter(t => {
        const cats = Array.isArray(t.category) ? t.category : [t.category];
        return cats.some(c => categoryMap[usecase]?.some(mc => c.includes(mc)));
    });
    
    if (filtered.length === 0) {
        rec.innerHTML = "<p>No tools found for this use case</p>";
        return;
    }
    
    filtered.forEach(tool => {
        const card = document.createElement("div");
        const quadrantClass = tool.quadrant ? tool.quadrant.toLowerCase() : "niche";
        card.className = `tool-card ${quadrantClass}`;
        const categories = Array.isArray(tool.category) ? tool.category.join(", ") : tool.category;
        
        card.innerHTML = `
            <h3>${tool.name}</h3>
            <div class="developer">${tool.developer}</div>
            <span class="badge">${categories}</span>
            <button class="btn" onclick="openToolDetail('${tool.id}')">View Tool</button>
        `;
        rec.appendChild(card);
    });
}

// Update statistics
function updateStats() {
    if (!tools || tools.length === 0) return;
    
    const leaders = tools.filter(t => t.quadrant === "Leader").length;
    const visionaries = tools.filter(t => t.quadrant === "Visionary").length;
    const challengers = tools.filter(t => t.quadrant === "Challenger").length;
    const niche = tools.filter(t => t.quadrant === "Niche").length;
    
    // Update distribution boxes if they exist
    const distBoxes = document.querySelectorAll(".dist-box");
    if (distBoxes.length >= 4) {
        distBoxes[0].querySelector("h3").textContent = `${leaders} Leaders`;
        distBoxes[1].querySelector("h3").textContent = `${visionaries} Visionaries`;
        distBoxes[2].querySelector("h3").textContent = `${challengers} Challengers`;
        distBoxes[3].querySelector("h3").textContent = `${niche} Niche`;
    }
}

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
            target.scrollIntoView({ behavior: "smooth" });
        }
    });
});