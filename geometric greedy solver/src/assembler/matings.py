class VertexMating():

    def __init__(self,first_piece_id,first_piece_coords, second_piece_id, second_piece_coords) -> None:
        self.first_piece_id = first_piece_id
        self.first_piece_coords = first_piece_coords
        self.second_piece_id = second_piece_id
        self.second_piece_coords = second_piece_coords

    def __repr__(self) -> str:
        return f"{self.first_piece_id}_{self.first_piece_coords}<--->{self.second_piece_id}_{self.second_piece_coords}"
    
    def __str__(self) -> str:
        return f"{self.first_piece_id},{self.first_piece_coords},{self.second_piece_id},{self.second_piece_coords}\r\n"
    
    def as_list(self):
        return [self.first_piece_id,self.first_piece_coords,self.second_piece_id,self.second_piece_coords]

    def as_dict(self):
        return {
                "firstPiece": self.first_piece_id,
                "firstPieceLocalCoords": self.first_piece_coords,
                "secondPiece": self.second_piece_id,
                "secondPieceLocalCoords": self.second_piece_coords
            }
