import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, precision_score, recall_score, f1_score
from tabulate import tabulate

from retrieval import InitRetrievalSystem


def read_groundtruth(path):
    groundtruth = {}
    for file in glob.iglob(path):
        with open(file, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.split()
                if line[0] not in groundtruth:
                    groundtruth[line[0]] = [line[1]]
                else:
                    groundtruth[line[0]].append(line[1])
    return groundtruth
  
def get_groundtruth_by_query_id(groundtruth, query_id):
    groundtruth_by_number = {}
    groundtruth_by_number = groundtruth[query_id]
    return groundtruth_by_number

def precision_score(y_true, y_pred):
    """
        Calculates precision score for a list of relevant documents and the groundtruth.
        
        Parameters
        ----------
        y_true : list
            List of known relevant documents for a given query.
        y_pred : list
            List of retrieved documents.  
        
        Returns
        -------
        Score: float
            Precision = TP / (TP + FP)
    """
    return precision_score(y_true, y_pred)
    

def recall_score(y_true, y_pred):
    """
        Calculates recall score for a list of relevant documents and the groundtruth.
        
        Parameters
        ----------
        y_true : list
            List of known relevant documents for a given query.
        y_pred : list
            List of retrieved documents.  
        
        Returns
        -------
        Score: float
            Recall = TP / (TP + FN)
    """
    return recall_score(y_true, y_pred)

def fscore(y_true, y_pred, beta=1.0):
    """
        Calculates f-measure for a list of relevant documents and the groundtruth.
        
        Parameters
        ----------
        y_true : list
            List of known relevant documents for a given query.
        y_pred : list
            List of retrieved documents.  
        beta : float
            beta parameter weighting precision vs. recall
        
        Returns
        -------
        Score: float
            F-Measure = (1 + beta^2) \cdot \frac{Precision \cdot Recall}{beta^2 \cdot Precision+Recal}
    """
    f1_score(y_true, y_pred, beta=beta)

def precision_recall_fscore(y_true, y_pred, beta=1.0):
    """
        Convenience function, calculating precision, recall and f-measure.
        
        Parameters
        ----------
        y_true : list
            groundtrouth
            List of known relevant documents for a given query.
        y_pred : list
            manually retrived documents
            List of retrieved documents.  
        beta : float
            beta parameter weighting precision vs. recall
        
        Returns
        -------
        Score: tuple
            (precision, recall, f-measure)
    """
    precision, recall, f_measure = precision_score(y_true, y_pred), recall_score(y_true, y_pred),fscore(y_true, y_pred, beta=beta)
    return precision, recall, f_measure

def displayEvaluationInTable(header, data):
        print(tabulate(data, headers=header, tablefmt="grid"))

def plotPrecisionCurve(data, scores):
    # calculate precision and recall
    precision, recall, thresholds = precision_recall_curve(data, scores)

    # create precision recall curve
    fig, ax = plt.subplots()
    ax.plot(recall, precision, color="purple")

    # add axis labels to plot
    ax.set_title("Precision-Recall Curve")
    ax.set_ylabel("Precision")
    ax.set_xlabel("Recall")

    # display plot
    plt.show()
    
def execute_evaluation():
    path = "./CISI/CISI.REL"
    all_groundtruths = read_groundtruth(path)
    groundtruths = {}
    query_ids = [5,10,20, 50]
    for id in query_ids:
        groundtruths[id] = get_groundtruth_by_query_id(all_groundtruths, str(id))
        #print(groundtruths[id])
    print(groundtruths)
    
    retrieval = InitRetrievalSystem()
    retrievalScorer = RetrievalScorer()
    # 5
    query_5 =""
    r_precision_5 = retrievalScorer.rPrecision(groundtruths[5], query_5)
    average_precision_5 = retrievalScorer.aveP(query_5, groundtruths[5])
    # 10
    query_10 =""
    r_precision_10 = retrievalScorer.rPrecision(groundtruths[10], query_10)
    average_precision_10 = retrievalScorer.aveP(query_10, groundtruths[10])
    # 20    
    query_20 =""
    r_precision_20 = retrievalScorer.rPrecision(groundtruths[20], query_20)
    average_precision_20 = retrievalScorer.aveP(query_20, groundtruths[20])
    # 50
    query_50 =""
    r_precision_50 = retrievalScorer.rPrecision(groundtruths[50], query_50)
    average_precision_50 = retrievalScorer.aveP(query_50, groundtruths[50])
    
    map = retrievalScorer.MAP([query_5, query_10, query_20, query_50], [groundtruths[5], groundtruths[10], groundtruths[20], groundtruths[50]])
    
    header = ["Query", "R-Precision", "Average Precision"]
    data = [["5", r_precision_5, average_precision_5], ["10", r_precision_10, average_precision_10], ["20", r_precision_20, average_precision_20], ["50", r_precision_50, average_precision_50]]
    displayEvaluationInTable(data=data, header=header)
    print("MAP: ", map)
    
        
    
    

            
class RetrievalScorer:
    """
    Retrieval score system. 
    Provides functions like RScore, Average Precision and Mean-Average-Precision. 

    Attributes
    ----------
    retrieval_system : class object
           A Retrieval system. Must implement the abstract class InitRetrievalSystem.
    Methods
    -------
    rPrecision(y_true, query)
        Calculate the RScore.
    aveP(query, groundtruth)
        Calculate the average precision score for a query.
    MAP(queries, groundtruths)
        Calculate the mean average precision for a list of queries.

    """
    def __init__(self, system):
        """
        Initializes a RetrievalScorer class object
        
        Parameters
        ----------
        system : class object
            A retrieval system that implements InitRetrievalSystem.
        """
        self.retrieval_system = system
    
    def rPrecision(self, y_true, query):
        """
        Calculates the precision at R where R denotes the number of all relevant
        documents to a given query.
        
        Parameters
        ----------
        y_true : list
            List of known relevant documents for a given query.
        query : str
            A query.

        Returns
        -------
        Score: float
            R-precision = TP / (TP + FN)
        """
        r_precision = 0
        return r_precision
    
    def elevenPointAP(self, query, y_true):
        """
        Calculate the 11-point average precision score.
        
        Parameters
        ----------
        y_true : list
            List of known relevant documents for a given query.
        query : str
            A query.

        Returns
        -------
        Tuple: (float, list, list)
            (11-point average precision score, recall levels, precision levels).
        """
        eleven_point_ap = 0
        recall_levels = []
        precision_levels = []
        return eleven_point_ap, recall_levels, precision_levels
    
    def MAP(self, queries, groundtruths):
        """
        Calculate the mean average precision.
        
        Parameters
        ----------
        groundtruths : list(list)
            A double nested list. Each entry contains a list of known relevant documents for a given query.
        queries : list(str)
            A list of queries. Each query maps exactly to one groundtruth list in groundtruths.

        Returns
        -------
        Score: float
            MAP = frac{1}{|Q|} \cdot \sum_{q \in Q} AP(q).
        """
        
if __name__ == "__execute_evaluation__":
    execute_evaluation()     