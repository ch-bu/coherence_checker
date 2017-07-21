# encoding: utf-8

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize
from itertools import combinations
import re
import spacy

# https://stackoverflow.com/questions/39763091/how-to-extract-subjects-in-a-sentence-and-their-respective-dependent-phrases
# https://github.com/krzysiekfonal/textpipeliner
class CohesionAnalyzerEnglish:

    def __init__(self, text):
        # Prepare text and remove unwanted characters
        self.text = self._prepareText(text)

        # Get sentences
        self.sentences = sent_tokenize(self.text)

        # Get parts of speech of text
        self.pos = self._pos_sentences()

        # Generate nouns per sentence
        self.nouns = self._generate_nouns()

        # Generate word pairs
        self.word_pairs = self.generate_word_pairs(self.pos)


    def _prepareText(self, text):
        """Prepares text for further
        data analysis. Preparation involves removal
        of unwanted characters"""

        paragraph_split = text.split('[LINEBREAK')

        # Remove brackets and parenthesis from text
        new_text = re.sub(r'[\(\[].*?[\)\]]', '', text)

        # Remove percent sign
        new_text = re.sub(r'%', '', new_text)

        # Remove trailing white space
        new_text = new_text.strip()

        # Remove line breaks
        new_text = new_text.rstrip()

        # If text doesn't end with a dot, fill it in
        if not new_text[-1:] in ['.', '!', '?']:
                new_text += '.'

        return new_text


    def _pos_sentences(self):
        """Generate list of sentences and their
        pos"""

        sentences = []

        # Init lemmatizer
        wordnet_lemmatizer = WordNetLemmatizer()

        # Loop over every sentence with pos
        for sentence in self.sentences:
            # Get parts of speech per sentence
            pos = nltk.pos_tag(nltk.word_tokenize(sentence))

            # Build lemmas
            lemma_words = [(word[0], wordnet_lemmatizer.lemmatize(word[0].lower()), word[1]) for word in pos]

            # Remove punctuation from data
            lemma_words = filter(lambda x: not bool(re.search('[,\.!?]', x[0])), lemma_words)

            sentences.append(lemma_words)


        return sentences


    def _generate_nouns(self):
        """Filter all nouns from sentences and
        return list of sentences with nouns"""

        nouns = []

        for sentence in self.pos:
            current_sentence = filter(lambda x: x[2] == 'NNP', sentence)
            nouns.append(current_sentence)

        return nouns


    def generate_word_pairs(self, sentences):

        word_pairs = []

        # Get word pairs from nouns
        for sentence in self.nouns:
            pairs_current_sentence = list(combinations(sentence, 2))
            # print(pairs_current_sentence)
            for pair in pairs_current_sentence:
                word_pairs.append({'source': pair[0][1], 'target': pair[1][1]})

        return word_pairs



model = CohesionAnalyzerEnglish("""
    Steven Arthur Pinker is a Canadian-born American cognitive scientist,
    psychologist, linguist, and popular science author! He is
    Johnstone Family Professor in the Department of Psychology at
    Harvard University, and is known for his advocacy of
    evolutionary psychology and the computational theories of mind.""")

model.nouns

# from nltk.stem import WordNetLemmatizer
# wordnet_lemmatizer = WordNetLemmatizer()
# print(wordnet_lemmatizer.lemmatize("theories"))
