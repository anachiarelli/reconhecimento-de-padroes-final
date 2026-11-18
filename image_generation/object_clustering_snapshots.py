
import csv
import random
import re
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path("output/object_clustering")
OUTPUT_DIR = Path("results/object_clustering/snapshots")

NUM_ROBOTS = 2
NUM_OBJECTS = 5

DIAMETER_ROBOT = 7.4
DIAMETER_OBJECT = 10.0

WORLD_SIZE = 112

ROBOT_COLOR = "tab:blue"
OBJECT_COLOR = "tab:red"

NUM_SNAPSHOTS = 50
SEED = 42


# ============================================================
# LOCALIZAÇÃO DA EXECUÇÃO
# ============================================================

def find_latest_execution():

    executions = [
        p for p in BASE_DIR.iterdir()
        if p.is_dir()
    ]

    if not executions:
        raise FileNotFoundError(
            f"Nenhuma execução encontrada em {BASE_DIR}"
        )

    def execution_date(path):
        try:
            return datetime.strptime(
                path.name,
                "%d-%m-%Y %H-%M-%S"
            )
        except ValueError:
            return datetime.fromtimestamp(
                path.stat().st_mtime
            )

    return max(executions, key=execution_date)


# ============================================================
# IDENTIFICAÇÃO DOS ARQUIVOS
# ============================================================

def parse_filename(filename):

    stem = Path(filename).stem

    parts = stem.split("_")

    if len(parts) < 2:
        return None

    try:
        individual_id = int(parts[0])
    except ValueError:
        return None

    match = re.search(
        r"(?:run)?(\d+)$",
        stem,
        re.IGNORECASE
    )

    if not match:
        return None

    run = int(match.group(1))

    return individual_id, run


def find_matching_files(generation_dir):

    robots_dir = generation_dir / "positions" / "robots"
    objects_dir = generation_dir / "positions" / "objects"

    if not robots_dir.is_dir() or not objects_dir.is_dir():
        return []

    def build_map(directory):

        result = {}

        for path in directory.iterdir():

            if not path.is_file() or path.suffix.lower() != ".csv":
                continue

            key = parse_filename(path.name)

            if key is not None:
                result[key] = path

        return result

    robot_map = build_map(robots_dir)
    object_map = build_map(objects_dir)

    common_keys = sorted(
        set(robot_map.keys()) & set(object_map.keys())
    )

    return [
        (key, robot_map[key], object_map[key])
        for key in common_keys
    ]


# ============================================================
# LEITURA DOS ESTADOS FINAIS
# ============================================================

def read_final_row(csv_path, expected_values):

    last_row = None

    with csv_path.open("r", newline="") as file:

        reader = csv.reader(file)

        for row in reader:

            values = [
                value.strip()
                for value in row
                if value.strip()
            ]

            if not values:
                continue

            try:
                numeric_values = [
                    float(value) for value in values
                ]
            except ValueError:
                continue

            last_row = numeric_values

    if last_row is None:
        raise ValueError(
            f"Arquivo vazio: {csv_path.name}"
        )

    if len(last_row) != expected_values:
        raise ValueError(
            f"{csv_path.name}: esperados {expected_values} "
            f"valores, encontrados {len(last_row)}."
        )

    data = np.asarray(last_row, dtype=float)

    if not np.isfinite(data).all():
        raise ValueError(
            f"Valores inválidos em {csv_path.name}"
        )

    return data


def read_final_robots(csv_path):

    data = read_final_row(
        csv_path,
        NUM_ROBOTS * 3,
    )

    data = data.reshape(NUM_ROBOTS, 3)

    return data[:, :2], data[:, 2]


def read_final_objects(csv_path):

    data = read_final_row(
        csv_path,
        NUM_OBJECTS * 2,
    )

    return data.reshape(NUM_OBJECTS, 2)


# ============================================================
# GERAÇÃO DA IMAGEM
# ============================================================

def save_snapshot(
    robot_positions,
    object_positions,
    output_path,
):

    fig, ax = plt.subplots(figsize=(8, 8))

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.set_xlim(0, WORLD_SIZE)
    ax.set_ylim(0, WORLD_SIZE)
    ax.set_aspect("equal")

    ax.axis("off")

    # Robôs
    for x, y in robot_positions:

        ax.add_patch(
            Circle(
                (x, y),
                radius=DIAMETER_ROBOT / 2,
                facecolor=ROBOT_COLOR,
                edgecolor="black",
                linewidth=0.8,
                alpha=0.95,
            )
        )

    # Objetos
    for x, y in object_positions:

        ax.add_patch(
            Circle(
                (x, y),
                radius=DIAMETER_OBJECT / 2,
                facecolor=OBJECT_COLOR,
                edgecolor="black",
                linewidth=0.8,
                alpha=0.9,
            )
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
        pad_inches=0,
        facecolor="white",
    )

    plt.close(fig)


# ============================================================
# SELEÇÃO DAS GERAÇÕES
# ============================================================

def select_generations(generation_dirs):

    if len(generation_dirs) <= NUM_SNAPSHOTS:
        return generation_dirs

    indices = np.linspace(
        0,
        len(generation_dirs) - 1,
        NUM_SNAPSHOTS,
    )

    indices = sorted(set(
        round(index) for index in indices
    ))

    return [
        generation_dirs[index]
        for index in indices
    ]


# ============================================================
# PROCESSAMENTO
# ============================================================

def main():

    rng = random.Random(SEED)

    if not BASE_DIR.is_dir():
        raise FileNotFoundError(
            f"Pasta não encontrada: {BASE_DIR}"
        )

    input_root = find_latest_execution()

    generation_dirs = sorted(
        [
            path for path in input_root.iterdir()
            if path.is_dir() and path.name.isdigit()
        ],
        key=lambda path: int(path.name),
    )

    if not generation_dirs:
        raise FileNotFoundError(
            f"Nenhuma geração encontrada em {input_root}"
        )

    selected_generations = select_generations(
        generation_dirs
    )

    print(f"Execução: {input_root}")
    print(f"Gerações encontradas: {len(generation_dirs)}")
    print(f"Gerações selecionadas: {len(selected_generations)}")

    generated = 0

    for generation_dir in selected_generations:

        generation = generation_dir.name

        candidates = find_matching_files(
            generation_dir
        )

        if not candidates:
            print(
                f"Geração {generation}: "
                "nenhum par de arquivos encontrado."
            )
            continue

        # Seleciona indivíduo e execução aleatoriamente.
        key, robot_file, object_file = rng.choice(candidates)

        individual_id, run = key

        try:

            robot_positions, robot_angles = read_final_robots(
                robot_file
            )

            object_positions = read_final_objects(
                object_file
            )

            output_path = (
                OUTPUT_DIR / f"generation_{generation}.png"
            )

            save_snapshot(
                robot_positions=robot_positions,
                object_positions=object_positions,
                output_path=output_path,
            )

            generated += 1

            print(f"Geração {generation}: OK")

        except Exception as error:

            print(
                f"Geração {generation}: erro - {error}"
            )

    print("\n========== CONCLUÍDO ==========")
    print(f"Imagens geradas: {generated}")
    print(f"Destino: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
