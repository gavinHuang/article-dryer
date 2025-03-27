import re
import logging
from typing import List, Dict, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordProcessor:
    """
    A class for normalizing words including:
    - Inflected Forms (plurals, verb tenses, comparatives/superlatives)
    - Contractions (e.g., "don't" -> "do not")
    - Compound and Hyphenated Words (e.g., "self-driving" -> "self driving")
    - Abbreviations & Acronyms (e.g., "Dr." -> "doctor")
    - Possessives (e.g., "teacher's" -> "teacher")
    - Slang and Informal Language (e.g., "lemme" -> "let me")
    """
    
    def __init__(self):
        """Initialize the WordProcessor with necessary tools"""
        self.contractions_map = self._create_contractions_map()
        self.abbreviations_map = self._create_abbreviations_map()
        self.slang_map = self._create_slang_map()
        self.inflection_rules = self._create_inflection_rules()
        
    def _create_contractions_map(self) -> Dict[str, str]:
        """Create a map of English contractions to their expanded forms"""
        return {
            # Common contractions
            "aren't": "are not",
            "can't": "cannot",
            "couldn't": "could not",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he would",
            "he'll": "he will",
            "he's": "he is",
            "i'd": "i would",
            "i'll": "i will",
            "i'm": "i am",
            "i've": "i have",
            "isn't": "is not",
            "it's": "it is",
            "let's": "let us",
            "mightn't": "might not",
            "mustn't": "must not",
            "shan't": "shall not",
            "she'd": "she would",
            "she'll": "she will",
            "she's": "she is",
            "shouldn't": "should not",
            "that's": "that is",
            "there's": "there is",
            "they'd": "they would",
            "they'll": "they will",
            "they're": "they are",
            "they've": "they have",
            "we'd": "we would",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what'll": "what will",
            "what're": "what are",
            "what's": "what is",
            "what've": "what have",
            "where's": "where is",
            "who'd": "who would",
            "who'll": "who will",
            "who're": "who are",
            "who's": "who is",
            "who've": "who have",
            "won't": "will not",
            "wouldn't": "would not",
            "you'd": "you would",
            "you'll": "you will",
            "you're": "you are",
            "you've": "you have",
            # Additional contractions
            "ain't": "am not",
            "could've": "could have",
            "gonna": "going to",
            "gotta": "got to",
            "i'ma": "i am going to",
            "might've": "might have",
            "must've": "must have",
            "should've": "should have",
            "that'd": "that would",
            "that'll": "that will",
            "there'd": "there would",
            "there'll": "there will",
            "they'd've": "they would have",
            "we'd've": "we would have",
            "would've": "would have",
            "y'all": "you all",
            "y'all'd": "you all would",
            "y'all'd've": "you all would have",
        }
        
    def _create_abbreviations_map(self) -> Dict[str, str]:
        """Create a map of common abbreviations to their expanded forms"""
        return {
            # Titles
            "dr.": "doctor",
            "mr.": "mister",
            "mrs.": "missus",
            "ms.": "miss",
            "prof.": "professor",
            "rev.": "reverend",
            "col.": "colonel",
            "gen.": "general",
            "lt.": "lieutenant",
            "sgt.": "sergeant",
            "capt.": "captain",
            "cmdr.": "commander",
            
            # Organizations
            "govt.": "government",
            "dept.": "department",
            "univ.": "university",
            "corp.": "corporation",
            "inc.": "incorporated",
            "co.": "company",
            "ltd.": "limited",
            
            # Common abbreviations
            "approx.": "approximately",
            "appt.": "appointment",
            "apt.": "apartment",
            "assn.": "association",
            "asst.": "assistant",
            "avg.": "average",
            "bldg.": "building",
            "blvd.": "boulevard",
            "dept.": "department",
            "est.": "established",
            "etc.": "etcetera",
            "exec.": "executive",
            "fig.": "figure",
            "hrs.": "hours",
            "info.": "information",
            "intl.": "international",
            "jr.": "junior",
            "min.": "minutes",
            "misc.": "miscellaneous",
            "mtg.": "meeting",
            "natl.": "national",
            "orig.": "original",
            "pres.": "president",
            "ref.": "reference",
            "sec.": "second",
            "sr.": "senior",
            "yr.": "year",
            
            # Common acronyms (with periods)
            "u.s.a.": "united states of america",
            "u.k.": "united kingdom",
            "e.g.": "for example",
            "i.e.": "that is",
            
            # Common acronyms (without periods)
            "nasa": "national aeronautics and space administration",
            "nato": "north atlantic treaty organization",
            "un": "united nations",
            "eu": "european union",
            "fbi": "federal bureau of investigation",
            "cia": "central intelligence agency",
            "ceo": "chief executive officer",
            "cfo": "chief financial officer",
            "cto": "chief technology officer",
            "hr": "human resources",
            "id": "identification",
            "it": "information technology",
            "tv": "television",
            "pc": "personal computer",
            "asap": "as soon as possible",
        }
        
    def _create_slang_map(self) -> Dict[str, str]:
        """Create a map of common slang and informal expressions to their standard forms"""
        return {
            # Internet slang
            "lol": "laugh out loud",
            "brb": "be right back",
            "btw": "by the way",
            "fyi": "for your information",
            "idk": "i do not know",
            "tbh": "to be honest",
            "imo": "in my opinion",
            "imho": "in my honest opinion",
            "thx": "thanks",
            "ty": "thank you",
            "pls": "please",
            "plz": "please",
            "rn": "right now",
            "yep": "yes",
            "nope": "no",
            "omg": "oh my goodness",
            "wtf": "what the heck",
            "rofl": "rolling on floor laughing",
            "fomo": "fear of missing out",
            
            # Informal contractions
            "lemme": "let me",
            "gimme": "give me",
            "wanna": "want to",
            "dunno": "do not know",
            "kinda": "kind of",
            "sorta": "sort of",
            "outta": "out of",
            "hafta": "have to",
            "tryna": "trying to",
            "shoulda": "should have",
            "coulda": "could have",
            "woulda": "would have",
            "ya": "you",
            "goin": "going",
            "cuz": "because",
            "cause": "because",
            "bout": "about",
            "ima": "i am going to",
            
            # Nonstandard spellings
            "tonite": "tonight",
            "lite": "light",
            "thru": "through",
            "nite": "night",
            "tho": "though",
            "luv": "love",
            "em": "them",
            "bro": "brother",
            "ur": "your",
            "u": "you",
            "r": "are",
            "n": "and",
            "2": "to",
            "4": "for",
            "gr8": "great",
            "l8": "late",
            "l8r": "later",
            "b4": "before",
            "m8": "mate",
            "str8": "straight",
        }
    
    def _create_inflection_rules(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Create rules for normalizing inflected forms:
        - Plural nouns to singular
        - Verb tenses to base form
        - Comparatives & superlatives to base form
        
        Each rule is a tuple of (pattern, replacement)
        """
        return {
            # Plural nouns to singular
            "plural_to_singular": [
                (r"([^aeiou])ies$", r"\1y"),      # puppies -> puppy
                (r"([aeiou]y)s$", r"\1"),         # boys -> boy
                (r"(ss|[sxz]|[cs]h)es$", r"\1"),  # glasses -> glass, boxes -> box
                (r"([^s])ves$", r"\1fe"),         # wives -> wife
                (r"ves$", r"f"),                  # leaves -> leaf
                (r"i$", r"us"),                   # cacti -> cactus
                (r"ae$", r"a"),                   # formulae -> formula
                (r"a$", r"on"),                   # phenomena -> phenomenon
                (r"(child)ren$", r"\1"),          # children -> child
                (r"(ox)en$", r"\1"),              # oxen -> ox
                (r"(m|l)ice$", r"\1ouse"),        # mice -> mouse, lice -> louse
                (r"feet$", "foot"),               # feet -> foot
                (r"teeth$", "tooth"),             # teeth -> tooth
                (r"geese$", "goose"),             # geese -> goose
                (r"men$", "man"),                 # men -> man
                (r"women$", "woman"),             # women -> woman
                (r"people$", "person"),           # people -> person
                (r"s$", r""),                     # general rule: cats -> cat
            ],
            
            # Verb tenses to base form
            "verb_to_base": [
                (r"([^aeiou])ied$", r"\1y"),      # studied -> study
                (r"([aeiou])ied$", r"\1y"),       # played -> play
                (r"([^e])ing$", r"\1"),           # running -> run
                (r"ying$", r"y"),                 # lying -> lie
                (r"eing$", r"e"),                 # seeing -> see
                (r"([^e])ed$", r"\1"),            # jumped -> jump
                (r"eed$", r"ee"),                 # freed -> free
                (r"ies$", r"y"),                  # flies -> fly
                (r"([^aiou])es$", r"\1e"),        # closes -> close
                (r"([aeiou][pst])s$", r"\1"),     # stops -> stop
                (r"is$", r"be"),                  # is -> be
                (r"are$", r"be"),                 # are -> be
                (r"was$", r"be"),                 # was -> be
                (r"were$", r"be"),                # were -> be
                (r"am$", r"be"),                  # am -> be
                (r"been$", r"be"),                # been -> be
                (r"has$", r"have"),               # has -> have
                (r"had$", r"have"),               # had -> have
                (r"does$", r"do"),                # does -> do
                (r"did$", r"do"),                 # did -> do
                (r"said$", r"say"),               # said -> say
                (r"made$", r"make"),              # made -> make
                (r"went$", r"go"),                # went -> go
                (r"taken$", r"take"),             # taken -> take
                (r"took$", r"take"),              # took -> take
                (r"gave$", r"give"),              # gave -> give
                (r"given$", r"give"),             # given -> give
                (r"came$", r"come"),              # came -> come
                (r"became$", r"become"),          # became -> become
                (r"saw$", r"see"),                # saw -> see
                (r"seen$", r"see"),               # seen -> see
                (r"knew$", r"know"),              # knew -> know
                (r"known$", r"know"),             # known -> know
            ],
            
            # Comparatives & superlatives to base form
            "comparative_to_base": [
                (r"([^aeiou])ier$", r"\1y"),      # happier -> happy
                (r"([aeiou])ier$", r"\1y"),       # crazier -> crazy
                (r"([^aeiou])iest$", r"\1y"),     # happiest -> happy
                (r"([aeiou])iest$", r"\1y"),       # craziest -> crazy
                (r"([aeioulmnr])er$", r"\1e"),    # nicer -> nice
                (r"([^e])er$", r"\1"),            # smaller -> small
                (r"([aeioulmnr])est$", r"\1e"),   # nicest -> nice
                (r"([^e])est$", r"\1"),           # smallest -> small
                (r"better$", r"good"),            # better -> good
                (r"best$", r"good"),              # best -> good
                (r"worse$", r"bad"),              # worse -> bad
                (r"worst$", r"bad"),              # worst -> bad
                (r"more$", r"many"),              # more -> many
                (r"most$", r"many"),              # most -> many
                (r"less$", r"little"),            # less -> little
                (r"least$", r"little"),           # least -> little
            ],
        }

    def normalize_word(self, word: str) -> str:
        """
        Normalize a word by:
        1. Converting to lowercase
        2. Expanding contractions, abbreviations, and slang
        3. Handling possessives
        4. Handling compound/hyphenated words
        5. Normalizing inflected forms to base forms
        6. Removing non-alphabetic characters
        """
        if not word or not isinstance(word, str):
            return ""
        
        # Convert to lowercase and strip whitespace
        word = word.lower().strip()
        
        # Handle abbreviations (with and without periods)
        word_no_period = word.rstrip('.')
        if word in self.abbreviations_map:
            word = self.abbreviations_map[word]
        elif word_no_period in self.abbreviations_map:
            word = self.abbreviations_map[word_no_period]
            
        # Expand contractions
        if word in self.contractions_map:
            word = self.contractions_map[word]
            
        # Handle slang and informal language
        if word in self.slang_map:
            word = self.slang_map[word]
            
        # Handle general possessives (e.g., teacher's -> teacher)
        if word.endswith("'s") or word.endswith("'"):
            word = word.rstrip("'s")
            word = word.rstrip("'")
            
        # Handle compound/hyphenated words (convert to space-separated)
        word = word.replace('-', ' ')
        
        # Apply inflection rules to normalize to base forms
        word = self._normalize_inflection(word)
        
        # Remove any remaining punctuation and special characters
        word = re.sub(r'[^\w\s]', '', word)
        
        return word.strip()
        
    def _normalize_inflection(self, word: str) -> str:
        """Apply inflection rules to normalize a word to its base form"""
        original_word = word
        
        # Try applying plural to singular rules
        for pattern, replacement in self.inflection_rules['plural_to_singular']:
            if re.search(pattern, word):
                word = re.sub(pattern, replacement, word)
                break
                
        # If the word changed, return it
        if word != original_word:
            return word
            
        # Try applying verb to base form rules
        for pattern, replacement in self.inflection_rules['verb_to_base']:
            if re.search(pattern, word):
                word = re.sub(pattern, replacement, word)
                break
                
        # If the word changed, return it
        if word != original_word:
            return word
            
        # Try applying comparative/superlative to base form rules
        for pattern, replacement in self.inflection_rules['comparative_to_base']:
            if re.search(pattern, word):
                word = re.sub(pattern, replacement, word)
                break
                
        return word

    def normalize_words(self, words: List[str]) -> List[str]:
        """Normalize multiple words"""
        normalized = []
        for word in words:
            if not word or not isinstance(word, str):
                continue
                
            try:
                normalized_word = self.normalize_word(word)
                normalized.append(normalized_word)
            except Exception as error:
                logger.error(f'Error normalizing word: {word} - {error}')
                normalized.append(word.lower())
                
        return normalized
        
    def extract_words(self, text: str) -> List[str]:
        """Extract individual words from text, filtering out punctuation, hyphens, and numbers"""
        # Split text into words using regex that only allows alphabetic characters
        # This will match words containing only letters, excluding hyphens, apostrophes, numbers
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return [word for word in words if word]