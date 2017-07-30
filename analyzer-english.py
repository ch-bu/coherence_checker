# encoding: utf-8

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
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
        self.sents = [sent for sent in self.text.sents]

        # Init empty word pairs
        # self.word_pairs = []


    def _generate_nouns(self):
        """Filter all nouns from sentences and
        return list of sentences with nouns"""

        word_pairs = []

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
                        word_pairs.append({'source': subject.lemma_, 'target': noun.lemma_})
            # There is no subject in the sentence
            else:
                # Generate all combinations
                combs = combinations(nouns, 2)

                # Loop over every combination
                for comb in combs:
                    word_pairs.append({'source': comb[0].lemma_, 'target': comb[1].lemma_})

        return word_pairs


    def _generate_hyponyms_hyperonyms(self):
        """Generates a word pair list of hyperonyms and
        hyponyms from a given dataset"""

        word_pairs = []

        # Loop over every sentence
        for index, sentence in enumerate(self.sents):
            # Do not loop over last sentence
            if index < (len(self.sents) - 1):

                # Get all nouns from current and next sentence
                nouns_current_sentence = [noun.lemma_ for noun in sentence if any(noun.pos_ in s for s in ['PROPN', 'NOUN'])]
                nouns_next_sentence = [noun.lemma_ for noun in self.sents[index + 1] if any(noun.pos_ in s for s in ['PROPN', 'NOUN'])]

                # Loop over every noun in current sentence
                for noun in nouns_current_sentence:
                    ###############################
                    # Get hypernyms and hyponyms
                    ###############################
                    # Get all synsets of current noun
                    synsets_current_noun = [synset for synset in wn.synsets(noun)]

                    # Get all hyponyms and hyperonyms from all synsets
                    hyponyms_current_noun = [synset.hyponyms() for synset in synsets_current_noun]
                    hypernyms_current_noun = [synset.hypernyms() for synset in synsets_current_noun]

                    # Get all synsets of hyperonyms and hypernyms
                    synsets = [synset for synsets in (hyponyms_current_noun + hypernyms_current_noun) for synset in synsets]

                    # Get all lemmas
                    hypernyms_hyponyms = ([lemma.name().replace('_', ' ') for synset in synsets for lemma in synset.lemmas()])

                    ################################
                    # Connect to next sentence
                    ################################
                    # sentences_share_element = bool(set(hypernyms_hyponyms) & set(nouns_next_sentence))
                    sentences_shared_elements = list(set(hypernyms_hyponyms).intersection(nouns_next_sentence))

                    if len(sentences_shared_elements) > 0:
                        # print(sentences_share_element)
                        for shared_element in sentences_shared_elements:
                            word_pairs.append({'source': noun, 'target': shared_element})

        return word_pairs

    def generate_word_pairs(self):

        # Get word pairs
        # print self._generate_nouns
        # print self._generate_hyponyms_hyperonyms
        word_pairs = self._generate_hyponyms_hyperonyms() + \
                     self._generate_nouns()

        print word_pairs

        # Get sentence boundaries
        # sents_boundaries = [(sent.start, sent.end) for sent in self.sents]

        # print(sents_boundaries)
        # print(self.sents)
        # merge0 = self.text[sents_boundaries[0][0]:sents_boundaries[0][1]].merge(tag = "NNP")
        # merge1 = self.text[sents_boundaries[1][0]:sents_boundaries[1][1]].merge(tag = "NNP")
        # merge2 = self.text[sents_boundaries[2][0]:sents_boundaries[2][1]].merge(tag = "NNP")

        # police, and_, policeman = self.nlp(u'Police and policeman')
        # print(apples.vector)
        # print(police.similarity(policeman))
        # print(merge1.lemma_)
        # self._generate_nouns()
        #
        # )



            # print sent.start

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
    John Grisham graduated from Mississippi State University before attending the University of Mississippi School of Law in 1981.
    He practiced criminal law for about a decade and served in the House of Representatives in Mississippi from January 1984 to September 1990.
    His first novel, A Time to Kill, was published in June 1989, four years after he began writing it.
    As of 2012, his books and novellas have sold over 275 million copies worldwide.
    A Galaxy British Book Awards winner, Grisham is one of only three authors to sell 2 million copies on a first printing.""")

# model2 = CohesionAnalyzerEnglish(u'Credit and mortgage account holders must submit their requests within 30 days')

print(model.generate_word_pairs())

# from nltk.stem import WordNetLemmatizer
# wordnet_lemmatizer = WordNetLemmatizer()
# print(wordnet_lemmatizer.lemmatize("theories"))
