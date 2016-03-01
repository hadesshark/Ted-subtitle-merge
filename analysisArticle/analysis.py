# -*- coding:utf-8 -*-
def FilterIgnorableChars( text ):
  punctuationMarks = '. \' ! ? , ; : ( ) { } [ ] - ‘ “ ‘ " ~ : ’ — & $ %'.split()
  numbers = []
  for i in range(0,10):
    numbers.append(str(i))

  filteredChars = punctuationMarks + numbers
  for p in filteredChars:
    text = text.replace(p,'')

  return text
 


filename = 'globishWords.txt'
articleFile = 'a.txt'
globishWords = [line.rstrip('\n') for line in open(filename)]
articleLines = [line.rstrip('\n') for line in open(articleFile)]
articleString = '\n'.join(articleLines).lower()




articleString = FilterIgnorableChars( articleString )
#print articleStringWithoutPunctuationMark
articleWords = articleString.split()
#print len(articleWords)
articleWordsWithoutDuplication = sorted(articleWords) #sorted(list(set(articleWords)))
#print articleWords
#print len(articleWordsWithoutDuplication)

matchedCount = 0
for word in articleWordsWithoutDuplication:
  if word in globishWords:
    matchedCount += 1

matchedPercent = int(100*float(matchedCount)/len(articleWordsWithoutDuplication)) 
print str(matchedPercent) + "%"
print articleWordsWithoutDuplication
#print punctuationMarks