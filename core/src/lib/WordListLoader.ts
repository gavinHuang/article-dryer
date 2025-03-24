import axios from 'axios';
import * as fs from 'fs/promises';
import * as path from 'path';
import { NlpManager } from 'node-nlp';
import { pipeline } from '@huggingface/transformers';

export interface WordLists {
  cefr: {
    a1: Set<string>;
    a2: Set<string>;
    b1: Set<string>;
    b2: Set<string>;
    c1: Set<string>;
    c2: Set<string>;
  };
}

export class WordListLoader {
  private static instance: WordListLoader;
  private static instancePromise: Promise<WordListLoader>;
  private wordLists: WordLists | null = null;
  private dataDir: string;
  private tokenizer: any;
  private nlpManager: NlpManager;
  private initialized: boolean = false;

  private constructor() {
    this.dataDir = path.join(__dirname, '../data');
    this.nlpManager = new NlpManager({ languages: ['en'] });
  }

  private async initialize() {
    if (this.initialized) return;
    console.log('Initializing NLP components...');
    await this.initNLP();
    console.log('Ensuring word list file exists...');
    await this.ensureWordListFile();
    this.initialized = true;
  }

  static async getInstance(): Promise<WordListLoader> {
    if (!WordListLoader.instancePromise) {
      WordListLoader.instancePromise = (async () => {
        const instance = new WordListLoader();
        await instance.initialize();
        return instance;
      })();
    }
    return WordListLoader.instancePromise;
  }

  private async initNLP() {
    try {
      console.log('Loading tokenizer...');
      this.tokenizer = await pipeline('token-classification', 'Xenova/bert-base-uncased');
      // NlpManager doesn't need async initialization
    } catch (error) {
      console.error('Error initializing NLP:', error);
      throw error;
    }
  }

  private async ensureWordListFile(): Promise<void> {
    const oxfordFilePath = path.join(this.dataDir, 'oxford-5000.json');
    try {
      await fs.access(oxfordFilePath);
    } catch {
      console.log('Downloading Oxford 5000 word list...');
      await this.downloadOxfordList();
    }
  }

  private async downloadOxfordList(): Promise<void> {
    const url = 'https://raw.githubusercontent.com/tyypgzl/Oxford-5000-words/refs/heads/main/full-word.json';
    const response = await axios.get(url);
    await fs.mkdir(this.dataDir, { recursive: true });
    await fs.writeFile(
      path.join(this.dataDir, 'oxford-5000.json'),
      JSON.stringify(response.data, null, 2)
    );
  }

  async loadWordLists(): Promise<WordLists> {
    if (this.wordLists) {
      return this.wordLists;
    }

    try {
      const cefrWords = await this.loadWordFile('oxford-5000.json');
      this.wordLists = {
        cefr: {
          a1: new Set(await this.processWords(cefrWords.a1)),
          a2: new Set(await this.processWords(cefrWords.a2)),
          b1: new Set(await this.processWords(cefrWords.b1)),
          b2: new Set(await this.processWords(cefrWords.b2)),
          c1: new Set(await this.processWords(cefrWords.c1)),
          c2: new Set(await this.processWords(cefrWords.c2))
        }
      };
      return this.wordLists;
    } catch (error) {
      console.error('Failed to load local word lists, attempting internet fetch:', error);
      try {
        const cefrWords = await this.fetchCEFR();
        this.wordLists = { cefr: cefrWords };
        await this.saveToCache(this.wordLists);
        return this.wordLists;
      } catch (fetchError) {
        console.error('Failed to fetch word lists from internet:', fetchError);
        return this.getFallbackLists();
      }
    }
  }

  private async loadWordFile(filename: string): Promise<any> {
    try {
      const filePath = path.join(this.dataDir, filename);
      const data = await fs.readFile(filePath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.error(`Failed to load ${filename}:`, error);
      throw error;
    }
  }

  private async saveToCache(lists: WordLists): Promise<void> {
    try {
      await fs.mkdir(this.dataDir, { recursive: true });
      await fs.writeFile(
        path.join(this.dataDir, 'oxford-5000.json'),
        JSON.stringify({
          a1: Array.from(lists.cefr.a1),
          a2: Array.from(lists.cefr.a2),
          b1: Array.from(lists.cefr.b1),
          b2: Array.from(lists.cefr.b2),
          c1: Array.from(lists.cefr.c1),
          c2: Array.from(lists.cefr.c2)
        }, null, 2)
      );
    } catch (error) {
      console.error('Failed to cache word lists:', error);
    }
  }

  private async fetchCEFR(): Promise<any> {
    const oxfordFilePath = path.join(this.dataDir, 'oxford-5000.json');
    const data = await fs.readFile(oxfordFilePath, 'utf8');
    const words = JSON.parse(data);
    
    const wordsByLevel: { [key: string]: Set<string> } = {
      a1: new Set(),
      a2: new Set(),
      b1: new Set(),
      b2: new Set(),
      c1: new Set(),
      c2: new Set()
    };

    for (const wordObj of words) {
      const level = wordObj.level.toLowerCase();
      if (level in wordsByLevel) {
        const processedWords = await this.processWords([wordObj.word]);
        processedWords.forEach(word => wordsByLevel[level].add(word));
      }
    }

    return wordsByLevel;
  }

  private async processWords(words: string[]): Promise<string[]> {
    const processed = new Set<string>();
    
    for (const word of words) {
      if (!word || typeof word !== 'string') continue;
      
      try {
        const tokens = await this.tokenizer(word, { skipSpecialTokens: true });
        // Use node-nlp's tokenizer and lemmatizer
        const tokenized = this.nlpManager.tokenizer.tokenize(word);
        const stemmed: string[] = tokenized.map((token: string) => 
          this.nlpManager.stemmer.stem(token.toLowerCase())
        );
        
        processed.add(stemmed[0]); // Add stemmed version
        processed.add(word.toLowerCase()); // Add original version
      } catch (error) {
        console.error(`Error processing word: ${word}`, error);
        processed.add(word.toLowerCase());
      }
    }

    return Array.from(processed);
  }

  private getFallbackLists(): WordLists {
    return {
      cefr: {
        a1: new Set(['hello', 'world']),
        a2: new Set(['simple', 'basic']),
        b1: new Set(['intermediate', 'progress']),
        b2: new Set(['advanced', 'complex']),
        c1: new Set(['proficient', 'master']),
        c2: new Set(['expert', 'fluent'])
      }
    };
  }
}