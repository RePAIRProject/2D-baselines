from PIL import Image
import math
import src.shared_parameters as shared_parameters
import re
from shapely import Polygon as shapelyPolygon
from shapely import affinity
from src.assembler import physical_assemler

LOW_NOISE_TRANSPARENCY = 20        
ORIGINAL_TO_EXTRAPOLATION_SIZE_RATION = 2000/512

def _mask_transparency(piece_img):
    piece_mask = Image.new("L",piece_img.size,color=255)
    pixels = piece_img.load()

    for row in range(piece_img.size[0]):
        for col in range(piece_img.size[1]):
            if pixels[row,col][3] < LOW_NOISE_TRANSPARENCY:
                piece_mask.putpixel((row,col),0)

    return piece_mask


def _mask(piece_img,rot_radians):
    piece_mask = _mask_transparency(piece_img)
    rot_degrees= math.degrees(-rot_radians)
    rotated_mask = piece_mask.rotate(rot_degrees)
    
    return rotated_mask

def position_final_assembly_image(assembly_json,is_extrapolation=False,background_size=(3000,3000),piece_img_width=None):
    screen_center_x = background_size[0]//2
    screen_center_y = background_size[1]//2 

    first_piece_offset_x = None
    first_piece_offset_y = None
    positions = []

    for transformation in assembly_json[f"piecesFinalTransformations"]:
        piece_name = re.search("RPf_\d{5}",transformation["pieceId"]).group(0)
        piece = shared_parameters.active_pieces[piece_name]
        
        tx,ty = physical_assemler.get_final_translation_vector_unbias(assembly_json,piece)
        
        # The original images are 2000x2000 whereas the extrapolations are in 512x512
        if is_extrapolation:
            tx=tx//ORIGINAL_TO_EXTRAPOLATION_SIZE_RATION
            ty=ty//ORIGINAL_TO_EXTRAPOLATION_SIZE_RATION

        if first_piece_offset_x is None:
            first_piece_offset_x = tx
            first_piece_offset_y = ty
        
        tx = tx - first_piece_offset_x
        ty = ty - first_piece_offset_y
      

        if piece_img_width is None:
            if is_extrapolation:
                piece_img = piece.extrapolated_img
            else:
                piece_img = piece.original_img
                
            piece_img_width = piece_img.width

        # Because the origin is in the top-left corner
        pos_x = int(screen_center_x + tx - piece_img_width//2) 
        pos_y = int(screen_center_y + ty - piece_img_width//2)
        final_pos = (pos_x,pos_y)

        positions.append(final_pos)

    
    return positions 


def mask_final_assembly_image(assembly_json,is_extrapolation=False):
    masks = []

    for transformation in assembly_json[f"piecesFinalTransformations"]:
        piece_name = re.search("RPf_\d{5}",transformation["pieceId"]).group(0)
        piece = shared_parameters.active_pieces[piece_name]
        
        if is_extrapolation:
            piece_img = piece.extrapolated_img
        else:
            piece_img = piece.original_img

        piece_mask = _mask_transparency(piece_img)
        rot_degrees= math.degrees(-transformation["rotationRadians"])
        rotated_mask = piece_mask.rotate(rot_degrees)
        masks.append(rotated_mask)
    
    return masks

def rotate_pieces_img_final_assembly_image(assembly_json,is_extrapolation=False):
    imgs = []

    for transformation in assembly_json[f"piecesFinalTransformations"]:
        piece_name = re.search("RPf_\d{5}",transformation["pieceId"]).group(0)
        piece = shared_parameters.active_pieces[piece_name]
        
        if is_extrapolation:
            piece_img = piece.extrapolated_img
        else:
            piece_img = piece.original_img

        rot_degrees= math.degrees(-transformation["rotationRadians"])
        rotated_img = piece_img.rotate(rot_degrees)
        imgs.append(rotated_img)
    
    return imgs

def restore_final_assembly_image(assembly_json,is_extrapolation=False,background_size=(3000,3000)):
    background_img = Image.new("RGBA",background_size,color=0)
    
    positions = position_final_assembly_image(assembly_json,is_extrapolation=is_extrapolation,background_size=background_size)
    masks = mask_final_assembly_image(assembly_json,is_extrapolation=is_extrapolation)
    rotated_images = rotate_pieces_img_final_assembly_image(assembly_json,is_extrapolation=is_extrapolation)

    for img,(mask,pos) in zip(rotated_images,zip(masks,positions)):
        background_img.paste(img,box=pos,mask=mask)
    
    return background_img

    
