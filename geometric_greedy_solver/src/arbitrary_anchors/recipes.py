from src.arbitrary_anchors.anchor_conf import AnchorConf
from src.assembler.matings import VertexMating
from src.assembler import physical_assemler


def conf_to_matings_(conf1:AnchorConf,conf2:AnchorConf):
    '''
        note - the order of the anchor_points of conf1 and conf2 matters!
    '''
    i = 0
    matings = []

    while i < conf1.get_num_anchors() and i < conf2.get_num_anchors():
        matings.append(
            VertexMating(conf1.parent_piece.get_full_name(),conf1.anchor_points[i],
                         conf2.parent_piece.get_full_name(),conf2.anchor_points[i]))
        i+=1
    
    return matings

def simulate(pairs2confs:dict,is_debug=False):
    '''
        conf_pairs - list of tuples of AnchorConf to simulate their overlapping
    '''
    pair2response = {}

    for pair,confs in pairs2confs.items():
        conf1,conf2 = confs
        
        matings = conf_to_matings_(conf1,conf2)
        response = physical_assemler.simulate(matings,isDebug=is_debug) # 
        pair2response[pair] = response

    return pair2response
