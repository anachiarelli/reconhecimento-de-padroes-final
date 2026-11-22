import os
import matplotlib.pyplot as plt

WORLD_SIZE = 450.0
ROBOT_RADIUS = 3.6

# read files in samples/sorting_groups
for file in os.listdir("samples/sorting_groups"):
    if file.endswith(".csv"):
        # initialize plot
        plt.figure(figsize=(10, 10))
        plt.xlim(0, WORLD_SIZE)
        plt.ylim(0, WORLD_SIZE)
        plt.gca().set_aspect('equal', adjustable='box')

        with open(f"samples/sorting_groups/{file}", "r") as f:
            # read last line
            last_line = f.readlines()[-1].split(",")
            for i in range(0, len(last_line) -1, 6):
                x = float(last_line[i])
                y = float(last_line[i + 1])
                theta = float(last_line[i + 2])
                r = float(last_line[i + 3])
                g = float(last_line[i + 4])
                b = float(last_line[i + 5])
                # plot robot as a circle
                circle = plt.Circle((x, y), ROBOT_RADIUS, color=(r, g, b), fill=True)
                plt.gca().add_artist(circle)


        # save plot to samples/sorting_groups/{generation}_{individual_id}.png
        plt.savefig(f"samples/sorting_groups/{file.replace('.csv', '.png')}")
        plt.clf()  # clear the plot for the next file

# read files in samples/sorting_groups
for file in os.listdir("samples/sorting_groups/undefined"):
    if file.endswith(".csv"):
        # initialize plot
        plt.figure(figsize=(10, 10))
        plt.xlim(0, WORLD_SIZE)
        plt.ylim(0, WORLD_SIZE)
        plt.gca().set_aspect('equal', adjustable='box')

        with open(f"samples/sorting_groups/undefined/{file}", "r") as f:
            # read last line
            last_line = f.readlines()[-1].split(",")
            for i in range(0, len(last_line) -1, 6):
                x = float(last_line[i])
                y = float(last_line[i + 1])
                theta = float(last_line[i + 2])
                r = float(last_line[i + 3])
                g = float(last_line[i + 4])
                b = float(last_line[i + 5])
                # plot robot as a circle
                circle = plt.Circle((x, y), ROBOT_RADIUS, color=(r, g, b), fill=True)
                plt.gca().add_artist(circle)



        # save plot to samples/sorting_groups/undefined/{generation}_{individual_id}.png
        plt.savefig(f"samples/sorting_groups/undefined/{file.replace('.csv', '.png')}")
        plt.clf()  # clear the plot for the next file