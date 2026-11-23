
import csv
import time
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# Target names for classification report
target_names = {
    0: "grouping",
    1: "sorting_groups",
    2: "object_clustering",
    3: "undefined"
}

# Read dataset.csv and create X, y lists
X = []
y = []

with open("dataset.csv", "r") as dataset_file:
    reader = csv.reader(dataset_file)
    next(reader)

    for row in reader:
        number_of_colors = int(row[0])
        density = float(row[1])
        number_of_clusters = float(row[2])
        number_of_outliers = float(row[3])
        sum_of_clusters_by_color = float(row[4])
        sum_of_outliers_by_color = float(row[5])
        cluster_mean_density = float(row[6])
        cluster_density_variance = float(row[7])
        mean_cluster_density_by_color = float(row[8])
        cluster_density_variance_by_color = float(row[9])

        X.append([
            number_of_colors,
            density,
            number_of_clusters,
            number_of_outliers,
            cluster_mean_density,
        ])

        y.append(int(row[-1]))

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    train_size=0.7,
    random_state=42,
    stratify=y
)

# Scale the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


def evaluate_model(model, name):
    # Training
    start = time.perf_counter()
    model.fit(X_train, y_train)
    training_time = time.perf_counter() - start

    # Prediction
    start = time.perf_counter()
    predictions = model.predict(X_test)
    prediction_time = time.perf_counter() - start

    # Metrics
    print(f"\n{name} Classification Report:")
    print(classification_report(
        y_test,
        predictions,
        labels=sorted(target_names.keys()),
        target_names=[
            target_names[i]
            for i in sorted(target_names.keys())
        ],
        zero_division=0
    ))

    print(f"Training time: {training_time:.6f} seconds")
    print(f"Prediction time: {prediction_time:.6f} seconds")
    print(f"Total time: {training_time + prediction_time:.6f} seconds")


#######################################
# Naive Bayes

nb = GaussianNB()
evaluate_model(nb, "Naive Bayes")


#######################################
# KNN

knn = KNeighborsClassifier(n_neighbors=5)
evaluate_model(knn, "KNN")


#######################################
# Random Forest

rf = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
evaluate_model(rf, "Random Forest")
