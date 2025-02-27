import { Redis } from '@upstash/redis'

export interface FeaturedArticle {
  title: string;
  url: string;
  source: string;
}

export interface Article {
    title: string;
    url: string;
    source: string;
    content:[{
        shortend: string;
        original: string;
        keywords: string[];
    }]
}

// This file only runs on the server
const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
})

export { redis }