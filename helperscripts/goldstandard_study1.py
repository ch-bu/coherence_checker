# encoding: utf-8

from pandas import DataFrame
from analyzer import analyzeTextCohesion
import re

# Path for data file
path = '/home/christian/Repositories/goldstandardstudy-ss17/data/study1/raw_data.csv'

# Read data into dataframe
data = DataFrame.from_csv(path, sep=';', index_col=False)
        # encoding='utf-8')

# Create empty data frame
data_with_values = DataFrame(columns=('id', 'subject','text', 'num_words',
    'num_sentences', 'num_clusters',
    'local_cohesion', 'num_concepts', 'num_coh_sentences', 'num_non_coh_sentences',
    'num_relations', 'num_compounds', 'num_coreferences',
    'num_stem_relations',
    'num_hyper_hypo', 'num_lexical_overlaps'))

for index, row in data.iterrows():

    print('Text %s with id %i' % (row['subject'], row['id']))

    # Analyze current text
    res = analyzeTextCohesion(row['text'])

    # Retrieve important variables from data
    sentences = res['numSentences']
    num_clusters = res['numCluster']
    local_cohesion = res['local cohesion']
    num_concepts = res['numConcepts']
    num_coh_sentences = res['cohSentences']
    num_non_coh_sentences = res['cohNotSentences']
    num_relations = res['numRelations']
    num_lexical_overlaps = res['numPureLexicalOverlaps']


    # Add row to data frame
    data_with_values.loc[index] = [row['id'], row['subject'], row['text'],
        row['num_words'], sentences, num_clusters, local_cohesion,
        num_concepts, num_coh_sentences, num_non_coh_sentences,
        num_relations, num_lexical_overlaps]

# Save data as csv
data_with_values.to_csv(
    '/home/christian/Repositories/goldstandardstudy-ss17/data/study1/data_lexical_coref.csv',
    encoding='utf-8', index=False)
