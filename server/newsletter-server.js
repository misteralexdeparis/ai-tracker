// newsletter-server.js
// Serveur Node.js pour gérer la newsletter automatique

// Fix SSL certificate issue on Windows
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const express = require('express');
const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');
const cron = require('node-cron');
require('dotenv').config();

const app = express();

// ===== CORS FIX =====
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, x-admin-key');
    
    if (req.method === 'OPTIONS') {
        return res.sendStatus(200);
    }
    next();
});

app.use(express.json());

const SUBSCRIBERS_FILE = path.join(__dirname, 'subscribers.json');

// ===== UTILITIES =====
function loadSubscribers() {
    try {
        const data = fs.readFileSync(SUBSCRIBERS_FILE, 'utf8');
        return JSON.parse(data);
    } catch {
        return [];
    }
}

function saveSubscribers(subscribers) {
    fs.writeFileSync(SUBSCRIBERS_FILE, JSON.stringify(subscribers, null, 2));
}

// ===== EMAIL CONFIG =====
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASSWORD
    }
});

// Verify email config
transporter.verify((error, success) => {
    if (error) {
        console.error('❌ Email config error:', error);
    } else {
        console.log('✅ Email ready');
    }
});

// ===== ROUTES =====

// Subscribe
app.post('/api/subscribe', (req, res) => {
    const { email } = req.body;
    
    if (!email || !email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
        return res.status(400).json({ error: 'Invalid email' });
    }
    
    const subscribers = loadSubscribers();
    
    if (subscribers.find(s => s.email.toLowerCase() === email.toLowerCase())) {
        return res.status(400).json({ error: 'Already subscribed' });
    }
    
    subscribers.push({
        email: email.toLowerCase(),
        subscribedAt: new Date().toISOString(),
        active: true,
        confirmed: false
    });
    
    saveSubscribers(subscribers);
    console.log(`✅ New subscriber: ${email}`);
    
    res.json({ 
        success: true, 
        message: 'Subscribed! Check your email for confirmation.' 
    });
});

// Unsubscribe
app.post('/api/unsubscribe', (req, res) => {
    const { email } = req.body;
    const subscribers = loadSubscribers();
    
    const updated = subscribers.map(s => 
        s.email.toLowerCase() === email.toLowerCase() 
            ? { ...s, active: false } 
            : s
    );
    
    saveSubscribers(updated);
    console.log(`✅ Unsubscribed: ${email}`);
    
    res.json({ success: true });
});

// Confirm subscription
app.post('/api/confirm/:email', (req, res) => {
    const { email } = req.params;
    const subscribers = loadSubscribers();
    
    const updated = subscribers.map(s => 
        s.email.toLowerCase() === email.toLowerCase() 
            ? { ...s, confirmed: true } 
            : s
    );
    
    saveSubscribers(updated);
    res.json({ success: true });
});

// Admin - Get subscribers
app.get('/admin/subscribers', (req, res) => {
    const adminKey = req.headers['x-admin-key'];
    if (adminKey !== process.env.ADMIN_KEY) {
        return res.status(403).json({ error: 'Unauthorized' });
    }
    
    const subscribers = loadSubscribers();
    const active = subscribers.filter(s => s.active).length;
    const confirmed = subscribers.filter(s => s.confirmed).length;
    
    res.json({ 
        total: subscribers.length,
        active,
        confirmed,
        subscribers
    });
});

// Admin - Send test email
app.post('/admin/send-test', async (req, res) => {
    const adminKey = req.headers['x-admin-key'];
    if (adminKey !== process.env.ADMIN_KEY) {
        return res.status(403).json({ error: 'Unauthorized' });
    }
    
    const { email } = req.body;
    
    try {
        await sendTestEmail(email);
        res.json({ success: true, message: 'Test email sent' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ===== EMAIL TEMPLATES =====

function getNewsletterTemplate(updates, news) {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #32b8c6 0%, #1a6b78 100%); color: white; padding: 30px; border-radius: 8px; text-align: center; margin-bottom: 30px; }
            h1 { margin: 0; font-size: 28px; }
            .section { margin-bottom: 30px; }
            .section h2 { color: #32b8c6; font-size: 20px; border-bottom: 2px solid #32b8c6; padding-bottom: 10px; }
            .update-item { background: #f5f5f5; padding: 15px; border-left: 4px solid #32b8c6; margin: 10px 0; border-radius: 4px; }
            .update-item strong { color: #1a6b78; }
            .news-item { background: #fafafa; padding: 15px; border-left: 4px solid #f59e0b; margin: 10px 0; border-radius: 4px; }
            .news-item h3 { margin: 0 0 8px 0; font-size: 16px; }
            .news-item small { color: #666; }
            .footer { text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px; }
            .footer a { color: #32b8c6; text-decoration: none; }
            .cta-button { display: inline-block; background: #32b8c6; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI Tools Tracker</h1>
                <p>Weekly Update - ${new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
            </div>

            <div class="section">
                <h2>📊 This Week's Tool Updates</h2>
                ${updates && updates.length > 0 
                    ? updates.map(u => `
                        <div class="update-item">
                            <strong>${u.toolName}</strong><br>
                            ${u.change}
                        </div>
                    `).join('')
                    : '<p>No major updates this week.</p>'
                }
            </div>

            <div class="section">
                <h2>📰 AI News Roundup</h2>
                ${news && news.length > 0
                    ? news.slice(0, 5).map(n => `
                        <div class="news-item">
                            <h3>${n.title}</h3>
                            <p>${n.summary}</p>
                            <small>📌 ${n.source} • ${new Date(n.date).toLocaleDateString()}</small>
                        </div>
                    `).join('')
                    : '<p>No news this week.</p>'
                }
            </div>

            <div class="section" style="text-align: center;">
                <a href="https://ai-tracker.example.com" class="cta-button">View Full Tracker</a>
            </div>

            <div class="footer">
                <p>© 2025 AI Tools Tracker. All rights reserved.</p>
                <p>
                    <a href="https://ai-tracker.example.com">Website</a> • 
                    <a href="https://discord.gg/rMWTpNQVBD">Discord</a> • 
                    <a href="https://ai-tracker.example.com/unsubscribe?email={{email}}">Unsubscribe</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    `;
}

function getConfirmationTemplate(email) {
    return `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #32b8c6 0%, #1a6b78 100%); color: white; padding: 30px; border-radius: 8px; text-align: center; }
            .cta-button { display: inline-block; background: #32b8c6; color: white; padding: 12px 24px; border-radius: 4px; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to AI Tools Tracker! 🎉</h1>
            </div>
            <p>Hi there!</p>
            <p>Thanks for subscribing to our weekly AI tools newsletter. Confirm your subscription to start receiving updates:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://your-domain.com/api/confirm/${email}" class="cta-button">Confirm Email</a>
            </div>
            <p>If you didn't subscribe, you can ignore this email.</p>
        </div>
    </body>
    </html>
    `;
}

// ===== EMAIL SENDING =====

async function sendTestEmail(recipientEmail) {
    const updates = [
        { toolName: 'Claude 4.5', change: 'New vision capabilities released' },
        { toolName: 'GPT-5 Pro', change: 'Upgraded API rate limits' }
    ];
    
    const news = [
        { title: 'OpenAI releases new model', summary: 'Latest GPT update shows 30% improvement', source: 'TechCrunch', date: new Date() },
        { title: 'Anthropic announces partnership', summary: 'Claude integration with major platforms', source: 'The Verge', date: new Date() }
    ];

    await transporter.sendMail({
        from: process.env.EMAIL_USER,
        to: recipientEmail,
        subject: '🤖 AI Tools Tracker - Test Newsletter',
        html: getNewsletterTemplate(updates, news)
    });
}

async function sendWeeklyNewsletter(updates, news) {
    const subscribers = loadSubscribers().filter(s => s.active && s.confirmed);
    
    if (subscribers.length === 0) {
        console.log('⚠️ No confirmed subscribers');
        return;
    }
    
    console.log(`📧 Sending newsletter to ${subscribers.length} subscribers...`);
    
    for (const subscriber of subscribers) {
        try {
            const template = getNewsletterTemplate(updates, news);
            const html = template.replace('{{email}}', subscriber.email);
            
            await transporter.sendMail({
                from: process.env.EMAIL_USER,
                to: subscriber.email,
                subject: '🤖 AI Tools Tracker - Weekly Update',
                html: html
            });
            console.log(`✅ Sent to ${subscriber.email}`);
        } catch (error) {
            console.error(`❌ Failed to send to ${subscriber.email}:`, error.message);
        }
    }
}

// ===== CRON JOBS =====

// Every Monday at 9 AM
cron.schedule('0 9 * * 1', async () => {
    console.log('📅 Running weekly newsletter job...');
    
    // Fetch updates and news
    const updates = await getWeeklyUpdates();
    const news = await getAINews();
    
    await sendWeeklyNewsletter(updates, news);
});

async function getWeeklyUpdates() {
    // TODO: Compare JSON versions, get changelog
    return [
        { toolName: 'ChatGPT-5 Pro', change: 'New canvas features added' },
        { toolName: 'Claude 4.5', change: 'Vision API improvements' }
    ];
}

async function getAINews() {
    // TODO: Scrape AI news from RSS/API
    return [
        { 
            title: 'OpenAI releases GPT-5 preview', 
            summary: 'New model shows significant improvements in reasoning and code generation',
            source: 'OpenAI Blog',
            date: new Date()
        }
    ];
}

// ===== SERVER =====

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`✅ Newsletter server running on port ${PORT}`);
    console.log(`📧 Email: ${process.env.EMAIL_USER}`);
    console.log(`🔑 Admin endpoints: /admin/subscribers, /admin/send-test`);
});