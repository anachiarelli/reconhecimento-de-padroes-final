
import os
import csv
import scipy
import sklearn.cluster
import statistics
from scipy.spatial import ConvexHull

# Classes to labels as a dictionary
CLASSES = {
    "grouping": 0,
    "sorting_groups": 1,
    "object_clustering": 2,
    "undefined": 3
}

def extract_number_of_colors(points):
    colors = set()
    for point in points:
        if len(point) >= 3:
            colors.add(point[2])
    return len(colors)

def extract_density(points):
    if not points:
        return 0
    # Calculate the area of convex hull of the points
    points_array = [[float(point[0]), float(point[1])] for point in points]
    if len(points_array) < 3:
        return 0  # Not enough points to form a convex hull
    hull = ConvexHull(points_array)
    area = hull.volume 
    return area / len(points_array) if len(points_array) > 0 else 0
    
def extract_clusters(points, eps=(3.6 * 4), min_samples=3):
    if not points:
        return 0
    # Use DBSCAN to find clusters
    points_array = [[float(point[0]), float(point[1])] for point in points]
    db = sklearn.cluster.DBSCAN(eps=eps, min_samples=min_samples).fit(points_array)
    labels = db.labels_
    # Count the number of clusters (ignoring noise points labeled as -1)
    num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    outliers = list(labels).count(-1)
    return num_clusters, outliers

def extract_clusters_by_color(points, eps=(3.6 * 4), min_samples=3):
    if not points:
        return {}
    # Group points by color
    color_groups = {}
    for point in points:
        color = point[2]
        if color not in color_groups:
            color_groups[color] = []
        color_groups[color].append([float(point[0]), float(point[1])])
    
    # Use DBSCAN to find clusters for each color group
    clusters_by_color = {}
    for color, group_points in color_groups.items():
        db = sklearn.cluster.DBSCAN(eps=eps, min_samples=min_samples).fit(group_points)
        labels = db.labels_
        num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        outliers = list(labels).count(-1)
        clusters_by_color[color] = (num_clusters, outliers)

    # return sum of clusters and outliers for all colors
    total_clusters = sum(num for num, _ in clusters_by_color.values())
    total_outliers = sum(out for _, out in clusters_by_color.values())
    return total_clusters, total_outliers

def cluster_density(points, eps=(3.6 * 4), min_samples=3):
    if not points:
        return 0
    # Use DBSCAN to find clusters
    points_array = [[float(point[0]), float(point[1])] for point in points]
    db = sklearn.cluster.DBSCAN(eps=eps, min_samples=min_samples).fit(points_array)
    labels = db.labels_
    
    # Calculate density for each cluster
    cluster_densities = []
    unique_labels = set(labels)
    for label in unique_labels:
        if label == -1:
            continue  # Skip noise points
        cluster_points = [points_array[i] for i in range(len(points_array)) if labels[i] == label]
        if len(cluster_points) < 3:
            continue  # Not enough points to form a convex hull
        # catch QhullError exception when calculating convex hull
        try:
            hull = ConvexHull(cluster_points)
        except scipy.spatial._qhull.QhullError:
            continue
        area = hull.volume 
        density = area / len(cluster_points) if len(cluster_points) > 0 else 0
        cluster_densities.append(density)
    
    # Return the mean and variance of the density of all clusters
    if cluster_densities:
        return statistics.mean(cluster_densities), (statistics.variance(cluster_densities) if len(cluster_densities) > 1 else 0)
    else:
        return 0, 0

def calculate_mean_cluster_density_by_color(points, eps=(3.6 * 4), min_samples=3):
    if not points:
        return {}
    # Group points by color
    color_groups = {}
    for point in points:
        color = point[2]
        if color not in color_groups:
            color_groups[color] = []
        color_groups[color].append([float(point[0]), float(point[1])])
    
    # Use DBSCAN to find clusters for each color group and calculate density
    densities_by_color = {}
    cluster_densities = []

    for color, group_points in color_groups.items():
        db = sklearn.cluster.DBSCAN(eps=eps, min_samples=min_samples).fit(group_points)
        labels = db.labels_
        
        unique_labels = set(labels)
        for label in unique_labels:
            if label == -1:
                continue  # Skip noise points
            cluster_points = [group_points[i] for i in range(len(group_points)) if labels[i] == label]
            if len(cluster_points) < 3:
                continue  # Not enough points to form a convex hull
            # catch QhullError exception when calculating convex hull
            try:
                hull = ConvexHull(cluster_points)
            except scipy.spatial._qhull.QhullError:
                continue
            area = hull.volume 
            density = area / len(cluster_points) if len(cluster_points) > 0 else 0
            cluster_densities.append(density)
        
    # Store the mean and variance of the density of all clusters between all colors
    if cluster_densities:
        return statistics.mean(cluster_densities), (statistics.variance(cluster_densities) if len(cluster_densities) > 1 else 0)
    else:
        return 0, 0

# Create dataset CSV file
with open("dataset.csv", "w", newline="") as dataset_file:
    writer = csv.writer(dataset_file)

    # Write header
    writer.writerow(["num_colors", "density", "number_of_clusters", "class_label", "number_of_outliers", "sum_of_clusters_by_color", "sum_of_outliers_by_color", "cluster_mean_density", "cluster_density_variance", "mean_cluster_density_by_color", "cluster_density_variance_by_color", "class_label"])

    # Extract features for each individual
    for class_name in CLASSES:
        for file in os.listdir(f"parsed/{class_name}"):
            if file.endswith(".csv"):
                with open(f"parsed/{class_name}/{file}", "r") as f:
                    reader = csv.reader(f)
                    points = list(reader)
                    num_colors = extract_number_of_colors(points)
                    density = extract_density(points)
                    number_of_clusters, outliers = extract_clusters(points)
                    number_of_clusters_by_color, outliers_by_color = extract_clusters_by_color(points)
                    mean_cluster_density, cluster_density_variance = cluster_density(points)
                    mean_cluster_density_by_color, cluster_density_variance_by_color = calculate_mean_cluster_density_by_color(points)

                writer.writerow([num_colors, density, number_of_clusters, outliers, number_of_clusters_by_color, outliers_by_color, mean_cluster_density, cluster_density_variance, mean_cluster_density_by_color, cluster_density_variance_by_color, CLASSES[class_name]])
