import { redis } from '@/lib/redis'
import { NextResponse } from 'next/server'
import type { Article } from '@/lib/redis'

export async function GET(url: string) {
  try {
    const article = await redis.get<Article>(url)
    return NextResponse.json(article)
  } catch (error) {
    console.error('Failed to fetch articles:', error)
    return NextResponse.json({}, { status: 500 })
  }
}