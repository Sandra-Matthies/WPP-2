import glob
import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import average_precision_score, precision_recall_curve, precision_score, recall_score, f1_score
from tabulate import tabulate

from retrieval import InitRetrievalSystem

def get_query_by_id(query_id):
    for file in glob.iglob("./CISI/CISI.QRY"):
        with open(file, "r") as f:
            lines = f.readlines()
            query = ""
            for l in range(0,len(lines)-1):
                if lines[l].startswith('.I '+str(query_id)):
                    l+=2
                    while(not(lines[l].startswith('.I'))):
                        print(lines[l])
                        query += lines[l]
                        l+=1
    print(query)         
    return query

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

def get_precision_score(y_true, y_pred):
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
    

def get_recall_score(y_true, y_pred):
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

def get_fscore(y_true, y_pred, beta=1.0):
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

def get_precision_recall_fscore(y_true, y_pred, beta=1.0):
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
    precision, recall, f_measure = get_precision_score(y_true, y_pred), get_recall_score(y_true, y_pred), get_fscore(y_true, y_pred, beta=beta)
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
    
def main():
    get_query_by_id(1)
    path = "./CISI/CISI.REL"
    all_groundtruths = read_groundtruth(path)
    groundtruths = {}
    query_ids = [1, 2, 3 ,4, 5, 6, 7, 8, 9, 10, 11,12, 13, 14, 15,16, 17, 18, 19, 20, 21,22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
    for id in query_ids:
        groundtruths[id] = get_groundtruth_by_query_id(all_groundtruths, str(id))
        #print(groundtruths[id])
    print(groundtruths)
    
    retrieval = InitRetrievalSystem()
    retrievalScorer = RetrievalScorer()
    retrievalScorer.retrieval_system = retrieval
    all_retriveals = retrieval.retrieve()
    retrievals = {
        5:retrieval.retrieve(k=5),
        10:retrieval.retrieve(k=10),
        20:retrieval.retrieve(k=20),
        50:retrieval.retrieve(k=50)
        }
    # Precision@k means the proportion of the top k documents retrieved that are relevant to the query.
    # k = 5
    precision_5 = get_precision_score(retrievals[5], get_query_by_id(query_ids[0]))
    f1_5 = get_fscore(retrievals[5], get_query_by_id(query_ids[0]))
    # k = 10
    precision_10 = get_precision_score(retrievals[10], get_query_by_id(query_ids[0]))
    f1_10 = get_fscore(retrievals[10], get_query_by_id(query_ids[0]))
    # k = 20    
    precision_20 = get_precision_score(retrievals[20], get_query_by_id(query_ids[0]))
    f1_20 = get_fscore(retrievals[20], get_query_by_id(query_ids[0]))
    # k = 50
    precision_50 = get_precision_score(retrievals[50], get_query_by_id(query_ids[0]))
    f1_50 = get_fscore(retrievals[50], get_query_by_id(query_ids[0]))
    header = ["k","R-Precision", "F1 Score"]
    data = [["5", precision_5, f1_5], ["10", precision_10, f1_10], ["20", precision_20, f1_20], ["50", precision_50, f1_50]]
    displayEvaluationInTable(data=data, header=header)
    
    # MAP = Mean Average Precision 
    map = retrievalScorer.MAP(query_ids, all_retriveals)
    print("MAP: ", map)
    
    # R-Precision = Precision at Rank r
    r_precision = retrievalScorer.rPrecision(query_ids, all_retriveals)
    print("R-Precision: ", r_precision)
    
    # Precision-Recall Curve
    q11 = get_query_by_id(query_ids[10])
    q14 = get_query_by_id(query_ids[13])
    q19 = get_query_by_id(query_ids[18])
    q20 = get_query_by_id(query_ids[19])
    q11_res = retrievalScorer.elevenPointAP(q11, all_retriveals)
    plotPrecisionCurve(all_retriveals, q11_res)
    q14_res = retrievalScorer.elevenPointAP(q14, all_retriveals)
    plotPrecisionCurve(all_retriveals, q14_res)
    q19_res = retrievalScorer.elevenPointAP(q19, all_retriveals)
    plotPrecisionCurve(all_retriveals, q19_res)
    q20_res = retrievalScorer.elevenPointAP(q20, all_retriveals)
    plotPrecisionCurve(all_retriveals, q20_res)
            
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
        # TODO: get all relevant documents for a given query at rank r
        r_precision = get_precision_score(y_true, query)
        
        return r_precision
    
    def elevenPointAP(self, query: str, y_true: list):
        """
        Calculate the 11-point average precision score.
        
        Parameters
        ----------
        y_true : list
            groundtruth
            List of known relevant documents for a given query.
        query : str
            A query.

        Returns
        -------
        Tuple: (float, list, list)
            (11-point average precision score, recall levels, precision levels).
        """
        eleven_point_ap = average_precision_score(y_true, query)
        recall_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        precision_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        
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
        avg_precicions =[]
        for query in queries:
            avg_precicions.append(self.elevenPointAP(query, groundtruths))
            
        map_score = 1/len(queries) * sum(avg_precicions)
        return map_score
        
if __name__ == "__main__":
    main()     