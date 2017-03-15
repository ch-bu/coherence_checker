# encoding: utf-8

import re
import constants
import subprocess
from pygermanet import load_germanet
from nltk.corpus import stopwords # We might need to remove this line
import itertools


def getPOSElement(element, regex, tags):
    """Returns an array with a boolean
    value of the specified element.
    If element exists, element is true.

    Args:
        element (String) - Element to be extracted
        regex (reg)      - Regular Expression
        tags (Array)     - List of word dictionaries
    Returns:
        Array of text elements
    """

    return [dict(tag.items() + {element: bool(re.match(regex,
        tag['pos']))}.items()) for tag in tags]


def getHyponymPairs(sentences, gn):
    """Generates all hyponmys of
    a list of nouns

    Returns:
        Array of hyponyms in lemma form
    """

    wordPairs = []

    for val, sentence in enumerate(sentences):

        if val != (len(sentences) - 1):
            for word in sentences[val]:
                if word['noun'] is True:
                    # Init hypo array
                    hypos = []

                    # Get all synsets of current word
                    synsets = gn.synsets(word['lemma'])

                    # Get all hyponyms of current word and append
                    for synset in synsets:
                        for hypo in synset.hyponyms:
                            for lemma in hypo.lemmas:
                                hypos.append(lemma.orthForm)

                    # Get next sentence
                    nextSentence = [wordNext['lemma']
                        for wordNext in sentences[val + 1] if wordNext['noun']]

                    # Get nouns of current sentence
                    sentence = [wordThis['lemma'] for wordThis in sentences[val]
                        if wordThis['noun']]

                    # Find common elements in hypos and next sentence
                    intersections = list(set(hypos).intersection(nextSentence))

                    # Loop over every intersections and append
                    for intersection in intersections:
                        if intersection != word['orth']:
                            wordPairs.append([word['lemma'], intersection,
                                'hyponym'])

    return wordPairs



def analyzeTextCohesion(text):
    """Analyzed the cohesion of a txt.
    Args:
        text (String) - A string that is Analyzed
    Returns:
        Array - An array of word pairs
    """

    # Check if text is string or unicode
    if type(text) is not str:
        raise TypeError('you did not pass a string as argument')

    # Remove brackets and parenthesis from text
    text = re.sub(r"[\(\[].*?[\)\]]", "", text)

    # If text doesn't end with a dot, fill it in
    if not text[-1:] in ['.', '!', '?']:
            text += '.'

    ############################################################################
    # Tag text
    ############################################################################
    # Save text to file
    f = open(constants.temp_text, 'w')
    f.write(text)
    f.close()

    # Tokenize
    f = open(constants.temp_tokens, 'w')
    subprocess.call([constants.tokenizer, constants.temp_text], \
        stdout=f, shell=False)
    f.close()

    # Tag Tokens from temp_tokens
    f = open(constants.temp_tags, 'w')
    subprocess.call([constants.rftagger, constants.german_par, \
        constants.temp_tokens], stdout=f, shell=False)
    f.close()

    # Read tags from file
    f = open(constants.temp_tags, 'r')
    tags = f.readlines()
    f.close()

    # Split tags in array
    tags = [str.split(tag, '\t') for tag in tags]

    # Remove last entry
    # the entry is only a \n character and can
    # be ignored. It is a percularity of the
    # RFTagger
    tags.pop()

    # Remove \n from end of tag
    tags = [[tag[0].decode('utf-8'), tag[1][:-1]] for tag in tags]

    ############################################################################
    # Further processing
    ############################################################################

    # Load germanet
    gn = load_germanet()

    # Lemmatise all words
    tags = [{'orth': tag[0], 'lemma': gn.lemmatise(tag[0])[0],
               'pos': tag[1]} for tag in tags]

    # Filter only relevant tags: Verbs, Nouns, Pronouns
    regex = re.compile(
        r'.*N.Name.*|.*N.Reg.*|.*SYM.Pun.Sent.*|.*VFIN.*|.*PRO.Pers.*|.*PRO.Dem')

    # Filtered tags
    tags = [tag for tag in tags if regex.match(tag['pos']) != None]

    # Get specific elements of words
    tags = getPOSElement('singular', r'.*Sg', tags)
    tags = getPOSElement('accusative', r'.*N.Reg.Acc', tags)
    tags = getPOSElement('dative', r'.*N.Reg.Dat', tags)
    tags = getPOSElement('nominative', r'.*N.Reg.Nom', tags)
    tags = getPOSElement('genitive', r'.*N.Reg.Gen', tags)
    tags = getPOSElement('feminin', r'.*Fem', tags)
    tags = getPOSElement('noun', r'.*N.Name.*|.*N.Reg', tags)
    # tags = getPOSElement('pronoun', r'.*PRO.Pers.*|.*PRO.Dem', tags)
    tags = getPOSElement('pronoun', r'.*PRO.Dem', tags)
    tags = getPOSElement('verb', r'.*VFIN', tags)

    # Get sentences
    sentences = []
    sentenceArray = []

    for word in tags:
        if word['pos'] != 'SYM.Pun.Sent':
                sentenceArray.append(word)
        else:
            sentences.append(sentenceArray)
            sentenceArray = []

    ############################################################################
    # Build word pairs
    ############################################################################

    # Init word pairs array
    wordPairs = []

    # Build lexical overlap word pairs
    for val, sentence in enumerate(sentences):
        nouns = [word['lemma'] for word in sentence if word['noun'] == True]
        for subset in itertools.combinations_with_replacement(nouns, 2):
            if subset[0] != subset[1]:
                pairArray = list(subset)
                pairArray.append('lexical overlap')
                wordPairs.append(pairArray)

    # Get hyponym pairs
    hyponymPairs = getHyponymPairs(sentences, gn)

    print(hyponymPairs)

    # Merge lexical overlaps and hyponyms
    wordPairs = wordPairs + hyponymPairs

    return None



text = """Im Folgenden möchte ich euch das Modell
    der Cognitive-Load-Theory erklären. Diese Theorie beschreibt die beim Lernen
    auftretenden Belastungen, bedingt durch die geringe Speicherkapazität
    des Arbeitsgedächtnisses. Laut der Cognitive-Load-Theory gibt es drei
    verschiedene Formen der Belastung: Die extrinsische Belastung,
    die Intrinsische-Belastung und die lernbezogene Belastung. Hierbei
    beschreibt die Extrinsische-Belastung äußere Einflüsse, die dem
    effizienten Lernen entgegenwirken. Eine große Rolle spielt die Ablenkung.
    Diese wird zum Beispiel gefördert, wenn ein Text nicht klar strukturiert
    ist, da der Lernende seinen Fokus zuerst auf das ordnen des Textes legen
    muss, bevor er den Inhalt verarbeiten kann. Ein weiteres Beispiel wäre
    eine zu detaillierte Erklärung für einen Lernenden mit hohem Vorwissen.
    In diesem Fall würde der Lernende von einer Informationsflut dessen,
    was er bereits gelernt hat, abgelenkt werden. Die Intrinsische-Belastung
    in der Cognitive-Load-Theory beschreibt die Belastung, die auf eine zu
    komplexe Art des Lernens zurückzuführen ist. Hier kann man beispielsweise
    das Verständnislernen anbringen: diese Art des Lernens ist wesentlich
    effizienter als das reine Auswendiglernen von Informationen, bedeutet
    jedoch gleichzeitig eine höhere Belastung, da man die neuen Informationen
    mit bereits Gelerntem in Bezug setzen muss. Dies führt zu einer
    Integration des neuen Wissens und somit zu einer Verknüpfung und
    besserem Verständnis kommt. Die Lernbezogene-Belastung tritt bei einer
    Kombination von hoher intrinsischer und niedriger Extrinsische-Belastung
    zustande.  Demnach beschreibt die Cognitive-Load-Theory die Belastung,
    der das menschliche Gehirn, besonders das Arbeitsgedächtnis, ausgesetzt.
    Das Spiel läuft. Das Fußballspiel macht heute Spaß."""

text2 = """Die Cognitive-Load-Theory geht davon aus, dass der Speicher des
    Arbeitsgedächtnisses, welchesInformationen verarbeitet, begrenzt ist.
    Daher muss eine Lehrkraft darauf achten, dass sie die Speicherung nicht
    überfordert. Dies kann passieren, wenn der Schüler zu vielen Belastungen
    auf einmal ausgesetzt ist. Man unterscheidet in drei Arten von Belastung.
    Den germane ( lernbezogenen), den extrinsic und den Intrinsic-Load.
    Unter dem Extrinsic-Load versteht man jene Belastung, die ausschließlich
    von außen kommt und den Schüler so am Lernen hindert. Zum Beispiel zu viel
    Lärm, keine konzentrierte Arbeitsatmosphäre oder Ablenkung anderer Art.
    Dieser kann vom Lehrenden beeinflusst werden. Der Lehrende sollte darauf
    achten, diese Belastung so gering wie möglich zu halten, um dem zu
    Lehrenden ein besseres Lernen zu ermöglichen.  Der Intrinsic-Load
    bezeichnet die Belastung, die zum Verstehen eines Themas auf den
    Schüler einwirkt. Sie ist stark abhängig vom Vorwissen des Schülers.
    Hat ein Schüler also hohes Vorwissen zu einem Thema, welches er
    bearbeiten muss, ist der Intrinsic-Load gering, d.h. er muss keine
    hohe kognitive Arbeit aufwenden, um das Thema zu verstehen, da er es
    leicht mit bereits Gelerntem verknüpfen kann. Der Germane-Load bezeichnet
    die kognitive Belastung eines Schülers beim Lernen und Verarbeiten des
    tatsächlich zu lernenden Stoffes. Also den kognitiven Aufwand zur
    Verknüpfung mit bereits gelernten Themen, dem Verstehen des aktuellen
    Themas und das Einordnen des Themas in den Gesamtzusammenhang des Faches.
    Auch diese Belastung ist vom Lehrenden beeinflussbar, zum Beispiel
    durch klare Erklärungen, stimmige Präsentation und Umfang und
    Zusammenhang der einzelnen Elemente.  Insgesamt sollte man darauf
    achten, dass der extrinsic und Intrinsic-Load möglichst gering
    gehalten werden, während der Germane-Load möglichst hoch sein sollte.
    Ist eine der anderen beiden Belastungen zu hoch, geht Speicherplatz
    und somit Kapazität für den Germane-Load verloren, was zu einem
    ineffizienten Lernen führt. Ein Fahrer geht nach Hause. Der
    LKW-Fahrer auch. Der Hund geht in das Kino. Dieser Dackel macht einem
    Probleme."""

print(analyzeTextCohesion(text))
