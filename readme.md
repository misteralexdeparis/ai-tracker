# 🚀 Community AI Tracker

Real-time database of 50+ AI tools across LLM, Vibe Coding, Video Generation, Image Generation, and AI Agents.

## Features

- ✅ 50+ AI tools tracked
- ✅ Daily Notion sync
- ✅ Automated news monitoring
- ✅ Real-time updates
- ✅ Beautiful website (coming tomorrow)

## Data Categories

- **LLM**: GPT-5, Claude 4.5, Gemini 2.5, Grok 4, DeepSeek, LeChat, Qwen, Mixtral, Llama 3.2
- **Vibe Coding**: Cursor, Claude Code, Bolt, Lovable, Windsurf, Gemini Code Assist, v0, Replit AI
- **AI Agents**: Devin, Crew AI, Devika
- **Video Generation**: Sora 2, Runway Gen-4, Pika 2.1, Google Veo 3
- **Image Generation**: DALL-E 3, Midjourney, Flux, Stable Diffusion, Ideogram

## Setup

### 1. Clone Repository
git clone https://github.com/alex/ai-tracker.git
cd ai-tracker

text

### 2. Install Dependencies
python -m venv venv
source venv/Scripts/activate # Windows
pip install -r scripts/requirements.txt

text

### 3. Configure Secrets (GitHub)
Go to Settings → Secrets and add:
- `NOTION_API_KEY` - Your Notion integration token
- `DISCORD_WEBHOOK_URL` (optional) - For alerts

### 4. Run Locally (Optional)
python scripts/sync-notion.py
python scripts/monitor-news.py

text

## Automation

- **Daily Sync** (9 AM UTC): Syncs Notion to JSON
- **News Monitor** (Mon/Wed/Fri 9 AM UTC): Checks for AI tool updates
- **Manual Trigger**: Go to Actions tab and run manually

## Website

Frontend coming tomorrow - will display this data beautifully on Vercel.

## Contributing

Community contributions welcome! Add tools, fix data, suggest features.

## License

MIT

---

**Last Updated**: October 30, 2025
**Tools Tracked**: 50+
**Auto-Updated**: Daily