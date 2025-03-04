import { Plugin, ContentData, OutputHandler } from '../types';
import { LLMClient } from '../lib/LLMClient';

export class SummarizerPlugin implements Plugin {
  name = 'summarizer';
  private llmClient: LLMClient;
  
  constructor(config: Record<string, any>) {
    if (!config.apiKey) {
      throw new Error('API key is required for SummarizerPlugin. Set OPENAI_API_KEY environment variable.');
    }
    try {
      this.llmClient = new LLMClient({
        apiKey: config.apiKey,
        model: config.model || 'gpt-4',
        baseURL: config.baseURL,
        maxTokens: config.maxTokens || 1000,
        stream: config.stream || true
      });
    } catch (error) {
      throw new Error(`Failed to initialize LLM client: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  async process(data: ContentData, outputHandler?: OutputHandler): Promise<ContentData> {
    const systemPrompt = `Understand the meaning of this paragraph, rewrite it into a shorter version with keywords. 
    Return with markdown format like this:
    # Shortened
    Shortened text...
    # Keywords
    - keyword1
    - keyword2`;

    try {
      if (outputHandler) {
        await outputHandler({
          type: 'text',
          content: 'Generating summary...\n'
        });
      }

      const summary = await this.llmClient.generateResponse(
        data.content,
        systemPrompt,
        async (chunk) => {
          if (outputHandler) {
            await outputHandler({
              type: 'text',
              content: chunk
            });
          }
        }
      );

      return {
        ...data,
        metadata: {
          ...data.metadata,
          summary,
          processedAt: new Date().toISOString()
        }
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      const isAuthError = errorMessage.toLowerCase().includes('unauthorized') || 
                         errorMessage.toLowerCase().includes('invalid api key');
      
      if (outputHandler) {
        await outputHandler({
          type: 'error',
          content: isAuthError 
            ? `Authentication failed: Please check your OpenAI API key (OPENAI_API_KEY)`
            : `Summarization failed: ${errorMessage}`
        });
      }
      throw error;
    }
  }
}