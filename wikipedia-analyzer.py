# encoding: utf-8

from pandas import DataFrame
from analyzer import analyzeTextCohesion
# from analyzerenglish import CohesionAnalyzerEnglish
import re
import spacy

# Path for data file
path = '/home/christian/Repositories/goldstandardstudy-ss17/data/study2/wikipedia_raw.csv'
# path = '/home/christian/Downloads/test.csv'

# Read data into dataframe
data = DataFrame.from_csv(path, sep=',', index_col=False)
        # encoding='utf-8')

# Create empty data frame
data_with_values = DataFrame(columns=('title', 'url', 'summary', 'datetime',
    'num_sentences', 'num_clusters', 'local_cohesion',
    'num_concepts','num_coh_sentences', 'num_non_coh_sentences',
    'num_relations'))

    # 'num_compounds_pre', 'num_coreferences_pre', 'num_stem_relations_pre',
    # 'num_hyper_hypo_pre'))

# Load spacy
# nlp = spacy.load('en_core_web_md')

# analyzer = CohesionAnalyzerEnglish(nlp)

for index, row in data.iterrows():

    print("Index: {}".format(index))

    print('%s' % (row['title']))

    # Analyze current text
    res = analyzeTextCohesion(row['summary'])

    # Retrieve important variables from data
    num_sentences = res['numSentences']
    num_clusters = res['numCluster']
    local_cohesion = res['local cohesion']
    num_concepts = res['numConcepts']
    num_coh_sentences = res['cohSentences']
    num_non_coh_sentences = res['cohNotSentences']
    num_relations = res['numRelations']

    # Add row to data frame
    data_with_values.loc[index] = [row['title'], row['url'], row['summary'],
        row['datetime'],
        num_sentences, num_clusters, local_cohesion, num_concepts,
        num_coh_sentences, num_non_coh_sentences, num_relations]

# Save data as csv
data_with_values.to_csv(
    '/home/christian/Repositories/goldstandardstudy-ss17/data/study2/wikipedia-analyzed_lexical-coref_improved.py',
    encoding='utf-8', index=False)
