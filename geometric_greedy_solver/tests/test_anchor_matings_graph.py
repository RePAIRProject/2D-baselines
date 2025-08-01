import unittest
import sys
sys.path.append("geometric_greedy_solver")

from src.piece import Piece
from src.arbitrary_anchors import mating_graph 
from src.arbitrary_anchors.anchor_conf import AnchorConf
import matplotlib.pyplot as plt
from src.arbitrary_anchors import recipes
from src.assembler import physical_assemler


class TestAnchorMatingsGraph(unittest.TestCase):

    def test_toy_example(self):
        group = "RPobj_g28_o0028"
        piece1 = Piece("RPf_00194",group)
        piece2 = Piece("RPf_00197",group)

        anchors_confs = [
            AnchorConf([[734.4363693319759,1006.955673897721]] ,piece1),
            AnchorConf([[270.8407352941176,384.5944117647059]] ,piece1),
            AnchorConf([[66.6498978473929, 439.4158647440263]] ,piece2),
            AnchorConf([[683.2693400246188, 1164.8895464444654]] ,piece2)
        ]
        
        mating_graph.initGraph(anchors_confs)
        mating_graph.draw()

        plt.show()

        pairs2confs = mating_graph.get_confs_pairing()
        pair2response = recipes.simulate(pairs2confs,is_debug=True)

        pair2overlapping = {}
        for pair, res in pair2response.items():
            pair2overlapping[pair] = physical_assemler.score_pairwise(res)
        
        print(pair2overlapping)






if __name__ == "__main__":
    unittest.main()