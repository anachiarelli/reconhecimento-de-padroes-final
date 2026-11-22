import csv
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
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
        X.append([int(row[0]), float(row[1])])  #num_colors and density
        # last column is the class label, convert it to int and append to y
        y.append(int(row[-1]))

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.5,
    train_size=0.5,
    random_state=42,
    stratify=y
)

# Scale the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# KNN
knn = KNeighborsClassifier(n_neighbors=3)

## Treino
knn.fit(X_train, y_train)

## Teste
knn_pred = knn.predict(X_test)

## Métricas
print(classification_report(
    y_test,
    knn_pred,
    target_names=[target_names[i] for i in sorted(target_names.keys())]
))