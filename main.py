
import csv
import sys
import statistics
import random

from sklearn.preprocessing import StandardScaler
from lib.shared import predict, calculate_error


if __name__ == '__main__':
    r1, r2, r3 = map(float, sys.argv[1:4])

    # Load the dataset from CSV files
    with open("./results/features.csv", newline="") as features_file:
        features = list(csv.DictReader(features_file))

    with open("./results/labels.csv", newline="") as labels_file:
        labels = list(csv.DictReader(labels_file))

    # Associate features and labels by row order
    X, y = [], []

    for feature, label in zip(features, labels):
        X.append([float(feature["num_colors"])])
        y.append(int(label["class_label"]))

    # Divide the dataset into classes
    data_by_target = {}

    for data, target in zip(X, y):
        if target not in data_by_target:
            data_by_target[target] = []
        data_by_target[target].append(data)

    # Split the data into three parts based on the specified ratios
    Z1, Z2, Z3 = [], [], []

    for target, data_points in data_by_target.items():
        n = len(data_points)
        n1 = int(n * r1)
        n2 = int(n * r2)

        Z1.extend([(d, target) for d in data_points[:n1]])
        Z2.extend([(d, target) for d in data_points[n1:n1+n2]])
        Z3.extend([(d, target) for d in data_points[n1+n2:]])

    # Normalize using only Z1
    scaler = StandardScaler()

    Z1_X = [data for data, target in Z1]
    Z2_X = [data for data, target in Z2]
    Z3_X = [data for data, target in Z3]

    Z1_X = scaler.fit_transform(Z1_X)
    Z2_X = scaler.transform(Z2_X)
    Z3_X = scaler.transform(Z3_X)

    Z1 = [(data, target) for data, (_, target) in zip(Z1_X, Z1)]
    Z2 = [(data, target) for data, (_, target) in zip(Z2_X, Z2)]
    Z3 = [(data, target) for data, (_, target) in zip(Z3_X, Z3)]

    # LAZY LEARNING
    # Predict the classes of Z2 using Z1 as the base dataset
    min_k = 3
    max_k = 15
    error_rates = []

    for k in range(min_k, max_k, 2):
        predictions = predict(Z1, Z2, k)
        true_labels = [t[1] for t in Z2]
        error_rates.append(calculate_error(predictions, true_labels))

    # Get the first index of the minimum error rate
    min_error_index = 0

    for i in range(1, len(error_rates)):
        if error_rates[i] < error_rates[min_error_index]:
            min_error_index = i

    # Get the k with the minimum error rate
    best_k = min_k + min_error_index * 2
    print(f"Best K: {best_k}")

    # Generate 20 random subsets of the whole dataset
    # with Z3 length and calculate the error rate for each subset
    subset_size = len(Z3)
    all_data = Z1 + Z2 + Z3

    subset_error_rates = []

    for i in range(20):
        subset = random.sample(all_data, subset_size)
        predictions = predict(Z1, subset, best_k)
        true_labels = [t[1] for t in subset]
        error_rate = calculate_error(predictions, true_labels)
        subset_error_rates.append(error_rate)

    # Calculate the average error rate across all subsets
    average_error_rate = statistics.mean(subset_error_rates)
    std_dev_error_rate = statistics.stdev(subset_error_rates)

    print(
        f"Dataset: Swarm, "
        f"Average Error Rate: {average_error_rate:.4f}, "
        f"Standard Deviation: {std_dev_error_rate:.4f}"
    )
