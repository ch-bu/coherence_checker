# encoding: utf-8

import pandas as pd
import nltk
from nltk import word_tokenize
from nltk.collocations import TrigramCollocationFinder
from nltk.collocations import BigramCollocationFinder
from nltk.collocations import TrigramAssocMeasures
from nltk.collocations import BigramAssocMeasures

def get_collocations(file):

    df = pd.read_csv(file)

    clt = df['text.clt.draft']
    knowledge = df['text.knowledge']

    text = ''

    for entry in clt:
        text += entry + ' '

    for entry in knowledge:
        text += entry + ' '

    text = nltk.Text(word_tokenize(text.decode('utf-8')))

    bigram_measures = BigramAssocMeasures()
    bigrams = BigramCollocationFinder.from_words(text)
    bigrams.apply_freq_filter(4)

    bigrams = bigrams.nbest(bigram_measures.pmi, 90)

    trigram_measures = TrigramAssocMeasures()
    trigrams = TrigramCollocationFinder.from_words(text)
    trigrams.apply_freq_filter(4)
    trigrams = trigrams.nbest(trigram_measures.pmi, 120)

    print(bigrams)
    # print(bigrams)
    # for i in trigrams.score_ngrams(trigram_measures.pmi):
    #     print i
    # print(text.collocations())
    # print(trigram_measures.from_words(text))
    # print(list(nltk.bigrams(text)))

    return None

get_collocations('data.csv')
