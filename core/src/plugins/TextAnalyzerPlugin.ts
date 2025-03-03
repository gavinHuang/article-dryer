import { Plugin, ContentData, OutputHandler } from '../types';

export class TextAnalyzerPlugin implements Plugin {
  name = 'text-analyzer';
  private wordCountThreshold: number = 100;

  configure(options: Record<string, any>): void {
    if (options.wordCountThreshold) {
      this.wordCountThreshold = options.wordCountThreshold;
    }
  }

  async process(data: ContentData, outputHandler?: OutputHandler): Promise<ContentData> {
    const { content } = data;
    const wordCount = content.split(/\s+/).length;
    const sentenceCount = content.split(/[.!?]+/).length;
    
    // Stream analysis progress
    if (outputHandler) {
      await outputHandler({
        type: 'text',
        content: `Analyzing text: ${wordCount} words, ${sentenceCount} sentences`
      });

      // Stream intermediate results
      if (wordCount > this.wordCountThreshold) {
        await outputHandler({
          type: 'json',
          content: {
            alert: 'Text length exceeds threshold',
            wordCount,
            threshold: this.wordCountThreshold
          }
        });
      }
    }
    
    return {
      ...data,
      metadata: {
        ...data.metadata,
        wordCount,
        sentenceCount,
        isLongText: wordCount > this.wordCountThreshold,
      },
    };
  }
}