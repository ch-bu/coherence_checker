# encoding: utf-8

from nltk.corpus import wordnet as wn
from itertools import combinations, permutations, chain, repeat
from collections import Counter
import re
import spacy

class CohesionAnalyzerEnglish:

    def __init__(self, text):
        # Load spacy
        self.nlp = spacy.load('en_core_web_md')

        # Remove parenthesis in the whole text
        text_nlp = text.decode('utf-8').replace('[LINEBREAK]', '')
        text_nlp = re.sub("([\(\[]).*?([\)\]])", "", text_nlp)
        text_nlp = re.sub('\n', ' ', text_nlp)

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
            # print (subject, subject.root.dep_, subject.root.pos_)
            # Append subject to list
            subjects.append(subject)

            # We only have one noun chunk
            if len(noun_chunks) == 1:
                # print noun_chunks
                if not noun_chunks[0].root.lemma_ in word_dict:
                    word_dict[noun_chunks[0].root.lemma_] = noun_chunks[0].orth_

                # Append
                word_pairs.append({'source': word_dict[noun_chunks[0].root.lemma_],
                                   'target': word_dict[noun_chunks[0].root.lemma_],
                                   'device': 'within'})
            # The subject is a pronoun and we have only one noun phrase
            elif subject.root.pos_ == 'PRON' and len(noun_chunks) == 2:
                if not noun_chunks[1].root.lemma_ in word_dict:
                    word_dict[noun_chunks[1].root.lemma_] = noun_chunks[1].orth_

                # Append
                word_pairs.append({'source': word_dict[noun_chunks[1].root.lemma_],
                                   'target': word_dict[noun_chunks[1].root.lemma_],
                                   'device': 'within'})
            # We have a subject
            elif subject:
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
                                word_dict[chunk.root.lemma_] = chunk.orth_
                                word_pairs.append({'source': word_dict[subject.root.lemma_],
                                                   'target': chunk.orth_,
                                                   'device': 'within'})
                        # We haven't stored the current subject
                        else:
                            word_dict[subject.root.lemma_] = subject.orth_
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
                my_combinations = list(list(zip(r, p)) for (r, p) in zip(repeat(noun_chunks), permutations(noun_chunks_next)))

                # Calculate similarity between pairs
                similarity_pairs = [(pair[0], pair[1], pair[0].similarity(pair[1])) for comb in my_combinations for pair in comb]

                # We are only interested in pairs with a high similarity
                similarity_filter = filter(lambda x: x[2] > .72, similarity_pairs)

                # We have found chunks that are similar
                if similarity_filter:
                    # Loop over every pair and append
                    for pair in similarity_filter:
                        if pair[0].orth_ != pair[1].orth_:
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


    def _get_html_string(self, node_list, word_cluster_index):
        """Generates an html string with spans for each word in order
        to signal the mapping between visualization and text

        Args:
            word_lemma_mapping (dict) - A dict with words as key and lemmas as values
            word_cluster_index (dict) - Words as key and int of cluster as value

        Returns:
            String - An html formatted string
        """
        # Init string to return
        html_string = ''

        # Loop over every paragraph in text
        for paragraph in self.paragraphs:
            # Start string
            html_string += '<p>'

            # Divide text into sentences
            tokens = self.nlp(paragraph)
            tokenized_sentences = [sent for sent in tokens.sents]

            # Loop over every sentence
            for index, sent in enumerate(tokenized_sentences):
                # Do not look at the last sentence
                if index != (len(tokenized_sentences) - 1):
                    # Get cluster of current sentence
                    indexes_cur_sentence = [word_cluster_index[node] for node in node_list if sent.text.find(node) != -1]
                    indexes_next_sentence = [word_cluster_index[node] for node in node_list if tokenized_sentences[index + 1].text.find(node) != -1]

                    # Get most common cluster of current sentence
                    most_common_cluster_cur = Counter(indexes_cur_sentence).most_common(1)
                    most_common_cluster_next = Counter(indexes_next_sentence).most_common(1)

                    # Get cluster for each sentence
                    cluster_cur = -1 if len(most_common_cluster_cur) == 0 else most_common_cluster_cur[0][0]
                    cluster_next = -1 if len(most_common_cluster_next) == 0 else most_common_cluster_next[0][0]

                    # Did the cluster change?
                    cluster_changed = False if cluster_cur == cluster_next else True

                    # Append sentence to string
                    html_string += sent.text + ' '

                    # Add cluster change symbol
                    html_string = html_string + '&#8660; ' if cluster_changed else html_string
                # Append last sentence
                else:
                    html_string += sent.text

            # Finish paragraph
            html_string += '</p>'

        # Replace strings with
        for node in node_list:
            # Get cluster
            cluster = word_cluster_index[node]

            # Change to span element
            html_string = html_string.replace(node, '<span class="cluster-' + str(cluster) + '">' + node + '</span>')


        return html_string


    def get_data_for_visualization(self):
        """Get all data for get_data for visualization"""

        # Get clusters
        cluster = self._get_clusters()

        # Create dictionary of words and it's corresponding clusters
        word_cluster_index = self._get_word_cluster_index(cluster)

        # Get unique nodes
        nodes = map(lambda x: [x['source'], x['target']], self.word_pairs)
        nodes_list = list(set(list(chain(*nodes))))
        nodes_dict = [{'id': word, 'index': ind} for ind, word, in enumerate(nodes_list)]

        # Generate html string
        html_string = self._get_html_string(nodes_list, word_cluster_index)

        print html_string
        # return self.word_pairs
        # return {'links': self.word_pairs,
        #         'nodes': nodes_dict,
        #         'numSentences': len(self.sents),
        #         'numConcepts': len(nodes),
        #         'clusters': cluster,
        #         # 'lemmaWordRelations': lemma_word_mapping,
        #         # 'wordLemmaRelations': word_lemma_mapping,
        #         'numRelations': self._calculate_number_relations(),
        #         'numCluster': len(cluster),
        #         'numSentences': len(self.sents),
        #         'numConcepts': len(self.concepts),
        #         'wordClusterIndex': word_cluster_index}
                # 'html_string': html_string}
                # 'subjects': self.subjects}


text = u"""Forgetting is the apparent loss or
modification of information already encoded and stored in an
individual's long-term memory. It is a spontaneous or gradual
process in which old memories are unable to be recalled from memory storage.
Peter Pan dreams of a fight."""

# text = u"""I go the cinema. Bill goes to school. New york is great."""

analyzer = CohesionAnalyzerEnglish(text)

print analyzer.get_data_for_visualization()
