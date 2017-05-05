# encoding: utf-8

from pandas import DataFrame
from analyzer import analyzeTextCohesion

# Path for data file
path = '/home/christian/Repositories/goldstandardstudy-ss17/data/raw-data.csv'

# Read data into dataframe
data = DataFrame.from_csv(path, sep=',', index_col=False,
        encoding='utf-8')

# Create empty data frame
data_with_values = DataFrame(columns=('id', 'subject', 'text',
    'num_sentences', 'num_clusters', 'local_cohesion', 'num_concepts',
    'num_coh_sentences', 'num_non_coh_sentences'))

for index, row in data.iterrows():
    # print(row['text'])
    # print(type(row['text']))
    res = analyzeTextCohesion(row['text'].encode('utf-8'))
    sentences = res['numSentences']
    clusters = res['numCluster']
    local_cohesion = res['local cohesion']
    num_concepts = res['numConcepts']
    num_coh_sentences = res['cohSentences']
    num_non_coh_sentences = res['cohNotSentences']

    data_with_values.loc[index] = [row['id'], row['subject'], row['text'],
        sentences, clusters, local_cohesion, num_concepts,
        num_coh_sentences, num_non_coh_sentences]

    print(data_with_values)
    # print ['id'], row['subject']

# Save data as csv
data_with_values.to_csv(
    '/home/christian/Repositories/goldstandardstudy-ss17/data/data_lexical_hyper_coref_compound.csv',
    encoding='utf-8', index=False)
