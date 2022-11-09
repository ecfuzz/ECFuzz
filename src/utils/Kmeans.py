from collections import defaultdict
from random import uniform
from math import sqrt


class Kmeans(object):
    
    def __init__(self, dataset, k) -> None:
        self.dataset = dataset
        self.k = k

    def point_avg(self, points):
        """
        Accepts a list of points, each with the same number of dimensions.
        NB. points can have more dimensions than 2
        
        Returns a new point which is the center of all the points.
        """
        dimensions = len(points[0])

        new_center = []

        for dimension in range(dimensions):
            dim_sum = 0  # dimension sum
            for p in points:
                dim_sum += p[dimension]

            # average of each dimension
            new_center.append(dim_sum / float(len(points)))

        return new_center

    def update_centers(self, data_set, assignments):
        """
        Accepts a dataset and a list of assignments; the indexes 
        of both lists correspond to each other.
        Compute the center for each of the assigned groups.
        Return `k` centers where `k` is the number of unique assignments.
        """
        new_means = defaultdict(list)
        centers = []
        for assignment, point in zip(assignments, data_set):
            new_means[assignment].append(point)

        for count, points in new_means.items():
            centers.append(self.point_avg(points))

        return centers

    def assign_points(self, data_points, centers):
        """
        Given a data set and a list of points betweeen other points,
        assign each point to an index that corresponds to the index
        of the center point on it's proximity to that point. 
        Return a an array of indexes of centers that correspond to
        an index in the data set; that is, if there are N points
        in `data_set` the list we return will have N elements. Also
        If there are Y points in `centers` there will be Y unique
        possible values within the returned list.
        """
        assignments = []
        for point in data_points:
            shortest = float('inf')  # positive infinity
            shortest_index = 0
            for i in range(len(centers)):
                val = self.distance(point, centers[i])
                if val < shortest:
                    shortest = val
                    shortest_index = i
            assignments.append(shortest_index)
        return assignments

    def distance(self, a, b):
        """
        """
        dimensions = len(a)

        _sum = 0
        for dimension in range(dimensions):
            difference_sq = (a[dimension] - b[dimension]) ** 2
            _sum += difference_sq
        return sqrt(_sum)

    def generate_k(self, data_set, k):
        """
        Given `data_set`, which is an array of arrays,
        find the minimum and maximum for each coordinate, a range.
        Generate `k` random points between the ranges.
        Return an array of the random points within the ranges.
        """
        centers = []
        dimensions = len(data_set[0])
        min_max = defaultdict(int)

        for point in data_set:
            for i in range(dimensions):
                val = point[i]
                min_key = 'min_%d' % i
                max_key = 'max_%d' % i
                if min_key not in min_max or val < min_max[min_key]:
                    min_max[min_key] = val
                if max_key not in min_max or val > min_max[max_key]:
                    min_max[max_key] = val

        for _k in range(k):
            rand_point = []
            for i in range(dimensions):
                min_val = min_max['min_%d' % i]
                max_val = min_max['max_%d' % i]

                rand_point.append(uniform(min_val, max_val))

            centers.append(rand_point)

        return centers

    def k_means(self):
        k_points = self.generate_k(self.dataset, self.k)
        assignments = self.assign_points(self.dataset, k_points)
        old_assignments = None
        while assignments != old_assignments:
            new_centers = self.update_centers(self.dataset, assignments)
            old_assignments = assignments
            assignments = self.assign_points(self.dataset, new_centers)
        return assignments, self.dataset
