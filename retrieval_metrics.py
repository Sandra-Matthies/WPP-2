import glob

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve
from tabulate import tabulate

# import pandas as pd
from retrieval import InitRetrievalSystem, RankedResult


def calculate_matrix(found, relevant):
    tp, tn, fp, fn = 0, 0, 0, 0
    for docID in found:
        contains = False
        for relID in relevant:
            if docID == relID:
                contains = True
                break
        if contains:
            tp += 1
        else:
            fp += 1
    fn = len(relevant) - tp
    return np.matrix([tp, tn, fp, fn])


def positionOf(val, lst):
    for i, curr in enumerate(lst):
        if curr == val:
            return i
    return -1


def get_query_by_id(query_id: int) -> str:
    query = ""
    for file in glob.iglob("./CISI/CISI.QRY.docs/" + str(query_id)):
        with open(file, "r") as f:
            lines = f.readlines()
            for l in range(0, len(lines)):
                query += lines[l]
    return query


def read_groundtruth(path):
    groundtruth = {}
    for file in glob.iglob(path):
        with open(file, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.split()
                if line[0] not in groundtruth:
                    groundtruth[line[0]] = [int(line[1])]
                else:
                    groundtruth[line[0]].append(int(line[1]))
    return groundtruth


def get_groundtruth_by_query_id(groundtruth, query_id):
    groundtruth_by_number = {}
    groundtruth_by_number = groundtruth[query_id]
    return groundtruth_by_number


def get_precision_score(y_true: list[int], y_pred: list[int]):
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
    confusion_matrix = calculate_matrix(y_pred, y_true)
    return confusion_matrix[0, 0] / (confusion_matrix[0, 0] + confusion_matrix[0, 2])


def get_recall_score(y_true: list[int], y_pred: list[int]):
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
    confusion_matrix = calculate_matrix(y_pred, y_true)
    return confusion_matrix[0, 0] / (confusion_matrix[0, 0] + confusion_matrix[0, 3])


def get_fscore(y_true: list[int], y_pred: list[int], beta=1.0):
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
    return (
        (beta**2 + 1)
        * get_recall_score(y_true, y_pred)
        * get_precision_score(y_true, y_pred)
    ) / (
        (
            get_recall_score(y_true, y_pred)
            + (beta**2) * get_precision_score(y_true, y_pred)
        )
    )


def get_precision_recall_fscore(y_true: list[int], y_pred: list[int], beta=1.0):
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
    precision, recall, f_measure = (
        get_precision_score(y_true, y_pred),
        get_recall_score(y_true, y_pred),
        get_fscore(y_true, y_pred, beta=beta),
    )
    return precision, recall, f_measure


def displayEvaluationInTable(header, data):
    print(tabulate(data, headers=header, tablefmt="grid"))


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

    def __init__(self, system: InitRetrievalSystem):
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
        confusion_matrix = calculate_matrix(
            self.retrieval_system.retrieve(get_query_by_id(query)), y_true
        )
        r_precision = confusion_matrix[0, 0] / (
            confusion_matrix[0, 0] + confusion_matrix[0, 3]
        )
        print("R-Precision: ", confusion_matrix)

        return r_precision

    def avp(self, query: str, y_true: list[int]):
        """_summary_

        Args:
            query (str): _description_
            y_true (list): _description_

        Returns:
         Average precision score for a given query and the ground trouth.
        """
        retrieval = self.retrieval_system.retrieve(query)
        retrieval_doc_ids = list(map(lambda x: x.doc_id, retrieval))

        s = get_precision_score(y_true, retrieval_doc_ids)
        print(f"S IS: {s}")
        return s

    def plot_precision_recall_curve(self, y_true: list[int], y_pred: list[int]):
        """
        Calculate the precision recall curve.

        Parameters
        ----------
        y_true : list
            List of known relevant documents for a given query.
        y_pred : list
            List of retrieved documents for a given query.

        Returns
        -------
        Tuple: (float, list, list)
            (11-point average precision score, recall levels, precision levels).
        """
        eleven_point_ap = []
        eleven_point_ar = []
        correct = 0

        for i in range(0, 10):
            if i < len(y_pred) and y_pred[i] in y_true:
                correct += 1
            eleven_point_ap.append(correct / (i + 1))
            eleven_point_ar.append(correct / len(y_pred))

        x_ys = list(zip(eleven_point_ar, eleven_point_ap))
        p = map(lambda x: x[1], x_ys)
        r = map(lambda x: x[0], x_ys)
        data = list(zip(range(1, 11), p, r))

        # No need to display the R-Precision separately as it is just one entry in the table.
        displayEvaluationInTable(header=["Top k", "R-Precision", "Recall"], data=data)

        def plot_curve():
            _, ax = plt.subplots()

            ax.plot(eleven_point_ar, eleven_point_ap, color="purple")
            plt.axis([0, 1, 0, 1])

            # add axis labels to plot
            ax.set_title("Precision-Recall Curve")
            ax.set_ylabel("Precision")
            ax.set_xlabel("Recall")

            # display plot
            plt.show()

        plot_curve()

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
        sum = 0
        for groundtruth in groundtruths:
            query = queries[: positionOf(groundtruth, queries)]
            retrievals = self.retrieval_system.retrieve(get_query_by_id(query))
            retrieved_docids = list(map(lambda x: x.doc_id, retrievals))
            # sum += get_precision_score(retrieved_docids, groundtruth)
        map_score = sum / len(groundtruths)
        return map_score


class Evaluation:
    @staticmethod
    def execute_evaluation(ir_system: InitRetrievalSystem):
        path = "./CISI/CISI.REL"
        all_groundtruths = read_groundtruth(path)
        groundtruths: dict[int, list[int]] = {}
        for id in range(1, 36):
            groundtruths[id] = get_groundtruth_by_query_id(all_groundtruths, str(id))

        retrievalScorer = RetrievalScorer(ir_system)

        retrievalsat_k = {
            5: ir_system.retrieve_k(query=get_query_by_id(1), k=5),
            10: ir_system.retrieve_k(query=get_query_by_id(1), k=10),
            20: ir_system.retrieve_k(query=get_query_by_id(1), k=20),
            50: ir_system.retrieve_k(query=get_query_by_id(1), k=50),
        }

        retrievals_eleven_point = {
            11: ir_system.retrieve_k(query=get_query_by_id(11), k=11),
            14: ir_system.retrieve_k(query=get_query_by_id(14), k=11),
            19: ir_system.retrieve_k(query=get_query_by_id(19), k=11),
            20: ir_system.retrieve_k(query=get_query_by_id(20), k=11),
        }

        # Precision@k means the proportion of the top k documents retrieved that
        # are relevant to the query.
        # k = 5
        retrieved_docids = list(map(lambda x: x.doc_id, retrievalsat_k[5]))
        precision_5 = get_precision_score(groundtruths[1], retrieved_docids)
        recall_5 = get_recall_score(groundtruths[1], retrieved_docids)
        f1_5 = get_fscore(groundtruths[1], retrieved_docids)

        # k = 10
        retrieved_docids = list(map(lambda x: x.doc_id, retrievalsat_k[10]))
        precision_10 = get_precision_score(groundtruths[1], retrieved_docids)
        recall_10 = get_recall_score(groundtruths[1], retrieved_docids)
        f1_10 = get_fscore(groundtruths[1], retrieved_docids)

        # k = 20
        retrieved_docids = list(map(lambda x: x.doc_id, retrievalsat_k[20]))
        precision_20 = get_precision_score(groundtruths[1], retrieved_docids)
        recall_20 = get_recall_score(groundtruths[1], retrieved_docids)
        f1_20 = get_fscore(groundtruths[1], retrieved_docids)
        # k = 50

        retrieved_docids = list(map(lambda x: x.doc_id, retrievalsat_k[50]))
        precision_50 = get_precision_score(groundtruths[1], retrieved_docids)
        recall_50 = get_recall_score(groundtruths[1], retrieved_docids)
        f1_50 = get_fscore(groundtruths[1], retrieved_docids)
        header = ["k", "Precision", "Recall", "F1 Score"]

        data = [
            ["5", precision_5, recall_5, f1_5],
            ["10", precision_10, recall_10, f1_10],
            ["20", precision_20, recall_20, f1_20],
            ["50", precision_50, recall_50, f1_50],
        ]
        print("Precision, Recall, F1 @ 5|10|20|50:")
        displayEvaluationInTable(data=data, header=header)

        # TODO
        # MAP = Mean Average Precision
        # Out Of Range ????
        # _map = retrievalScorer.MAP(query_ids, all_retriveals)
        # print("MAP: ", _map)

        # Precision-Recall Curves
        print("\nQuery 11:")
        retrievalScorer.plot_precision_recall_curve(
            groundtruths[11], list(map(lambda x: x.doc_id, retrievals_eleven_point[11]))
        )

        print("\nQuery 14:")
        retrievalScorer.plot_precision_recall_curve(
            groundtruths[14], list(map(lambda x: x.doc_id, retrievals_eleven_point[14]))
        )

        print("\nQuery 19:")
        retrievalScorer.plot_precision_recall_curve(
            groundtruths[19], list(map(lambda x: x.doc_id, retrievals_eleven_point[19]))
        )

        print("\nQuery 20:")
        retrievalScorer.plot_precision_recall_curve(
            groundtruths[20], list(map(lambda x: x.doc_id, retrievals_eleven_point[20]))
        )
