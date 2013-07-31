import PDetective
import Search
import Tokenizer
import Document
import winsound
import CompareResults
import Performance
import sys
import os

if __name__ == "__main__":

    #suspdir = "C:\\Users\\Gunny\\Dropbox\\NU\\Text Mining\\Plagiarism Detection\\Dataset\\2halftexts"
    #suspdir = "C:\\Users\\Gunny\\Dropbox\\NU\\Text Mining\\Plagiarism Detection\\Dataset\\1halftexts"
    #suspdir = "C:\\Users\\Gunny\\Dropbox\\NU\\Text Mining\\Plagiarism Detection\\Dataset\\texts5"
    #suspdir = "C:\\Users\\Gunny\\Dropbox\\NU\\Text Mining\\Plagiarism Detection\\Dataset\\doc65"
    #suspdir = "C:\\Users\\Gunny\\Dropbox\\NU\\Text Mining\\Plagiarism Detection\\Dataset\\alltexts"
    #suspdir = "C:\\Users\\Gunny\\Dropbox\\NU\\Text Mining\\Plagiarism Detection\\Dataset\\docsmall"
    suspdir = "C:\\Users\\Gunny\\Dropbox\\NU\\Text Mining\\Plagiarism Detection\\Dataset\\texts5"
    outdir = "C:\\Users\\Gunny\\Dropbox\\NU\\Text Mining\\Plagiarism Detection\\logs"
    #token = "c114e249d2ecc65e5ac732da507d8496"
    token = "7eb96d7390b5f76d6fc4ffb175eaedac"
    
    if not (os.path.exists(suspdir)):
        raise IOError("suspect directory does not exist, please enter a valid path")
    if not (os.path.exists(outdir)):
        raise IOError("output directory does not exist, please enter a valid path")
    
    pDet = PDetective.Detector(suspdir, outdir, True, 50, 5, True)#, 3, 6)
    pDet.DoSearch(1, 0.5, token, "chatnoir", True)
    #Performance.CalcPerformance(pDet)
    
    winsound.Beep(3000,400)
    winsound.Beep(3000,400)
