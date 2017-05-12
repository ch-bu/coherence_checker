# encoding: utf-8

from pandas import DataFrame
from analyzer import get_clusters


def rewrite_text_rating(text):
    """
    Nests the tabular data into
    a hierarchy that we can
    use to analyze the dependent
    variables
    """
    # Init return variable
    output = []

    # Loop over every row in dataset
    for index, row in text[1].iterrows():
        pair = {'device': row['device'],
                'source': {'lemma': row['source'], 'sentence': row['satz.source']},
                'target': {'lemma': row['target'], 'sentence': row['satz.target']}}
        output.append(pair)

    return output


def get_number_of_relations(text):
    """
    Calculate the number of relations from
    the text
    """

    word_tuples = map(lambda x: (x['source']['lemma'], x['target']['lemma']), text)
    word_tuples = list(set([(pair['source']['lemma'], pair['target']['lemma'])
        for pair in text if pair['source']['lemma'] != pair['target']['lemma']]))

    return len(word_tuples)


# Path to rating file
path = '/home/christian/Repositories/goldstandardstudy-ss17/data/rater-data/probe-ricarda-3.csv'

# Read data from csv
rating = DataFrame.from_csv(path, sep=',', index_col=False,
    encoding='utf-8')

# Group text by text id
# We want to analyze every text on it's own
texts = rating.groupby(['id.text'])

for text in texts:
    # Get word pairs
    rating_nested = rewrite_text_rating(text)

    # Get dependent variables
    number_of_clusters = len(get_clusters(rating_nested, [1, 2, 3]))
    number_of_relations = get_number_of_relations(rating_nested)
