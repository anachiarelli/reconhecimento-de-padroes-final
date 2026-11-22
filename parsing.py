import os

os.makedirs("parsed/grouping", exist_ok=True)
os.makedirs("parsed/sorting_groups", exist_ok=True)
os.makedirs("parsed/object_clustering", exist_ok=True)
os.makedirs("parsed/undefined", exist_ok=True)

### GROUPING ###
# Read the selected individual CSV files from /samples/grouping
for file in os.listdir("samples/grouping"):
    if file.endswith(".csv"):
        with open(f"samples/grouping/{file}", "r") as f:
            last_line = f.readlines()[-1].split(",")

            # Create the file if it doesn't exist
            with open(f"parsed/grouping/{file}", "w") as p:
                for i in range(0, len(last_line) - 1, 3):
                    x = float(last_line[i])
                    y = float(last_line[i + 1])
                    p.write(f"{x},{y},blue\n")

# Read the selected individual CSV files from /samples/grouping/undefined
for file in os.listdir("samples/grouping/undefined"):
    if file.endswith(".csv"):
        with open(f"samples/grouping/undefined/{file}", "r") as f:
            last_line = f.readlines()[-1].split(",")

            # Create the file if it doesn't exist
            with open(f"parsed/undefined/g_{file}", "w") as p:
                for i in range(0, len(last_line) - 1, 3):
                    x = float(last_line[i])
                    y = float(last_line[i + 1])
                    p.write(f"{x},{y},blue\n")


### SORTING GROUPS ###
# Read the selected individual CSV files from /samples/sorting_groups
for file in os.listdir("samples/sorting_groups"):
    if file.endswith(".csv"):
        with open(f"samples/sorting_groups/{file}", "r") as f:
            last_line = f.readlines()[-1].split(",")

            # Create the file if it doesn't exist
            with open(f"parsed/sorting_groups/{file.replace('robots', '')}", "w") as p:
                for i in range(0, len(last_line) - 1, 6):
                    x = float(last_line[i])
                    y = float(last_line[i + 1])
                    r = float(last_line[i + 3])
                    g = float(last_line[i + 4])
                    b = float(last_line[i + 5])
                    if r == 1:
                        color = "red"
                    elif g == 1:
                        color = "green"
                    elif b == 1:
                        color = "blue"
                    p.write(f"{x},{y},{color}\n")

# Read the selected individual CSV files from /samples/sorting_groups/undefined
for file in os.listdir("samples/sorting_groups/undefined"):
    if file.endswith(".csv"):
        with open(f"samples/sorting_groups/undefined/{file}", "r") as f:
            last_line = f.readlines()[-1].split(",")

            # Create the file if it doesn't exist
            with open(f"parsed/undefined/s_{file.replace('robots', '')}", "w") as p:
                for i in range(0, len(last_line) - 1, 6):
                    x = float(last_line[i])
                    y = float(last_line[i + 1])
                    r = float(last_line[i + 3])
                    g = float(last_line[i + 4])
                    b = float(last_line[i + 5])
                    if r == 1:
                        color = "red"
                    elif g == 1:
                        color = "green"
                    elif b == 1:
                        color = "blue"
                    p.write(f"{x},{y},{color}\n")


### OBJECT CLUSTERING ###
# Read the selected individual CSV files from /samples/object_clustering
for file in os.listdir("samples/object_clustering"):
    if file.endswith("robots.csv"):
        with open(f"samples/object_clustering/{file}", "r") as robots_file:
            with open(f"samples/object_clustering/{file.replace('robots', 'objects')}", "r") as objects_file:
                last_line_robots = robots_file.readlines()[-1].split(",")
                last_line_objects = objects_file.readlines()[-1].split(",")

                # Create the file if it doesn't exist
                with open(f"parsed/object_clustering/{file.replace('robots', '')}", "w") as p:
                    for i in range(0, len(last_line_robots) - 1, 3):
                        x = float(last_line_robots[i])
                        y = float(last_line_robots[i + 1])
                        p.write(f"{x},{y},blue\n")
                    for i in range(0, len(last_line_objects) - 1, 2):
                        x = float(last_line_objects[i])
                        y = float(last_line_objects[i + 1])
                        p.write(f"{x},{y},red\n")

# Read the selected individual CSV files from /samples/object_clustering/undefined
for file in os.listdir("samples/object_clustering/undefined"):
    if file.endswith("robots.csv"):
        with open(f"samples/object_clustering/undefined/{file}", "r") as robots_file:
            with open(f"samples/object_clustering/undefined/{file.replace('robots', 'objects')}", "r") as objects_file:
                last_line_robots = robots_file.readlines()[-1].split(",")
                last_line_objects = objects_file.readlines()[-1].split(",")

                # Create the file if it doesn't exist
                with open(f"parsed/undefined/o_{file.replace('robots', '')}", "w") as p:
                    for i in range(0, len(last_line_robots) - 1, 3):
                        x = float(last_line_robots[i])
                        y = float(last_line_robots[i + 1])
                        p.write(f"{x},{y},blue\n")
                    for i in range(0, len(last_line_objects) - 1, 2):
                        x = float(last_line_objects[i])
                        y = float(last_line_objects[i + 1])
                        p.write(f"{x},{y},red\n")