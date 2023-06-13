import math
from tabulate import tabulate
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt


class Ranking:
    @staticmethod
    def fastCosineScore(q, index, k):
        queryScores = {}
        for term in q:
            if term in index.index:
                wt = Ranking.getQueryWeight()
                for doc in index.index[term]:
                    queryScores[doc.doc_id] = queryScores.get(doc.doc_id, 0) + wt 
            for doc in queryScores:
                queryScores[doc] = queryScores[doc] / index.docLengths[doc]
        return queryScores[0:k]
         

    # tf = term frequency
    # df = document frequency
    # doc = document
    # n = number of documents
    # k = constant
    @staticmethod
    def getQueryWeight(tf, doc, k, df, n):
        return (tf / (tf + k * (doc.length/doc.avgDocLen)) * math.log(n/df) )
    
    
    @staticmethod
    def displayEvaluationInTable(header, data):
        print(tabulate(data, headers=header, tablefmt="grid"))
        
    @staticmethod
    def plotPrecisionCurve(data, scores):
        #calculate precision and recall
        precision, recall, thresholds = precision_recall_curve(data, scores)

        #create precision recall curve
        fig, ax = plt.subplots()
        ax.plot(recall, precision, color='purple')

        #add axis labels to plot
        ax.set_title('Precision-Recall Curve')
        ax.set_ylabel('Precision')
        ax.set_xlabel('Recall')

        #display plot
        plt.show()
        