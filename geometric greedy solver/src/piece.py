from src import DIR_OF_PIECES_IMAGES,PIECE_COORDS_DIR
from PIL import Image
from src.curvature import segment_polygon_contour_by_theshold
import src.shared_parameters as shared_parameters
from shapely import Polygon as ShapelyPolygon
import pandas as pd
from numpy import pi
import glob
import re


class Piece():

    def __init__(self,piece_id,group_id,
                 count_in_shared_parameters=True,original_img_path=None) -> None:
        self.piece_id = piece_id
        self.group_id = group_id

        self.polygon_coords_path = f"{PIECE_COORDS_DIR}/{piece_id}_intact_mesh.csv"
        self.polygon = None
        self.shifted_polygon = None # for debugging because of the RDP results (the "32 pixels shift problem....")
        self.segmenting_polygon_points = None

        # self.original_img_path = DIR_OF_PIECES_IMAGES+f'/group_{group_id}/{piece_id}_intact_mesh.png' if original_img_path is None else original_img_path
        self.original_img_path = f"{DIR_OF_PIECES_IMAGES}/{group_id}/{piece_id}_intact_mesh.png"
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
        return f"gr_{self.group_id}_frag_{self.piece_id}"
    
    def load_polygon(self):
        df_coords = pd.read_csv(self.polygon_coords_path)
        xs = df_coords["x"].values.tolist()
        ys = df_coords["y"].values.tolist()
        
        self.polygon = ShapelyPolygon(list(zip(xs,ys)))

        # For exaplaination to the shift: run test_compute_cropped_img_and_polygon in test_piece.py 
        xs_shifted = [x-32 for x in xs]
        ys_shifted = [y-32 for y in ys]
        self.shifted_polygon = ShapelyPolygon(list(zip(xs_shifted,ys_shifted)))

    def get_polygon(self):
        if self.polygon is None:
            self.load_polygon()
        
        return self.polygon
    
    def segment_polygon_by_curvedness(self,curvedness_threshold=0.2):
        xs,ys = self.polygon.exterior.xy
        self.segmenting_polygon_points = segment_polygon_contour_by_theshold(xs,ys,curvedness_threshold)

        return self.segmenting_polygon_points
    


def explore_group(group,pieces_images_path=None):
    if pieces_images_path is None:
        pieces_images_path =f"{DIR_OF_PIECES_IMAGES}/{group}" #f"{DIR_OF_PIECES_IMAGES}/group_{group}"
    pieces = []

    for piece_img_path in glob.glob(pieces_images_path+"/*"):
        file_name = piece_img_path.split("/")[-1]
        piece_name = re.search("RPf_\d{5}",file_name).group(0)
        piece = Piece(piece_name,group)
        pieces.append(piece)
    
    return pieces