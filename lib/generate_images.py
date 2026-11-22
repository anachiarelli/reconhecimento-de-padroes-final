
import os
import glob
import csv
import matplotlib.pyplot as plt


def generate_images():
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scenario = "grouping"
    scenario_dir = os.path.join(ROOT_DIR, "instances", scenario)
    output_dir = os.path.join(ROOT_DIR, "images", scenario)

    os.makedirs(output_dir, exist_ok=True)

    for individual_file in glob.glob(os.path.join(scenario_dir, "*.csv")):
        individual_id = os.path.splitext(os.path.basename(individual_file))[0]

        with open(individual_file, newline="") as file:
            reader = csv.reader(file)
            data = list(reader)

        x = [float(row[0]) for row in data]
        y = [float(row[1]) for row in data]

        plt.figure(figsize=(8, 6))
        plt.scatter(x, y, s=50)

        plt.title(f"Individual {individual_id} - Scenario: {scenario}")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.grid(True)

        plt.savefig(os.path.join(output_dir, f"{individual_id}.png"))
        plt.close()


if __name__ == "__main__":
    generate_images()
