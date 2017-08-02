# encoding: utf-8

from pandas import DataFrame
from analyzer import analyzeTextCohesion
import re

# Path for data file
path = '/home/christian/Repositories/goldstandardstudy-ss17/data/study3/study3_raw_data.csv'

# Read data into dataframe
data = DataFrame.from_csv(path, sep=';', index_col=False)
        # encoding='utf-8')

# Create empty data frame
data_with_values = DataFrame(columns=('id', 'age','sex',
    'understandability_pre', 'understandability_post',
    'pre_text', 'pre_num_sentences', 'pre_num_cluster', 'pre_local_cohesion',
    'pre_num_concepts', 'pre_num_coh_sentences', 'pre_num_non_coh_sentences',
    'pre_num_relations',
    'post_text', 'post_num_sentences', 'post_num_cluster', 'post_local_cohesion',
    'post_num_concepts', 'post_num_coh_sentences', 'post_num_non_coh_sentences',
    'post_num_relations'))

    # 'num_compounds_pre', 'num_coreferences_pre', 'num_stem_relations_pre',
    # 'num_hyper_hypo_pre'))

for index, row in data.iterrows():
    # Analyze current text
    res = analyzeTextCohesion(row['pre_text'].replace('[BREAK]', ' '))

    # Retrieve important variables from data
    sentences_pre = res['numSentences']
    num_clusters_pre = res['numCluster']
    local_cohesion_pre = res['local cohesion']
    num_concepts_pre = res['numConcepts']
    num_coh_sentences_pre = res['cohSentences']
    num_non_coh_sentences_pre = res['cohNotSentences']
    num_relations_pre = res['numRelations']
    # num_pure_lexical_overlaps = res['numPureLexicalOverlaps']

    res_post = analyzeTextCohesion(row['post_text'].replace('[BREAK]', ' '))

    # Retrieve important variables from data
    sentences_post = res_post['numSentences']
    num_clusters_post = res_post['numCluster']
    local_cohesion_post = res_post['local cohesion']
    num_concepts_post = res_post['numConcepts']
    num_coh_sentences_post = res_post['cohSentences']
    num_non_coh_sentences_post = res_post['cohNotSentences']
    num_relations_post = res_post['numRelations']
    # num_pure_lexical_overlaps = res['numPureLexicalOverlaps']


    # Add row to data frame
    data_with_values.loc[index] = [row['id'], row['age'], row['sex'],
        row['understandability_pre'], row['understandability_post'],
        row['pre_text'], sentences_pre, num_clusters_pre, local_cohesion_pre,
        num_concepts_pre, num_coh_sentences_pre, num_non_coh_sentences_pre,
        num_relations_pre,
        row['post_text'], sentences_post, num_clusters_post, local_cohesion_post,
        num_concepts_post, num_coh_sentences_post, num_non_coh_sentences_post,
        num_relations_post]

# Save data as csv
data_with_values.to_csv(
    '/home/christian/Repositories/goldstandardstudy-ss17/data/study3/study3_data_analyzed_version5.csv',
    encoding='utf-8', index=False)

# data_with_values.to_csv(
#     '/home/christian/Repositories/goldstandardstudy-ss17/data/data_lexical_hyper_coref_compound.csv',
#     encoding='utf-8', index=False)
