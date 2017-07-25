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
        # Load spacy
        self.nlp = spacy.load('en')

        # Prepare text and remove unwanted characters
        self.text = self.nlp(text)

        # Extract sentences
        self.sents = self.text.sents

        # Init empty word pairs
        self.word_pairs = []


    def _generate_nouns(self):
        """Filter all nouns from sentences and
        return list of sentences with nouns"""

        for sentence in self.sents:

            # Get root from sentence
            root = [w for w in sentence if w.head is w][0]

            # Get subject
            subject = list(root.lefts)[0]

            # Extract nouns from sentence
            nouns = [word for word in sentence if any(word.pos_ in s for s in ["PROPN", "NOUN"])]

            # Subject is a noun
            if any(subject.pos_ in s for s in ["NOUN", "PROPN"]):
                # Build word pairs
                for noun in nouns:
                    # Subject should not be the noun
                    if noun.lemma_ != subject.lemma_:
                        # Append word pair
                        self.word_pairs.append({'source': subject.lemma_, 'target': noun.lemma_})
            # There is no subject in the sentence
            else:
                # Generate all combinations
                combs = combinations(nouns, 2)

                # Loop over every combination
                for comb in combs:
                    self.word_pairs.append({'source': comb[0].lemma_, 'target': comb[1].lemma_})


            print self.word_pairs



    def generate_word_pairs(self):

        # word_pairs = []

        self._generate_nouns()

        # Get word pairs from nouns
        # for sentence in self.text.sents:
            # for index, word in enumerate(sentence):
            #     if index < len(sentence) - 1:
            #         print '%s and %s: %f' % (word, sentence[index + 1], word.similarity(sentence[index + 1]))

        # for index, sentence in enumerate(self.text.sents):
        #     if index < len(self.text.sents) - 1:
        #         print '%s and %s: %f' % (sentence, self.text.sents[index + 1], sentence.similarity(self.text.sents[index + 1]))

        # print '%s and %s: %f' % (self.text.sents[0], self.text.sents[1], sentence.similarity(self.text.sents[1]))
            # print sentence
                    # print(word.similarity(sentence[index + 1]))
                    # print(sentence[index + 1])
                # for w in word.subtree:
                    # print w
                    # print "\n"
                # print '%s, %s, %s: %s' % (word.dep_, word.pos_, word.tag_, word.lemma_)


            # print(sentence.lemma_)
            # for ent in sentence.:
            #     print(ent.label_, ent.text)
            # print(sentence)
            # pairs_current_sentence = list(combinations(sentence, 2))
            # # print(pairs_current_sentence)
            # for pair in pairs_current_sentence:
            #     word_pairs.append({'source': pair[0][1], 'target': pair[1][1]})

        # return word_pairs



model = CohesionAnalyzerEnglish(u"""
    ohn Grisham graduated from Mississippi State University before attending the University of Mississippi School of Law in 1981. He practiced criminal law for about a decade and served in the House of Representatives in Mississippi from January 1984 to September 1990.[4]
His first novel, A Time to Kill, was published in June 1989, four years after he began writing it. As of 2012, his books have sold over 275 million copies worldwide.[5] A Galaxy British Book Awards winner, Grisham is one of only three authors to sell 2 million copies on a first printing.""")

# model2 = CohesionAnalyzerEnglish(u'Credit and mortgage account holders must submit their requests within 30 days')

print(model.generate_word_pairs())

# from nltk.stem import WordNetLemmatizer
# wordnet_lemmatizer = WordNetLemmatizer()
# print(wordnet_lemmatizer.lemmatize("theories"))
