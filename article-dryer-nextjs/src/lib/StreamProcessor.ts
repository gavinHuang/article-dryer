export interface Paragraph {
    original:string,
    shortened: string;
    keywords: string[];
  }

  const debug = true;
export class StreamProcessor {
    private buffer: string;
    public parsedRecords: Paragraph[];
    // private originalToShortened: Map<string, string>;

    constructor() {
      this.buffer = "";
      this.parsedRecords = [];
    //   this.originalToShortened = new Map();
    }
  
    processChunk(original:string, chunk:string) {
      const l1 = this.parsedRecords.length;
      const l2 = l1 > 0 ? this.parsedRecords[l1 - 1].shortened.length : 0;
      const l3 = l1 > 0 ? this.parsedRecords[l1 - 1].keywords.length : 0;

      if (chunk.startsWith("#")) {
        this.buffer += "\n\n" + chunk;
      }else {
        this.buffer += chunk;
      }
      const record = this.getRecordForOriginal(original);
      if (!record){
        const record: Paragraph = {original: original, shortened: "", keywords: []};
        this.parsedRecords.push(record);
      }
      this.parseRecords(original);

      const l11 = this.parsedRecords.length;
      const l12 = l11 > 0 ? this.parsedRecords[l11 - 1].shortened.length : 0;
      const l13 = l11 > 0 ? this.parsedRecords[l11 - 1].keywords.length : 0;
      let changed = false;
      if ( chunk.trim().length > 0 && (l2 != l12 || l3 != l13 )) {
        if (debug) console.log("processChunk: ",chunk.trim());
        changed = true;
      }

      return changed;
    }
    
    parseRecords(original:string) {
      const recordStrings = this.buffer.split(/\n\n+/).filter(s => s.trim().length > 0);
      // const potentiallyIncompleteRecord = recordStrings.pop();
      // if (potentiallyIncompleteRecord?.startsWith("#") || potentiallyIncompleteRecord?.trim()?.startsWith("-")){
      //   this.buffer = potentiallyIncompleteRecord ?? "";
      // }else{
      //   recordStrings.push(potentiallyIncompleteRecord ?? "");
      //   this.buffer = "";
      // }
      
      for (const recordString of recordStrings) {
        const record = this.parseRecord(recordString);
        if (record && (record.shortened || record.keywords.length > 0)) {
          const existingRecord = this.getRecordForOriginal(original);
          if (existingRecord) {
            if (record.shortened) existingRecord.shortened = record.shortened;
            if (record.keywords && record.keywords.length > 0) existingRecord.keywords = record.keywords;
            // if (debug && existingRecord.keywords.length > 0 && existingRecord.shortened.trim().length > 0 && existingRecord.original.trim().length > 0) {
            //   console.log("-full record parsed: ", JSON.stringify(existingRecord));
            // }
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
      // if (debug) {
      //   console.log("parseRecord: ",recordString);
      //   console.log("record: ",record);
      // }
      
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