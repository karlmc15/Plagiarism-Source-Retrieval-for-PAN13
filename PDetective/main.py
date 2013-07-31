import PDetective, Search, Tokenizer, Document, Performance, sys

if __name__ == "__main__":
##    if len(sys.argv) == 4:
##        suspdir = sys.argv[1]
##        outdir  = sys.argv[2]
##        token   = sys.argv[3]
##        pDet = PDetective.Detector(suspdir, outdir)
##        pDet.DoSearch(2, 0.6, token, "chatnoir")
##        Performance.CalcPerformance(pDet, token)
##    else:
##        print'\n'.join(["Unexpected number of command line arguments.",
##        "Usage: ./pan13_source_retrieval_example.py {susp-dir} {out-dir} {token}"])
##    reload(PDetective)
##    reload(Search)
##    reload(Performance)

    suspdir = "/home/osama/Dropbox/NU/Text Mining/Plagiarism Detection/Dataset/texts"
    suspdir = "/home/gunny/Dropbox/NU/Text Mining/Plagiarism Detection/Dataset/texts5"
    outdir  = "/home/osama/Dropbox/NU/Text Mining/Plagiarism Detection/logs/"
    outdir  = "/home/gunny/Dropbox/NU/Text Mining/Plagiarism Detection/logs/"
    token   = "c114e249d2ecc65e5ac732da507d8496"

    pDet = PDetective.Detector(suspdir, outdir, True,80,30)#, 3, 6)
    pDet.DoSearch(1, 0.5, token, "chatnoir", True)
    #Performance.CalcPerformance(pDet)
    
    #pDet = PDetective.Detector(suspdir, outdir)#, 1, 4)
    #pDet.DoSearch(1, 0.6, token, "indri")
    #Performance.CalcPerformance(pDet)
