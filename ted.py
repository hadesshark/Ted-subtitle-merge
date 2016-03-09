# -*- coding: utf8 -*-
import json
import os
import urllib2

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


DebugTagType = enum( 'GroupToParagraph', 'MergeSubtitles', 'PrintSubtitles', 'File' )

def InitDebugTags():
  debugTags = []
  #debugTags.append(DebugTagType.GroupToParagraph)
  #debugTags.append(DebugTagType.MergeSubtitles)
  debugTags.append(DebugTagType.PrintSubtitles)
  #debugTags.append(DebugTagType.File)

  return debugTags

debugTags = InitDebugTags()

class TedSubtitle(object):
  """docstring for TedSubtitle"""
  def __init__(self, startOfParagraph = True, startTime = 0, duration = 0, content = ''):
    super(TedSubtitle, self).__init__()
    self.startOfParagraph = startOfParagraph
    self.startTime = startTime / 1000
    self.duration = duration / 1000
    self.content = content
    self.endTime = self.startTime + self.duration



  def Description(self):
    return '\n'.join(["startTime : " + str(self.startTime),
                      "duration  : " + str(self.duration),
                      "content   : " + self.content.encode('utf8'),
                      ''])    


  def TrimNewLine(self):
    self.content = self.content.replace('\n','')




def GetSubtitles(talkID, languageCode):
  subtitleUrl = "http://www.ted.com/talks/subtitles/id/%s/lang/%s" % (talkID, languageCode)
  response = urllib2.urlopen(subtitleUrl)
  html = response.read() 
  subtitles = json.loads(html)["captions"]
  tedSubtitles = []
  for subtitle in subtitles:
    tedSubtitle = TedSubtitle(subtitle["startOfParagraph"], 
                              subtitle["startTime"], 
                              subtitle["duration"], 
                              subtitle["content"])
    tedSubtitles.append(tedSubtitle)

  return tedSubtitles




def json2srt(subtitles):

  def conv(t):
    return '%02d:%02d:%02d,%03d' % (
        t / 1000 / 60 / 60,
        t / 1000 / 60 % 60,
        t / 1000 % 60,
        t % 1000)




  for i, item in enumerate(subtitles):
    print (i,
           conv(item.startTime),
           conv(item.startTime + item.duration - 1),
           item.content)

def Difference( num1, num2 ):
  return abs( num1 - num2 )

def HasContainsEndMark(content):
  if len( content) < 2:
    return False

  endMarks = [ '.', '?', '!', '。', '？', '！' ]
  for i in endMarks:
    if content[-1].encode('utf8') == i:
      return True


  return False


def PrintSubtitles(subtitles):
 for i in range(len(subtitles)):
    print subtitles[i].Description()
    

def ResetStartTime(arr):
  for i in range(len(arr)):
    arr[i].startTime -= arr[0].startTime

  return arr

def HasEvenQuotes( content ):
  return content.count('"') % 2 == 0 

def HasPairChar( content ):
  leftChars =  [ u'「', u'(', u'（', u'{', u'【', u'｛', u'[']
  rightChars = [ u'」', u')', u'）', u'}', u'】', u'｝', u']']
  
  for i in range(len(leftChars)):
    if ( content.count(leftChars[i].encode('utf8')) == content.count(rightChars[i].encode('utf8')) ):
      return True

  return False

def IsNewParagraph(isStartOfParagraph, sentence):
  maxCharInSentence = 50
  
  newParagraph = isStartOfParagraph
  newParagraph = newParagraph or len(sentence) > maxCharInSentence
  newParagraph = newParagraph and HasEvenQuotes(sentence)
  newParagraph = newParagraph and HasContainsEndMark(sentence)
  newParagraph = newParagraph and HasPairChar(sentence.encode('utf8'))
  newParagraph = newParagraph and len(sentence) != 0
  newParagraph = newParagraph or len(sentence) > 150
  return newParagraph
  





   
talkURL = "http://www.ted.com/talks/richard_st_john_s_8_secrets_of_success"
##talkURL = "http://www.ted.com/talks/kenneth_cukier_big_data_is_better_data"
talkTitle = talkURL.split('/')[-1].replace('_',' ')

print talkTitle
print
#print '\n\n'
command = "curl -s %s | grep source=facebook | awk -F '=' '{print $3}' | awk -F '&' '{print $1}'" % ( talkURL )
talkID = os.popen(command).readlines()[0].strip()


chineselanguageCode = 'zh-tw'
englishlanguageCode = 'en'



engSubtitles = ResetStartTime(GetSubtitles( talkID, englishlanguageCode ))
chineseSubtitles = ResetStartTime(GetSubtitles( talkID, chineselanguageCode ))



def GroupToParagraph(subtitles):
  lastAddedIndex = 0
  lastAddedChar = ' '
  paragraphs = []
  paragraph = TedSubtitle()

  subtitles.insert(0, subtitles[0])

  for i in xrange(1,len(subtitles)):
    subtitle = subtitles[i]

    if paragraph.startOfParagraph:
      paragraph.startTime = subtitles[i-1].startTime
      paragraph.startOfParagraph = False    
    
    if IsNewParagraph(subtitle.startOfParagraph, paragraph.content):
      paragraph.TrimNewLine()
      if paragraph.duration == 0:
        paragraph.duration = subtitles[i-1].endTime


      paragraphs.append(paragraph)
      paragraph = TedSubtitle(content = subtitle.content)
      lastAddedIndex = i
    else:
      paragraph.content += subtitle.content
      paragraph.duration = subtitle.endTime
      

  if lastAddedIndex < len(subtitles):
    paragraphs.append(paragraph)


  return paragraphs




filteredChineseSubtitles = GroupToParagraph(chineseSubtitles)

if False:
  PrintSubtitles(filteredChineseSubtitles)



def MergeSubtitles( filteredChineseSubtitles, engSubtitles ):
  
  idxForEnglishSubtitles = 0
  lengthForChineseSubtitles = len(filteredChineseSubtitles)
  lengthForEnglishSubtitles = len(engSubtitles)
  
  lastObject = engSubtitles[lengthForEnglishSubtitles-1]
  lastObject.startTime = lastObject.endTime
  engSubtitles.append(lastObject)

  paragraph = TedSubtitle()

  filteredEnglishSubtitles = []
  for chineseSubtitle in filteredChineseSubtitles:
    currentDurationDifference = 0

    idxForLastEnglishSubtitles = idxForEnglishSubtitles

    if DebugTagType.MergeSubtitles in debugTags:
      print chineseSubtitle.content.encode('utf8')
  

    while idxForLastEnglishSubtitles < lengthForEnglishSubtitles:
      paragraph.duration = engSubtitles[idxForLastEnglishSubtitles + 1].startTime
      preDurationDifference = currentDurationDifference
      currentDurationDifference = chineseSubtitle.duration - paragraph.duration

      if DebugTagType.MergeSubtitles in debugTags:
        print chineseSubtitle.duration , paragraph.duration
        print

      if currentDurationDifference <= 0:
        if abs(preDurationDifference) >= abs(currentDurationDifference):
          idxForLastEnglishSubtitles += 1

        break

      idxForLastEnglishSubtitles += 1


    if DebugTagType.MergeSubtitles in debugTags:
      print "idx: ", idxForEnglishSubtitles, idxForLastEnglishSubtitles

    contents = [e.content for e in engSubtitles[idxForEnglishSubtitles:idxForLastEnglishSubtitles]]
    
    if DebugTagType.MergeSubtitles in debugTags:
      for k in contents:
        #pass
        print k

      print '-' * 20

    paragraph.content += ' '.join(contents)
    idxForEnglishSubtitles = idxForLastEnglishSubtitles

    paragraph.content = paragraph.content.replace('\n',' ')
    filteredEnglishSubtitles.append(paragraph)
    paragraph = TedSubtitle()

  return filteredEnglishSubtitles

filteredEnglishSubtitles = MergeSubtitles( filteredChineseSubtitles, engSubtitles )

def PrintResult(filteredChineseSubtitles, filteredEnglishSubtitles):
  indexOfSentenceNumber = 0
  indexOfFirstSentence = 1
  indexOfSecondSentence = 2
  numOfNewLine = 3

  contents = []
  for i in xrange(len(filteredChineseSubtitles)):    
    print i + 1
    print filteredEnglishSubtitles[i].content
    print #filteredChineseSubtitles[i].content.encode('utf8')
    print
    print

if DebugTagType.PrintSubtitles in debugTags:
  PrintResult(filteredChineseSubtitles, filteredEnglishSubtitles)

def ReadFileContent(filePath):
  fileRead = open(filePath, 'r')
  return fileRead.read().split('\n')


def WriteFileContent(filePath, content):
  fileWrite = open(filePath,'w')
  fileWrite.write(content) # python will convert \n to os.linesep
  fileWrite.close() 

if DebugTagType.File in debugTags:
  filePath = 'practice/49.txt'
  contents = ReadFileContent(filePath)
  indexOfFirstSentence = contents.index('1')
  lengthForChineseSubtitles = len(filteredChineseSubtitles)
  i = indexOfFirstSentence + 2

  idxForChineseSubtitles = 0
  while i < len(contents):
    hasTranslate = len(contents[i]) > 0

    if hasTranslate:
      contents[i] = filteredChineseSubtitles[idxForChineseSubtitles].content.encode('utf8')
    
    i += 5
    idxForChineseSubtitles += 1
    
  WriteFileContent(filePath,'\n'.join(contents))
