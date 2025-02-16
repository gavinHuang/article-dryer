export interface Summary {
    keyPoints: string[];
    limitations: string[];
  }
  
  export interface ArticleDryerState {
    article: string;
    summary: Summary | null;
    isProcessing: boolean;
    isCopied: boolean;
  }