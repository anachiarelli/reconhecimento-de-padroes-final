
import os
import csv
import scipy
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
    

# Create dataset CSV file
with open("dataset.csv", "w", newline="") as dataset_file:
    writer = csv.writer(dataset_file)

    # Write header
    writer.writerow(["num_colors", "density", "class_label"])

    # Extract features for each individual
    for class_name in CLASSES:
        for file in os.listdir(f"parsed/{class_name}"):
            if file.endswith(".csv"):
                with open(f"parsed/{class_name}/{file}", "r") as f:
                    reader = csv.reader(f)
                    points = list(reader)
                    num_colors = extract_number_of_colors(points)
                    density = extract_density(points)

                writer.writerow([num_colors, density, CLASSES[class_name]])
