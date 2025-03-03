import { Plugin } from './types';

type PluginConstructor = new (config: Record<string, any>) => Plugin;
type PluginFactory = () => Plugin;

interface PluginRegistration {
  type: 'constructor' | 'factory';
  value: PluginConstructor | PluginFactory;
}

export class PluginRegistry {
  private static instance: PluginRegistry;
  private plugins: Map<string, PluginRegistration> = new Map();

  private constructor() {}

  static getInstance(): PluginRegistry {
    if (!PluginRegistry.instance) {
      PluginRegistry.instance = new PluginRegistry();
    }
    return PluginRegistry.instance;
  }

  register(name: string, plugin: PluginConstructor | PluginFactory): void {
    if (this.plugins.has(name)) {
      throw new Error(`Plugin with name ${name} is already registered`);
    }

    const type = this.isConstructor(plugin) ? 'constructor' : 'factory';
    this.plugins.set(name, { type, value: plugin });
  }

  private isConstructor(plugin: PluginConstructor | PluginFactory): plugin is PluginConstructor {
    return 'prototype' in plugin;
  }

  create(name: string, config?: Record<string, any>): Plugin {
    const registration = this.plugins.get(name);
    if (!registration) {
      throw new Error(`Plugin ${name} not found in registry`);
    }
    
    try {
      if (registration.type === 'constructor') {
        const Constructor = registration.value as PluginConstructor;
        return new Constructor(config || {});
      } else {
        const factory = registration.value as PluginFactory;
        return factory();
      }
    } catch (error) {
      throw new Error(`Failed to create plugin ${name}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  getAvailablePlugins(): string[] {
    return Array.from(this.plugins.keys());
  }
}