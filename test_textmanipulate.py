# encoding: utf-8

import unittest
from textmanipulate import TextManipulation


# ********************* Texts *************************************************

# Empty data set
text0 = " "
data0 = {'text': text0}

# Simple example
text1 = """Ich bin ein Hund. Der Hund geht in den Garten.
	   Bilbo könnte gerne in den Garten gehen, wenn er 
	   nur gestern nicht auf der Varanda eingeschlafen 
	   wäre. Das hätte sich Mario auch gewünscht, wenn
	   er nur nicht im Bierhaus gelandet wäre"""
data1 = {'text': text1, 'num_sentences': 4, 
		'num_not_coh_s': 1, 'num_coh_s': 2,
		'num_clusters': 2, 'num_concepts': 6}
t_class1 = TextManipulation(data1['text'])

# Real example
text2 = """Eine Erklärung ist genau dann lernförderlich, wenn sie bei allen 
gut ankommt. Man muss also etwas so erklären, dass jeder in der Lage ist 
in einem Satz die Erklärung grob wiedergeben zu können. Daher spielt die 
Art und Weise der Erklärung die größte Rolle, d.h. die Erklärung darf nicht 
zu trocken sein. Die Schüler/innen brauchen Beispiele mit denen sie 
vielleicht die Erklärung verknüpfen können. Hier kommt dann der Lehrende
 ins Spiel. Er muss mit verschiedenen Methoden den Sachverhalt übermitteln 
 können. Und am effektivsten ist es natürlich, wenn der Lehrende selbst 
 mit dem Sachverhalt gründlich vertraut ist. D.h. der Lehrende muss viele 
 Beispiele zu dem betroffenen Sachverhalt mitbringen. Wenn man das ganze 
 über die Teilhabe-Perspektive macht, dann sind die Lernenden meist mehr 
 begeistert und bemühen sich mehr den Sachverhalt zu verstehen. Die Lernenden 
 müssen bei der Sache Spaß haben können. Die reine Vermittlung 
 vom Wissen gefällt nicht jeden.
 """
data2 = {'text': text2, 'num_sentences': 11,
		'num_not_coh_s': 3, 'num_coh_s': 7}
t_class2 = TextManipulation(data2['text'])

# Quatsch Text
text3 = """assklöj salfjka"""
data3 = {'text': text3, 'num_sentences': 1}
t_class3 = TextManipulation(data3['text'])

# Real example 2
text4 = """Schulleistungsstudien sollen die Wissenstände von Schülerinnen 
und Schülern möglichst genau erfassen und so einen Vergleich zwischen 
Ländern oder Schulen möglich machen. Dabei werden die sogenannten 
Schulleistungen überprüft. Darunter zählen das deklarative und prozedurale 
Wissen in verschiedenen Fächern (z.B. Mathematik oder Deutsch), besonders 
aber auch fachübergreifende Kompetenzen wie z.B. das Leseverstehen. Weiterhin 
werden Bedingungsfaktoren angedeutet, die für ein bestimmtes Ergebnis 
verantwortlich sein können. Ist das soziale Umfeld für den Lernzuwachs 
entscheidend? So können sich Länder anhand ihrer Bildungsergebnisse messen 
und daraus Schlüsse für das eigenen Bildungssytem ziehen. So schnitt 
Deutschland in der Pisa-Studie verhältnismäßig schlecht ab, worauf 
verschiedene Schritte zur Besserung des Schulsystems eingeleitet wurden. 
Auf der anderen Seiten können die Indikatoren festgestellt werden, welche 
ein gutes Schulsystem ausmachen. Danach können sich Länder, die 
verhältnismäßig schlechter abgeschnitten haben, besser orientieren und 
gezieltere Verbesserungen vornehmen. Solche können sein: Ausgaben für 
Bildung, Schulkultur, Schulleistungen, soziale Faktoren.Trotzdem können 
solche Studien nur gröbere Prozesse bewerten, Feinheiten oder Details 
werden somit ausgelassen. Deshalb ist es nicht einfach vorauszusehen, 
ob eine Interventionsmaßnahme wirklich Wirkung zeigt."""
data4 = {'text': text4, 'num_sentences': 12, 
		'num_not_coh_s': 10, 'num_coh_s': 1}
t_class4 = TextManipulation(data4['text'])

# ************************* TestSuites ****************************************

# Empty dataset
class TestTextManipulation_0(unittest.TestCase):

	def test_empty_string(self):
		with self.assertRaises(ValueError):
			TextManipulation(data0['text'])


# Self made dataset
class TestTextManipulation_1(unittest.TestCase):

	def test_text_typeerror(self):
		"""Raise TypeError if argument is not a string
		"""

		with self.assertRaises(TypeError):
			TextManipulation(2)

	def test_number_of_sentences(self):
		self.assertEqual(t_class1.get_num_sentences(), 
			data1['num_sentences'])

	def test_number_of_incoherent_sentences(self):
		self.assertEqual(t_class1.get_coherence_sentences()['coh_not_sen'], 
			data1['num_not_coh_s'])

	def test_number_of_coherent_sentences(self):
		self.assertEqual(t_class1.get_coherence_sentences()['coh_sen'], 
			data1['num_coh_s'])

	def test_number_of_clusters(self):
		self.assertEqual(t_class1.get_num_clusters(),
			data1['num_clusters'])

	def test_number_of_concepts(self):
		self.assertEqual(t_class1.get_num_concepts(),
			data1['num_concepts'])

# Real dataset
class TestTextManipulation_2(unittest.TestCase):

	def test_number_of_sentences(self):
		self.assertEqual(t_class2.get_num_sentences(), 
			data2['num_sentences'])

	def test_number_of_incoherent_sentences(self):
		self.assertEqual(t_class2.get_coherence_sentences()['coh_not_sen'],  
			data2['num_not_coh_s'])

	def test_number_of_coherent_sentences(self):
		self.assertEqual(t_class2.get_coherence_sentences()['coh_sen'],
			data2['num_coh_s'])


# Quatsch Text
class TestTextManipulation_3(unittest.TestCase):

	def test_number_of_sentences(self):
		self.assertEqual(t_class3.get_num_sentences(),
			data3['num_sentences'])

	def test_number_of_incoherent_sentences(self):
		with self.assertRaises(ValueError):
			t_class3.get_coherence_sentences()

# Real dataset 2
class TestTextManipulation_4(unittest.TestCase):

	def test_number_of_sentences(self):
		self.assertEqual(t_class4.get_num_sentences(), 
			data4['num_sentences'])

	def test_number_of_incoherent_sentences(self):
		self.assertEqual(t_class4.get_coherence_sentences()['coh_not_sen'],  
			data4['num_not_coh_s'])

	def test_number_of_coherent_sentences(self):
		self.assertEqual(t_class4.get_coherence_sentences()['coh_sen'],
			data4['num_coh_s'])


# ********************** Check Suites *****************************************
def suite():
	"""Gather all the tests from this module in a test suite
	"""

	# Set up suit
	suite = unittest.TestSuite()
	
	# Add test suites
	suite.addTest(unittest.makeSuite(TestTextManipulation_0))
	suite.addTest(unittest.makeSuite(TestTextManipulation_1))
	suite.addTest(unittest.makeSuite(TestTextManipulation_2))
	suite.addTest(unittest.makeSuite(TestTextManipulation_3))
	suite.addTest(unittest.makeSuite(TestTextManipulation_4))

	return suite


if __name__ == '__main__':
	
	mySuite = suite()
	runner = unittest.TextTestRunner()
	runner.run(mySuite)