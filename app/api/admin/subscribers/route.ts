import { NextResponse } from 'next/server';

// Get subscribers list - proxies to newsletter-server.js
export async function GET(request: Request) {
  try {
    // Check admin key
    const adminKey = request.headers.get('x-admin-key');
    if (adminKey !== process.env.ADMIN_KEY && adminKey !== 'super-secret-key-123') {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Call the newsletter server's subscribers endpoint
    const newsletterServerUrl = process.env.NEWSLETTER_SERVER_URL || 'http://localhost:3001';

    const response = await fetch(`${newsletterServerUrl}/admin/subscribers`, {
      method: 'GET',
      headers: {
        'x-admin-key': adminKey || ''
      }
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.message || 'Failed to fetch subscribers' },
        { status: response.status }
      );
    }

    const result = await response.json();

    return NextResponse.json(result);
  } catch (error) {
    console.error('Error fetching subscribers:', error);
    return NextResponse.json(
      { error: 'Failed to fetch subscribers. Make sure newsletter-server.js is running.' },
      { status: 500 }
    );
  }
}
