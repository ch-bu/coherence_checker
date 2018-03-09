# encoding: utf-8

from pandas import DataFrame
from analyzer import analyzeTextCohesion
import csv

# Path for data file
path = '/home/christian/Repositories/goldstandardstudy-ss17/data/study2/wikipedia_raw.csv'

# Read data into dataframe
data = DataFrame.from_csv(path, sep=',', index_col=False)
        # encoding='utf-8')

def get_pairs(pair):
    return (pair['source']['lemma'], pair['target']['lemma'])

# Create empty data frame
data_with_values = DataFrame(columns=('id', 'title', 'url', 'summary', 'datetime',
    'num_sentences', 'num_clusters', 'local_cohesion',
    'num_concepts', 'num_coh_sentences', 'num_non_coh_sentences',
    'num_relations'))

# Loop over every text
for index, row in data.iterrows():
    print(index + 1, row['title'])
    # Analyze current text
    res = analyzeTextCohesion(row['summary'].replace('[LINEBREAK]', ' '))

    # Add row to data frame
    data_with_values.loc[index] = [index + 1, row['title'], row['url'], row['summary'],
        row['datetime'], res['numSentences'], res['numCluster'], res['local cohesion'],
        res['numConcepts'], res['cohSentences'], res['cohNotSentences'],
        res['numRelations']]

    # Get word pairs as tuples
    pairs = map(get_pairs, res['word_pairs'])

    # Write pairs to disc
    with open('/home/christian/Repositories/goldstandardstudy-ss17/data/study2/wikipedia_german_pairs/' + str(index + 1) + '_pairs.csv', 'wb') as out:
        csv_out = csv.writer(out)

        csv_out.writerow(['from', 'to'])

        for pair in pairs:
            csv_out.writerow([pair[0].encode('utf-8'), pair[1].encode('utf-8')])


# Save data as csv
data_with_values.to_csv(
    '/home/christian/Repositories/goldstandardstudy-ss17/data/study2/wikipedia_analyzed_baseline_version.csv',
    encoding='utf-8', index=False)
