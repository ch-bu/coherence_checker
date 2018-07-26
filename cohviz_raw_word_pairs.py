# encoding: utf-8

from pandas import DataFrame
from analyzer import analyzeTextCohesion
import re

# Path for data file
path = '/home/christian/Repositories/goldstandardstudy-ss17/data/study1/raw-data.csv'

# Read data into dataframe
data = DataFrame.from_csv(path, sep=',', index_col=False)

# Create empty data frame
data_with_values = DataFrame(columns=('id', 'source', 'target', 'device', 'sentence_source', 'sentence_target'))

index_new = 0

for index, row in data.iterrows():

    # print(data_with_values)

    print('User %s ****' % (row['id']))

    # print(row['pre_text'].replace('[BREAK]', ' '))

    try:
        # Analyze current text
        res = analyzeTextCohesion(row['text'])
    except TypeError:
        continue

    # print(res['word_pairs'])
    # print(str(res['numConcepts']) + " - " + str(len(res['concepts'])))

    # # Retrieve important variables from data
    # num_sentences = res['numSentences']
    # num_clusters = res['numCluster']
    # local_cohesion = res['local cohesion']
    # num_concepts = res['numConcepts']
    # num_coh_sentences = res['cohSentences']
    # num_non_coh_sentences = res['cohNotSentences']
    # num_relations = res['numRelations']

    # Add row to data frame
    for pair in res['word_pairs']:
        # print(pair['source'])
        # print([row['id'], pair['source']['lemma'],
        # pair['target']['lemma'], pair['device'],pair['source']['sentence'],
        # pair['target']['sentence']])

        data_with_values.loc[index_new] = [row['id'], pair['source']['lemma'],
            pair['target']['lemma'], pair['device'], pair['source']['sentence'],
            pair['target']['sentence']]

        index_new = index_new + 1

    # num_sentences, num_clusters, local_cohesion, num_concepts,
        # num_coh_sentences, num_non_coh_sentences, num_relations]

# # Save data as csv
data_with_values.to_csv(
    '/home/christian/Repositories/goldstandardstudy-ss17/data/study1/cohviz_raw.csv',
    encoding='utf-8', index=False)
