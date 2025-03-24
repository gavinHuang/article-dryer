import { WordListLoader } from '../src/lib/WordListLoader';

async function testWordList() {
    try {
        console.log('Initializing WordListLoader...');
        const loader = await WordListLoader.getInstance();
        
        console.log('Loading word lists...');
        const wordLists = await loader.loadWordLists();
        
        // Print statistics for each CEFR level
        Object.entries(wordLists.cefr).forEach(([level, words]) => {
            console.log(`\nCEFR ${level.toUpperCase()} Statistics:`);
            console.log(`Total words: ${words.size}`);
            console.log('Sample words:', Array.from(words).slice(0, 5));
        });

    } catch (error) {
        console.error('Error testing word lists:', error);
        if (error instanceof Error && error.stack) {
            console.error('Stack trace:', error.stack);
        }
    }
}

// Run the test
console.log('Starting WordListLoader test...');
testWordList()
    .then(() => console.log('Test completed.'))
    .catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
