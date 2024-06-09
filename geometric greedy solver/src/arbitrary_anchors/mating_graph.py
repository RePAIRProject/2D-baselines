import networkx as nx
import matplotlib.pyplot as plt
from src.arbitrary_anchors.anchor_conf import AnchorConf

graph_ =  nx.Graph()
group2node_ = {}
piece2node_ = {}

pos_ = {}
PAIRING_DELIMITER = "<=>"
STRONG_SPRING_CONNECTION = 1
WEAK_SPRING_CONNECTION = 0.5

LINK_TYPE_SAME_PIECE = "same_piece"
LINK_TYPE_INTER_PIECE = "inter_piece"


def initGraph(anchor_confs:list):
    
    for conf in anchor_confs:
        assert isinstance(conf,AnchorConf)

    global graph_
    global group2node_
    global pos_
    global piece2node_

    graph_ = nx.Graph()

    for conf in anchor_confs:
        graph_.add_node(repr(conf),conf=conf)

    for ii,conf1 in enumerate(anchor_confs):
        for conf2 in anchor_confs[ii+1:]:
            
            edge_type = LINK_TYPE_SAME_PIECE
            pos_weight = STRONG_SPRING_CONNECTION

            if conf1.parent_piece != conf2.parent_piece:
                edge_type = LINK_TYPE_INTER_PIECE
                pos_weight = WEAK_SPRING_CONNECTION

            graph_.add_edge(repr(conf1),repr(conf2),edge_type=edge_type,pos_weight=pos_weight)
    
    pos_tmp = nx.shell_layout(graph_)  
    pos_ = nx.kamada_kawai_layout(graph_,pos=pos_tmp,weight="pos_weight")


# def get_node_name(anchor_point,piece):
#     return f"{repr(piece)}--{anchor_point}"

def get_inter_piece_edges(is_data=True):
    global graph_

    graph_links = graph_.edges(data=True)
    
    if is_data:
        return [(u,v,data) for u,v,data in graph_links if data["edge_type"] == LINK_TYPE_INTER_PIECE]
    else:
        return [(u,v) for u,v,data in graph_links if data["edge_type"] == LINK_TYPE_INTER_PIECE]
    
def get_confs_pairing()->dict:
    global graph_

    graph_links = graph_.edges(data=True)
    pairs = {}

    for u,v,data in graph_links:
        if data["edge_type"] == LINK_TYPE_INTER_PIECE:
            data_u = graph_.nodes[u]
            data_v = graph_.nodes[v]
            pairs[(u,v)] = (data_u["conf"],data_v["conf"])
    
    return pairs


def get_node_data(node):
    global graph_

    return graph_.nodes[node]

def draw( ax=None,**kwargs):
    global graph_
    global pos_

    if ax is None:
        ax = plt.subplot()

    
    pos_spaced = pos_ #nx.kamada_kawai_layout(graph_,pos=pos_,weight="draw_weight")
    
    nx.draw_networkx_nodes(graph_, pos=pos_spaced, node_color="skyblue",ax=ax)
    nx.draw_networkx_labels(graph_, pos=pos_spaced, font_size=8, font_color='black',ax=ax)

    graph_links = graph_.edges(data=True)

    inter_piece_links = []
    same_piece_links = []

    for u,v,data in graph_links:
        if data["edge_type"] == LINK_TYPE_SAME_PIECE:
            same_piece_links.append((u,v,data))
        elif data["edge_type"] == LINK_TYPE_INTER_PIECE:
            inter_piece_links.append((u,v,data))


    nx.draw_networkx_edges(graph_,pos=pos_spaced,edge_color="black",edgelist=same_piece_links,width=3,ax=ax)
    nx.draw_networkx_edges(graph_,pos=pos_spaced,edge_color="blue",edgelist=inter_piece_links,width=3,ax=ax)


def remove_edges(edges_to_remove:list):
    '''
        edges_to_remove - list of tuples
    '''
    global graph_
    global pos_

    graph_.remove_edges_from(edges_to_remove)
    pos_tmp = nx.shell_layout(graph_)  
    pos_ = nx.kamada_kawai_layout(graph_,pos=pos_tmp,weight="pos_weight")