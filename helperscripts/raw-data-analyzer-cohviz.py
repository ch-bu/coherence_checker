# encoding: utf-8

from pandas import DataFrame
from analyzer import analyzeTextCohesion
import re

# Path for data file
path = '/media/christian/TOSHIBA/rohdaten_andi.csv'

# Read data into dataframe
data = DataFrame.from_csv(path, sep=';', index_col=False)
        # encoding='utf-8')

# Create empty data frame
data_with_values = DataFrame(columns=('subject', 'group', 'treatment', 'measure',
    'submission', 'pre_text',
    'num_sentences_pre', 'num_clusters_pre', 'local_cohesion_pre',
    'num_concepts_pre','num_coh_sentences_pre', 'num_non_coh_sentences_pre',
    'num_relations_pre', 'duration_pre',
    'post_text',
    'num_sentences_post', 'num_clusters_post', 'local_cohesion_post',
    'num_concepts_post','num_coh_sentences_post', 'num_non_coh_sentences_post',
    'num_relations_post','duration_post'))

    # 'num_compounds_pre', 'num_coreferences_pre', 'num_stem_relations_pre',
    # 'num_hyper_hypo_pre'))

for index, row in data.iterrows():

    print('User %s with measure %i' % (row['subject'], row['measure']))

    # print(row['pre_text'].replace('[BREAK]', ' '))

    # Analyze current text
    res_pre = analyzeTextCohesion(row['pre_text'].replace('[BREAK]', ' '))

    # Retrieve important variables from data
    sentences_pre = res_pre['numSentences']
    num_clusters_pre = res_pre['numCluster']
    local_cohesion_pre = res_pre['local cohesion']
    num_concepts_pre = res_pre['numConcepts']
    num_coh_sentences_pre = res_pre['cohSentences']
    num_non_coh_sentences_pre = res_pre['cohNotSentences']
    num_relations_pre = res_pre['numRelations']

    res_post = analyzeTextCohesion(row['post_text'].replace('[BREAK]', ' '))

    # Retrieve important variables from data
    sentences_post = res_post['numSentences']
    num_clusters_post = res_post['numCluster']
    local_cohesion_post = res_post['local cohesion']
    num_concepts_post = res_post['numConcepts']
    num_coh_sentences_post = res_post['cohSentences']
    num_non_coh_sentences_post = res_post['cohNotSentences']
    num_relations_post = res_post['numRelations']

    # Add row to data frame
    data_with_values.loc[index] = [row['subject'], row['group'], row['treatment'],
        row['measure'], row['submission'],
        row['pre_text'],
        sentences_pre, num_clusters_pre, local_cohesion_pre, num_concepts_pre,
        num_coh_sentences_pre, num_non_coh_sentences_pre, num_relations_pre,
        row['pre_page_duration'],
        row['post_text'],
        sentences_post, num_clusters_post, local_cohesion_post, num_concepts_post,
        num_coh_sentences_post, num_non_coh_sentences_post, num_relations_post,
        row['post_page_duration']]

# Save data as csv
data_with_values.to_csv(
    '/media/christian/TOSHIBA/rohdaten_andi_out.csv',
    encoding='utf-8', index=False)

# data_with_values.to_csv(
#     '/home/christian/Repositories/goldstandardstudy-ss17/data/data_lexical_hyper_coref_compound.csv',
#     encoding='utf-8', index=False)
