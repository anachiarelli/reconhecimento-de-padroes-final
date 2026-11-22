import os
import matplotlib.pyplot as plt

WORLD_SIZE = 316.0
ROBOT_RADIUS = 3.6

# read files in instances/grouping
for file in os.listdir("instances/grouping"):
    if file.endswith(".csv"):
        # initialize plot
        plt.figure(figsize=(10, 10))
        plt.xlim(0, WORLD_SIZE)
        plt.ylim(0, WORLD_SIZE)
        plt.gca().set_aspect('equal', adjustable='box')

        with open(f"instances/grouping/{file}", "r") as f:
            # read last line
            last_line = f.readlines()[-1].split(",")
            for i in range(0, len(last_line) -1, 3):
                x = float(last_line[i])
                y = float(last_line[i + 1])
                # plot robot as a circle
                circle = plt.Circle((x, y), ROBOT_RADIUS, color='blue', fill=True)
                plt.gca().add_artist(circle)

        # save plot to instances/grouping/{generation}_{individual_id}.png
        plt.savefig(f"instances/grouping/{file.replace('.csv', '.png')}")
        plt.clf()  # clear the plot for the next file

# read files in instances/grouping
for file in os.listdir("instances/grouping/undefined"):
    if file.endswith(".csv"):
        # initialize plot
        plt.figure(figsize=(10, 10))
        plt.xlim(0, WORLD_SIZE)
        plt.ylim(0, WORLD_SIZE)
        plt.gca().set_aspect('equal', adjustable='box')

        with open(f"instances/grouping/undefined/{file}", "r") as f:
            # read last line
            last_line = f.readlines()[-1].split(",")
            for i in range(0, len(last_line) -1, 3):
                x = float(last_line[i])
                y = float(last_line[i + 1])
                # plot robot as a circle
                circle = plt.Circle((x, y), ROBOT_RADIUS, color='blue', fill=True)
                plt.gca().add_artist(circle)


        # save plot to instances/grouping/undefined/{generation}_{individual_id}.png
        plt.savefig(f"instances/grouping/undefined/{file.replace('.csv', '.png')}")
        plt.clf()  # clear the plot for the next file