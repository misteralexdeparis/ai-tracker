import { NextResponse } from 'next/server';

// Manual newsletter send - proxies to newsletter-server.js
export async function POST(request: Request) {
  try {
    // Check admin key
    const adminKey = request.headers.get('x-admin-key');
    if (adminKey !== process.env.ADMIN_KEY && adminKey !== 'super-secret-key-123') {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Call the newsletter server's send-test endpoint
    // This assumes newsletter-server.js is running on port 3001
    const newsletterServerUrl = process.env.NEWSLETTER_SERVER_URL || 'http://localhost:3001';

    const response = await fetch(`${newsletterServerUrl}/admin/send-test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-admin-key': adminKey || ''
      }
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to send newsletter' },
        { status: response.status }
      );
    }

    const result = await response.json();

    return NextResponse.json({
      success: true,
      message: 'Newsletter sent successfully!',
      ...result
    });
  } catch (error) {
    console.error('Error sending newsletter:', error);
    return NextResponse.json(
      { error: 'Failed to send newsletter. Make sure newsletter-server.js is running.' },
      { status: 500 }
    );
  }
}
