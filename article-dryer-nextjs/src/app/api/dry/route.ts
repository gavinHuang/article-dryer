import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { text } = await request.json();
    
    // Return streaming response
    return new NextResponse(JSON.stringify({ result: text }), {
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch {  // Remove the unused error parameter
    return new NextResponse('Error processing request', { 
      status: 500,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}