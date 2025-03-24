declare module 'node-nlp' {
  export class NlpManager {
    constructor(options: { languages: string[] });
    tokenizer: {
      tokenize(text: string): string[];
    };
    stemmer: {
      stem(word: string): string;
    };
  }
}
