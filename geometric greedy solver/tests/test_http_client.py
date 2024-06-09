import sys
sys.path.append("geometric greedy solver")

import unittest
from src.assembler.my_http_client import SpringsHTTPClient 
import json


class TestHTTPClient(unittest.TestCase):
    
    def test_sanity(self):
        http = SpringsHTTPClient()
        print(http.send_sanity())



    def test_reconstruction_json(self):
        http = SpringsHTTPClient()
        matings = [
                {
                    "firstPiece": "RPf_00194_intact_mesh",
                    "firstPieceLocalCoords": [854,859],
                    "secondPiece": "RPf_00197_intact_mesh",
                    "secondPieceLocalCoords": [66,493]
                }
        ]

        body = {
            "matings":matings
        }

        encoded_body = json.dumps(body)
        res = http.send_reconstruct_request(encoded_body,isInteractive=True)
        print(res)


if __name__ == "__main__":
    unittest.main()