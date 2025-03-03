import { Plugin, ContentData, OutputHandler } from '../types';

export class JinaReaderPlugin implements Plugin {
  name = 'jina-reader';
  private skipImages: boolean = true;

  constructor(config: Record<string, any> = {}) {
    if (typeof config.skipImages === 'boolean') {
      this.skipImages = config.skipImages;
    }
  }

  configure(options: Record<string, any>): void {
    if (typeof options.skipImages === 'boolean') {
      this.skipImages = options.skipImages;
    }
  }

  async process(data: ContentData, outputHandler?: OutputHandler): Promise<ContentData> {
    try {
      // Validate URL
      const url = this.extractUrl(data.content);
      if (!url) {
        throw new Error('No valid URL found in input');
      }

      if (outputHandler) {
        await outputHandler({
          type: 'text',
          content: `Fetching content from ${url}...`
        });
      }

      const response = await fetch(`https://r.jina.ai/${url}`, {
        headers: {
          'Accept': 'text/plain'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch content: ${response.statusText}`);
      }

      const text = await response.text();
      const paragraphs = text.split('\n\n')
        .splice(3) // Skip initial metadata
        .filter((p: string) => !this.skipImages || !p.trim().startsWith('![Image'));

      if (outputHandler) {
        await outputHandler({
          type: 'json',
          content: {
            status: 'success',
            paragraphCount: paragraphs.length
          }
        });
      }

      return {
        ...data,
        content: paragraphs.join('\n\n'),
        metadata: {
          ...data.metadata,
          sourceUrl: url,
          originalParagraphCount: paragraphs.length,
          fetchedAt: new Date().toISOString()
        }
      };
    } catch (error) {
      if (outputHandler) {
        await outputHandler({
          type: 'error',
          content: `Failed to fetch markdown: ${error instanceof Error ? error.message : String(error)}`
        });
      }
      throw error;
    }
  }

  private extractUrl(input: string): string | null {
    // If input is already a URL, return it
    try {
      const url = new URL(input.trim());
      if (['http:', 'https:'].includes(url.protocol)) {
        return url.toString();
      }
    } catch {
      // Not a valid URL, continue with extraction
    }

    // Try to extract URL from text
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const matches = input.match(urlRegex);
    return matches ? matches[0] : null;
  }
}