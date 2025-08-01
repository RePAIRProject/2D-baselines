from src.piece import Piece
from functools import reduce

class AnchorConf():

    def __init__(self,anchor_points:list,parent_piece:Piece,**metadata) -> None:
        '''
            anchor_points - list of tuples of numbers
            parent_piece - piece to be anchored - the order in the list matters! (it determines the permutation)
        '''
        assert isinstance(anchor_points,list)
        self.anchor_points = anchor_points
        self.parent_piece = parent_piece
        self.__dict__.update(metadata)

    def __repr__(self) -> str:
        points_concatenated = reduce(lambda acc,x: acc+"&"+str(x),self.anchor_points,"")
        return f"{repr(self.parent_piece)}-{points_concatenated}"
    
    def get_num_anchors(self):
        return len(self.anchor_points)
