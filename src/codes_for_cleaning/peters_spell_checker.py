import re, collections


try:
    import enchant
    d = enchant.Dict("fr_FR")
except:
    d = None

from nltk.stem.snowball import FrenchStemmer
#try:
#except:
 #   FrenchStemmer = None


stemmer = FrenchStemmer()

import sys
if sys.version_info[0] > 2:
    pass
else:
    # py2
    import codecs
    import warnings
    def open(file, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None, closefd=True, opener=None):
        if newline is not None:
            warnings.warn('newline is not supported in py2')
        if not closefd:
            warnings.warn('closefd is not supported in py2')
        if opener is not None:
            warnings.warn('opener is not supported in py2')
        return codecs.open(filename=file, mode=mode, encoding=encoding,
                    errors=errors, buffering=buffering)




def words(text): return re.findall('[a-z]+', text.lower()) 

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        if len(f) <= 2:
            continue
        model[f] += 1
    return model

NWORDS = train(words(open('big.txt', encoding="utf8").read()))
print(len(NWORDS))
to_remove = []

##Python 2 + 3 compatibility for dict.iteritems() ~ dict.items()
if sys.version_info[0] > 2:
    NWORDS_GENERATOR = NWORDS.items()
else:
    NWORDS_GENERATOR = NWORDS.iteritems()

for k,v in NWORDS_GENERATOR:
    if v <= 3:
        to_remove.append(k)
for k in to_remove:
    del NWORDS[k]
print("Cleaned",len(NWORDS))
#with open('french_dict2.txt', 'r', encoding="utf8") as f:
#    for word in f:
#        NWORDS[word.split()[0]] += int(word.split()[1])
#with open('french_dict.txt', 'r', encoding="utf8") as f:
#    for word in f:
#        NWORDS[word.split()[0]] += int(word.split()[1])

#NWORDS = train(big_set)


alphabet = u"""'abcdefghijklmnopqrstuvwxyzéâêîôûàèùçëïü"""

def edits1(word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def correct(word,treshold=60):
    '''
    returns (None or word(str), is_corrected(boolean))
    '''
    if known([word]) or (d.check(word) if d else False):
        return (stemmer.stem(word),False)
    #elif len(word) <= 2:
    #    return "BAD"
    candidates = known(edits1(word)) #or known_edits2(word)# or [word]
    #return max(candidates, key=NWORDS.get)
    #if not candidates:
    #    return "BAD"
    #return candidates
    cand = max(candidates, key=NWORDS.get) if candidates else None
    if cand and NWORDS.get(cand) >= treshold:
        #return cand, "stemmed:",stemmer.stem(cand), NWORDS.get(cand)
        return (stemmer.stem(cand), True)
    else:
        return (word, False)
    #return d.suggest(word)
