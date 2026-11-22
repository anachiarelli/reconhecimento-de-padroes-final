import os
import shutil
import glob

# For each scenario in /output/{scenario}/, initialize a list to hold tuples of:
# (fitness_value, generation, individual_id, scenario) for each individual in each generation.
SCENARIOS = ("grouping", "sorting_groups", "object_clustering")
CLASS_SIZE = 10

UNDEFINED_INSTANCES_PER_SCENARIO = CLASS_SIZE // len(SCENARIOS)
REMAINDER_UNDEFINED_INSTANCES = CLASS_SIZE % len(SCENARIOS)

undefined_instances_per_scenario = {
    "grouping": UNDEFINED_INSTANCES_PER_SCENARIO,
    "sorting_groups": UNDEFINED_INSTANCES_PER_SCENARIO,
    "object_clustering": CLASS_SIZE - ((len(SCENARIOS) - 1) * UNDEFINED_INSTANCES_PER_SCENARIO)
}


scenario_data = {}
classes = {}
classes["undefined"] = []

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for scenario in SCENARIOS:
    scenario_dir = os.path.join(ROOT_DIR, "output", scenario)
    print(scenario_dir)
    scenario_data[scenario] = []

    for generation_dir in sorted(os.listdir(scenario_dir), key=int):
        fitness_file = os.path.join(scenario_dir, generation_dir, "fitness.csv")
        generation = int(generation_dir)

        for individual_id, line in enumerate(open(fitness_file), start=0):
            fitness_value = float(line.strip())
            scenario_data[scenario].append((fitness_value, generation, individual_id, scenario))

    # sort the list of tuples for each scenario by fitness_value in descending order
    scenario_data[scenario].sort(key=lambda x: x[0], reverse=True)

    # Select the top CLASS_SIZE individuals for each scenario and store them in the classes dictionary
    classes[scenario] = scenario_data[scenario][:CLASS_SIZE]

    # Select the bottom undefined_instances_per_scenario[scenario] individuals for each scenario and store them in the undefined class
    undefined_class = scenario_data[scenario][-undefined_instances_per_scenario[scenario]:]
    classes["undefined"].extend(undefined_class)

# Copy the selected individual CSV files to /instances/{scenario} except for the undefined class,
# which will be copied to /instances/{scenario}/undefined based on their original scenario.
# Copy selected individuals to /instances/{scenario}
for scenario, individuals in classes.items():
    for _, generation, individual_id, original_scenario in individuals:

        individual_id = f"{int(individual_id):03d}"

        # Define destination directory
        if scenario == "undefined":
            destination_dir = os.path.join(ROOT_DIR, "instances", original_scenario, "undefined")
        else:
            destination_dir = os.path.join(ROOT_DIR, "instances", scenario)

        os.makedirs(destination_dir, exist_ok=True)

        # Define source subdirectories based on original scenario
        if original_scenario == "object_clustering":
            subdirectories = ["robots", "objects"]
        elif original_scenario == "sorting_groups":
            subdirectories = ["robots"]
        else:
            subdirectories = [""]

        for subdirectory in subdirectories:
            source_pattern = os.path.join(
                ROOT_DIR,
                "output",
                original_scenario,
                f"{generation:03d}",
                "positions",
                subdirectory,
                f"{individual_id}_*.csv"
            )

            source_files = sorted(glob.glob(source_pattern))

            if source_files:
                shutil.copy2(source_files[0], destination_dir)
            else:
                print(f"Not found: {source_pattern}")
                