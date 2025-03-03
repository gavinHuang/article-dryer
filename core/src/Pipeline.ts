import { Plugin, ContentData, PipelineConfig, OutputHandler } from './types';
import { PluginRegistry } from './PluginRegistry';
import { WebRequest, WebResponse, WebOutputAdapter, WebStreamHandler } from './lib/WebAdapter';

export class Pipeline {
  private plugins: Plugin[] = [];
  private outputHandler?: OutputHandler;
  private webAdapter?: WebOutputAdapter;

  constructor(plugins: Plugin[] = [], outputHandler?: OutputHandler) {
    this.plugins = plugins;
    this.outputHandler = outputHandler || this.defaultOutputHandler;
  }

  private defaultOutputHandler: OutputHandler = async (output) => {
    if (this.webAdapter) {
      await this.webAdapter.handleOutput(output);
    } else if (output.type === 'error') {
      console.error(output.content);
    } else {
      console.log(JSON.stringify(output.content, null, 2));
    }
  };

  static async fromConfig(configPath: string, outputHandler?: OutputHandler): Promise<Pipeline> {
    const config = await import(configPath) as PipelineConfig;
    return Pipeline.fromConfigObject(config, outputHandler);
  }

  static fromConfigObject(config: PipelineConfig, outputHandler?: OutputHandler): Pipeline {
    const registry = PluginRegistry.getInstance();
    const plugins = config.plugins.map(pluginConfig => {
      const mergedConfig = {
        ...config.globalOptions,
        ...pluginConfig.options
      };
      const plugin = registry.create(pluginConfig.name, mergedConfig);
      if (plugin.configure && pluginConfig.options) {
        plugin.configure(pluginConfig.options);
      }
      return plugin;
    });
    
    return new Pipeline(plugins, outputHandler);
  }

  addPlugin(plugin: Plugin): Pipeline {
    this.plugins.push(plugin);
    return this;
  }

  setOutputHandler(handler: OutputHandler): Pipeline {
    this.outputHandler = handler;
    return this;
  }

  bindToWeb(response: WebResponse, streamHandler?: WebStreamHandler): Pipeline {
    this.webAdapter = new WebOutputAdapter(response, streamHandler);
    return this;
  }

  async processWebRequest(request: WebRequest): Promise<void> {
    if (!this.webAdapter) {
      throw new Error('Pipeline not bound to web response');
    }

    try {
      const result = await this.process(
        typeof request.body === 'string' ? request.body : JSON.stringify(request.body)
      );

      // Final output
      await this.webAdapter.handleOutput(result);
      await this.webAdapter.complete();
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      await this.webAdapter.handleError(error);
    }
  }

  async process(content: string, initialMetadata: Record<string, any> = {}): Promise<ContentData> {
    let data: ContentData = {
      content,
      metadata: { ...initialMetadata }
    };

    for (const plugin of this.plugins) {
      try {
        data = await plugin.process(data, this.outputHandler);
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        if (this.outputHandler) {
          await this.outputHandler({
            type: 'error',
            content: `Error in plugin ${plugin.name}: ${error.message}`
          });
        }
        throw error;
      }
    }

    return data;
  }
}