'use client';

import { ArticleSummarizer } from '@/components/ArticleSummarizer';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <ArticleSummarizer />
    </main>
  );
}