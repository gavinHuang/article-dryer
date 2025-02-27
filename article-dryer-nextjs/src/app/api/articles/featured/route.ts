import { redis } from '@/lib/redis'
import { NextResponse } from 'next/server'
import type { FeaturedArticle } from '@/lib/redis'

export async function GET() {
  try {
    const articles = await redis.get<FeaturedArticle[]>('featured-articles')
    return NextResponse.json(articles || [])
  } catch (error) {
    console.error('Failed to fetch featured articles:', error)
    return NextResponse.json([], { status: 500 })
  }
}

// export async function POST(request: Request) {
//   try {
//     const article = await request.json()
//     const articles = await redis.get<FeaturedArticle[]>('featured-articles') || []
//     articles.push(article)
//     await redis.set('featured-articles', articles)
//     return NextResponse.json({ success: true })
//   } catch (error) {
//     console.error('Failed to add featured article:', error)
//     return NextResponse.json({ success: false }, { status: 500 })
//   }
// }