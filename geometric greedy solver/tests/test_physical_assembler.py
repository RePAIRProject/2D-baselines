import unittest
import sys
sys.path.append("geometric greedy solver")

from src.assembler import physical_assemler 
from src.assembler.my_http_client import SpringsHTTPClient
from src.assembler.matings import VertexMating
from src.assembler import restore_assembly_img 
from src.piece import Piece
import matplotlib.pyplot as plt
from shapely import Polygon,Point
from PIL import Image
from src.assembler import restore_assembly_img


class TestSimulation(unittest.TestCase):
    
    def test_toy_example_visual(self):
        http = SpringsHTTPClient()
        mating = VertexMating("RPf_00194_intact_mesh",[738,1002],"RPf_00197_intact_mesh",[55,448])
        fixed_rotation = [
            {
            "piece":"RPf_00194_intact_mesh",
            "initialAngleRadians": -2.4996993444444446 
            },
            {
                "piece":"RPf_00197_intact_mesh",
                "initialAngleRadians": -2.4281893375 
            }
        ]

        res = physical_assemler.simulate([mating],fixed_rotation=fixed_rotation,isDebug=True)
        print(res)
    
    def test_collision_OffThenOn(self):
        http = SpringsHTTPClient()
        mating = VertexMating("RPf_00194_intact_mesh",[738,1002],"RPf_00197_intact_mesh",[55,448])
        fixed_rotation = [
            {
            "piece":"RPf_00194_intact_mesh",
            "initialAngleRadians": -2.4996993444444446 
            },
            {
                "piece":"RPf_00197_intact_mesh",
                "initialAngleRadians": -2.4281893375 
            }
        ]

        res = physical_assemler.simulate([mating],fixed_rotation=fixed_rotation,isDebug=True,collision="OffThenOn")
        print(res)



class TestDataRetrieval(unittest.TestCase):
    toy_example_response = {
        "piecesFinalCoords": [
    {
        "coordinates": [
            [
                -692.0327758789063,
                -517.2882080078125
            ],
            [
                -753.76318359375,
                -598.388671875
            ],
            [
                -759.255859375,
                -656.1803588867188
            ],
            [
                -736.763427734375,
                -723.0162353515625
            ],
            [
                -748.8007202148438,
                -870.5973510742188
            ],
            [
                -722.7320556640625,
                -952.239013671875
            ],
            [
                -729.5603637695313,
                -969.8280639648438
            ],
            [
                -698.4271850585938,
                -1011.4783935546875
            ],
            [
                -695.5222778320313,
                -1070.483154296875
            ],
            [
                -610.1417236328125,
                -1082.8203125
            ],
            [
                -478.63623046875,
                -1141.831787109375
            ],
            [
                -365.651123046875,
                -1151.0135498046875
            ],
            [
                -319.2996826171875,
                -1181.2882080078125
            ],
            [
                -236.08778381347656,
                -1174.0218505859375
            ],
            [
                -169.728271484375,
                -1199.32861328125
            ],
            [
                -118.59559631347656,
                -1241.0108642578125
            ],
            [
                8.799076080322266,
                -1244.4156494140625
            ],
            [
                113.34657287597656,
                -1277.384033203125
            ],
            [
                154.8023223876953,
                -1242.650390625
            ],
            [
                158.10250854492188,
                -1180.255859375
            ],
            [
                181.16854858398438,
                -1139.2926025390625
            ],
            [
                244.48489379882813,
                -1066.99462890625
            ],
            [
                311.95208740234375,
                -1025.3028564453125
            ],
            [
                385.9634094238281,
                -893.8216552734375
            ],
            [
                376.33465576171875,
                -787.4059448242188
            ],
            [
                299.529052734375,
                -666.2825927734375
            ],
            [
                337.1410217285156,
                -534.5430297851563
            ],
            [
                340.6676940917969,
                -455.74853515625
            ],
            [
                317.8844299316406,
                -445.3115234375
            ],
            [
                242.0596923828125,
                -460.7896728515625
            ],
            [
                112.2698745727539,
                -454.1811828613281
            ],
            [
                65.63568115234375,
                -475.3059997558594
            ],
            [
                32.05156326293945,
                -465.4521789550781
            ],
            [
                -23.571012496948242,
                -479.562744140625
            ],
            [
                -72.74579620361328,
                -463.88385009765625
            ],
            [
                -127.9964370727539,
                -495.19488525390625
            ],
            [
                -145.77960205078125,
                -484.7659912109375
            ],
            [
                -291.83099365234375,
                -516.5314331054688
            ],
            [
                -338.2143859863281,
                -506.25701904296875
            ],
            [
                -378.8451843261719,
                -525.3915405273438
            ],
            [
                -454.2174072265625,
                -508.0704345703125
            ],
            [
                -531.0535278320313,
                -530.547119140625
            ],
            [
                -576.4179077148438,
                -508.2740478515625
            ],
            [
                -598.4406127929688,
                -522.2387084960938
            ]
        ],
        "pieceId": "RPf_00194_intact_mesh"
    },
    {
        "coordinates": [
            [
                -533.83349609375,
                -1125.452880859375
            ],
            [
                -615.0150146484375,
                -1228.775390625
            ],
            [
                -621.121826171875,
                -1244.6407470703125
            ],
            [
                -608.0775146484375,
                -1250.5440673828125
            ],
            [
                -671.40673828125,
                -1253.7752685546875
            ],
            [
                -704.2393188476563,
                -1305.995849609375
            ],
            [
                -688.9309692382813,
                -1536.088623046875
            ],
            [
                -704.7018432617188,
                -1685.9561767578125
            ],
            [
                -679.7294311523438,
                -1782.0467529296875
            ],
            [
                -698.921630859375,
                -1851.556884765625
            ],
            [
                -675.5933227539063,
                -1921.2979736328125
            ],
            [
                -685.2850341796875,
                -2094.9990234375
            ],
            [
                -588.7675170898438,
                -2182.0703125
            ],
            [
                -522.8209228515625,
                -2181.86376953125
            ],
            [
                -503.98870849609375,
                -2195.98291015625
            ],
            [
                -428.5616760253906,
                -2182.28125
            ],
            [
                -279.1890869140625,
                -2185.25537109375
            ],
            [
                -233.65830993652344,
                -2202.718017578125
            ],
            [
                -161.09608459472656,
                -2179.593505859375
            ],
            [
                -40.51446533203125,
                -2218.065185546875
            ],
            [
                18.14556121826172,
                -2191.102294921875
            ],
            [
                79.96224975585938,
                -2189.179931640625
            ],
            [
                275.01104736328125,
                -2217.42578125
            ],
            [
                411.9195861816406,
                -2176.96435546875
            ],
            [
                463.703125,
                -2186.370849609375
            ],
            [
                475.43524169921875,
                -2121.993896484375
            ],
            [
                460.46875,
                -2054.27392578125
            ],
            [
                420.8688659667969,
                -1984.068359375
            ],
            [
                376.55828857421875,
                -1949.6793212890625
            ],
            [
                316.8172607421875,
                -1863.8424072265625
            ],
            [
                317.0919189453125,
                -1830.541748046875
            ],
            [
                299.4232177734375,
                -1810.1259765625
            ],
            [
                303.4753723144531,
                -1704.7857666015625
            ],
            [
                284.16156005859375,
                -1658.0203857421875
            ],
            [
                292.3746032714844,
                -1583.46484375
            ],
            [
                253.57435607910156,
                -1521.8243408203125
            ],
            [
                256.4229736328125,
                -1482.328857421875
            ],
            [
                232.90823364257813,
                -1464.3272705078125
            ],
            [
                233.0369873046875,
                -1423.2178955078125
            ],
            [
                149.08265686035156,
                -1309.40380859375
            ],
            [
                106.08148193359375,
                -1276.52685546875
            ],
            [
                38.317203521728516,
                -1282.27392578125
            ],
            [
                55.4609260559082,
                -1260.8240966796875
            ],
            [
                17.18616485595703,
                -1241.0491943359375
            ],
            [
                -76.92718505859375,
                -1248.440673828125
            ],
            [
                -137.31956481933594,
                -1230.6151123046875
            ],
            [
                -231.6398468017578,
                -1172.0599365234375
            ],
            [
                -279.59869384765625,
                -1168.6011962890625
            ],
            [
                -300.0144958496094,
                -1186.2703857421875
            ],
            [
                -377.7708740234375,
                -1143.797607421875
            ],
            [
                -415.3604431152344,
                -1153.84765625
            ],
            [
                -474.8511047363281,
                -1143.1767578125
            ],
            [
                -500.0238037109375,
                -1118.6749267578125
            ]
        ],
        "pieceId": "RPf_00197_intact_mesh"
    }
],
        "piecesFinalTransformations": [
    {
        "pieceId": "RPf_00194_intact_mesh",
        "rotationRadians": -2.499699354171753,
        "translateVectorX": 0.0,
        "translateVectorY": 0.0
    },
    {
        "pieceId": "RPf_00197_intact_mesh",
        "rotationRadians": -2.428189277648926,
        "translateVectorX": -181.4517822265625,
        "translateVectorY": -1726.102783203125
    }
]
    }

    def test_translation_vector(self):
        RPf_00194 = Piece("RPf_00194","RPobj_g28_o0028")
        RPf_00194.load_polygon()

        tx,ty = physical_assemler.get_final_tranlsation_vector(self.toy_example_response,RPf_00194)

        assert tx == 830 # On notebook 23 value is -846
        assert ty == -1310 # On notebook 23 value is -1292


    def test_transform_geom_as_final_polygon(self):
        fig,ax = plt.subplots(figsize=(8,12))

        RPf_00194 = Piece("RPf_00194","RPobj_g28_o0028")
        RPf_00194.load_polygon()
        RPf_00194.load_bands()
        
        RPf_00197 = Piece("RPf_00197","RPobj_g28_o0028")
        RPf_00197.load_polygon()
        RPf_00197.load_bands()

        poly_00194_xs,poly_00194_ys = RPf_00194.polygon.exterior.xy
        ax.plot(poly_00194_xs,poly_00194_ys,label="RPf_00194 In the beginning")
        poly_00197_xs,poly_00197_ys = RPf_00197.polygon.exterior.xy
        ax.plot(poly_00197_xs,poly_00197_ys,label="RPf_00197 In the beginning")

        band_intersection_points_00194 = RPf_00194.bands[0].contour_intersection_points
        band_intersection_points_00197 = RPf_00197.bands[0].contour_intersection_points

        ax.scatter([band_intersection_points_00194[0][0],band_intersection_points_00194[1][0]],[band_intersection_points_00194[0][1],band_intersection_points_00194[1][1]],
                   label="band_intersection_points_00194 (In beginning)")
        ax.scatter([band_intersection_points_00197[0][0],band_intersection_points_00197[1][0]],[band_intersection_points_00197[0][1],band_intersection_points_00197[1][1]],
                   label="band_intersection_points_00197 (In beginning)")
        


        RPf_00194_final_poly = Polygon(physical_assemler.get_final_coords(self.toy_example_response,RPf_00194))
        RPf_00197_final_poly = Polygon(physical_assemler.get_final_coords(self.toy_example_response,RPf_00197))

        poly_00194_xs,poly_00194_ys = RPf_00194_final_poly.exterior.xy
        ax.plot(poly_00194_xs,poly_00194_ys,label="RPf_00194 final coords ")
        poly_00197_xs,poly_00197_ys = RPf_00197_final_poly.exterior.xy
        ax.plot(poly_00197_xs,poly_00197_ys,label="RPf_00197 final coords ")


        band_intersection_points_00194_transformed = [physical_assemler.transform_geom_as_final_polygon(Point(point),self.toy_example_response,RPf_00194) for point in band_intersection_points_00194]
        band_intersection_points_00197_transformed = [physical_assemler.transform_geom_as_final_polygon(Point(point),self.toy_example_response,RPf_00197) for point in band_intersection_points_00197]

        ax.scatter([band_intersection_points_00194_transformed[0].x,band_intersection_points_00194_transformed[1].x],
                   [band_intersection_points_00194_transformed[0].y,band_intersection_points_00194_transformed[1].y],
                   label="band_intersection_points_00194 (Final)")
        ax.scatter([band_intersection_points_00197_transformed[0].x,band_intersection_points_00197_transformed[1].x],
                   [band_intersection_points_00197_transformed[0].y,band_intersection_points_00197_transformed[1].y],
                   label="band_intersection_points_00197 (Final)")
        

        ax.legend()
        ax.yaxis_inverted()
        ax.axis("equal")


        plt.show()

    
    def test_get_final_transformations(self):
        transformations = physical_assemler.get_final_transformations(self.toy_example_response)
        RPf_00194_transformation,RPf_00197_transformation = transformations
        print(transformations)

        RPf_00194 = Piece("RPf_00194","RPobj_g28_o0028")
        RPf_00194.load_original_image()
        
        RPf_00197 = Piece("RPf_00197","RPobj_g28_o0028")
        RPf_00197.load_original_image()

        background_img = Image.new("RGBA",(5000,5000),color=0)

        rotated_00194 = RPf_00194.original_img.rotate(RPf_00194_transformation["rotation_degree"])
        mask_00194 = restore_assembly_img._mask_transparency(rotated_00194)
        rotated_00197 = RPf_00197.original_img.rotate(RPf_00197_transformation["rotation_degree"])
        mask_00197 = restore_assembly_img._mask_transparency(rotated_00197)

        bias = background_img.width//2
        background_img.paste(rotated_00194,box=(RPf_00194_transformation["tx"]+bias,RPf_00194_transformation["ty"]+bias),mask=mask_00194)
        background_img.paste(rotated_00197,box=(RPf_00197_transformation["tx"]+bias,RPf_00197_transformation["ty"]+bias),mask=mask_00197)

        fig,ax = plt.subplots(figsize=(8,12))
        ax.imshow(background_img)

        plt.show()






if __name__  == "__main__":
    unittest.main()