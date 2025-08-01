import os

DEBUG_COLORS = [
            [255,255,255],
            [255,0,0],
            [255,255,0],
            [0,255,0],
            [0,255,255],
            [0,0,255],
            [255,0,255],
            [255,77,0],
            [30,144,255],
            [173,255,47],        
            [255,4,0]]

DIR_OF_PIECES_IMAGES = f"REPAIR_DATASET_NIPS_24/2D_Fragments/2D_Images"
SPRING_SERVER = os.path.join("geometric_greedy_solver","springs_server","data","RePAIR")
PIECE_COORDS_DIR = os.path.join(SPRING_SERVER,"csv")
