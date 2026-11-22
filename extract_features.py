
import os
import csv

# Classes to labels as a dictionary
CLASSES = {
    "grouping": 0,
    "sorting_groups": 1,
    "object_clustering": 2,
    "undefined": 3
}

def extract_number_of_colors(reader):
    colors = set()
    for row in reader:
        if len(row) >= 3:
            colors.add(row[2])
    return len(colors)

# Create dataset CSV file
with open("dataset.csv", "w", newline="") as dataset_file:
    writer = csv.writer(dataset_file)

    # Write header
    writer.writerow(["num_colors", "class_label"])

    # Extract features for each individual
    for class_name in CLASSES:
        for file in os.listdir(f"parsed/{class_name}"):
            if file.endswith(".csv"):
                with open(f"parsed/{class_name}/{file}", "r") as f:
                    reader = csv.reader(f)
                    num_colors = extract_number_of_colors(reader)

                writer.writerow([num_colors, CLASSES[class_name]])
