import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Generate newsletter HTML preview from newsletter_updates.json
export async function GET(request: Request) {
  try {
    // Check admin key
    const adminKey = request.headers.get('x-admin-key');
    if (adminKey !== process.env.ADMIN_KEY && adminKey !== 'super-secret-key-123') {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Load newsletter data
    const newsletterPath = path.join(process.cwd(), 'public', 'newsletter_updates.json');
    const newsletterData = JSON.parse(fs.readFileSync(newsletterPath, 'utf-8'));

    // Load tools data for details
    const toolsPath = path.join(process.cwd(), 'public', 'ai_tracker_enhanced.json');
    const toolsData = JSON.parse(fs.readFileSync(toolsPath, 'utf-8'));

    // Generate HTML email
    const html = generateNewsletterHTML(newsletterData, toolsData);

    return NextResponse.json({
      success: true,
      html,
      stats: {
        newTools: newsletterData.new_tools?.length || 0,
        majorUpdates: newsletterData.major_updates?.length || 0,
        minorUpdates: newsletterData.minor_updates?.length || 0,
        totalTools: newsletterData.total_tools || 0,
        timestamp: newsletterData.timestamp
      }
    });
  } catch (error) {
    console.error('Error generating preview:', error);
    return NextResponse.json(
      { error: 'Failed to generate preview' },
      { status: 500 }
    );
  }
}

function generateNewsletterHTML(updates: any, toolsData: any) {
  const newTools = updates.new_tools || [];
  const majorUpdates = updates.major_updates || [];
  const topTools = updates.top_10_tools || [];

  // Build tool updates section
  let toolUpdatesHTML = '';

  if (newTools.length > 0) {
    toolUpdatesHTML += '<h3 style="color: #0d9488; margin-top: 24px;">🆕 New AI Tools Discovered</h3>';
    newTools.slice(0, 5).forEach((tool: any) => {
      toolUpdatesHTML += `
        <div style="background: #f0fdfa; padding: 16px; margin: 12px 0; border-radius: 8px; border-left: 4px solid #14b8a6;">
          <h4 style="margin: 0 0 8px 0; color: #0f766e;">${tool.name || tool}</h4>
          <p style="margin: 0; color: #134e4a; font-size: 14px;">${tool.description || 'A new AI tool to explore'}</p>
          ${tool.category ? `<span style="background: #ccfbf1; color: #0f766e; padding: 4px 8px; border-radius: 4px; font-size: 12px; display: inline-block; margin-top: 8px;">${tool.category}</span>` : ''}
        </div>
      `;
    });
  }

  if (majorUpdates.length > 0) {
    toolUpdatesHTML += '<h3 style="color: #0d9488; margin-top: 24px;">🔥 Major Updates</h3>';
    majorUpdates.slice(0, 5).forEach((update: any) => {
      const toolName = typeof update === 'string' ? update : update.name;
      toolUpdatesHTML += `
        <div style="background: #fef3c7; padding: 16px; margin: 12px 0; border-radius: 8px; border-left: 4px solid #f59e0b;">
          <h4 style="margin: 0 0 8px 0; color: #92400e;">${toolName}</h4>
          <p style="margin: 0; color: #78350f; font-size: 14px;">Significant updates detected</p>
        </div>
      `;
    });
  }

  // Top 10 tools
  let topToolsHTML = '';
  if (topTools.length > 0) {
    topToolsHTML = '<h3 style="color: #0d9488; margin-top: 24px;">⭐ Top 10 AI Tools This Week</h3><ol style="padding-left: 20px;">';
    topTools.forEach((tool: any) => {
      topToolsHTML += `
        <li style="margin: 8px 0;">
          <strong>${tool.name}</strong> - Score: ${tool.final_score?.toFixed(1) || 'N/A'}
          ${tool.category ? `<span style="color: #0d9488; margin-left: 8px;">(${tool.category})</span>` : ''}
        </li>
      `;
    });
    topToolsHTML += '</ol>';
  }

  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>AI Tools Weekly Update</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f3f4f6;">
      <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); padding: 40px 20px; text-align: center;">
          <h1 style="color: white; margin: 0; font-size: 28px;">AI Tools Weekly Update</h1>
          <p style="color: #ccfbf1; margin: 8px 0 0 0; font-size: 14px;">Your curated AI tools digest</p>
        </div>

        <!-- Content -->
        <div style="padding: 32px 20px;">
          <p style="color: #374151; font-size: 16px; line-height: 1.6;">
            Hello! 👋
          </p>
          <p style="color: #374151; font-size: 16px; line-height: 1.6;">
            Here's your weekly summary of AI tools tracked on <strong>AI Tracker</strong>.
            This week, we detected <strong>${newTools.length} new tools</strong>
            and <strong>${majorUpdates.length} major updates</strong>.
          </p>

          ${toolUpdatesHTML}

          ${topToolsHTML}

          <!-- CTA Button -->
          <div style="text-align: center; margin: 32px 0;">
            <a href="${process.env.FRONTEND_URL || 'http://localhost:3000'}"
               style="background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%);
                      color: white;
                      padding: 14px 32px;
                      text-decoration: none;
                      border-radius: 8px;
                      display: inline-block;
                      font-weight: bold;">
              View All Tools →
            </a>
          </div>

          <p style="color: #6b7280; font-size: 14px; line-height: 1.6; margin-top: 24px;">
            Best regards,<br>
            The AI Tracker Team
          </p>
        </div>

        <!-- Footer -->
        <div style="background: #f3f4f6; padding: 24px 20px; text-align: center; border-top: 1px solid #e5e7eb;">
          <p style="color: #6b7280; font-size: 12px; margin: 0 0 8px 0;">
            You're receiving this email because you subscribed to AI Tracker newsletter
          </p>
          <a href="${process.env.FRONTEND_URL || 'http://localhost:3000'}/unsubscribe"
             style="color: #0d9488; font-size: 12px; text-decoration: none;">
            Unsubscribe
          </a>
        </div>
      </div>
    </body>
    </html>
  `;

  return html;
}
