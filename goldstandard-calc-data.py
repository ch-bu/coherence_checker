# encoding: utf-8

from pandas import DataFrame
from analyzer import get_clusters
import csv

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


def local_cohesion_analysis(text):
    """Calculates the local cohesion
    from the word pairs.

    Returns:
        Float - local cohesion
    """

    # Create index of words in
    # each sentence
    sentence_index = {}

    # Loop over every word pair
    for pair in text:
        index_source = pair['source']['sentence']
        index_target = pair['target']['sentence']
        source = pair['source']['lemma']
        target = pair['target']['lemma']

        # Add source words to list
        if index_source in sentence_index:
            sentence_index[index_source].append(source)
        else:
            sentence_index[index_source] = [source]

        # Add target words to list
        if index_target in sentence_index:
            sentence_index[index_target].append(target)
        else:
            sentence_index[index_target] = [target]

    # Init array that will hold the tuples of
    # all connected sentences
    connected_sentences = []

    # Calculate number of sentences
    num_sentences = int(max([key for key, index in sentence_index.iteritems()]))

    # Get tuples of bridged sentences
    for index in range(1, num_sentences + 1):
        # Do not loop over last sentence
        if (index + 1) < (num_sentences + 1):
            # If the key doesn't exist, carry on
            try:
                # Check if current and next sentence are connected
                if bool(set(sentence_index[index]) &
                        set(sentence_index[index + 1])):
                        # If both sentences are connected add them as
                        # a tuple to to array of connected sentences
                        connected_sentences.append((index, index + 1))
            except KeyError:
                pass

    # We have now calculated all lexical overlaps. The other cohesion
    # relations are still missing. Let's add these to our list of
    # connected sentences

    # Lets build all tuples from the missing cohesion relations
    cohesion_relations = [(pair['source']['sentence'], pair['target']['sentence'])
                    for pair in text if pair['source']['sentence'] !=
                                        pair['target']['sentence']]

    # Let's combine lexical overlaps and the other cohesion relations
    relations = list(set(connected_sentences + cohesion_relations))

    # Calculate local cohesion
    local_cohesion = len(relations) / float((num_sentences - 1))

    return {'local_cohesion': local_cohesion,
            'number_sentences': num_sentences}


# Path to rating file
path = '/home/christian/Repositories/goldstandardstudy-ss17/data/ricarda-100.csv'

# Read data from csv
rating = DataFrame.from_csv(path, sep=',', index_col=False,
    encoding='utf-8')

# Group text by text id
# We want to analyze every text on it's own
texts = rating.groupby(['id'])

# Write data to disk
# DataFrame.to_csv(rating)
import csv


with open('/home/christian/Repositories/goldstandardstudy-ss17/data/ricarda-100-analyzed.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=';',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['id', 'number_clusters',
                         'number_relations', 'number_concepts',
                         'local_cohesion', 'number_sentences'])

    for text in texts:
        # Get word pairs
        rating_nested = rewrite_text_rating(text)

        # Get dependent variables
        number_of_clusters = len(get_clusters(rating_nested, [1, 2, 3]))
        number_of_relations = get_number_of_relations(rating_nested)
        number_of_concepts = set([pair['source']['lemma']
                    for pair in rating_nested]).union([pair['target']['lemma']
                    for pair in rating_nested])

        local_cohesion = local_cohesion_analysis(rating_nested)

        print('############ %s #############' % text[0])
        print('Number of clusters: %s' % number_of_clusters)
        print('Number of relations: %s' % number_of_relations)
        print('Number of concepts: %s' % len(number_of_concepts))
        print('Local cohesion: %s' % local_cohesion['local_cohesion'])
        print('Number of sentences: %s' % local_cohesion['number_sentences'])

        spamwriter.writerow([text[0], number_of_clusters,
                             number_of_relations, len(number_of_concepts),
                             local_cohesion['local_cohesion'],
                             local_cohesion['number_sentences']])
