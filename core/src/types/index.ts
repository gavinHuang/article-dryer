export interface ContentData {
  content: string;
  metadata: Record<string, any>;
  [key: string]: any;
}

export interface PluginOutput {
  type: 'text' | 'json' | 'error';
  content: any;
}

export type OutputHandler = (output: PluginOutput) => void | Promise<void>;

export interface Plugin {
  name: string;
  process(data: ContentData, outputHandler?: OutputHandler): Promise<ContentData>;
  configure?(options: Record<string, any>): void;
}

export interface PipelineConfig {
  plugins: Array<{
    name: string;
    options?: Record<string, any>;
  }>;
  globalOptions?: Record<string, any>;
}