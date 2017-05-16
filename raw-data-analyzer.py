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
    'num_coh_sentences', 'num_non_coh_sentences', 'num_relations',
    'num_compounds', 'num_coreferences', 'num_stem_relations',
    'num_hyper_hypo'))

for index, row in data.iterrows():
    # Analyze current text
    res = analyzeTextCohesion(row['text'].encode('utf-8'))

    # Retrieve important variables from data
    sentences = res['numSentences']
    num_clusters = res['numCluster']
    local_cohesion = res['local cohesion']
    num_concepts = res['numConcepts']
    num_coh_sentences = res['cohSentences']
    num_non_coh_sentences = res['cohNotSentences']
    num_relations = res['numRelations']
    num_compounds = res['numCompounds']
    num_coreferences = res['numCoreferences']
    num_stem_relations = res['numStemRelations']
    num_hyper_hypo = res['numHypoHyper']

    # Add row to data frame
    data_with_values.loc[index] = [row['id'], row['subject'], row['text'],
        sentences, num_clusters, local_cohesion, num_concepts,
        num_coh_sentences, num_non_coh_sentences, num_relations,
        num_compounds, num_coreferences, num_stem_relations, num_hyper_hypo]

# Save data as csv
data_with_values.to_csv(
    '/home/christian/Repositories/goldstandardstudy-ss17/data/data_lexical_hyper_coref_compound_stem.csv',
    encoding='utf-8', index=False)
# data_with_values.to_csv(
#     '/home/christian/Repositories/goldstandardstudy-ss17/data/data_lexical_hyper_coref_compound.csv',
#     encoding='utf-8', index=False)
