export * from './types';
export * from './Pipeline';
export * from './PluginRegistry';
export * from './plugins/TextAnalyzerPlugin';
export * from './plugins/SummarizerPlugin';
export * from './plugins/JinaReaderPlugin';
export * from './lib/LLMClient';
export * from './lib/WebAdapter';

// Initialize and export a default registry instance
import { PluginRegistry } from './PluginRegistry';
import { TextAnalyzerPlugin } from './plugins/TextAnalyzerPlugin';
import { SummarizerPlugin } from './plugins/SummarizerPlugin';
import { JinaReaderPlugin } from './plugins/JinaReaderPlugin';

// Register built-in plugins
const registry = PluginRegistry.getInstance();
registry.register('text-analyzer', TextAnalyzerPlugin);
registry.register('summarizer', SummarizerPlugin);
registry.register('jina-reader', JinaReaderPlugin);

export { registry as defaultRegistry };