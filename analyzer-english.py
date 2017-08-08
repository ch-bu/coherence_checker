# encoding: utf-8

from nltk.corpus import wordnet as wn
from itertools import combinations, permutations, chain
import re
import spacy

class CohesionAnalyzerEnglish:

    def __init__(self, text):
        # Load spacy
        self.nlp = spacy.load('en_core_web_md')

        # Remove parenthesis in the whole text
        text_nlp = text.decode('utf-8').replace('[LINEBREAK]', '')
        text_nlp = re.sub("([\(\[]).*?([\)\]])", "", text_nlp)

        # Prepare text and remove unwanted characters
        self.text = self.nlp(text_nlp)

        # Paragraphs
        self.paragraphs = text.decode('utf-8').split('[LINEBREAK]')

        # Extract sentences
        self.sents = [sent for sent in self.text.sents]

        # Word pairs
        nouns, self.subjects = self._generate_nouns()
        self.word_pairs = nouns

        # All concepts
        self.concepts = list(set([pair['source'] for pair in self.word_pairs] +
                       [pair['target'] for pair in self.word_pairs]))


    def _generate_nouns(self):
        """Filter all nouns from sentences and
        return list of sentences with nouns"""

        word_pairs = []
        subjects = []
        word_dict = {}

        for index, sentence in enumerate(self.sents):
            # Get noun chunks
            noun_chunks = list(sentence.noun_chunks)

            # Get first subject
            subject = [sub for sub in noun_chunks if any(sub.root.dep_ for s in ['nsubj', 'csubj', 'nsubjpass'])][0]

            # Append subject to list
            subjects.append(subject)

            # We have a subject
            if subject:
                # Combine subject with noun_chunks
                for chunk in noun_chunks:
                    # Do not combine the same chunk
                    if chunk.orth_ != subject.orth_ \
                        and chunk.root.pos_ != 'PRON' \
                        and subject.root.pos_ != 'PRON':
                        # We already stored a subject with the same root
                        if subject.root.lemma_ in word_dict:
                            # We alredy stored the noun chunk
                            if chunk.root.lemma_ in word_dict:
                                word_pairs.append({'source': word_dict[subject.root.lemma_],
                                                   'target': word_dict[chunk.root.lemma_],
                                                   'device': 'within'})
                            # The noun chunk is new to us
                            else:
                                word_dict[chunk.root.lemma_] = chunk
                                word_pairs.append({'source': word_dict[subject.root.lemma_],
                                                   'target': chunk.orth_,
                                                   'device': 'within'})
                        # We haven't stored the current subject
                        else:
                            word_dict[subject.root.lemma_] = subject
                            word_pairs.append({'source': subject.orth_,
                                               'target': chunk.orth_,
                                               'device': 'within'})
            # If there is no subject combine every pair
            else:
                no_sub_combinations = combinations(noun_chunks_next, 2)

                # There are combinations
                if no_sub_combinations:
                    # Add all combinations
                    for comb in combinations:
                        if comb[0].root.pos_ != 'PRON' \
                            and comb[1].root.pos_ != 'PRON':
                            if comb[0].root.lemma_ in word_dict:
                                if comb[1].root.lemma_ in word_dict:
                                    word_combs.append({'source': word_dict[comb[0].root.lemma_],
                                                       'target': word_dict[comb[1].root.lemma_],
                                                       'device': 'between'})

                                else:
                                    word_dict[comb[1].root.lemma_] = comb[1].orth_
                                    word_combs.append({'source': word_dict[comb[0].root.lemma_],
                                                       'target': comb[1].orth_,
                                                       'device': 'between'})
                            else:
                                word_dict[comb[0].root.lemma_] = comb[0].orth_
                                word_combs.append({'source': comb[0].orth_,
                                                   'target': comb[1].orth_,
                                                   'device': 'between'})


            # Lets look at the next sentence if there is a link between the two
            if index < (len(self.sents) - 1):
                # Get noun chunks of next sentence
                noun_chunks_next = list(self.sents[index + 1].noun_chunks)

                # Combine all chunks between two sentences
                my_combinations = [zip(x, noun_chunks_next) for x in combinations(noun_chunks, 2)]

                # Calculate similarity between pairs
                similarity_pairs =  [(pair[0], pair[1], pair[0].similarity(pair[1])) for comb in my_combinations for pair in comb]

                # We are only interested in pairs with a high similarity
                similarity_filter = filter(lambda x: x[2] > .72, similarity_pairs)

                # We have found chunks that are similar
                if similarity_filter:
                    # Loop over every pair and append
                    for pair in similarity_filter:
                        print pair[0].root.lemma_
                        if pair[0].root.lemma_ in word_dict:
                            if pair[1].root.lemma_ in word_dict:
                                word_pairs.append({'source': word_dict[pair[0].root.lemma_],
                                                   'target': word_dict[pair[1].root.lemma_],
                                                   'device': 'between'})

                            else:
                                word_dict[pair[1].root.lemma_] = pair[1].orth_
                                word_pairs.append({'source': word_dict[pair[0].root.lemma_],
                                                   'target': pair[1].orth_,
                                                   'device': 'between'})
                        else:
                            word_dict[pair[0].root.lemma_] = pair[0].orth_
                            word_pairs.append({'source': pair[0].orth_,
                                               'target': pair[1].orth_,
                                               'device': 'between'})

        print word_pairs
        return word_pairs, subjects


    def _calculate_number_relations(self):
        """Calculates the number of relations"""

        # Make tuples from word_pairs
        tuples = map(lambda x: (x['source'], x['target']), self.word_pairs)

        # Remove duplicates
        tuples = list(set([(pair[0], pair[1])
            for pair in tuples if pair[0] != pair[1]]))

        return len(tuples)


    def _get_clusters(self):
        """Calculates the number of computed
        clusters"""

        # If we only have one sentence return word pairs
        # as single cluster
        if len(self.sents) == 1:
            return self.word_pairs

        # Initialize clusters. The cluster
        # later stores all clusters as a list containing
        # the word pair dictionaries
        clusters = []

        # Store all words that have already been
        # assigned to a cluster
        assigned_words = []

        # Loop over every word pair
        for num in range(0, len(self.word_pairs)):
            # Store all words that are stored in the current cluster
            current_word_pair = [self.word_pairs[num]['source'],
                    self.word_pairs[num]['target']]

            # Only assign a new cluster if the current word pair has
            # not already been processed
            if (not bool(set(current_word_pair) & set(assigned_words))):
                # Init current cluster
                current_cluster = [self.word_pairs[num]]

                # Remember that we already added the words of the current cluster
                assigned_words.append(current_word_pair[0])
                assigned_words.append(current_word_pair[1])

                # Index of word_pair we already added to current cluster.
                # We store the index to reduce the computation. If we already
                # added an index to the current cluster, there is no need
                # to look at it again
                index_pairs_added = [num]

                # Found set to true for while loop
                found = True

                # As long as we still find connections keep on looping
                while found:
                    # Found set to false
                    found = False

                    # Loop over every word pair again
                    for num_again in range(0, len(self.word_pairs)):
                        # Word pairs do not match
                        if num_again not in index_pairs_added:
                            # Store both words of current pair in list
                            iter_word_pair = [self.word_pairs[num_again]['source'],
                                    self. word_pairs[num_again]['target']]

                            # Lemmas in current cluster
                            current_cluster_lemma_source = map(lambda x: x['source'], current_cluster)
                            current_cluster_lemma_target = map(lambda x: x['target'], current_cluster)

                            # Get all words in current cluster
                            current_cluster_lemma = current_cluster_lemma_source + \
                                        current_cluster_lemma_target

                            # Both pairs share an element
                            shared_element = bool(set(current_cluster_lemma) & set(iter_word_pair))

                            # If they share an element append to current cluster
                            if shared_element:
                                # Append pair to current cluster
                                current_cluster.append(self.word_pairs[num_again])

                                # Remember that we already appended this
                                # pair to the current cluster
                                index_pairs_added.append(num_again)

                                # Add word pair that belongs to current cluster
                                # to list of assigned word pairs. By doing this
                                # we know if a word has already been assigned
                                # to a cluster.
                                assigned_words.append(iter_word_pair[0])
                                assigned_words.append(iter_word_pair[1])

                                # We found a candidate. When we found a connection
                                # a new word might be added to the current
                                # cluster. Therefore we have too loop over
                                # every word pair again to see if we
                                # missed a connection with the new word
                                found = True

                # Append current cluster to all clusters
                clusters.append(current_cluster)

        return clusters


    def _get_word_cluster_index(self, cluster):
        """Generate a dictionary that
        has the words as key and the cluster number
        as value"""

        # When clusters are calculated assign them to the word_pairs as
        # an additional value
        word_cluster_index = {}

        # Loop over every cluster
        for index, single_cluster in enumerate(cluster):
            # Get words for current cluster
            source_words = map(lambda x: x['source'], single_cluster)
            target_words = map(lambda x: x['target'], single_cluster)

            # Concatenate sources and targets in to one array
            words = source_words + target_words

            # Assign index to word_cluster_index dict
            for word in words:
                word_cluster_index[word] = index

        return word_cluster_index


    def _get_lemma_word_mapping(self, nodes):
        """Returns a dictionary with the lemma as key and the
        inflected words as values"""

        # Init mapping
        mapping = {}

        # Loop over every word in text
        for token in self.text:
            # Word is part of nodes for visualization
            if token.lemma_ in nodes:
                # We have already assigned this word to a key
                if token.lemma_ in mapping:
                    # Avoid duplicates
                    if token.orth_ not in mapping[token.lemma_]:
                        mapping[token.lemma_].append(token.orth_)
                # This word is knew, let's start a knew key
                else:
                    mapping[token.lemma_] = [token.orth_]

        return mapping


    def _get_word_lemma_mapping(self, nodes):
        """Returns a dictionary with the word as a key
        and the lemma as a value"""

        mapping = {}

        # Loop over every word in text
        for token in self.text:
            # Word ist part of nodes for visualization
            if token.lemma_ in nodes:
                # We have already assigned this word to a key
                if token.orth_ in mapping:
                    # Avoid duplicates
                    if token.lemma_ not in mapping[token.orth_]:
                        mapping[token.orth_].append(token.lemma_)
                # This word is knew, let's start a knew key
                else:
                    mapping[token.orth_] = [token.lemma_]

        return mapping


    def _get_html_string(self, word_lemma_mapping, word_cluster_index):
        """Generates an html string with spans for each word in order
        to signal the mapping between visualization and text

        Args:
            word_lemma_mapping (dict) - A dict with words as key and lemmas as values
            word_cluster_index (dict) - Words as key and int of cluster as value

        Returns:
            String - An html formatted string
        """

        html_string = '';

        for paragraph in self.paragraphs:
            #######################################
            # Render text for integrated group
            #######################################

            # Split text into sentences
            tokens = self.nlp(paragraph)
            tokenized_sentences = [sent for sent in tokens.sents]

            # for sentence in tokenized_sentences:
            #     print sentence.orth_.split()

            # Split words within sentences
            words_split_per_sentence = [sentence.orth_.split() for sentence in tokenized_sentences]

            # Prepare html string
            paragraph_string = '<p>'

            # Loop over every sentence
            for index, sentence in enumerate(words_split_per_sentence):
                # Store cluster uf current sentence
                cluster_current = []

                # Store the end of line character
                # We need to store the character to append it
                # afterwards
                end_of_line_character = sentence[-1][-1]

                # Remove end of line characters
                words = [re.sub(r'[.\!?]', '', s) for s in sentence]

                # Loop over every word in current sentence
                for word in words:
                    # We need to reset the carrier for every word otherwise
                    # every word will be appended with the carrier
                    carrier = None

                    # Check if word ends with a special character
                    if word.endswith(':') or word.endswith(',') or word.endswith(';'):
                        carrier = word[-1]
                        word = re.sub(r'[:,;]', '', word)

                    # Check if there is a lemma for current word and catch
                    # any KeyError
                    try:
                        # Get lemma for word
                        lemma = word_lemma_mapping[word][0]

                        # Get cluster number for word
                        cluster_of_word = word_cluster_index[lemma]

                        # Push cluster ot current cluster list
                        cluster_current.append(cluster_of_word)

                        # Append html string with span tag and according class
                        paragraph_string += '<span class="cluster-' + str(cluster_of_word) + '">' + word + '</span>'

                    # The word does not occur in the word lemma dicitonary
                    # It should not be assigned a class for highlighting
                    except KeyError:
                        paragraph_string += '<span>' + word + '</span>'

                    # Append carrier if it exists
                    paragraph_string += carrier if carrier else ''
                    paragraph_string += ' '

                ############################################################
                # Check if cluster changes for next sentence
                ############################################################
                if index != (len(words_split_per_sentence) - 1) \
                        and len(tokenized_sentences) > 1:
                    # Get words for next sentence
                    words_next_sentence = [re.sub(r'[.\!?]', '', s) for s in words_split_per_sentence[index + 1]]

                    # Initialize cluster of next sentence
                    cluster_next = []

                    for word in words_next_sentence:
                        # Catch errors
                        try:
                            lemma = word_lemma_mapping[word][0]

                            cluster_of_word_next_sentence = word_cluster_index[lemma]

                            cluster_next.append(cluster_of_word_next_sentence)
                        except KeyError:
                            pass

                # If we only have one sentence append only the end of line character
                if len(tokenized_sentences) <= 1:
                    paragraph_string = paragraph_string[:-1]
                    paragraph_string += end_of_line_character
                    paragraph_string += ' '
                # We have more than one sentence
                else:
                    # See if cluster of adjacent sentence differ
                    cluster_changed = set(cluster_current) != set(cluster_next)

                    # Append end of line character and add an empty space.
                    # The empty space is necessary otherwise the next sentence
                    # will directly align to the current sentence
                    paragraph_string = paragraph_string[:-1]
                    paragraph_string += end_of_line_character
                    paragraph_string += '&#8660; ' if cluster_changed else ''
                    paragraph_string += ' '

            # End paragraph
            paragraph_string += '</p>'

            html_string += paragraph_string

        return html_string


    def get_data_for_visualization(self):
        """Get all data for get_data for visualization"""

        # Get clusters
        cluster = self._get_clusters()

        # Create dictionary of words and it's corresponding clusters
        # word_cluster_index = self._get_word_cluster_index(cluster)

        # Get unique nodes
        # nodes = map(lambda x: [x['source'], x['target']], self.word_pairs)
        # nodes_list = list(set(list(chain(*nodes))))
        # nodes_dict = [{'id': word, 'index': ind} for ind, word, in enumerate(nodes_list)]

        # Generate dict with lemma as key and orth as value
        # lemma_word_mapping = self._get_lemma_word_mapping(nodes_list)

        # Generate dict with orth as key and lemma as value
        # word_lemma_mapping = self._get_word_lemma_mapping(nodes_list)

        # Generate html string
        # html_string = self._get_html_string(word_lemma_mapping, word_cluster_index)


        return self.word_pairs
        # return {'links': self.word_pairs,
        #         'nodes': nodes_dict,
        #         'numSentences': len(self.sents),
        #         'numConcepts': len(nodes),
        #         'clusters': cluster,
        #         'lemmaWordRelations': lemma_word_mapping,
        #         'wordLemmaRelations': word_lemma_mapping,
        #         'numRelations': self._calculate_number_relations(),
        #         'numCluster': len(cluster),
        #         'numSentences': len(self.sents),
        #         'numConcepts': len(self.concepts),
        #         'wordClusterIndex': word_cluster_index,
        #         'html_string': html_string,
        #         'subjects': self.subjects}


text = u"""Forgetting is the apparent loss or
modification of information already encoded and stored in an
individual's long-term memory. It is a spontaneous or gradual
process in which old memories are unable to be recalled from memory storage.
Forgetting also helps to reconcile the storage of new information with old
knowledge.[1] Problems with remembering, learning and retaining new
information are a few of the most common complaints of older adults.
 Memory performance is usually related to the active functioning
 of three stages. These three stages are encoding, storage and retrieval."""

text = u"""The universe is a vast space. The earth in is the middle of it.
    He was taken to the hospital."""

analyzer = CohesionAnalyzerEnglish(text)

analyzer.get_data_for_visualization()
