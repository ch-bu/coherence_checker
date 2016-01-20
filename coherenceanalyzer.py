# encoding: utf-8

import re
import os
import itertools
import constants
import subprocess
import enchant
from more_itertools import unique_everseen
# https://github.com/wroberts/pygermanet#setup
#from pygermanet import load_germanet
from enchant.checker import SpellChecker
from collections import Counter


class CoherenceAnalyzer:

	def __init__(self, text):

		# self.text is string
		if type(text) == str:
			self.text = self.replace_unwanted_chars(text.strip())

			# Check if string is empty
			if not self.text: 
				raise ValueError('You string is empty.')
			
			self.add_dot()
			self.spellcheck_text()
			self.tags = self.get_tags()
			self.word_pairs = self.get_word_pairs()
		
		# self.text is not a string
		else:
			raise TypeError('self.text is not a string')
	

	def replace_unwanted_chars(self, text):
		"""Replaces chars that mess up the data
		analysis
		"""

		new_text = text
		replacements = [r'[Bb]sp\.?\:?', 
						r'[Dd]\.?[Hh]\.?',
						r'[zZ]\.?[Bb]\.?']

		for replacement in replacements: 
			new_text = re.sub(replacement, '', new_text)

		return new_text


	def add_dot(self):
		"""Adds a dot at the end of the text if no end of line character
		can be found
		"""

		# List of end_of_line_characters
		end_of_line_chars = ['.', '!', '?']

		# Check if last character in self.text is not an end-of-line-character
		if not self.text[-1:] in end_of_line_chars:
			# Add dot to self.text if true
			self.text += '.'


	def get_words(self):
		"""Returns dict with words and counts 
		from pairs"""

		words = {}	
		pairs = self.word_pairs

		for pair in pairs:
			#print(pair)
			try: 
				words[pair[0]] = \
				words[pair[0]] + 1
			except KeyError:
				words[pair[0]] = 1
		
			try:
				words[pair[1]] \
				= words[pair[1]] + 1
			except KeyError:
				words[pair[1]] = 1

		return words


	def spellcheck_text(self):
		"""Spellcheckes text and saves spellchecked text in 
		self.text.
		"""

		# Variable declaration
		errors = list() # spelling errors
		chkr = SpellChecker('de_DE') # spellchecker for whole text
		dic = enchant.Dict('de_DE') # enchant dict
		
		# Run spellchecker over whole text
		chkr.set_text(self.text)
		
		# Loop over every error 
		for err in chkr:
			# Save error in errors list
			errors.append(err.word)

		# There are errors
		if len(errors) > 0:
			# Replace errors with proper word
			for error in errors:
				
				# Check if there is a substitute
				try:
					self.text = self.text.replace(error, dic.suggest(error)[0])
				except IndexError:
					pass


	def remove_synonyms(self, tags_from_function, g):
		"""Removes synonymes from self.tags

		Returns:
			Tags without synonyms
		"""

		# List of tags
		tags = tags_from_function

		# List of all words
		words = [tag[0] for tag in tags if tag[0] != '.']

		# Count of all words
		count = dict(Counter(words))

		# Loop over every combination of words
		for comb in itertools.combinations(count.keys(), 2):

			try:
				# Calculate Jiang-Conrath distance
				dist = g.synsets(comb[0])[0].dist_jcn(g.synsets(comb[1])[0])
				
				# We found a synonym
				if dist == 0:	

					# First word occurs more often
					if count[comb[0]] > count[comb[1]]:
						most_freq_word = comb[0]
					# Second word occurs more often
					elif count[comb[1]] > count[comb[0]]:
						most_freq_word = comb[1]
					# Words occurences don't differ
					else:
						most_freq_word = comb[0]

					# Loop over tags
					for tag in tags:
						# Assign tag[0] to most_frequent_word
						if tag[0] == comb[0] or tag[0] == comb[1]:
							tag[0] = most_freq_word

			except IndexError:
				pass
		
		return tags


	def get_tags(self):
		"""Generates tags from string.

		Takes a text as input and extracts nominatives using RFTagger.

		Args:
			None

		Returns:
			List with tags
		"""

		# Create directory temp if not existent
		if not os.path.exists(constants.temp_dir):
			os.makedirs(constants.temp_dir)
		
		# Save text to file
		f = open(constants.temp_text, 'w')
		f.write(self.text)
		f.close()

		# Tokenize 
		f = open(constants.temp_tokens, 'w')
		subprocess.call([constants.tokenizer, constants.temp_text], \
			stdout = f, shell = False)
		f.close()

		# Tag Tokens from temp_tokens
		f = open(constants.temp_tags, 'w')
		subprocess.call([constants.rftagger, constants.german_par, \
			constants.temp_tokens], stdout = f, shell = False)
		f.close()

		# Read tags from file
		f = open(constants.temp_tags, 'r')
		tags = f.readlines()
		f.close()

		# Regular Expression
		regex = re.compile(r'.*N.Name.*|.*N.Reg.*|.*SYM.Pun.Sent')

		# Filtered tags
		filtered_tags = [regex.match(tag).string for tag in tags \
			if regex.match(tag) != None]

		# Split tags in lists
		splited_tags = [str.split(tag, '\t') for tag in filtered_tags]
		
		# Load germanet
		#g = load_germanet()
	
		# Build Lemmas
		#splited_tags_lemma = [[g.lemmatise(tag[0].decode('utf-8'))[0] \
		#, tag[1]] for tag in splited_tags]

		# Update self.tags
		#tags = splited_tags_lemma

		# Remove synonyms
		# tags = self.remove_synonyms(tags, g)

		return splited_tags


	def get_sentences(self):
		"""Returns sentences from text
		"""

		sentence_list = list()
		curr_sentence = list()
		regex_sym = re.compile(r'.*SYM.*')
		tags = self.tags

		# Loop over every nominative
		for item in tags:
			# Item is not an end-of-line character
			if not re.match(regex_sym, item[1]) != None:
				# TODO: lemmatize item[0]
				curr_sentence.append(item[0])
			# Item is an end-of-line-character
			else:
				sentence_list.append(curr_sentence)
				curr_sentence = list()

		# Return list with sentences
		return sentence_list


	def get_num_sentences(self):
		"""Returns number of sentences in get_tags
		"""

		return len(self.get_sentences())


	def get_coherence_sentences(self):
		""""Calculates number of coherent sentences and
		non-coherent sentences from text.
		"""

		# Get sentences
		sentences = self.get_sentences()
		num_sentences = self.get_num_sentences()

		if num_sentences <= 1:
			raise ValueError("You do not have enough sentences")

		# Initialize variable
		num_coh = 0
		num_not_coh = 0

		# Check if text has at least 2 sentences
		if num_sentences > 1:

			# Calcuate num coherent and non-coherent sentences
			for sentence in range(0, num_sentences):
				
				# Before last sentence is reached
				if sentence == num_sentences - 1:
					pass
				else:
					# overlap true if two adjacent sentences share a word
					overlap = bool(set(sentences[sentence]) \
						& set(sentences[sentence + 1]))
					
					# Update overlapping sentences
					if overlap:
						num_coh = num_coh + 1
					# Update non-overlapping sentences
					else:
						num_not_coh = num_not_coh + 1

		# Return dict with coherence sentences
		return {"coh_sen": num_coh, "coh_not_sen": num_not_coh}


	def append_word_pairs(self, word_pairs, list1, list2):
		""" Combine all possible combinations of 
		two lists without repetition
		"""

		pairs = word_pairs

		# List1 one consists of more than 1 element
		if len(list1) > 1:
			for word1 in list1:
				for word2 in list2:
					pairs.append((word1, word2))

		# List1 contains 1 element
		elif len(list1) == 1:
			for word in list2:
				pairs.append((list1[0], word))
		return pairs


	def get_clusters(self):
		"""Calculates the number of clusters based on
		word pairs
		"""

		# Initialize Clusters
		clusters = []
		tempClusters = []
		found = True
		pairs = self.word_pairs

		# Loop over every word pair
		for num in range(0, len(pairs)):
			
			# Get link data
			source = pairs[num][0]
			target = pairs[num][1]
			
			# Temporary list
			tempClusters = [source, target]

			# Found set to true for while loop
			found = True

			while found == True:

				# Found set to faulse
				found = False

				# Loop over every word pair again
				for num_again in range(0, len(pairs)):

					# Word pairs do not match
					if num != num_again:

						# Initialize temporary source and target
						tempSource = pairs[num_again][0]
						tempTarget = pairs[num_again][1]

						# Temporary Array
						tempArray = [tempSource, tempTarget]

						# Temporary sources and targets in array position
						tempPosSource = tempSource in tempClusters
						tempPosTarget = tempTarget in tempClusters

						# Either of the two is in tempClusters
						if tempPosSource or tempPosTarget:

							# TempSource is in tempClusters
							if tempPosSource:
								# TempTarget ist not in tempClusters
								if not tempPosTarget:
									found = True;
									tempClusters.append(tempTarget)

							# TempTarget is in tempClusters
							if tempPosTarget:
								# TempSource is not in tempClusters
								if not tempPosSource:
									found = True
									tempClusters.append(tempSource)
			
			# Remove duplicates from tempClusters
			tempClusters = list(unique_everseen(tempClusters))


			clusterIn = False

			# Clusters has at least one element
			if len(clusters) > 0:
				# Loop over every cluster
				for cluster in range(0, len(clusters)):

					# Current Cluster
					currentCluster = clusters[cluster]

					# Loop over every element in tempClusters
					for c in range(0, len(tempClusters)):
						if tempClusters[c] in currentCluster:
							clusterIn = True
							break

				# tempClusters does not exist yet in clusters
				if not clusterIn:
					clusters.append(tempClusters)
				
			# Clusters is empty
			else:
				clusters.append(tempClusters)

		return clusters


	def get_num_clusters(self):
		"""Returns number of clusters in text
		"""

		return len(self.get_clusters())


	def get_num_concepts(self):
		"""Calculates the oncepts in the text
		"""

		# Inititialize empty list
		concepts = []
		pairs = self.word_pairs

		for pair in pairs:
			first = pair[0]
			second = pair[1]

			concepts.append(first)
			concepts.append(second)

		num_concepts = len(list(unique_everseen(concepts)))

		return num_concepts


	def get_word_pairs(self):
		"""Generates word pairs in order to calculate breaks and
		number of concepts
		"""

		tags = self.tags

		# Regular expressions
		regex_nom = re.compile(r'.*Nom.*')
		regex_acc = re.compile(r'.*Acc.*')
		regex_gen = re.compile(r'.*Gen.*')
		regex_dat = re.compile(r'.*Dat.*')
		regex_sym = re.compile(r'.*SYM.*')

		# Initialize word-pairs and noun lists
		word_pairs = []
		nom = []
		acc = []
		dat = []
		gen = []

		# Loop over splited_tags
		for tag in tags:

			# tag is nominativ
			if re.match(regex_nom, tag[1]) != None:
				nom.append(tag[0])
			# tag is accusative
			elif re.match(regex_acc, tag[1]) != None:
				acc.append(tag[0])
			# tag is dativ
			elif re.match(regex_dat, tag[1]) != None:
				dat.append(tag[0])
			# tag is genitive
			elif re.match(regex_gen, tag[1]) != None:
				gen.append(tag[0])
			# tag is dot
			elif re.match(regex_sym, tag[1]) != None:

				# Remove duplicates
				nom = sorted(set(nom))
				acc = sorted(set(acc))
				dat = sorted(set(dat))
				gen = sorted(set(gen))

				# There is at least a dative
				if len(dat) > 0:
					# There is at least an accusative
					if len(acc) > 0:
						# Accusative - Dative
						word_pairs = self.append_word_pairs(word_pairs, \
							dat, acc)

				# There is at least 1 nominative
				if len(nom) > 0:
					# There is at least an accusative
					if len(acc) > 0:
						# Nominativ - Accusative
						word_pairs = self.append_word_pairs(word_pairs, \
							nom, acc)

					# There is at least a dativ
					if len(dat) > 0:
						# Nominativ - Dative
						word_pairs = self.append_word_pairs(word_pairs, \
							nom, dat)
					
					# There is at least a genitiv
					if len(gen) > 0:
						# Nominativ - Genitive
						word_pairs = self.append_word_pairs(word_pairs, \
							nom, gen)
					
					# There are at least 2 nominatives
					if len(nom) > 1:
						# Nominative - Nominativ
						nom_nom = itertools.combinations(nom, 2)
						for pair in nom_nom:
							word_pairs.append(pair)

				
				# Reinitialize lists	
				nom = []
				acc = []
				dat = []
				gen = []


		word_list = []
		
		# Append tuples to word_list
		for pair in set(word_pairs):
			word_list.append((pair[0], pair[1]))

		# Return word_list
		return word_list



# if __name__ == '__main__':
	
# 	text = CoherenceAnalyzer("""Der italienische Filmemacher Ettore Scola ist tot. 
# 		Der Regisseur sei am Dienstag im Alter von 84 Jahren in der Poliklinik 
# 		in Rom gestorben, berichteten italienische Medien. Demnach war Scola in
# 		 die Abteilung für Herzchirurgie der Klinik eingeliefert worden und 
# 		 dort am Sonntag ins Koma gefallen.""")

# 	print("Word_pairs: " + str(text.get_word_pairs()))