import nltk, re, os, sys, numpy, math, json
from nltk.corpus import stopwords
from Document import Document
from Tokenizer import Tokenizer
from Search import Search
import codecs
import time
import subprocess
import socket

class Detector(object):
    def __init__(self, suspdir, outdir, debug=False, w=50, k=5, training=False):
        self.filterPattern = re.compile(r"[^a-zA-Z|\s]")
        self.dataPath = suspdir
        self.outPath = outdir
        self.docs = []
        self.tokenizer = Tokenizer()
        self.searcher = Search()
        self.numDocs = 0
        print >> sys.stdout, "Loading data from: %s" % suspdir
        self.LoadData(suspdir, debug, w, k, training)
        self.WriteQueries(debug)

    def LoadData(self, path, debug, w, k, training):
        '''
        Load data from a directory and process it
        '''

        #Initialize TextTiling Tokenizer
        topicTokenizer = nltk.TextTilingTokenizer(w, k)

        #Crawl a given OS directory for text files
        for root,dirs,files in os.walk(path):
            for txtFile in files:                
                if txtFile.lower().startswith("readme"):
                    continue
                #Read text files
                if txtFile.endswith(".txt"):                    
                    if debug:
                        print >> sys.stdout, "Loading file: %s" % txtFile
                    self.numDocs += 1
                    f = open(os.path.join(path,txtFile), 'r')                    
                    text = f.read()
                    f.close()

                    #Create a document object
                    doc = Document()
                    doc.docId = txtFile[-7:-4]
                    doc.rawText = text

                    #Preprocess (punctuation and whitespace)
                    doc.processedText = self.tokenizer.PreProcess(text)

                    #Tokenize the document
                    doc.tokens = self.tokenizer.Tokenize(doc.processedText)                    

                    #Calculate frequency distribution
                    doc.text = nltk.Text(doc.tokens)
                    doc.fdist = nltk.FreqDist(doc.tokens)

                    #Get true sources (annotated dataset)
                    if (training):
                        f = open(os.path.join(path,'suspicious-document%s.json' % doc.docId), 'r')
                        jsonDoc = json.load(f)
                        for jDoc in jsonDoc['plagiarism']:
                            doc.trueSources.append(jDoc['source-url'])
                        f.close()

                    #Break document into topically related segments
                    doc.topics = topicTokenizer.tokenize(doc.rawText)                    

                    #Add document to list
                    self.docs.append(doc)

    def WriteQueries(self, debug):
        '''
        Formulate queries, the strategy is that unique words are probably the
        most representative of the segment, and as such unique words are
        extracted per 4-sentence chunk
        '''

        #KPMiner server process
        #If running from Linux
        #kpProcess = subprocess.Popen("java -jar KPMinerLinux.jar", shell = True)
        
        #If running from Windows
        kpProcess = subprocess.Popen("java -jar KPMiner.jar", shell = False)
        
        #Connect to the KPMiner server
        host = 'localhost'
        port = 54321
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

        
        for doc in self.docs:
            if debug:
                print >> sys.stdout, "Formulating queries of doc-%s" % doc.docId            

            #For each of the topics produced by the TextTiling algorithm
            for topic in doc.topics:
                #Get topic's keyphrase
                s.sendall(topic)                
                topicKp = s.recv(1024)
                topicKp = topicKp.split(" ")
                
                if debug:
                    print >>sys.stdout, topicKp

                #Get topic sentences
                topicSentences = self.tokenizer.SentTokenize(topic)

                #Group sentences into chunks of 4
                sentChunkSize = 4

                #Loops on chunks
                for i in range(0,len(topicSentences), sentChunkSize):
                    chunk = " ".join(topicSentences[i:i+sentChunkSize])
                    chunk = chunk.replace("-"," ")
                    chunk = chunk.replace("\n"," ")
                    chunk = re.sub(self.filterPattern, " ", chunk.strip())
                    chunk = re.sub(re.compile(r"[\s]+"), " ", chunk.strip())
                    #Get list of words in chunk after removing stopwords, and words < 3 characters
                    chunkWordList = [chunkWord for chunkWord in chunk.split(" ") 
                                if ( (chunkWord not in nltk.corpus.stopwords.words("english"))
                                     and (len(chunkWord) > 2) )]
                    
                    #List of unique/rare words in the chunk
                    rWords = []
                    for word in chunkWordList:
                        #Identify unique/rare words in the chunk
                        if doc.fdist[word] == 1:                            
                            rWords.append(word.strip())

                    #Get the rare words of the sentence
                    if len(rWords) > 0:
                        doc.rareWords.append(rWords)
                        
                        #Formulate the query
                        qList = []
                        if len(rWords) >= 1:
                            
                            #Index of the first rare word
                            wFIdx = chunkWordList.index(rWords[0])

                            #Consume rare words into the query
                            for rWord in rWords:
                                qList.append(chunkWordList.pop(chunkWordList.index(rWord)))

                            #Handle if sentence begins with a rare word
                            if wFIdx > 0:
                                qList += chunkWordList[wFIdx-1:]
                            else:
                               qList += chunkWordList[wFIdx:]


                        #Sort words by frequencies
                        def CompareWords(word1, word2):
                            return doc.text.count(word1) - doc.text.count(word2)
                        temp = set(qList)
                        qList = list(temp)
                        qList.sort(cmp=CompareWords)

                        #Simply pop the last > 10 items
                        while (len(qList) > 10):
                            qList.pop(-1)

                        for elem in topicKp:
                            if (elem not in qList):
                                qList.pop(-1)
                                qList.insert(0, elem)

                        if len(qList) > 3:
                            q = " ".join(set(qList)).replace("'s","")
                            q = re.sub(self.filterPattern, " ", q)
                            q = re.sub(re.compile(r"[\s]+"), " ", q)
                            doc.queries.append( (q, doc.topics.index(topic)) )

        s.sendall("Bye.")
        s.close()
        #Dirty call for terminating the server on Linux
        os.system("pkill java")      

    def DoSearch(self, MAX_RESULTS, MAX_SCORE, accessToken, sEngine, debug=False):
        for doc in self.docs:
            #For each document, search for candidate sources
            docCandidates = []
            numQueries = 0
            
            if debug:
                print >> sys.stdout, "Searching for queries of doc-%s" % doc.docId
            
            logFile = open(self.outPath + os.sep + "suspicious-document%s.log" % doc.docId,"w")
            
            #Search with the first query to obtain the first candidate
            query = doc.queries[0] #query = ("query text",topicId)
            numQueries += 1
            snippets = self.searcher.Search(logFile, doc.docId,
                                         query, accessToken,
                                         sEngine, MAX_RESULTS, debug)            
            
            #Check the first query: if snippet > score then download candidate
            #snippets = list of snippet dictionaries, dir(snippet) -> id, snippet
            for snippet in snippets:
                if (self.CheckQueryAgainstSnippet(query[0], snippet['snippet'], MAX_SCORE, debug)):
                    candidate = self.searcher.DownloadPage(doc.docId, query[1], snippet['id'], logFile, accessToken, debug)
                    candidate.tokens = self.tokenizer.Tokenize(self.tokenizer.PreProcess(candidate.rawText))
                    docCandidates.append(candidate)
                    if candidate.isSource:
                        doc.foundSources.append(candidate.longId)
                        doc.timeToFirstDetection = 1
            
            #For the rest of the queries, check the already downloaded pages,
            #if the query does not pass the similarity score with the document,
            #then download new ones
            for i in range(1,len(doc.queries)):
                query = doc.queries[i]
                #Check query against current list of candidates, if not, then search with it and get new candidates
                foundQueryCandidate = False
                if debug:
                    print >>sys.stdout, "query: " + query[0]

                for candidateDoc in docCandidates:
                    if ( (candidateDoc.isSource) and (candidateDoc.longId not in doc.foundSources) ):
                        doc.foundSources.append(candidateDoc.longId)
                        #Calculate time to first detection in queries
                        if doc.timeToFirstDetection == 0:
                            doc.timeToFirstDetection = numQueries                            
                    #Check query against candidate, if score higher than thresh,
                    #then candidate is a refined candidate
                    #The 0.6 score is hard-coded because it is the best performing
                    if (self.CheckQueryAgainstCandDoc(query[0], candidateDoc, 0.6, debug)):
                        #Query-level filtering for refined candidates                        
                        foundQueryCandidate = True
                        break

                #If query not in candidates, search again
                if not (foundQueryCandidate):
                    snippets = self.searcher.Search(logFile, doc.docId, query, accessToken, sEngine, MAX_RESULTS, debug)
                    numQueries += 1                    
                    for snippet in snippets:
                        if (self.CheckQueryAgainstSnippet(query[0], snippet['snippet'], MAX_SCORE, debug)):
                            candidate = self.searcher.DownloadPage(doc.docId, query[1], snippet['id'], logFile, accessToken, debug)
                            candidate.tokens = self.tokenizer.Tokenize(self.tokenizer.PreProcess(candidate.rawText))
                            docCandidates.append(candidate)
                            if ( (candidate.isSource) and (candidate.longId not in doc.foundSources) ):
                                doc.foundSources.append(candidate.longId)
                                if doc.timeToFirstDetection == 0:
                                    doc.timeToFirstDetection = numQueries

            doc.allCandidates = list(set(docCandidates))
            doc.numCandidates = len(doc.allCandidates)
            doc.numQueries = numQueries
            doc.precision = len(doc.foundSources)/float(doc.numCandidates)
            doc.recall = len(doc.foundSources)/float(len(doc.trueSources))
            if debug:
                print "prec = %f, rec = %f" % (doc.precision, doc.recall)
            logFile.close()

    def CheckQueryAgainstCandDoc(self, query, candidateDoc, MAX_SCORE, debug):
        '''
        Check if query belongs to the current candidate document
        '''
        score = self.Score(query, candidateDoc.tokens)
        if debug:
            print "Score against cand", score
        if (score >= MAX_SCORE):
            return True
        return False

    def CheckQueryAgainstSnippet(self, query, snippet, MAX_SCORE, debug):
        '''
        Check if query belongs to the current candidate document
        '''
        tokSnip = self.tokenizer.Tokenize(self.tokenizer.PreProcess(snippet))
        score = self.Score(query, tokSnip)
        if debug:
            print "score against snippet", score
        if (score >= MAX_SCORE):
            return True
        return False

    def Score(self, query, tokens):
        '''
        Score query against a tokenized documents
        '''
        numTokens = 0
        qTokens = query.split(" ")        
        for token in qTokens:            
            if token in tokens:                
                numTokens += 1
            
        return float(numTokens)/len(qTokens)


