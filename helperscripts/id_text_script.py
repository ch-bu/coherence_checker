# encoding: utf-8

from pandas import DataFrame
from analyzer import analyzeTextCohesion
import re

# Path for data file
path = '/home/christian/Downloads/andi_osmose_good.csv'

# Read data into dataframe
data = DataFrame.from_csv(path, sep=',', index_col=False)

# Create empty data frame
data_with_values = DataFrame(columns=('id', 'text',
    'num_sentences', 'num_clusters', 'local_cohesion',
    'num_concepts','num_coh_sentences', 'num_non_coh_sentences',
    'num_relations'))

for index, row in data.iterrows():

    print('User %s ****' % (row['id']))

    # print(row['pre_text'].replace('[BREAK]', ' '))

    # Analyze current text
    res = analyzeTextCohesion(row['text'])

    # Retrieve important variables from data
    num_sentences = res['numSentences']
    num_clusters = res['numCluster']
    local_cohesion = res['local cohesion']
    num_concepts = res['numConcepts']
    num_coh_sentences = res['cohSentences']
    num_non_coh_sentences = res['cohNotSentences']
    num_relations = res['numRelations']

    # Add row to data frame
    data_with_values.loc[index] = [row['id'], row['text'],
        num_sentences, num_clusters, local_cohesion, num_concepts,
        num_coh_sentences, num_non_coh_sentences, num_relations]

# Save data as csv
data_with_values.to_csv(
    '/home/christian/Downloads/andi_osmose_analyzed.csv',
    encoding='utf-8', index=False)
