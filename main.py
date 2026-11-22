import csv
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler

# Target names for classification report
target_names = {0: "grouping", 1: "sorting_groups", 2: "object_clustering", 3: "undefined"}

# Read dataset.csv and create X, y lists
X = []
y = []

with open("dataset.csv", "r") as dataset_file:
    reader = csv.reader(dataset_file)
    next(reader)  # Skip header
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
            # number_of_clusters,
            number_of_outliers,
            sum_of_clusters_by_color,
            # sum_of_outliers_by_color,
            cluster_mean_density,
            # cluster_density_variance,
            mean_cluster_density_by_color,
            # cluster_density_variance_by_color
        ])
        
        # last column is the class label, convert it to int and append to y
        y.append(int(row[-1]))

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    train_size=0.8,
    random_state=42,
    stratify=y
)

# Scale the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# KNN
knn = KNeighborsClassifier(n_neighbors=5)

## Treino
knn.fit(X_train, y_train)

## Teste
knn_pred = knn.predict(X_test)

## Métricas
print("KNN Classification Report:")
print(classification_report(
    y_test,
    knn_pred,
    target_names=[target_names[i] for i in sorted(target_names.keys())]
))

# Naive Bayes
nb = GaussianNB()

## Treino
nb.fit(X_train, y_train)

## Teste
nb_pred = nb.predict(X_test)

## Métricas
print("Naive Bayes Classification Report:")
print(classification_report(
    y_test,
    nb_pred,
    target_names=[target_names[i] for i in sorted(target_names.keys())]
))