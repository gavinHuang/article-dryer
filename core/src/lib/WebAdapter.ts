export interface WebRequest {
  body: any;
  headers: Record<string, string>;
  method: string;
}

export interface WebResponse {
  write(data: string): void;
  end(data?: string): void;
  setHeader(name: string, value: string): void;
  status(code: number): WebResponse;
}

export interface WebStreamHandler {
  onChunk(chunk: string): Promise<void>;
  onComplete?(): Promise<void>;
  onError?(error: Error): Promise<void>;
}

export class WebOutputAdapter {
  private response: WebResponse;
  private streamHandler?: WebStreamHandler;

  constructor(response: WebResponse, streamHandler?: WebStreamHandler) {
    this.response = response;
    this.streamHandler = streamHandler;
  }

  async handleOutput(output: any): Promise<void> {
    if (this.streamHandler) {
      if (typeof output === 'string') {
        await this.streamHandler.onChunk(output);
      } else {
        await this.streamHandler.onChunk(JSON.stringify(output) + '\n');
      }
    } else {
      if (typeof output === 'string') {
        this.response.write(output);
      } else {
        this.response.write(JSON.stringify(output) + '\n');
      }
    }
  }

  async handleError(error: Error): Promise<void> {
    if (this.streamHandler?.onError) {
      await this.streamHandler.onError(error);
    } else {
      const errorResponse = JSON.stringify({ error: error.message });
      this.response.status(500);
      this.response.end(errorResponse);
    }
  }

  async complete(): Promise<void> {
    if (this.streamHandler?.onComplete) {
      await this.streamHandler.onComplete();
    } else {
      this.response.end();
    }
  }
}