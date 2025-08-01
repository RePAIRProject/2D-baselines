import unittest
import sys
sys.path.append("geometric_greedy_solver")

from src.piece import Piece
import matplotlib.pyplot as plt
import src.shared_parameters as shared_parameters

class TestLoadingPieceData(unittest.TestCase):

    def test_load_original_image(self,group="RPobj_g1_o0001",piece_id="RPf_00004"):
        piece = Piece(piece_id,group)
        img = piece.load_original_image()

        assert img.height == 2000 
        assert img.width == 2000 

        plt.imshow(img)
        plt.show()
    
    def test_load_polygon(self,group="RPobj_g1_o0001",piece_id="RPf_00004"):
        piece = Piece(piece_id,group)
        piece.load_polygon()

        xs,ys = piece.polygon.exterior.xy
        ax = plt.subplot()
        ax.plot(xs,ys)
        ax.set_xlim((0,2000))
        ax.set_ylim((0,2000))
        ax.invert_yaxis()
        plt.show()
        print(piece.polygon)
        
    def test_counted_in_active_pieces(self,group="RPobj_g1_o0001",piece_id="RPf_00004"):
        piece = Piece(piece_id,group)
        print(shared_parameters.active_pieces.keys())
        assert piece_id in shared_parameters.active_pieces.keys()


if __name__ == "__main__":
    unittest.main()