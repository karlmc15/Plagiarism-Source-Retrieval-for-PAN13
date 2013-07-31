import numpy, Search, sys
from Tokenizer import Tokenizer

tokenizer = Tokenizer()
def CalcPerformance(pDet):
    try:
        precisionArr = []
        recallArr = []
        timeArr = []
        querArr = []
        downArr = []
        noDetection = 0
        print >> sys.stdout, "Calculating performance of detection"    
        f = open("results.csv","w")
        pf = open("perf.log","a")
        #f.write("ID,Precision,Recall,numTokens\n")
    
        for doc in pDet.docs:
            #print >> sys.stdout, "Calculating performance of doc-%s" % doc.docId
            #For each document, we need to formulate the vector of it and
            #all its relevant documents, whether downloaded or true sources
            #The vector is to be all the words encountered in this
            #set of docs: candidates, true sources       

            
            #allCandSets = []
            #allCandSetsURL = []
##            for cand in doc.allCandidates:
##                cand.tokens, cand.stemmedTokens = tokenizer.TokenizeStem(tokenizer.PreProcess(cand.rawText))
##                allCandSets.append(set(cand.stemmedTokens))

            #Filter duplicates
##            uniqueCands = doc.allCandidates[:]
##            duplicateIndices = set()
##            for i in range(len(allCandSets)-1):
##                for j in range(i+1, len(allCandSets)):
##                    if (CompareSets(allCandSets[i], allCandSets[j], 0.9)):
##                        duplicateIndices.add(j)                    
##            
##            for index in sorted(duplicateIndices,reverse=True):
##                del uniqueCands[index]
##
##            numCorrect = 0
##            for uniqueCand in uniqueCands:
##                if (uniqueCand.isSource):
##                    numCorrect += 1

            recall = len(doc.foundSources) / float(len(doc.trueSources))
            if doc.numCandidates == 0:
                precision = 0
            else:
                precision = len(doc.foundSources) / float(doc.numCandidates)
            print >> sys.stdout, "For doc-%s, prec = %f, rec = %f" % (doc.docId, precision, recall)
            print >> pf, "For doc-%s, prec = %f, rec = %f" % (doc.docId, precision, recall)
            print >> sys.stdout, "For doc-%s, numQueries = %d, timeToFirstDetection = %d" % (doc.docId, doc.numQueries, doc.timeToFirstDetection)
            print >> pf, "For doc-%s, numQueries = %d, timeToFirstDetection = %d, numDownloads = %d" % (doc.docId, doc.numQueries, doc.timeToFirstDetection, doc.numCandidates)
            f.write("%s,%f,%f,%d,%d,%d,%d\n" % (doc.docId, precision, recall,
                                                len(doc.tokens),doc.numCandidates,
                                                doc.numQueries, doc.timeToFirstDetection))
            precisionArr.append(precision)
            recallArr.append(recall)        
            querArr.append(doc.numQueries)        
            downArr.append(doc.numCandidates)
            if doc.timeToFirstDetection == 0:
                noDetection += 1
                continue
            timeArr.append(doc.timeToFirstDetection)
    
        
        print "average precision = ", numpy.mean(precisionArr)
        print "average recall = ", numpy.mean(recallArr)
        print >>pf, "average precision = ", numpy.mean(precisionArr)
        print >>pf, "average recall = ", numpy.mean(recallArr)
        print "average number of queries = ", numpy.mean(querArr)
        print "average number of downloads = ", numpy.mean(downArr)
        print "average time to first detection = ", numpy.mean(timeArr)
        print "Number of non-detected docs = ", noDetection
        print >>pf,"average number of queries = ", numpy.mean(querArr)
        print >>pf,"average time to first detection = ", numpy.mean(timeArr)
        print >>pf,"average number of downloads = ", numpy.mean(downArr)
        print >>pf,"Number of non-detected docs = ", noDetection
        f.close()
        pf.close()
        
    except Exception:
        f.close()
        pf.close()
        
def CalcPerformanceSets(pDet, accessToken):
    '''
    Calculate precision and recall of the system
    '''
    
    precisionArr = []
    recallArr = []
    #Firstly need to filter out the sources from the candidates by filtering out duplicates?
    #Download the true sources in plaintext,
    print >> sys.stdout, "Calculating performance of detection"
    for doc in pDet.docs:
        print >> sys.stdout, "Calculating performance of doc-%s" % doc.docId
        #For each document, we need to formulate the vector of it and
        #all its relevant documents, whether downloaded or true sources
        #The vector is to be all the words encountered in this
        #set of docs: candidates, true sources
        trueSrcSets = []
        #corpusDocs.append(doc.stemmedTokens)            
        #Download true sources in plaintext and stem them and update vector          
        for src in doc.trueSources:
            stemPage = Search.DownloadPage(src, accessToken)
            trueSrcSets.append(set(stemPage))
            
        #doc.vectorWords.update()
        allCandSets = []
        allCandSetsURL = []
        for cand in doc.allCandidates:
            allCandSets.append(set(cand.stemmedTokens))
            allCandSetsURL.append(cand.URL)

        #Filter duplicates
        uniqueAllCands = allCandSets[:]
        uniqueAllCandsURLs = allCandSetsURL[:]
        duplicateIndices = set()
        for i in range(len(allCandSets)-1):
            for j in range(i+1, len(allCandSets)):
                if (CompareSets(allCandSets[i], allCandSets[j], 0.9)):
                    duplicateIndices.add(j)                    
        
        for index in sorted(duplicateIndices,reverse=True):
            del uniqueAllCands[index]
            del uniqueAllCandsURLs[index]

        #Find number of sources within cands
        srcsInCands = uniqueAllCands[:]
        srcsInCandsURLs = uniqueAllCandsURLs[:]
        sourceIndices = set()        
        for cand in uniqueAllCands:
           for truSrc in trueSrcSets:
                if (CompareSets(truSrc, cand, 0.9)):
                    sourceIndices.add(uniqueAllCands.index(cand))

        sources = []
        for index in sorted(sourceIndices,reverse=True):
            sources.append( (srcsInCands[index], srcsInCandsURLs[index]) )

        recall = len(sources) / float(len(doc.trueSources))
        precision = len(sources) / float(doc.numCandidates)
        print >> sys.stdout, "For doc-%s, prec = %f, rec = %f " % (doc.docId, precision, recall)
        precisionArr.append(precision)
        recallArr.append(recall)
        
    print "average precision = ", numpy.mean(precisionArr)
    print "average recall = ", numpy.mean(recallArr)
    
        
        
def CompareSets(Set1, Set2, thresh):
    score1 = len(Set1.intersection(Set2)) / float(len(Set1))
    score2 = len(Set2.intersection(Set1)) / float(len(Set2))
    score = max([score1, score2])
    if score >= thresh:
        return True
    return False
                                                
