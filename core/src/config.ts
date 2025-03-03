import { load } from 'js-yaml';
import { readFile } from 'fs/promises';
import { PipelineConfig } from './types';

export async function loadConfig(configPath: string): Promise<PipelineConfig> {
  const content = await readFile(configPath, 'utf8');
  return load(content) as PipelineConfig;
}