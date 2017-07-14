# encoding: utf-8

from pandas import DataFrame
from analyzer import analyzeTextCohesion
import re

# Path for data file
path = '/home/christian/Repositories/goldstandardstudy-ss17/data/raw-data.csv'

# Read data into dataframe
data = DataFrame.from_csv(path, sep=',', index_col=False)
        # encoding='utf-8')

# Create empty data frame
data_with_values = DataFrame(columns=('id', 'subject','lexical.overlaps'))

    # 'num_compounds_pre', 'num_coreferences_pre', 'num_stem_relations_pre',
    # 'num_hyper_hypo_pre'))

for index, row in data.iterrows():

    # print(row)

    # print('User %s with measure %i' % (row['subject'], row['measure']))

    # print(row['pre_text'].replace('[BREAK]', ' '))

    # Analyze current text
    res = analyzeTextCohesion(row['text'].replace('[BREAK]', ' '))

    # Retrieve important variables from data
    sentences_pre = res['numSentences']
    num_clusters_pre = res['numCluster']
    local_cohesion_pre = res['local cohesion']
    num_concepts_pre = res['numConcepts']
    num_coh_sentences_pre = res['cohSentences']
    num_non_coh_sentences_pre = res['cohNotSentences']
    num_relations_pre = res['numRelations']
    num_pure_lexical_overlaps = res['numPureLexicalOverlaps']

    # Add row to data frame
    data_with_values.loc[index] = [row['id'], row['subject'], num_pure_lexical_overlaps]

# Save data as csv
data_with_values.to_csv(
    '/home/christian/Repositories/goldstandardstudy-ss17/data/pure_lexical_overlaps.csv',
    encoding='utf-8', index=False)

# data_with_values.to_csv(
#     '/home/christian/Repositories/goldstandardstudy-ss17/data/data_lexical_hyper_coref_compound.csv',
#     encoding='utf-8', index=False)
