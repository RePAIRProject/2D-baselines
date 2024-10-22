import json
import pandas as pd
import numpy as np
import os
from PIL import Image

def frag_area(path):
    """
    Calculates the area of a fragment by counting the number of non-transparent pixels in the image.

    Args:
    -----
    path: str
        The path to the image file of the fragment.

    Returns:
    --------
    area: int
        The number of non-transparent pixels in the image.
    """
    image = np.array(Image.open(path).convert('RGBA'))
    mask = image[:, :, 3] > 0
    return np.abs(np.sum(mask))


def load_areas_matrix(root_dir):
    """
    Loads the areas of all fragments in a directory and return a matrix of the sum of the areas of each pair of fragments.

    Args:
    -----
    root_dir: str
        The path to the directory containing the fragments.

    Returns:
    --------
    areas_matrix: np.array
        A matrix of the sum of the areas of each pair of fragments.
    """
    paths = [os.path.join(root_dir, path) for path in os.listdir(root_dir) if path.endswith('.png')]
    areas = [frag_area(path) for path in paths]
    return np.array([[areas[i] + areas[j] for j in range(len(areas))] 
                     for i in range(len(areas))])


def load_adj_matrix(path):
    """
    Loads an adjacency matrix from a file.

    Args:
    -----
    path: str
        The path to the file containing the adjacency matrix.
        CSV files are expected to have each fragment name as a column with 1 indicating adjacency with another fragment.
        JSON files are expected to have a dictionary with fragment names as keys and a list of adjacent fragments as values.

    Returns:
    --------
    adj_matrix: np.array
        The adjacency matrix.
    """
    if path.endswith('.csv'):
        df = pd.read_csv(path)
        return df.values
    elif path.endswith('.json'):
        with open(path, 'r') as f:
            adj_dict = json.load(f)
        mat = [[1 if frag in adj_dict[frag2] else 0 for frag2 in adj_dict] for frag in adj_dict]
        return np.array(mat)
    
def prescision(adj_pred, adj_true, areas_matrix):
    """
    Calculates the prescision of the predicted adjacency matrix.

    Args:
    -----
    adj_pred: np.array
        The predicted adjacency matrix.

    adj_true: np.array
        The true adjacency matrix.

    areas_matrix: np.array
        The matrix of the sum of the areas of each pair of fragments.

    Returns:
    --------
    precision: float
        The prescision score of the predicted adjacency matrix.
    """
    both = np.logical_and(adj_pred, adj_true)
    both_areas = np.sum(both * areas_matrix)
    true_areas = np.sum(adj_true * areas_matrix)
    return both_areas / true_areas if true_areas > 0 else 0

def recall(adj_pred, adj_true, areas_matrix):
    """
    Calculates the recall of the predicted adjacency matrix.

    Args:
    -----
    adj_pred: np.array
        The predicted adjacency matrix.

    adj_true: np.array
        The true adjacency matrix.

    areas_matrix: np.array
        The matrix of the sum of the areas of each pair of fragments.

    Returns:
    --------
    recall: float
        The recall score of the predicted adjacency matrix.
    """
    both = np.logical_and(adj_pred, adj_true)
    both_areas = np.sum(both * areas_matrix)
    pred_areas = np.sum(adj_pred * areas_matrix)
    return both_areas / pred_areas if pred_areas > 0 else 0
    
def f1(adj_pred, adj_true, areas_matrix):
    """
    Calculates the F1 score of the predicted adjacency matrix.

    Args:
    -----
    adj_pred: np.array
        The predicted adjacency matrix.

    adj_true: np.array
        The true adjacency matrix.

    areas_matrix: np.array
        The matrix of the sum of the areas of each pair of fragments.

    Returns:
    --------
    f1: float
        The F1 score of the predicted adjacency matrix.
    """
    _prescision = prescision(adj_pred, adj_true, areas_matrix)
    _recall = recall(adj_pred, adj_true, areas_matrix)
    return 2 * _prescision * _recall / (_prescision + _recall) if _prescision + _recall > 0 else 0
    
def score(adj_pred, adj_true, areas_matrix):
    """
    Calculates the prescision, recall, and F1 score of the predicted adjacency matrix.

    Args:
    -----
    adj_pred: np.array
        The predicted adjacency matrix.

    adj_true: np.array
        The true adjacency matrix.

    areas_matrix: np.array
        The matrix of the sum of the areas of each pair of fragments.

    Returns:
    --------
    precision: float
        The prescision score of the predicted adjacency matrix.

    recall: float
        The recall score of the predicted adjacency matrix.

    f1: float
        The F1 score of the predicted adjacency matrix.
    """
    _precision = prescision(adj_pred, adj_true, areas_matrix)
    _recall = recall(adj_pred, adj_true, areas_matrix)
    _f1 = f1(adj_pred, adj_true, areas_matrix)
    return _precision, _recall, _f1

def score_batch(batch):
    """
    Scores several adjacency matrices and saves the results to a CSV file.

    Args:
    -----
    batch: list
        A list of (frag_dir, adj_pred_path, adj_true_path) tuples where:
        frag_dir: str
            The path to the directory containing the fragments.
        adj_pred_path: str
            The path to the file containing the predicted adjacency matrix.
        adj_true_path: str
            The path to the file containing the true adjacency matrix.

    Returns:
    --------
    None (saves the results to a CSV file named 'scores.csv' at cwd).
    """
    results = []
    for frag_dir, adj_pred_path, adj_true_path in batch:
        print(frag_dir)
        adj_pred = load_adj_matrix(adj_pred_path)
        adj_true = load_adj_matrix(adj_true_path)
        areas_matrix = load_areas_matrix(frag_dir)
        precision, recall, f1 = score(adj_pred, adj_true, areas_matrix)
        results.append([frag_dir, precision, recall, f1])
    results_df = pd.DataFrame(results, columns=['frag_dir', 'precision', 'recall', 'f1'])
    results_df.to_csv('scores.csv', index=False) 