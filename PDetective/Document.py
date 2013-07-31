class Document(object):
    def __init__(self):
        self.docNumber = None
        self.docId = None
        self.rawText = None
        self.processedText = None
        self.stemmedTokens = None
        self.vectorWords = set()
        self.tokens = None
        self.topics = None
        self.keyPhrases = []
        self.allCandidates = []
        self.foundSources = []
        self.numCandidates = 0
        self.numQueries = 0
        self.numPossSources = 0
        self.timeToFirstDetection = 0
        self.trueSources = []
        self.precision = 0
        self.recall = 0
        self.sentences = None
        self.avgSentLen = None
        self.rareWords = []
        self.queries = []
        self.text = None
        self.fdist = None

class CandidateDocument(object):
    def __init__(self, longId, topicId, rawText, isSource):
    #def __init__(self, topicId, rawText, tokens, stemToks, URL, longId, isSource):
        self.topicId = topicId
        self.rawText = rawText
        self.tokens = None
        self.stemmedTokens = None        
        self.longId = longId
        self.isSource = isSource
