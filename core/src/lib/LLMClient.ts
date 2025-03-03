import OpenAI from 'openai';

export interface LLMConfig {
  apiKey: string;
  model: string;
  baseURL?: string;
  maxTokens?: number;
  stream?: boolean;
}

export type LLMOutputHandler = (chunk: string) => void | Promise<void>;

export class LLMClient {
  private config: LLMConfig;
  private client: OpenAI;

  constructor(config: LLMConfig) {
    // Remove any whitespace, quotes or newlines from API key
    const cleanApiKey = config.apiKey?.trim().replace(/["'\n]/g, '');
    
    this.config = {
      maxTokens: 1000,
      stream: false,
      ...config,
      apiKey: cleanApiKey
    };

    if (!this.config.apiKey?.trim() || !this.config.apiKey.startsWith('sk-')) {
      throw new Error('Invalid API key format. OpenAI API keys should start with "sk-"');
    }

    this.client = new OpenAI({
      apiKey: this.config.apiKey,
    //   baseURL: this.config.baseURL
    });
    console.log("apikey:", this.config.apiKey);
  }

  async generateResponse(
    content: string, 
    systemPrompt: string = "You are a helpful assistant that summarizes text concisely.",
    outputHandler?: LLMOutputHandler
  ): Promise<string> {
    try {
      const params: OpenAI.Chat.ChatCompletionCreateParams = {
        model: this.config.model,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content }
        ],
        max_tokens: this.config.maxTokens,
        stream: this.config.stream
      };

      if (this.config.stream) {
        const streamResponse = await this.client.chat.completions.create({
          ...params,
          stream: true
        });

        let fullResponse = '';
        for await (const chunk of streamResponse) {
          const content = chunk.choices[0]?.delta?.content || '';
          if (content && outputHandler) {
            await outputHandler(content);
          }
          fullResponse += content;
        }
        
        return fullResponse;
      } else {
        const completion = await this.client.chat.completions.create({
          ...params,
          stream: false
        });
        return completion.choices[0]?.message?.content || '';
      }
    } catch (error) {
      if (error instanceof OpenAI.APIError) {
        if (error.status === 401) {
          throw new Error('Authentication failed: Invalid API key');
        } else if (error.status === 429) {
          throw new Error('Rate limit exceeded: Too many requests');
        } else if (error.status === 404) {
          throw new Error(`Model '${this.config.model}' not found`);
        }
        throw new Error(`API Error: ${error.message}`);
      }

      // Handle network or other errors
      if (error instanceof Error && error.message.includes('ENOTFOUND')) {
        throw new Error(`Network error: Unable to connect to LLM API. Check your internet connection and API endpoint (${this.config.baseURL || 'default OpenAI endpoint'})`);
      }
      throw error;
    }
  }
}