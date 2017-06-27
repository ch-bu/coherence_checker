# encoding: utf-8

import pandas as pd
import nltk
from nltk import word_tokenize
from nltk.collocations import TrigramCollocationFinder
from nltk.collocations import BigramCollocationFinder
from nltk.collocations import TrigramAssocMeasures
from nltk.collocations import BigramAssocMeasures
from nltk.corpus import stopwords

def is_good_collocation(collocation):

    german_stopwords = stopwords.words('german')

    if (collocation[0].lower() in german_stopwords) or \
        (collocation[1].lower() in german_stopwords) or \
        collocation[1].islower() or \
        collocation[0].islower():
        return False
    else:
        return True

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
    bigrams.apply_freq_filter(6)

    bigrams = bigrams.nbest(bigram_measures.pmi, 120)

    trigram_measures = TrigramAssocMeasures()
    trigrams = TrigramCollocationFinder.from_words(text)
    trigrams.apply_freq_filter(4)
    trigrams = trigrams.nbest(trigram_measures.pmi, 150)

    # print(bigrams)
    # print(bigrams)
    # for i in trigrams.score_ngrams(trigram_measures.pmi):
    #     print i
    # print(text.collocations())
    # print(trigram_measures.from_words(text))
    # print(list(nltk.bigrams(text)))
    #
    # print(filter(lambda x: is_good_collocation(x), bigrams))
    print(filter(lambda x: is_good_collocation(x), trigrams))

    return None

get_collocations('data.csv')
