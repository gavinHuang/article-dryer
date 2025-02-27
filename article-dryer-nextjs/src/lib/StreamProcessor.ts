export interface Paragraph {
    original:string,
    shortened: string;
    keywords: string[];
  }
  
export class StreamProcessor {
    private buffer: string;
    private parsedRecords: Paragraph[];
    // private originalToShortened: Map<string, string>;

    constructor() {
      this.buffer = "";
      this.parsedRecords = [];
    //   this.originalToShortened = new Map();
    }
  
    processChunk(original:string, chunk:string) {
      this.buffer += chunk;
      const record = this.getRecordForOriginal(original);
      if (!record){
        const record: Paragraph = {original: original, shortened: "", keywords: []};
        this.parsedRecords.push(record);
      }
      this.parseRecords(original);
      return this.parsedRecords;
    }
    
    parseRecords(original:string) {
      const recordStrings = this.buffer.split(/\n\n+/);
      const potentiallyIncompleteRecord = recordStrings.pop();
      this.buffer = potentiallyIncompleteRecord ?? "";
      for (const recordString of recordStrings) {
        const record = this.parseRecord(recordString);
        if (record) {
          const existingRecord = this.getRecordForOriginal(original);
          if (existingRecord) {
            existingRecord.shortened = record.shortened;
            existingRecord.keywords = record.keywords;
          } else {
            record.original = original;
            this.parsedRecords.push(record);
          }
        }
      }
    }

    parseRecord(recordString:string) {
      const record: Paragraph = {original: "", shortened: "", keywords: []};
      
      const shortenedMatch = recordString.match(/# Shortened\s+([\s\S]+?)(?=\s+#|$)/);
      if (shortenedMatch) {
        record.shortened = shortenedMatch[1].trim();
      }
      
      const keywordsMatch = recordString.match(/# Keywords\s+([\s\S]+?)(?=\s+#|$)/);
      if (keywordsMatch) {
        record.keywords = keywordsMatch[1]
          .split('\n')
          .filter(line => line.trim().startsWith('-'))
          .map(line => line.replace('-', '').trim());
      }
      
      return record;
    }
    
    // getOriginalForShortened(shortened:string) {
    //   for (const [original, mappedShortened] of this.originalToShortened.entries()) {
    //     if (mappedShortened === shortened) {
    //       return original;
    //     }
    //   }
    //   return null;
    // }

    // This method is used to find the record for a given original text
    getRecordForOriginal(original:string) {
      for (const record of this.parsedRecords) {
        if (record.original === original) {
          return record;
        }
      }
      return null;
    }
  }