# Newsletter System - Setup Guide

## Architecture
```
ai-tracker-web/
├── landing/
│   └── index.html (avec formulaire newsletter)
├── server/
│   ├── newsletter-server.js (collecte + envoi)
│   ├── subscribers.json (DB simple des emails)
│   └── .env (variables d'env)
└── README.md
```

## 1. Backend Node.js (newsletter-server.js)

```javascript
const express = require('express');
const nodemailer = require('nodemailer');
const fs = require('fs');
const cron = require('node-cron');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(cors());

const SUBSCRIBERS_FILE = './subscribers.json';

// Load subscribers
function loadSubscribers() {
    try {
        return JSON.parse(fs.readFileSync(SUBSCRIBERS_FILE, 'utf8'));
    } catch {
        return [];
    }
}

// Save subscribers
function saveSubscribers(subscribers) {
    fs.writeFileSync(SUBSCRIBERS_FILE, JSON.stringify(subscribers, null, 2));
}

// Email transporter (Gmail/SendGrid/etc)
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASSWORD // App Password, not regular password
    }
});

// Subscribe endpoint
app.post('/api/subscribe', (req, res) => {
    const { email } = req.body;
    
    if (!email || !email.includes('@')) {
        return res.status(400).json({ error: 'Invalid email' });
    }
    
    const subscribers = loadSubscribers();
    
    // Check if already subscribed
    if (subscribers.find(s => s.email === email)) {
        return res.status(400).json({ error: 'Already subscribed' });
    }
    
    subscribers.push({
        email,
        subscribedAt: new Date().toISOString(),
        active: true
    });
    
    saveSubscribers(subscribers);
    
    console.log(`✅ New subscriber: ${email}`);
    res.json({ success: true, message: 'Subscribed successfully' });
});

// Unsubscribe endpoint
app.post('/api/unsubscribe', (req, res) => {
    const { email } = req.body;
    const subscribers = loadSubscribers();
    
    const updated = subscribers.map(s => 
        s.email === email ? { ...s, active: false } : s
    );
    
    saveSubscribers(updated);
    res.json({ success: true });
});

// Send newsletter
async function sendNewsletter(updates, news) {
    const subscribers = loadSubscribers().filter(s => s.active);
    
    if (subscribers.length === 0) return;
    
    const htmlContent = `
        <h1>🤖 AI Tools Tracker - Weekly Update</h1>
        
        <h2>📊 This Week's Updates</h2>
        <ul>
            ${updates.map(u => `<li><strong>${u.toolName}</strong>: ${u.change}</li>`).join('')}
        </ul>
        
        <h2>📰 AI News Roundup</h2>
        ${news.map(n => `
            <div style="margin: 15px 0; padding: 10px; border-left: 3px solid #32b8c6;">
                <h3>${n.title}</h3>
                <p>${n.summary}</p>
                <small>Source: ${n.source}</small>
            </div>
        `).join('')}
        
        <hr>
        <p><a href="https://ai-tracker.example.com">View Full Tracker</a> | 
           <a href="https://ai-tracker.example.com/unsubscribe?email={{email}}">Unsubscribe</a></p>
    `;
    
    for (const subscriber of subscribers) {
        try {
            await transporter.sendMail({
                from: process.env.EMAIL_USER,
                to: subscriber.email,
                subject: '🤖 AI Tools Tracker - Weekly Update',
                html: htmlContent.replace('{{email}}', subscriber.email)
            });
            console.log(`✅ Sent to ${subscriber.email}`);
        } catch (error) {
            console.error(`❌ Failed to send to ${subscriber.email}:`, error);
        }
    }
}

// Weekly newsletter (every Monday at 9 AM)
cron.schedule('0 9 * * 1', async () => {
    console.log('📧 Sending weekly newsletter...');
    
    // Get updates from JSON
    const updates = await getWeeklyUpdates();
    const news = await getAINews();
    
    await sendNewsletter(updates, news);
});

// Admin dashboard
app.get('/admin/subscribers', (req, res) => {
    if (req.headers['x-admin-key'] !== process.env.ADMIN_KEY) {
        return res.status(403).json({ error: 'Unauthorized' });
    }
    
    const subscribers = loadSubscribers();
    const active = subscribers.filter(s => s.active).length;
    
    res.json({ 
        total: subscribers.length, 
        active, 
        subscribers 
    });
});

app.listen(process.env.PORT || 3000, () => {
    console.log('✅ Newsletter server running');
});
```

## 2. .env File

```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
ADMIN_KEY=your-secret-key
PORT=3000
NODE_ENV=production
```

## 3. Update Frontend (index.html)

Modifier le formulaire newsletter:

```javascript
async function handleNewsletter(event) {
    event.preventDefault();
    const email = event.target.querySelector('input[type="email"]').value;
    
    try {
        const response = await fetch('https://your-domain.com/api/subscribe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ Subscribed! Check ${email} for confirmation.`);
            event.target.reset();
        } else {
            alert(`❌ ${data.error}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to subscribe');
    }
}
```

## 4. Setup Instructions

```bash
# Install dependencies
npm install express nodemailer cors dotenv node-cron

# Gmail Setup (if using Gmail):
# 1. Enable 2-Factor Authentication
# 2. Create App Password at myaccount.google.com/apppasswords
# 3. Copy the 16-char password to .env

# Run server
node newsletter-server.js

# Deploy to Heroku/Railway/etc
git push heroku main
```

## 5. Alternative: Use Service Like Mailchimp/SendGrid

**Simpler approach:**

```javascript
const mailchimp = require("@mailchimp/marketing");

mailchimp.setConfig({
  apiKey: process.env.MAILCHIMP_API_KEY,
  server: "us1"
});

app.post('/api/subscribe', async (req, res) => {
    const { email } = req.body;
    
    try {
        await mailchimp.lists.addListMember(process.env.MAILCHIMP_LIST_ID, {
            email_address: email,
            status: "pending"
        });
        res.json({ success: true });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});
```

## 6. Weekly Update Process

**Pour les updates auto chaque semaine:**

1. **Tool Updates**: Vérifier le changelog du JSON
2. **AI News**: Scraper automatiquement avec Puppeteer/Cheerio
3. **Format & Send**: Via Cron job

## 7. Production Deployment

**Options:**
- **Heroku** : Gratuit (avec limites)
- **Railway.app** : $5/month
- **DigitalOcean** : $4-6/month
- **Vercel Serverless** : Gratuit avec DB

---

**Tu veux que je:**
1. ✅ Crée le serveur Node complet ?
2. ✅ Ajoute Mailchimp integration (plus simple) ?
3. ✅ Crée le scraper d'actualités IA ?
4. ✅ Ajoute Admin dashboard pour gérer les emails ?