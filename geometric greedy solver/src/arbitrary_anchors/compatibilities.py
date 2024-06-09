from src.assembler import physical_assemler

def overlapping(pair2response:dict):
    pair2overlapping = {}
    for pair, res in pair2response.items():
        pair2overlapping[pair] = physical_assemler.score_pairwise(res)
    
    return pair2overlapping