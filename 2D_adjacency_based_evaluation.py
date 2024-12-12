import json
import pandas as pd
import numpy as np
import os
from PIL import Image
from skimage.filters import gaussian

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


def expanded_mask(path, tsfm, canvas_size=(10000, 10000), sig=16):
    """
    Create a mask of a fragment expanded by a Gaussian blur.

    Args:
    -----
    path: str
        The path to the image file of the fragment.

    tsfm: dict
        A dictionary containing the transformation parameters of the fragment.

    canvas_size: tuple
        The size of the canvas to paste the fragment on.

    sig: int
        The standard deviation of the Gaussian blur.

    Returns:
    --------
    mask: np.array
        The mask of the fragment expanded by a Gaussian blur.
    """
    image = Image.open(path).convert('RGBA').resize((2000, 2000)).rotate(tsfm['rot'], expand=True)
    canvas = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    height, width = image.size
    x, y = tsfm['offset']
    x, y = np.round(x).astype(int) - (height // 2) + 2500, np.round(y).astype(int) - (width // 2) + 2500
    canvas.paste(image, (x, y), image)
    mask = np.array(canvas)[:, :, 3]
    mask = gaussian(mask, sig)
    return mask > 0


def calc_adj_matrix(frag_paths, tsfm_path, csv_path='adj.csv', json_path='adj.json'):  
    """
    Calculate the adjacency matrix of a set of fragments.

    Args:
    -----
    frag_paths: list
        A list of paths to the fragment images.

    tsfm_path: str
        The path to the file containing the transformations of the fragments.

    csv_path: str
        The path to save the adjacency matrix as a CSV file.

    json_path: str
        The path to save the adjacency matrix as a JSON file.

    Returns:
    --------
    adj: np.array
        The adjacency matrix.
    """
    frag_paths.sort(key=lambda x: x.split('_')[1])
    tsfms = [
        {
            'rpf': tsfm['rpf'],
            'offset': (tsfm['x'], tsfm['y']),
            'rot': tsfm['rot'],
        }
    for tsfm in pd.read_csv(tsfm_path).to_dict(orient='records')]
    tsfms.sort(key=lambda x: x['rpf'])

    masks = [expanded_mask(frag, tsfm) for frag, tsfm in zip(frag_paths, tsfms)]
    n_frags = len(masks)
    
    adj = np.zeros((n_frags, n_frags))
    for i in range(n_frags):
        for j in range(i + 1, n_frags):
            if np.sum(np.logical_and(masks[i], masks[j])) > 0:
                adj[i, j] = adj[j, i] = 1

    frag_names = ["RPf_" + path.split('\\')[-1].split('_')[1] for path in frag_paths]
    if csv_path is not None:
        adj_df = pd.DataFrame(adj, columns=frag_names, index=frag_names)
        adj_df.to_csv(csv_path, index=False)

    if json_path is None:
        adj_dict = {}
        for i, frag in enumerate(frag_names):
            adj_dict[frag] = [frag_names[j] for j in range(n_frags) if adj[i, j] == 1]
        with open(json_path, 'w') as f:
            json.dump(adj_dict, f, indent=4)

    return adj
