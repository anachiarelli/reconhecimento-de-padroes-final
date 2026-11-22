import os
import matplotlib.pyplot as plt

WORLD_SIZE = 112.0
ROBOT_RADIUS = 3.6
OBJECT_RADIUS = 5.0

# read files in samples/sorting_groups
for file in os.listdir("samples/object_clustering"):
    if file.endswith("robots.csv"):
        # initialize plot
        plt.figure(figsize=(10, 10))
        plt.xlim(0, WORLD_SIZE)
        plt.ylim(0, WORLD_SIZE)
        plt.gca().set_aspect('equal', adjustable='box')

        with open(f"samples/object_clustering/{file}", "r") as robots_file:
            with open(f"samples/object_clustering/{file.replace('robots', 'objects')}", "r") as objects_file:
                # read last line
                last_line = robots_file.readlines()[-1].split(",")
                for i in range(0, len(last_line) -1, 3):
                    x = float(last_line[i])
                    y = float(last_line[i + 1])
                    theta = float(last_line[i + 2])
                    # plot robot as a circle
                    circle = plt.Circle((x, y), ROBOT_RADIUS, color='blue', fill=True)
                    plt.gca().add_artist(circle)
                # read last line of objects file
                last_line = objects_file.readlines()[-1].split(",")
                for i in range(0, len(last_line) -1, 2):
                    x = float(last_line[i])
                    y = float(last_line[i + 1])
                    # plot object as a circle
                    circle = plt.Circle((x, y), OBJECT_RADIUS, color='red', fill=True)
                    plt.gca().add_artist(circle)


        # save plot to samples/object_clustering/{generation}_{individual_id}.png
        plt.savefig(f"samples/object_clustering/{file.replace('robots.csv', '.png')}")
        plt.clf()  # clear the plot for the next file


# read files in samples/sorting_groups
for file in os.listdir("samples/object_clustering/undefined"):
    if file.endswith("robots.csv"):
        # initialize plot
        plt.figure(figsize=(10, 10))
        plt.xlim(0, WORLD_SIZE)
        plt.ylim(0, WORLD_SIZE)
        plt.gca().set_aspect('equal', adjustable='box')

        with open(f"samples/object_clustering/undefined/{file}", "r") as robots_file:
            with open(f"samples/object_clustering/undefined/{file.replace('robots', 'objects')}", "r") as objects_file:
                # read last line
                last_line = robots_file.readlines()[-1].split(",")
                for i in range(0, len(last_line) -1, 3):
                    x = float(last_line[i])
                    y = float(last_line[i + 1])
                    theta = float(last_line[i + 2])
                    # plot robot as a circle
                    circle = plt.Circle((x, y), ROBOT_RADIUS, color='blue', fill=True)
                    plt.gca().add_artist(circle)
                # read last line of objects file
                last_line = objects_file.readlines()[-1].split(",")
                for i in range(0, len(last_line) -1, 2):
                    x = float(last_line[i])
                    y = float(last_line[i + 1])
                    # plot object as a circle
                    circle = plt.Circle((x, y), OBJECT_RADIUS, color='red', fill=True)
                    plt.gca().add_artist(circle)



        # save plot to samples/object_clustering/undefined/{generation}_{individual_id}.png
        plt.savefig(f"samples/object_clustering/undefined/{file.replace('robots.csv', '.png')}")
        plt.clf()  # clear the plot for the next file