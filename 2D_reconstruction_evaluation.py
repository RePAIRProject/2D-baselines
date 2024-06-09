import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageChops
from scipy.ndimage import rotate
from sklearn.metrics import mean_squared_error


def get_all_csv_files(directory):
    csv_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            csv_files.append(os.path.join(directory, filename))
    return csv_files

def adjust_transformations(input_csv, output_csv, flip_xy=True, make_non_negative=True):
    transformations_df = pd.read_csv(input_csv)
    if flip_xy:
        temp = transformations_df['x']
        transformations_df['x'] = transformations_df['y']
        transformations_df['y'] = temp
        transformations_df['rot'] = transformations_df['rot']

    if make_non_negative:
        # get minimum value of X and Y
        min_x = transformations_df['x'].min()
        min_y = transformations_df['y'].min()

        # subtract the minimum value from X and Y
        if min_x < 0:
            transformations_df['x'] = transformations_df['x'] + abs(min_x)

        if min_y < 0:
            transformations_df['y'] = transformations_df['y'] + abs(min_y)
    
    # save the new CSV file
    transformations_df.to_csv(output_csv, index=False)


def find_largest_fragment(input_dir):
    max_area = 0
    largest_image = None

    for filename in os.listdir(input_dir):
        if filename.endswith(".png"):
            img_path = os.path.join(input_dir, filename)
            img = Image.open(img_path)
            img_array = np.array(img)

            alpha_channel = img_array[:, :, 3]
            non_transparent_pixels = np.sum(alpha_channel > 0)
            
            if non_transparent_pixels > max_area:
                max_area = non_transparent_pixels
                largest_image = filename

    return largest_image

def read_transformations(transformations_dir):
    """
    Read transformations from a csv file, and return a pandas dataframe of the form:
    | rpf (piece filename) | x (translation x) | y (translation y) | rot (rotation) | 
    """
    transformations = pd.read_csv(transformations_dir)
    return transformations


def calculate_shared_canvas_size(pieces_dir, transformations_dir, gt_transformations_dir):
    """ 
    Calculate the dimensions of the shared canvas that will be used to place all the pieces, after applying the transformations on them.
    """
    # Find the largest piece
    largest_piece = find_largest_fragment(pieces_dir)
    largest_piece_path = os.path.join(pieces_dir, largest_piece)
    largest_piece_img = Image.open(largest_piece_path)
    largest_piece_array = np.array(largest_piece_img)

    # Read transformations
    transformations = read_transformations(transformations_dir)
    gt_transformations = read_transformations(gt_transformations_dir)

    # Initialize the shared canvas size with the dimensions of the largest piece
    shared_canvas_width = largest_piece_array.shape[1]
    shared_canvas_height = largest_piece_array.shape[0]

    # Apply the transformations on the largest piece to find the shared canvas size
    for index, row in transformations.iterrows():
        piece_filename = row['rpf']
        x = int(row['x'])
        y = int(row['y'])
        rot = row['rot']

        piece_path = os.path.join(pieces_dir, piece_filename)
        piece_img = Image.open(piece_path)

        # Apply rotation directly on the PIL image
        rotated_piece = piece_img.rotate(rot,expand=True)

        # Calculate new canvas size
        new_width = max(rotated_piece.width, rotated_piece.width + abs(x))
        new_height = max(rotated_piece.height, rotated_piece.height + abs(y))

        # Create a new blank image with the new dimensions and the same mode as the rotated image
        new_piece = Image.new(rotated_piece.mode, (new_width, new_height))

        # Calculate position to paste the rotated image onto the new canvas
        paste_x = max(0, x)
        paste_y = max(0, y)

        # Paste the rotated image onto the new canvas
        new_piece.paste(rotated_piece, (paste_x, paste_y))


        # Update the shared canvas size
        shared_canvas_width = max(shared_canvas_width, new_piece.width)
        shared_canvas_height = max(shared_canvas_height, new_piece.height)

    for index, row in gt_transformations.iterrows():
        piece_filename = row['rpf']
        x = int(row['x'])
        y = int(row['y'])
        rot = row['rot']

        piece_path = os.path.join(pieces_dir, piece_filename)
        piece_img = Image.open(piece_path)

        # Apply rotation directly on the PIL image
        rotated_piece = piece_img.rotate(rot, expand=True)

        # Calculate new canvas size
        new_width = max(rotated_piece.width, rotated_piece.width + abs(x))
        new_height = max(rotated_piece.height, rotated_piece.height + abs(y))

        # Create a new blank image with the new dimensions and the same mode as the rotated image
        new_piece = Image.new(rotated_piece.mode, (new_width, new_height))

        # Calculate position to paste the rotated image onto the new canvas
        paste_x = max(0, x)
        paste_y = max(0, y)

        # Paste the rotated image onto the new canvas
        new_piece.paste(rotated_piece, (paste_x, paste_y))

        # Update the shared canvas size
        shared_canvas_width = max(shared_canvas_width, new_piece.width)
        shared_canvas_height = max(shared_canvas_height, new_piece.height)

    return shared_canvas_width, shared_canvas_height

def get_transformation_for_largest_piece(pieces_dir, results_csv_path, gt_csv_path, largest_piece=None):
    # Load the CSV files
    results_df = pd.read_csv(results_csv_path)
    gt_df = pd.read_csv(gt_csv_path)
    
    if largest_piece is None:
        # Find the largest piece using the existing function
        largest_piece = find_largest_fragment(pieces_dir)
    
    # Get the ground truth transformation for the largest piece
    gt_largest_piece = gt_df[gt_df['rpf'] == largest_piece].iloc[0]
    results_largest_piece = results_df[results_df['rpf'] == largest_piece].iloc[0]
    
    # Calculate the transformation difference for the largest piece
    dx = gt_largest_piece['x'] - results_largest_piece['x']
    dy = gt_largest_piece['y'] - results_largest_piece['y']
    drot = gt_largest_piece['rot'] - results_largest_piece['rot']

    transformation = {
        'x': int(dx),
        'y': int(dy),
        'rot': (drot + 360) % 360,
        'res_x': results_largest_piece['x'],
        'res_y': results_largest_piece['y'],
        'res_rot': results_largest_piece['rot'],
        'largest_piece_name': largest_piece
    }
    
    return transformation


def apply_transformations_on_piece(piece_img, x, y, rot, additional_x=0, additional_y=0, additional_rot=0):
        # Apply rotation directly on the PIL image
        rotated_piece = piece_img.rotate(rot, expand=False)
        if additional_rot != 0:
            rotated_piece = rotated_piece.rotate(additional_rot, expand=False)

        # Calculate new canvas size
        new_width = max(rotated_piece.width, rotated_piece.width + abs(x) + abs(additional_x))
        new_height = max(rotated_piece.height, rotated_piece.height + abs(y) + abs(additional_y))

        # Create a new blank image with the new dimensions and the same mode as the rotated image
        new_piece = Image.new(rotated_piece.mode, (new_width, new_height))

        # Calculate position to paste the rotated image onto the new canvas
        paste_x = max(0, x)
        if additional_x != 0:
            paste_x = max(0, paste_x + additional_x)
        paste_y = max(0, y)
        if additional_y != 0:
            paste_y = max(0, paste_y + additional_y)

        # Paste the rotated image onto the new canvas
        new_piece.paste(rotated_piece, (paste_x, paste_y))

        return new_piece


def calculate_area(piece):
    piece_array = np.array(piece)
    alpha_channel = piece_array[:, :, 3]
    area = np.sum(alpha_channel > 0)
    return area

def pad_and_fit_images(image1, image2):
    width1, height1 = image1.size
    width2, height2 = image2.size
    new_width = max(width1, width2)
    new_height = max(height1, height2)
    new_image1 = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    new_image2 = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    new_image1.paste(image1, (0, 0))
    new_image2.paste(image2, (0, 0))
    return new_image1, new_image2

def calculate_shared_area(piece1, piece2):
    piece1, piece2 = pad_and_fit_images(piece1, piece2)
    piece1 = np.array(piece1)[:, :, 3]
    piece2 = np.array(piece2)[:, :, 3]
    intersection = np.logical_and(piece1 > 0, piece2 > 0)
    shared_area = np.sum(intersection)
    return shared_area

def calculate_pieces_weights(pieces_dir, exclude_largest_piece=False, largest_piece=None):
    pieces_weights = {}
    pieces_areas = {}
    for filename in os.listdir(pieces_dir):
        if filename.endswith(".png"):
            piece_path = os.path.join(pieces_dir, filename)
            piece = Image.open(piece_path)
            area = calculate_area(piece)
            pieces_areas[filename] = area
    if exclude_largest_piece and largest_piece is not None:
        del pieces_areas[largest_piece]
    areas_sum = sum(pieces_areas.values())
    for filename in pieces_areas:
        pieces_weights[filename] = pieces_areas[filename] / areas_sum
    return pieces_weights


def calculate_position_score(pieces_dir, transformations_dir, gt_transformations_dir, log=False, debug=False):
    """
    Calculates the score of the placement of the pieces on the shared canvas.

    ::param pieces_dir: the directory containing the pieces
    ::param transformations_dir: the csv file containing the result transformations
    ::param gt_transformations_dir: the csv file containing the ground truth transformations
    ::param log: whether to print the intermediate results or not
    """

    transformations = read_transformations(transformations_dir)
    gt_transformations = read_transformations(gt_transformations_dir)

    # Initialize the shared canvas with the largest piece

    shared_canvas_width, shared_canvas_height = calculate_shared_canvas_size(pieces_dir, transformations_dir, gt_transformations_dir)
    

    additional_transformation = get_transformation_for_largest_piece(pieces_dir, transformations_dir, gt_transformations_dir)

    additional_x = additional_x_for_gt = additional_y = additional_y_for_gt = 0
    if additional_transformation['x'] < 0:
        additional_x_for_gt = abs(additional_transformation['x'])
    else:
        additional_x = additional_transformation['x']
    if additional_transformation['y'] < 0:
        additional_y_for_gt = abs(additional_transformation['y'])
    else:
        additional_y = additional_transformation['y']
    
    additional_rot = additional_transformation['rot']

    pieces_weights = calculate_pieces_weights(pieces_dir, exclude_largest_piece=True, largest_piece=additional_transformation['largest_piece_name'])

    q_pos = 0

    image_canvases = {}
    gt_image_canvases = {}

    # Apply the transformations on all the pieces then place them on the shared canvas
    for index, row in transformations.iterrows():
        piece_filename = row['rpf']
        x = int(row['x'])
        y = int(row['y'])
        rot = row['rot']
        gt_x = int(gt_transformations[gt_transformations['rpf'] == piece_filename].iloc[0]['x'])
        gt_y = int(gt_transformations[gt_transformations['rpf'] == piece_filename].iloc[0]['y'])
        gt_rot = int(gt_transformations[gt_transformations['rpf'] == piece_filename].iloc[0]['rot'])

        piece_path = os.path.join(pieces_dir, piece_filename)
        piece_img = Image.open(piece_path)

        new_piece = apply_transformations_on_piece(piece_img, x, y, rot, additional_x, additional_y)
        new_canvas = Image.new('RGBA', (shared_canvas_width, shared_canvas_height), (0, 0, 0, 0))
        new_canvas.alpha_composite(new_piece)
        image_canvases[piece_filename] = new_canvas

        gt_new_piece = apply_transformations_on_piece(piece_img, gt_x, gt_y, gt_rot, additional_x_for_gt, additional_y_for_gt)
        new_gt_canvas = Image.new('RGBA', (shared_canvas_width, shared_canvas_height), (0, 0, 0, 0))
        new_gt_canvas.alpha_composite(gt_new_piece)
        gt_image_canvases[piece_filename] = new_gt_canvas
    
    rotated_image_canvases = {}
    largest_piece = image_canvases[f'{additional_transformation["largest_piece_name"]}']
    non_alpha_bbox = Image.fromarray(np.array(largest_piece)[:, :, 3]).getbbox()
    center_x = (non_alpha_bbox[2] + non_alpha_bbox[0]) / 2
    center_y = (non_alpha_bbox[3] + non_alpha_bbox[1]) / 2
    rotated_largest_piece = largest_piece.rotate(additional_rot, expand=False, center=(center_x, center_y))
    rotated_image_canvases[f'{additional_transformation["largest_piece_name"]}'] = rotated_largest_piece
    for piece_filename in image_canvases:
        if piece_filename == f'{additional_transformation["largest_piece_name"]}':
            continue
        else:
            piece = image_canvases[piece_filename]
            rotated_piece = piece.rotate(additional_rot, expand=False, center=(center_x, center_y))
            rotated_image_canvases[piece_filename] = rotated_piece

    # Calculate the Q_pos score
    for piece_filename in image_canvases:
        if piece_filename != f'{additional_transformation["largest_piece_name"]}':
            piece_weight = pieces_weights[piece_filename]
            result_area = calculate_area(rotated_image_canvases[piece_filename])
            shared_area = calculate_shared_area(rotated_image_canvases[piece_filename], gt_image_canvases[piece_filename])
            partial_q_pos_score = piece_weight * (shared_area / result_area)

            if log:
                print(f"Piece: {piece_filename}")
                print(f"Piece weight: {piece_weight}")
                print(f"Result area: {result_area}")
                print(f"Shared area: {shared_area}")
                print(f"Partial Q_pos score: {partial_q_pos_score}")

            q_pos += partial_q_pos_score

    if log:
        print(f"Q_pos score: {q_pos}")    
    
    return q_pos if not debug else (q_pos, rotated_image_canvases, gt_image_canvases)


def calculate_rmse_with_anchor(pieces_dir, results_csv, ground_truth_csv, pxls_to_m_scaler=(1/7.369)): 
    # Load the CSV files into pandas DataFrames
    results_df = pd.read_csv(results_csv)
    ground_truth_df = pd.read_csv(ground_truth_csv)
    
    # Merge the DataFrames on the 'rpf' column to align the results with the ground truth
    merged_df = pd.merge(results_df, ground_truth_df, on='rpf', suffixes=('_result', '_gt'))

    # Get the transformation for the largest piece
    additional_transformation = get_transformation_for_largest_piece(pieces_dir, results_csv, ground_truth_csv)
    # remove the "largest_piece" from merged_df
    merged_df = merged_df[merged_df['rpf'] != additional_transformation['largest_piece_name']]
    merged_df['x_result'] = merged_df['x_result'] + additional_transformation['x']
    merged_df['y_result'] = merged_df['y_result'] + additional_transformation['y']
    merged_df['rot_result'] = (merged_df['rot_result'] + additional_transformation['rot']) % 360


    rmse_translation = np.average(np.sqrt((merged_df['x_result'] - merged_df['x_gt'])**2 + 
                                            (merged_df['y_result'] - merged_df['y_gt'])**2) * pxls_to_m_scaler) * 1/np.sqrt(2)

    rmse_rot = 1/np.sqrt(2) * np.average(np.sqrt((merged_df['rot_result'] % 360 - merged_df['rot_gt'] % 360)**2))

    rmse_values = {
        'RMSE_rot': rmse_rot % 360,
        'RMSE_translation': rmse_translation
    }

    return rmse_values


if __name__ == "__main__":
    
    # parse args to get the input variables pieces_dir, results_dir, ground_truth_dir, scores_dir (optional)
    parser = argparse.ArgumentParser()
    parser.add_argument('--pieces_dir', type=str, required=True, help='Path to the directory containing the pieces')
    parser.add_argument('--results_dir', type=str, required=True, help='Path to the directory containing the results csv files')
    parser.add_argument('--ground_truth_dir', type=str, required=True, help='Path to the directory containing the ground truth csv files')
    parser.add_argument('--scores_dir', type=str, required=False, help='Path to the directory to save the scores')
    args = parser.parse_args()

    pieces_base_dir = args.pieces_dir
    results_dir = args.results_dir
    ground_truth_dir = args.ground_truth_dir
    scores_dir = args.scores_dir

    print(f"Calculating scores for the pieces in {pieces_base_dir} using the results in {results_dir} and the ground truth in {ground_truth_dir}")

    if scores_dir is not None:
        if not os.path.exists(scores_dir):
            os.makedirs(scores_dir)
    scores_df = pd.DataFrame(columns=['object_name', 'Q_pos', 'RMSE_rot', 'RMSE_translation'])

    # get all filenames within dir "g2_2d_csv" but without the ".csv" extension
    object_names = [os.path.splitext(filename)[0] for filename in os.listdir("test_set_gt")]

    for obj in object_names:
        pieces_dir = os.path.join(pieces_base_dir, obj)
        results_csv = os.path.join(results_dir, f"{obj}.csv")
        ground_truth_csv = os.path.join(ground_truth_dir, f"{obj}.csv")

        q_pos = 0
        rmse_values = {}
        rmse_values['RMSE_rot'] = 0
        rmse_values['RMSE_translation'] = 0
        try:
            # calculate Q_pos
            q_pos = calculate_position_score(pieces_dir, results_csv, ground_truth_csv)
            # calculate RMSE
            rmse_values = calculate_rmse_with_anchor(pieces_dir, results_csv, ground_truth_csv)
            # save the scores in a dataframe
        except Exception as e:
            print(f"Error calculating scores for object {obj}: {e}")
        new_row = pd.DataFrame([{'object_name': obj, 'Q_pos': q_pos, 'RMSE_rot': rmse_values['RMSE_rot'], 'RMSE_translation': rmse_values['RMSE_translation']}])
        scores_df = pd.concat([scores_df, new_row], ignore_index=True)
        # rewrite the above line but in a way that will not show the warning: c:\Users\Ofir\OneDrive - post.bgu.ac.il\RePAIR\Code\Fragment_Registration_Based_Global_Evaluation\2D_reconstruction_evaluation.py:422: FutureWarning: The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.


    # fill in blank values with 0
    scores_df.fillna(0, inplace=True)

    if scores_dir is not None:
        if not os.path.exists(scores_dir):
            os.makedirs(scores_dir)
        scores_df.to_csv(os.path.join(scores_dir, 'scores.csv'), index=False)
    
    avg_q_pos = scores_df['Q_pos'].mean()
    avg_rmse_rot = scores_df['RMSE_rot'].mean()
    avg_rmse_translation = scores_df['RMSE_translation'].mean()

    print(f"Average Q_pos: {avg_q_pos}")
    print(f"Average RMSE_rot: {avg_rmse_rot}")
    print(f"Average RMSE_translation: {avg_rmse_translation}")

    

# Example usage:
# python 2D_reconstruction_evaluation.py --pieces_dir RePAIR_objects/ --results_dir derech_results/ --ground_truth_dir test_set_gt/ --scores_dir scores/