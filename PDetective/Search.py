#!/usr/bin/env python
#encoding:utf-8

import urllib2, urllib, sys, json, codecs, time, socket, re
from Document import Document, CandidateDocument
from Tokenizer import Tokenizer
from bs4 import BeautifulSoup

class Search(object):
   def __init__(self):
      pass
      
   def Search(self, logFile, docId, query, accessToken,
              sEngine = "chatnoir", maxResults = 3, debug = False):
      
      if (sEngine == "chatnoir"):
         searchUrl = 'http://webis15.medien.uni-weimar.de/proxy/chatnoir/batchquery.json'
      else:
         searchUrl = 'http://webis15.medien.uni-weimar.de/proxy/indri/batchquery.json'
         
      queryText = query[0]
      topicId = query[1]
      
      resultPagesRaw = []
      snippets = []
      resultPagesToken = []
      resultPagesStem = []
      resultPagesOracle = []
      result = None
      queryRequest = """
{
       "max-results": %d,
       "suspicious-docid":%s,
       "queries": [
         {
           "query-string": "%s"
         }
      ]
}
""" % (maxResults, re.sub("^0+","",docId), queryText)
      
      if debug:
         print >> sys.stdout, "Searching for: %s" % queryText

      event = str(int(time.time())) + " " + queryText + "\n"
      logFile.write(event)
      
      request = urllib2.Request(searchUrl, queryRequest)
      request.add_header("Content-Type","application/json")
      request.add_header("Accept","application/json")
      request.add_header("Authorization",accessToken)
      request.get_method = lambda: 'POST'

      try:
         connection = urllib2.urlopen(request, timeout=120)
         result = json.load(connection)
         if (type(result) is not dict):
            print >> sys.stderr, "Type error: result is None"
            time.sleep(10)
            self.Search(logFile, docId, query, accessToken,
              sEngine, maxResults, debug)
      except urllib2.HTTPError as e:
         
         time.sleep(5)
         print >> sys.stderr, "HTTP Error: calling Search() again"
         error_message = e.read()
         print >> sys.stderr, error_message
         self.Search(logFile, docId, query, accessToken,
              sEngine, maxResults, debug)
      except socket.timeout:
         
         time.sleep(5)
         print >> sys.stderr, "Socket timeout: calling Search() again"
         self.Search(logFile, docId, query, accessToken,
              sEngine, maxResults, debug)
         
      return self.ParseResponseAndGetSnippets(result, query, sEngine,
                                              logFile, docId, accessToken,
                                              maxResults, debug)

   def ParseResponseAndGetSnippets(self, result, query, sEngine, logFile,
                                   docId, accessToken,
                                   maxResults = 3, debug = False):
      try:         
         snippets = []
         
         if (type(result) is not dict):
            print >> sys.stderr, "error in the results"
            time.sleep(1)
            self.Search(logFile, docId, query, accessToken,
              sEngine, maxResults, debug)
         for sResult in result[sEngine + '-batch-results'][0]['result-data']:
            #Get longId from result
            longId = sResult['longid']
            
            #Get snippet of longId and the query that returned it
            url = 'http://webis15.medien.uni-weimar.de/chatnoir/snippet?'
            url += "id=" + str(longId)
            url += "&query=" + query[0].strip()
            request = urllib2.Request(url)
            try:
               response = json.load(urllib2.urlopen(request))               
               snippets.append(response)
            except urllib2.HTTPError as e:
               time.sleep(5)
               print >> sys.stderr, "HTTP error while getting snippet"
               error_message = e.read()
               print >> sys.stderr, error_message
               self.Search(logFile, docId, query, accessToken,
                             sEngine, maxResults, debug)
         return snippets         
         
      except TypeError as e:
         print >> sys.stderr, e
         time.sleep(5)
         print >> sys.stderr, "Snippet: caught type error, trying again"
         self.ParseResponseAndGetSnippets(result, query, sEngine,
                                              logFile, docId, accessToken,
                                              maxResults, debug)

   def DownloadPage(self, docId, topicId, longId, logFile, accessToken, debug):
      clueWebURL = "http://webis15.medien.uni-weimar.de/proxy/clueweb/id/"
      url = clueWebURL + str(longId)
      request = urllib2.Request(url)
      request.add_header("Accept","application/json")
      request.add_header("Authorization",accessToken)
      request.add_header("suspicious-docid", docId)
      request.get_method = lambda: 'GET'

      if debug:
         print >> sys.stdout, "Fetching result page id: %s" % longId
      
      try:
         connection = urllib2.urlopen(request, timeout=120)
         response = json.load(connection)
         logURL = "http://webis15.medien.uni-weimar.de/chatnoir/clueweb?id=" + str(longId)
         event = str(int(time.time())) + " " + logURL + "\n"
         logFile.write(event.encode('utf-8'))

         isDocSource = False
         if response['oracle'] == u"source":
            isDocSource = True
            if debug:
               print >> sys.stdout, "Found source: %s" % longId         

         return CandidateDocument(longId, topicId, response['text'], isDocSource)

      except urllib2.URLError as e:
         
         time.sleep(5)         
         print >> sys.stderr, "url error, fetching page again"
         error_message = e.read()
         print >> sys.stderr, error_message
         self.DownloadPage(docId, topicId, longId, logFile, accessToken, debug)
      except urllib2.HTTPError as e:
         
         time.sleep(5)
         print >> sys.stderr, "http error, fetching page again"
         error_message = e.read()
         print >> sys.stderr, error_message
         self.DownloadPage(docId, topicId, longId, logFile, accessToken, debug)
      except socket.timeout:
         
         time.sleep(5)
         print >> sys.stderr, "timeout, fetching page again"
         self.DownloadPage(docId, topicId, longId, logFile, accessToken, debug)   
