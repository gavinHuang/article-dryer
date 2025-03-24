import { Plugin, ContentData, OutputHandler } from '../types';
import { WordListLoader } from '../lib/WordListLoader';

interface VocabularyProfile {
  ngsl: number;    // New General Service List words (basic)
  awl: number;     // Academic Word List words (academic)
  technical: number;  // Technical/specialized vocabulary
  other: number;   // Other words
}

export class TextStatisticsPlugin implements Plugin {
  name = 'text-statistics';
  private averageWPM: number = 250; // Average adult reading speed
  private wordListLoader: WordListLoader;
  
  // Technical patterns (common suffixes and patterns for technical terms)
  private technicalPatterns = [
    /[a-z]+ology\b/i,    // Words ending in "ology"
    /[a-z]+ization\b/i,  // Words ending in "ization"
    /[a-z]+icism\b/i,    // Words ending in "icism"
    /[a-z]+istic\b/i,    // Words ending in "istic"
    /[a-z]+esis\b/i,     // Words ending in "esis"
    /[a-z]+itis\b/i,     // Words ending in "itis"
    /[a-z]+omy\b/i,      // Words ending in "omy"
    /\b[a-z]+lyze\b/i,   // Words ending in "lyze"
    /\b[a-z]{3,}[^aeiou]{2}[a-z]{2,}\b/i  // Words with consonant clusters
  ];

  constructor() {
    this.wordListLoader = WordListLoader.getInstance();
  }

  configure(options: Record<string, any>): void {
    if (options.averageWPM) {
      this.averageWPM = options.averageWPM;
    }
  }

  async process(data: ContentData, outputHandler?: OutputHandler): Promise<ContentData> {
    const { content } = data;
    
    // Basic statistics
    const words = content.split(/\s+/)
      .filter(word => word.length > 0)
      .map(word => word.toLowerCase().replace(/[^a-z'-]/g, ''));
    
    const wordCount = words.length;
    const paragraphCount = content.split(/\n\n+/).filter(p => p.trim().length > 0).length;
    const sentenceCount = content.split(/[.!?]+\s/).filter(s => s.trim().length > 0).length;
    
    // Calculate reading time
    const readingTimeMinutes = Math.ceil(wordCount / this.averageWPM);
    
    // Analyze vocabulary levels
    const vocabProfile = await this.analyzeVocabularyProfile(words);
    
    // Calculate Gunning Fog Index (readability)
    const complexWords = words.filter(word => this.isComplexWord(word)).length;
    const gunningFog = 0.4 * ((wordCount / sentenceCount) + 100 * (complexWords / wordCount));
    
    // Calculate average word length
    const avgWordLength = words.reduce((sum, word) => sum + word.length, 0) / wordCount;

    const statistics = {
      wordCount,
      paragraphCount,
      sentenceCount,
      readingTimeMinutes,
      averageWordLength: avgWordLength.toFixed(1),
      wordsPerSentence: (wordCount / sentenceCount).toFixed(1),
      readabilityScore: gunningFog.toFixed(1),
      vocabularyProfile: {
        basic: {
          count: vocabProfile.ngsl,
          percentage: ((vocabProfile.ngsl / wordCount) * 100).toFixed(1)
        },
        academic: {
          count: vocabProfile.awl,
          percentage: ((vocabProfile.awl / wordCount) * 100).toFixed(1)
        },
        technical: {
          count: vocabProfile.technical,
          percentage: ((vocabProfile.technical / wordCount) * 100).toFixed(1)
        },
        other: {
          count: vocabProfile.other,
          percentage: ((vocabProfile.other / wordCount) * 100).toFixed(1)
        }
      }
    };

    // Stream analysis results
    if (outputHandler) {
      await outputHandler({
        type: 'json',
        content: {
          statistics,
          message: `Analysis complete: ${wordCount} words, Reading level: ${statistics.readabilityScore} (Gunning Fog Index)`
        }
      });
    }
    
    return {
      ...data,
      metadata: {
        ...data.metadata,
        textStatistics: statistics
      },
    };
  }

  private async analyzeVocabularyProfile(words: string[]): Promise<VocabularyProfile> {
    const wordLists = await this.wordListLoader.loadWordLists();
    
    const profile: VocabularyProfile = {
      ngsl: 0,
      awl: 0,
      technical: 0,
      other: 0
    };

    for (const word of words) {
      if (wordLists.ngsl.has(word)) {
        profile.ngsl++;
      } else if (wordLists.awl.has(word)) {
        profile.awl++;
      } else if (this.isTechnicalWord(word)) {
        profile.technical++;
      } else {
        profile.other++;
      }
    }

    return profile;
  }

  private isTechnicalWord(word: string): boolean {
    return this.technicalPatterns.some(pattern => pattern.test(word));
  }

  private isComplexWord(word: string): boolean {
    // Complex words are those with 3 or more syllables
    const syllables = this.countSyllables(word);
    return syllables >= 3;
  }

  private countSyllables(word: string): number {
    word = word.toLowerCase();
    if (word.length <= 3) return 1;
    
    // Remove common word endings
    word = word.replace(/(?:[^laeiouy]es|ed|[^laeiouy]e)$/, '');
    word = word.replace(/^y/, '');
    
    // Count vowel groups
    return (word.match(/[aeiouy]{1,2}/g) || []).length;
  }
}