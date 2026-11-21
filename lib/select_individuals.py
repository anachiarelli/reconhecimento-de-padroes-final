import os
import shutil
import glob

# For each scenario in /output/{scenario}/, initialize a list to hold tuples of:
# (fitness_value, generation, individual_id, scenario) for each individual in each generation.
SCENARIOS = ("grouping", "sorting_groups", "object_clustering")
CLASS_SIZE = 10

scenario_data = {}
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

# Create the scenarios classes with CLASS_SIZE best individuals for each scenario
classes = {
    scenario: scenario_data[scenario][:CLASS_SIZE]
    for scenario in SCENARIOS
}

# Create the unclassified class using the bottom individuals proportionally.
undefined_class = []

base_size = CLASS_SIZE // len(SCENARIOS)
remainder = CLASS_SIZE % len(SCENARIOS)

for i, scenario in enumerate(SCENARIOS):
    quantity = base_size + (1 if i < remainder else 0)

    undefined_class.extend(scenario_data[scenario][-quantity:] if quantity else [])

classes["undefined"] = undefined_class

# Copy the selected individual CSV files to /instances/{scenario}
for scenario, individuals in classes.items():
    scenario_dir = os.path.join(ROOT_DIR, "instances", scenario)
    os.makedirs(scenario_dir, exist_ok=True)

    for _, generation, individual_id, original_scenario in individuals:
        individual_id = f"{int(individual_id):03d}"

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

            source_files = glob.glob(source_pattern)

            if source_files:
                shutil.copy2(source_files[0], scenario_dir)
            else:
                print(f"Not found: {source_pattern}")