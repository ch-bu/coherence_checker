# encoding: utf-8

import re
import constants
import subprocess
from pygermanet import load_germanet
from nltk.corpus import stopwords # We might need to remove this line
import itertools


def nounify(verb_word):
    """ Transform a verb to the closest noun: die -> death """

    gn = load_germanet()

    verb_synsets = gn.synsets(gn.lemmatise(verb_word)[0], pos="v")

    # Word not found
    if not verb_synsets:
        return []

    # Get all verb lemmas of the word
    verb_lemmas = [l.orthForm for s in verb_synsets for l in s.lemmas]

    # verb_lemmas = [l for s in verb_synsets \
    #                for l in s.lemmas if s.name.split('.')[1] == 'v']
    # print(verb_lemmas)

    print(gn.synsets('Haus')[0].lemmas[0].rels())
    # Get related forms
    # derivationally_related_forms = [(l, l.derivationally_related_forms()) \
    #                                 for l in verb_lemmas]

    # # filter only the nouns
    # related_noun_lemmas = [l for drf in derivationally_related_forms \
    #                        for l in drf[1] if l.synset.name.split('.')[1] == 'n']

    # # Extract the words from the lemmas
    # words = [l.name for l in related_noun_lemmas]
    # len_words = len(words)

    # # Build the result in the form of a list containing tuples (word, probability)
    # result = [(w, float(words.count(w))/len_words) for w in set(words)]
    # result.sort(key=lambda w: -w[1])

    # return all the possibilities sorted by probability
    return None

# print(nounify('arbeitet'))

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


def getHypernymPairs(sentences, gn):
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
                        for hypo in synset.hypernyms:
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
                                'hypernym'])

    return wordPairs


def get_coreferences(sentences, gn):
    """Extracts all unambigous
    coreferences

    Args:
        sentences (Array) - all sentences of the text
        gn (Object)       - pygermanet object

    Returns:
        Array of of pronoun and noun pairs
    """

    word_pairs = []

    # Loop over every sentence
    for val, sentence in enumerate(sentences):

        # Do not analyze last sentence
        if val != (len(sentences) - 1):

            # Get nouns and pronouns of current and next sentence
            current_sentence = filter(lambda x: x['noun'], sentence)
            nouns_next_sentence = filter(lambda x: x['noun'],
                                    sentences[val + 1])
            pronouns_next_sentence = filter(lambda x: x['pronoun'],
                                    sentences[val + 1])

            # Loop over every pronoun in next sentence
            for pronoun in pronouns_next_sentence:

                # Check if gender and numerus is unique among
                # the nouns within the next sentence
                unique_next = not any([pronoun['feminin'] == noun['feminin'] and
                          pronoun['singular'] == noun['singular'] and
                          pronoun['neutrum'] == noun['neutrum']
                          for noun in nouns_next_sentence])



                if unique_next:
                    # Check if gender and numerus is unique among
                    # the nouns within the current sentence
                    unique_current = [pronoun['feminin'] == noun['feminin'] and
                              pronoun['singular'] == noun['singular'] and
                              pronoun['neutrum'] == noun['neutrum']
                              for noun in current_sentence]

                    # We found a candidate
                    if sum(unique_current) == 1:
                        # Get index of anaphor parent
                        anaphor_parent = [i for i, x in enumerate(unique_current) if x][0]

                        # Get lemma of anaphor parent
                        lemma_parent = current_sentence[anaphor_parent]['lemma']

                        # Create word pairs
                        pairs = [[lemma_parent, noun['lemma'], 'coreference'] for noun in
                            nouns_next_sentence]

                        # Append pairs to word pairs
                        word_pairs = word_pairs + pairs

    return word_pairs


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
    tags = getPOSElement('neutrum', r'.*Neut', tags)
    tags = getPOSElement('noun', r'.*N.Name.*|.*N.Reg', tags)
    tags = getPOSElement('pronoun', r'.*PRO.Dem.*|.*PRO.Pers', tags)
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
    hyponym_pairs = getHyponymPairs(sentences, gn)

    # Get hypernym pairs
    hypernym_pairs = getHypernymPairs(sentences, gn)

    # Get coreference resolutions
    coreferences = get_coreferences(sentences, gn)

    # Merge lexical overlaps and hyponyms
    wordPairs = wordPairs + hyponym_pairs + hypernym_pairs + coreferences

    print(wordPairs)

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

text3 = """Das Wissen zeichnet einen Menschen aus. Sprachkenntnis zum
    Beispiel ist wichtig, da Menschen sonst nicht Sprechen können. Der Bezug
    zur Realität ermöglicht dies. Vor allem der Praxisbezug ist dabei wichtig.
    """

text4 = """Peter kam in das Zimmer herein. Er gab Petra eine Schockolade.
    Sie wurde von Hans gemocht."""

text5 = """Lernen ist für Menschen wichtig. Auswendiglernen kann
    immer gelingen. Es kann die Liebe sein oder
    der Knast. """

text6 = """Hans geht in die Schule. Er hat Bäume und Pflanzen. Die
    Blume zum Beispiel steht im Garten. Die Nelke ist die schönste Pflanze. Der
    Lehrer steht im Garten. Diese Lehrkraft macht gerne Scherze."""



print(analyzeTextCohesion(text2))
