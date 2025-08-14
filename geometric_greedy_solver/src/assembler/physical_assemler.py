from shapely import Polygon
from shapely import unary_union
from src.assembler.my_http_client import SpringsHTTPClient
from functools import reduce
import json
import numpy as np
from shapely import Point
from src.assembler import rigid_transformations
from shapely import affinity
import math
import re
from src import shared_parameters
from shapely import errors as shapely_errors
    


http_ = SpringsHTTPClient()

def simulate(matings,fixed_rotation={}, screenshot_name="",isInteractive=False,isDebug=False,collision="Off"):
    '''
        matings - list of VertexMating
    '''
    matings_as_list = [mating.as_dict() for mating in matings]

    body = {
        "matings":matings_as_list,
    }

    if len(fixed_rotation) > 0:
        body["fixedRotation"] = fixed_rotation

    encoded_body = json.dumps(body)
    response = http_.send_reconstruct_request(encoded_body,screenshot_name=screenshot_name,
                                                    isInteractive=isInteractive,isDebug=isDebug,collision=collision)

    return response

def semi_dice_coef_overlapping(polygons:list):
    shapely_polygons = [Polygon(poly) for poly in polygons]
    dice_sum = 0

    for i in range(len(shapely_polygons)):
        other_polygons = [shapely_polygons[j] for j in range(len(shapely_polygons)) if i!=j]    
        other_union = unary_union(other_polygons)
        try:
            curr_intersect_with_other = shapely_polygons[i].intersection(other_union)
        except shapely_errors.GEOSException as e:
            curr_intersect_with_other = shapely_polygons[i].buffer(0).intersection(other_union.buffer(0))
        dice_sum+= curr_intersect_with_other.area/shapely_polygons[i].area

    return dice_sum


def score_pairwise(response):
    polygons_coords = [piece_json["coordinates"] for piece_json in response["piecesFinalCoords"]] 
    overalap_area = semi_dice_coef_overlapping(polygons_coords)

    return overalap_area

def get_transformation_angle(response,key_,piece):
    for trans in response[key_]:
        if trans["pieceId"] == piece.get_full_name():
            return trans["rotationRadians"]

def get_coords(response,key_,piece):
    for coord_json in response[key_]:
        if coord_json["pieceId"] == piece.get_full_name():
            return coord_json["coordinates"]

def get_final_coords(response,piece):
    return get_coords(response,"piecesFinalCoords",piece)
        
def _get_tranlsation_vector(response,key_,piece,polygon_attr="polygon"):  
    piece_initial_polygon = getattr(piece,polygon_attr)
    initial_center_mass = rigid_transformations.center_of_mass(piece_initial_polygon)

    if key_ == "piecesFinalTransformations":
        piece_final_polygon = Polygon(get_final_coords(response,piece))
        final_center_mass = rigid_transformations.center_of_mass(piece_final_polygon)

    return int(final_center_mass[0]-initial_center_mass[0]),int(final_center_mass[1]-initial_center_mass[1])
    # return int(final_center_mass[0]),int(final_center_mass[1])


def get_final_tranlsation_vector(response,piece):
    return _get_tranlsation_vector(response,"piecesFinalTransformations",piece)

def get_final_translation_vector_unbias(response,piece,polygon_attr="polygon"):
    # piece_initial_polygon = getattr(piece,polygon_attr)
    # initial_center_mass = rigid_transformations.center_of_mass(piece_initial_polygon)

    # if key_ == "piecesFinalTransformations":
    piece_final_polygon = Polygon(get_final_coords(response,piece))
    final_center_mass = rigid_transformations.center_of_mass(piece_final_polygon)

    return int(final_center_mass[0]),int(final_center_mass[1])

def transform_geom_as_final_polygon(geom,response,piece,polygon_attr="polygon"):  
    '''
        geom : could be point, polygon....
    '''
    radians = get_transformation_angle(response,"piecesFinalTransformations",piece)
    degrees = math.degrees(radians)
    piece_initial_polygon = getattr(piece,polygon_attr)
    initial_center_mass = rigid_transformations.center_of_mass(piece_initial_polygon)
    geom_rotated = affinity.rotate(geom,degrees,origin=initial_center_mass)

    tx,ty = get_final_tranlsation_vector(response,piece)
    return affinity.translate(geom_rotated,tx,ty)


def get_final_transformations(response,scale=1,canvas_size=10000):
    transfomations = []

    first_piece_offset_x = None
    first_piece_offset_y = None

    for coords_json,transformation_json in zip(response["piecesFinalCoords"],response[f"piecesFinalTransformations"]):
        assert coords_json["pieceId"] == transformation_json["pieceId"]

        piece_final_polygon = Polygon(coords_json["coordinates"])
        final_center_mass = rigid_transformations.center_of_mass(piece_final_polygon)
        tx,ty = int(final_center_mass[0]),int(final_center_mass[1])

        # if first_piece_offset_x is None:
        #     first_piece_offset_x = tx
        #     first_piece_offset_y = ty
        
        # tx = tx - first_piece_offset_x
        # ty = ty - first_piece_offset_y

        tx = int(tx)
        ty = int(ty)

        degrees = math.degrees(-transformation_json["rotationRadians"])

        transfomations.append({
            "rpf":coords_json["pieceId"],
            "x":tx*scale,
            "y":ty*scale,
            "rot": degrees
        })
    
    return transfomations


