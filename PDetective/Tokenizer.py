import re
import nltk

class Tokenizer(object):

        def __init__(self):
            self.stemmer = nltk.PorterStemmer()
            self.punctPattern = re.compile(r"[,.'-]")
            self.wspcePattern = re.compile(r"[\s]+")
            self.filterPattern = re.compile(r"[^a-zA-Z|\s]")

        def PreProcess(self, text):
            '''
            Returns a preprocessed string
            '''
            processedText = re.sub(self.punctPattern, " ", text)            
            processedText = processedText.replace("'s", "").lower()
            processedText = processedText.replace("\n"," ")
            processedText = re.sub(self.filterPattern, " ", processedText)
            processedText = re.sub(self.wspcePattern, " ", processedText)            
            return processedText

##        def StemText(self, text):
##            '''
##            Stem text and filter stopwords
##            '''
##            #processedText = re.sub(self.filterPattern, " ", text).lower()
##            #processedText = re.sub(self.wspcePattern, " ", processedText)
##            filtered_words = [stemmer.stem(w) for w in processedText.split(" ") if w not in words("english")]       
##            return filtered_words

        def Tokenize(self, text):
            '''
            Tokenizes a given string using nltk's word tokenizer
            '''
            tokens = nltk.word_tokenize(text)
            filteredTokens = []            
            for token in tokens:
                if (token.strip() not in nltk.corpus.stopwords.words("english")):
                    filteredTokens.append(token)
                    
            del tokens
            return filteredTokens

        def TokenizeStem(self, text):
            '''
            Tokenizes a given string using nltk's word tokenizer
            '''
            tokens = nltk.word_tokenize(text)
            filteredTokens = []
            stemmedTokens = []
            for token in tokens:
                if (token.strip() not in nltk.corpus.stopwords.words("english")):
                    filteredTokens.append(token)
                    stemmedTokens.append(self.stemmer.stem(token))
            del tokens
            return (filteredTokens, stemmedTokens)

        def SentTokenize(self, text):
            '''
            Tokenize text by sentence using nltk's sentence tokenizer
            '''
            sentData = nltk.sent_tokenize(text)
            for i in range(len(sentData)):                 
                sentData[i] = sentData[i].replace("\n"," ").replace("'s","").lower()
                #sentData[i] = re.sub(self.punctPattern, " ", sentData[i])
                sentData[i] = re.sub(self.wspcePattern, " ", sentData[i])
            return sentData

        def ParagraphTokenize(self, text):
            '''
            Tokenize text by paragraph
            '''
            paragraphList = text.split("\n\n")
            for i in range(len(paragraphList)):
                paragraphList[i] = paragraphList[i].replace("\n"," ").lower().replace("'s"," ")
                paragraphList[i] = re.sub(self.filterPattern, " ", paragraphList[i])
                paragraphList[i] = re.sub(self.wspcePattern, " ", paragraphList[i]).strip()
            return paragraphList
