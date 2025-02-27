import { redis } from '@/lib/redis'
import { NextResponse, NextRequest } from 'next/server'
import type { Article } from '@/lib/redis'

export async function GET(request: NextRequest) {
  try {
    const url = request.nextUrl.searchParams.get('url');
    if (!url) {
      return NextResponse.json({ error: 'URL parameter is required' }, { status: 400 })
    }
    const article = await redis.get<Article>(url);
    return NextResponse.json(article|| null);
  } catch (error) {
    console.error('Failed to fetch articles:', error)
    return NextResponse.json({}, { status: 500 })
  }
}