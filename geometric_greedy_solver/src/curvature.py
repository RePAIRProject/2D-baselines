import numpy as np
from shapely import Point,Polygon,LineString
from shapely.ops import nearest_points

def _compute_curvature(x, y):
    dx = np.gradient(x)
    dy = np.gradient(y)
    ddx = np.gradient(dx)
    ddy = np.gradient(dy)

    curvature = np.abs(dx * ddy - dy * ddx) / (dx**2 + dy**2)**1.5

    return curvature

def _get_points_curvature(xs:np.array,ys:np.array):
    curvature_values = _compute_curvature(xs,ys)
    scaled_curvature = (curvature_values-curvature_values.min())/(curvature_values.max()-curvature_values.min())

    return scaled_curvature

def segment_polygon_contour_by_theshold(xs:np.array,ys:np.array,curvature_thresh):
    scaled_curvature = _get_points_curvature(xs,ys)
    segmenting_points = np.array([(xs[i],ys[i]) for i,point_curv in enumerate(scaled_curvature) if point_curv > curvature_thresh])

    return segmenting_points

def segment_polygon_contour(xs:np.array,ys:np.array,min_num_segments = 3,max_num_segments = 8):
    curvature_values = _compute_curvature(xs,ys)
    indices = np.argsort(curvature_values)[::-1]
    num_contour_points = len(xs)
    xs = np.reshape(xs,(num_contour_points,)) # changing the data type could make side affects? 
    ys = np.reshape(ys,(num_contour_points,))
    num_segment_distance_errors = []

    for num_segments in range(min_num_segments,max_num_segments+1):
        segmenting_points_xs = xs[indices[:num_segments]]
        segmenting_points_ys = ys[indices[:num_segments]]

        segments = []

        for jj in range(num_segments):
            first_endpoint = (segmenting_points_xs[jj],segmenting_points_ys[jj])
            second_endpoint = (segmenting_points_xs[(jj+1)%num_segments],segmenting_points_ys[(jj+1)%num_segments])
            segments.append(LineString([first_endpoint,second_endpoint]))

        segment_points_distances = np.zeros((num_contour_points,num_segments))

        for ii in range(num_contour_points):
            for jj in range(num_segments):
                segment_points_distances[ii,jj] = Point(xs[ii],ys[ii]).distance(segments[jj])

        closest_segments = np.argmin(segment_points_distances,axis=1)
        distance_err = np.mean(segment_points_distances[np.arange(num_contour_points),closest_segments])
        num_segment_distance_errors.append(distance_err)

    errors_derivative = [num_segment_distance_errors[i-1]-num_segment_distance_errors[i] for i in range(len(num_segment_distance_errors[1:]))]
    error_drop_index = errors_derivative.index(max(errors_derivative)) 
    num_segments_selected = error_drop_index #- 1

    return np.array([(xs[indices[i]],ys[indices[i]]) for i in range(num_segments_selected)])

    return xs[indices[:num_segments_selected]],ys[indices[:num_segments_selected]]
        
def find_neighbors_right_left(centeral_point:Point,contour_polygon:Polygon):
    on_right = []
    on_right_distances = []
    on_left = []
    on_left_distances = []

    for contour_point in list(contour_polygon.exterior.coords)[:-1]:

        relative_to_point1 = Point(contour_point[0]-centeral_point.x,contour_point[1]-centeral_point.y)
        relative_dist = np.sqrt(relative_to_point1.x**2+relative_to_point1.y**2)

        if relative_to_point1.x < 0:
            on_left.append(contour_point)
            on_left_distances.append(relative_dist)
        else:
            on_right.append(contour_point)
            on_right_distances.append(relative_dist)

    right_closest_points =  [p for _,p in sorted(zip(on_right_distances,on_right))]
    left_closest_points =  [p for _,p in sorted(zip(on_left_distances,on_left))]
    return [right_closest_points[0],left_closest_points[0]]

