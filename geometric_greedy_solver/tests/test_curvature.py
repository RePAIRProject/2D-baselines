import unittest
import sys
sys.path.append("geometric_greedy_solver")

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from shapely import Polygon,LineString
import numpy as np
from src.curvature import _get_points_curvature,segment_polygon_contour_by_theshold,segment_polygon_contour,_compute_curvature
from src.piece import explore_group

    
class TestPocPolygonGeometry(unittest.TestCase):

    def test_toy_example_line_intersect_polygon(self):
        def segment_polygon_intersection(segment, polygon):
            # Ensure the input segment and polygon are of LineString and Polygon types
            if not isinstance(segment, LineString) or not isinstance(polygon, Polygon):
                raise ValueError("Input types must be LineString and Polygon")

            # Check if the segment intersects the polygon
            if not segment.intersects(polygon):
                return []

            # Find the intersection points
            intersection_points = segment.intersection(polygon.exterior)

            # If the intersection is a Point, convert it to a list of coordinates
            if intersection_points.is_empty:
                return []
            elif intersection_points.geom_type == 'Point':
                return [(float(intersection_points.x), float(intersection_points.y))]
            else:
                return [(float(x), float(y)) for x, y in zip(*intersection_points.xy)]



        # Define a segment (LineString) and a polygon (Polygon)
        segment = LineString([(0, 0), (3, 3)])
        polygon = Polygon([(1, 1), (1, 4), (4, 4), (4, 1)])

        # Find intersection points
        intersection_points = segment_polygon_intersection(segment, polygon)

        # Print the result
        print("Intersection Points:", intersection_points)


class TestCurvature(unittest.TestCase):

    def test_toy_example(self):
        xs = np.array([831.0, 909.0, 930.0, 902.0, 902.0, 865.0, 873.0, 849.0, 845.0, 812.0, 803.0, 736.0, 655.0, 612.0, 482.0, 443.0, 370.0, 249.0, 192.0, 126.0, 2.0, 0.0, 26.0, 135.0, 247.0, 349.0, 451.0, 551.0, 747.0, 831.0])
        ys = np.array([0.0, 25.0, 187.0, 245.0, 301.0, 349.0, 390.0, 445.0, 526.0, 550.0, 605.0, 667.0, 633.0, 592.0, 562.0, 529.0, 524.0, 443.0, 431.0, 382.0, 335.0, 166.0, 133.0, 117.0, 74.0, 58.0, 76.0, 47.0, 28.0, 0.0])

        curvatures = _get_points_curvature(xs,ys)

        plt.plot(xs,ys,label="Curve",color="orange")
        norm = Normalize()
        colors = plt.cm.hot(norm(curvatures))

        plt.scatter(xs,ys,c=colors,label='points',cmap="hot")
        cbar = plt.colorbar()
        cbar.set_label("Curvature")

        segmenting_points = segment_polygon_contour_by_theshold(xs,ys,0.2)
        plt.scatter(segmenting_points[:,0],segmenting_points[:,1],marker="X",s=150,color="purple",zorder=0)

        plt.legend()
        plt.title('Curvatures of a polygon vertices')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.show()

    def test_by_parameter(self):
        pieces =  explore_group("RPobj_g1_o0001")
        curvedness_segmenation_threshold = 0.1

        for piece in pieces:
            piece.load_polygon()

            xs,ys = piece.get_polygon().exterior.xy
            curvatures = _get_points_curvature(xs,ys)

            plt.plot(xs,ys,label="Curve")
            norm = Normalize()
            colors = plt.cm.hot(norm(curvatures))

            plt.scatter(xs,ys,c=colors,label='points',cmap="hot")
            cbar = plt.colorbar()
            cbar.set_label("Curvature")

            segmenting_points = segment_polygon_contour_by_theshold(xs,ys,curvedness_segmenation_threshold)
            plt.scatter(segmenting_points[:,0],segmenting_points[:,1],marker="X",linewidths=0.5,color="pink")

            plt.legend()
            plt.title('Curve with Curvature Visualization')
            plt.xlabel('X-axis')
            plt.ylabel('Y-axis')
            plt.show()

    def test_curvature_circle(self):
        
        def deg_to_rad(degrees):
            return degrees*(np.pi/180)
        
        angles_degrees = list(range(0,360,3)) + [0]
        bias = 0 #30
        circle = Polygon([(np.cos(deg_to_rad(angle))+bias, np.sin(deg_to_rad(angle))+bias) for angle in angles_degrees])
        xs,ys = circle.exterior.xy

        curva = _compute_curvature(xs,ys)

        # All the points should be with the same curvature
        print(curva)    


    def test_curvature_line(self):
        num_points = 120
        ys = range(num_points)
        xs = range(num_points)

        curva = _compute_curvature(xs,ys)

        # All the points should be with the ZERO curvature
        print(curva)


    def test_segmentation(self):
        coords = [[863.9998168945312, 0.0], [961.9998779296875, 27.999876022338867], [1000.9998779296875, 71.0000991821289], [1022.9996948242188, 138.0], [1121.000244140625, 249.00006103515625], [1149.0001220703125, 329.9999084472656], [1164.9998779296875, 340.0001220703125], [1164.9998779296875, 392.00018310546875], [1197.9998779296875, 440.9999694824219], [1137.0, 501.99981689453125], [1066.9998779296875, 628.000244140625], [981.9998168945312, 703.0000610351562], [963.000244140625, 755.0000610351562], [892.0001831054688, 798.999755859375], [854.0000610351562, 859.0001831054688], [838.000244140625, 922.9998168945312], [737.9998779296875, 1001.9998168945312], [673.999755859375, 1091.0], [619.9998779296875, 1088.000244140625], [579.9998779296875, 1039.9998779296875], [537.0001831054688, 1020.9998779296875], [442.99981689453125, 1000.9998779296875], [363.99981689453125, 1007.9998779296875], [225.99981689453125, 947.0], [170.00006103515625, 855.9998779296875], [158.99990844726562, 713.000244140625], [50.000186920166016, 630.0000610351562], [0.0, 569.000244140625], [12.000082969665527, 546.9998779296875], [81.99977111816406, 513.9999389648438], [182.00015258789062, 431.0002136230469], [231.99986267089844, 420.00006103515625], [253.000244140625, 392.00018310546875], [306.0002136230469, 369.9998779296875], [335.99993896484375, 328.00006103515625], [399.0001525878906, 320.0001525878906], [407.0000305175781, 301.0000915527344], [543.0001831054688, 238.9998321533203], [573.9998779296875, 203.00006103515625], [618.0, 194.00022888183594], [668.0001831054688, 135.00022888183594], [743.0, 106.99987030029297], [765.999755859375, 61.999794006347656], [791.999755859375, 59.99993896484375]]
        polygon = Polygon(coords)
        xs,ys = polygon.exterior.xy

        # xs_segmenting_points,ys_segmenting_points = segment_polygon_contour(xs,ys)
        segmenting_points = segment_polygon_contour(xs,ys)

        xs_segmenting_points = [segmenting_points[i][0] for i in range(segmenting_points.shape[0])]
        ys_segmenting_points = [segmenting_points[i][1] for i in range(segmenting_points.shape[0])]

        plt.plot(xs,ys,label="piece")
        plt.scatter(xs_segmenting_points,ys_segmenting_points,label="segmenting points")

        plt.legend()
        plt.show()






if __name__ == "__main__":
    unittest.main()