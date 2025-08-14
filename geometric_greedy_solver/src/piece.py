from src import DIR_OF_PIECES_IMAGES, PIECE_COORDS_DIR
from PIL import Image
from src.curvature import segment_polygon_contour_by_theshold
import src.shared_parameters as shared_parameters
from shapely import Polygon as ShapelyPolygon
import pandas as pd
from numpy import pi
import glob
import re


class Piece():

    def __init__(self, piece_id, original_img_path, polygon_coords_path,
                 count_in_shared_parameters=True) -> None:
        self.piece_id = piece_id
        self.group_id = None  # No longer needed for path construction

        self.polygon_coords_path = polygon_coords_path
        self.polygon = None
        self.shifted_polygon = None  # for debugging because of the RDP results (the "32 pixels shift problem....")
        self.segmenting_polygon_points = None

        self.original_img_path = original_img_path
        self.original_img = None
        self.original_cropped_img = None

        if count_in_shared_parameters:
            shared_parameters.active_pieces[piece_id] = self

    def get_full_name(self):
        return f"{self.piece_id}_intact_mesh"

    def load_original_image(self):
        self.original_img = Image.open(self.original_img_path)
        return self.original_img

    def __repr__(self) -> str:
        return f"frag_{self.piece_id}"

    def load_polygon(self):
        df_coords = pd.read_csv(self.polygon_coords_path)
        xs = df_coords["x"].values.tolist()
        ys = df_coords["y"].values.tolist()

        self.polygon = ShapelyPolygon(list(zip(xs, ys)))

        # For exaplaination to the shift: run test_compute_cropped_img_and_polygon in test_piece.py
        xs_shifted = [x - 32 for x in xs]
        ys_shifted = [y - 32 for y in ys]
        self.shifted_polygon = ShapelyPolygon(list(zip(xs_shifted, ys_shifted)))

    def get_polygon(self):
        if self.polygon is None:
            self.load_polygon()

        return self.polygon

    def segment_polygon_by_curvedness(self, curvedness_threshold=0.2):
        xs, ys = self.polygon.exterior.xy
        self.segmenting_polygon_points = segment_polygon_contour_by_theshold(xs, ys, curvedness_threshold)

        return self.segmenting_polygon_points


def explore_group(pieces_path, coordinates_path):
    pieces = []

    # Get all image files in the pieces directory
    piece_img_paths = sorted(glob.glob(f"{pieces_path}/*.png"))

    # Extract piece names from PNG files
    piece_names = []
    for img_path in piece_img_paths:
        img_filename = img_path.split("/")[-1]
        # Extract piece name from the filename (adjust pattern if needed)
        piece_match = re.search(r"RPf_\d{5}", img_filename)
        if piece_match:
            piece_name = piece_match.group(0)
        else:
            # Fallback: use filename without extension as piece name
            piece_name = img_filename.replace(".png", "").replace("_intact_mesh", "")
        piece_names.append(piece_name)

    # Get all CSV files in the coordinates directory
    all_coord_csv_paths = sorted(glob.glob(f"{coordinates_path}/*.csv"))

    # Filter CSV files to match only the piece names found in PNG files
    coord_csv_paths = []
    for piece_name in piece_names:
        matching_csv = None
        for csv_path in all_coord_csv_paths:
            csv_filename = csv_path.split("/")[-1]
            if piece_name in csv_filename:
                matching_csv = csv_path
                break

        if matching_csv is None:
            raise ValueError(f"No matching CSV file found for piece: {piece_name}")
        coord_csv_paths.append(matching_csv)

    # Ensure we have the same number of pieces and coordinate files
    if len(piece_img_paths) != len(coord_csv_paths):
        raise ValueError(f"Mismatch: {len(piece_img_paths)} piece images but {len(coord_csv_paths)} coordinate files")

    # Match pieces to coordinates by corresponding piece names
    for img_path, csv_path, piece_name in zip(piece_img_paths, coord_csv_paths, piece_names):
        piece = Piece(piece_name, img_path, csv_path)
        pieces.append(piece)

    return pieces