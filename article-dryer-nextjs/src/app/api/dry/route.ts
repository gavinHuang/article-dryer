import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { text } = await request.json();
    
    const response = await fetch(`${process.env.DRY_SERVER_URL}/dry`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    return new NextResponse(response.body, {
      headers: response.headers
    });
  } catch {
    return new NextResponse('Error processing request', { status: 500 });
  }
}