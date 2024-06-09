from shapely import Polygon as ShapelyPolygon
from shapely import affinity
import numpy as np

def polygon_translated(polygon:ShapelyPolygon,translate_x,translate_y,angle):
    translated_poly =  affinity.translate(polygon,translate_x,translate_y)
    translated_poly = affinity.rotate(translated_poly,angle)

    return translated_poly

def polygon_rotated(geom,degrees,**kwargs):
    return affinity.rotate(geom,degrees,**kwargs)
    
def point_translated_as_poly(point,polygon:ShapelyPolygon,translate_x,translate_y,angle):
    rotated_point = affinity.rotate(point,angle,origin=polygon.centroid) # Rotating by default by the polygon centroid could result in errors
    translted_point = affinity.translate(rotated_point,translate_x,translate_y)

    return translted_point




def center_of_mass(poly:ShapelyPolygon):   
    vertices = list(poly.exterior.coords)[:-1]
    # Initialize variables for weighted sums
    sum_x = 0
    sum_y = 0
    
    # Iterate through each edge of the polygon
    for i in range(len(vertices)):
        x_i, y_i = vertices[i]
        x_next, y_next = vertices[(i + 1) % len(vertices)]  # Use modulo to handle the last vertex
        
        # Calculate the midpoint of the edge
        mid_x = (x_i + x_next) / 2
        mid_y = (y_i + y_next) / 2
        
        # Update the weighted sums
        sum_x += mid_x
        sum_y += mid_y
    
    # Calculate the coordinates of the center of mass
    com_x = sum_x / len(vertices)
    com_y = sum_y / len(vertices)
    
    return com_x, com_y


