# encoding: utf-8

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
import re

class CohesionAnalyzerEnglish:

    def __init__(self, text):
        # Prepare text and remove unwanted characters
        self.text = self._prepareText(text)

        # Get parts of speech of text
        self.pos = nltk.pos_tag(nltk.word_tokenize(self.text))

        # Lemmatise all words
        # self._lemmatizeWords()

        # Get sentences
        self.sentences = sent_tokenize(self.text)

        self.build_tree()
        # self.text = text

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

    def _lemmatizeWords(self):
        """Lemmatize all words in the pos"""

        lowercase_words = [(word[0].lower(), word[1]) for word in self.pos]

        print(lowercase_words)

    def build_tree(self):
        """Build a tree from the text"""

        for sentence in self.sentences:
            groucho_grammar = nltk.CFG.fromstring(sentence.split())
            # print(sentence.split())


model = CohesionAnalyzerEnglish("""
    Steven Arthur Pinker is a Canadian-born American cognitive scientist,
    psychologist, linguist, and popular science author! He is
    Johnstone Family Professor in the Department of Psychology at
    Harvard University, and is known for his advocacy of
    evolutionary psychology and the computational theory of mind.""")
