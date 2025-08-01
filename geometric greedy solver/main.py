import sys
sys.path.append("geometric greedy solver")

import argparse
from src.piece import explore_group,Piece
from src.arbitrary_anchors.anchor_conf import AnchorConf
from src.arbitrary_anchors import mating_graph
from src.arbitrary_anchors import recipes
from src.arbitrary_anchors import compatibilities
from src import shared_parameters
import re
from src.assembler import physical_assemler
from src.assembler import restore_assembly_img
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path  


parser = argparse.ArgumentParser()
parser.add_argument("--groups", help="RPobj_g1_o0001") # 
parser.add_argument("--is_debug_final_assembly", action="store_true", help="Debug mode.",default=False)
parser.add_argument("--segmenting_curvedness_threshold",default="0.1")
parser.add_argument("--output_path")

args = parser.parse_args()

args_dict = vars(args)
args_inputted = {key:val for key, val in args_dict.items() if not val is None}

groups = [gr for gr in args.groups.split(",")]

print(f"Exploring groups {groups}")

pieces = []
for group in groups:
    pieces+= explore_group(group)

print("Segmenting")

anchor_confs = []
curvedness_threshold = eval(args_inputted["segmenting_curvedness_threshold"])
segmenting_points_to_index = {}

for piece in pieces:
    contour  = piece.get_polygon()
    segmenting_points = piece.segment_polygon_by_curvedness()
    num_segmenting_points = len(segmenting_points)
    
    for ii in range(num_segmenting_points):
        segmenting_point_1 = segmenting_points[ii].tolist()
        segmenting_point_2 = segmenting_points[(ii+1)%num_segmenting_points].tolist()
        
        segmenting_points_to_index[str(segmenting_point_1)] = ii
        segmenting_points_to_index[str(segmenting_point_2)] = (ii+1)%num_segmenting_points

        anchors = [segmenting_point_1,segmenting_point_2]
        anchor_confs.append(AnchorConf(anchors,piece))
        anchor_confs.append(AnchorConf(list(reversed(anchors)),piece))

        
print("Compute the mating graph")

mating_graph.initGraph(anchor_confs)
pieces_with_best_pairs = []
best_pairs = []
total_pieces_names = [piece.piece_id for piece in pieces]
pairs2confs = mating_graph.get_confs_pairing()
pair2response = recipes.simulate(pairs2confs)

for p,res in pair2response.items():
    assert not res["piecesFinalCoords"][0]["coordinates"][0][0] is None is None, f"{p} is problematic"

pair2overlapping = compatibilities.overlapping(pair2response)

while len(mating_graph.graph_.edges) > 0 and len(pieces_with_best_pairs) != len(total_pieces_names):
    best_pair = None
    min_overlapping = 999999999999

    for pair,overlapping in pair2overlapping.items():

        if pair in best_pairs:
            continue

        if overlapping < min_overlapping:
            best_pair = pair
            min_overlapping = overlapping

    best_pairs.append(best_pair)
    best_pair_parent1 = re.search("RPf_\d{5}",best_pair[0]).group(0)
    best_pair_parent2 = re.search("RPf_\d{5}",best_pair[1]).group(0)
    [pieces_with_best_pairs.append(parent) for parent in [best_pair_parent1,best_pair_parent2] if not parent in pieces_with_best_pairs]
    edges_to_remove = []

    for conf_pair in pair2overlapping.keys():
        parent1 = re.search("RPf_\d{5}",conf_pair[0]).group(0)
        parent2 = re.search("RPf_\d{5}",conf_pair[1]).group(0)

        if (best_pair_parent1 == parent1 and best_pair_parent2 == parent2) or (best_pair_parent1 == parent2 and best_pair_parent2 == parent1): 
            edges_to_remove.append(conf_pair)
            continue

        if best_pair[0] in conf_pair or best_pair[1] in conf_pair:
            edges_to_remove.append(conf_pair)
            continue

    for edge in edges_to_remove:
        del pair2overlapping[edge]


final_matings = []

for pair in best_pairs:
    conf = pairs2confs[pair]
    final_matings += recipes.conf_to_matings_(*conf)


print("Compute the final assembly")

response = physical_assemler.simulate(final_matings,collision="OffThenOn",isDebug=args.is_debug_final_assembly)

# if args.is_debug_final_assembly:

#     for piece in shared_parameters.active_pieces.values():
#         piece.load_original_image()

#     final_image = restore_assembly_img.restore_final_assembly_image(response,background_size=(5000,5000))
#     plt.imshow(final_image)
#     plt.show()

final_transfomations = physical_assemler.get_final_transformations(response)

df_output = pd.DataFrame(final_transfomations)

# Create output directory if it doesn't exist
output_path = Path(args_inputted["output_path"])
output_path.parent.mkdir(parents=True, exist_ok=True)

df_output.to_csv(args_inputted["output_path"],index=False)
print("finished")