
import argparse
import csv
import random
import re
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np


# ============================================================
# CONFIGURAÇÕES DO CENÁRIO
# ============================================================

NUM_ROBOTS = 2
NUM_OBJECTS = 5

DIAMETER_ROBOT = 7.4
DIAMETER_OBJECT = 10.0

WORLD_SIZE = 112

ROBOT_COLOR = "tab:blue"
OBJECT_COLOR = "tab:red"


# ============================================================
# IDENTIFICAÇÃO DOS ARQUIVOS
# ============================================================

def parse_filename(filename):
    """
    Identifica o indivíduo e a execução pelo nome.

    Exemplos esperados:
        001_genotype_run2.csv
        001_genotype_2.csv
        001_run2.csv
    """

    stem = Path(filename).stem
    parts = stem.split("_")

    if len(parts) < 2:
        return None

    try:
        individual_id = int(parts[0])
    except ValueError:
        return None

    # O último número do nome representa a execução.
    match = re.search(r"(?:run)?(\d+)$", stem, re.IGNORECASE)

    if not match:
        return None

    run = int(match.group(1))

    return individual_id, run


def find_matching_files(generation_dir):
    """Encontra pares de arquivos de robôs e objetos."""

    robots_dir = generation_dir / "positions" / "robots"
    objects_dir = generation_dir / "positions" / "objects"

    if not robots_dir.is_dir() or not objects_dir.is_dir():
        return []

    def build_map(directory):
        result = {}

        for path in directory.glob("*.csv"):
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
    """Lê somente a última linha numérica do CSV."""

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
                numeric_values = [float(v) for v in values]
            except ValueError:
                continue

            last_row = numeric_values

    if last_row is None:
        raise ValueError(f"Arquivo vazio: {csv_path.name}")

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
    """Lê posições x, y e ângulo dos robôs."""

    data = read_final_row(
        csv_path,
        NUM_ROBOTS * 3,
    )

    data = data.reshape(NUM_ROBOTS, 3)

    return data[:, :2], data[:, 2]


def read_final_objects(csv_path):
    """Lê posições x e y dos objetos."""

    data = read_final_row(
        csv_path,
        NUM_OBJECTS * 2,
    )

    return data.reshape(NUM_OBJECTS, 2)


# ============================================================
# VISUALIZAÇÃO
# ============================================================

def save_snapshot(
    robot_positions,
    object_positions,
    output_path,
    generation,
    individual_id,
    run,
):
    """Gera imagem com posições finais de robôs e objetos."""

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.set_xlim(0, WORLD_SIZE)
    ax.set_ylim(0, WORLD_SIZE)
    ax.set_aspect("equal")

    ax.set_title(
        f"Object Clustering | Generation {generation}\n"
        f"Individual={individual_id} | Run={run}",
        fontsize=11,
    )

    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # Robôs
    for i, (x, y) in enumerate(robot_positions):

        circle = Circle(
            (x, y),
            radius=DIAMETER_ROBOT / 2,
            facecolor=ROBOT_COLOR,
            edgecolor="black",
            linewidth=0.8,
            alpha=0.95,
        )

        ax.add_patch(circle)

        ax.text(
            x,
            y,
            f"R{i + 1}",
            ha="center",
            va="center",
            fontsize=7,
            color="white",
            fontweight="bold",
        )

    # Objetos
    for i, (x, y) in enumerate(object_positions):

        circle = Circle(
            (x, y),
            radius=DIAMETER_OBJECT / 2,
            facecolor=OBJECT_COLOR,
            edgecolor="black",
            linewidth=0.8,
            alpha=0.9,
        )

        ax.add_patch(circle)

        ax.text(
            x,
            y,
            str(i + 1),
            ha="center",
            va="center",
            fontsize=8,
            color="white",
            fontweight="bold",
        )

    ax.grid(alpha=0.2)

    fig.tight_layout()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(fig)


# ============================================================
# SELEÇÃO DAS GERAÇÕES
# ============================================================

def select_generations(generation_dirs, num_snapshots):
    """Seleciona gerações distribuídas uniformemente."""

    if len(generation_dirs) <= num_snapshots:
        return generation_dirs

    indices = np.linspace(
        0,
        len(generation_dirs) - 1,
        num_snapshots,
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

    parser = argparse.ArgumentParser(
        description="Gera snapshots aleatórios de object clustering."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Pasta object_clustering/{data}.",
    )

    parser.add_argument(
        "--num-snapshots",
        type=int,
        default=50,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    parser.add_argument(
        "--output",
        default="results/object_clustering/snapshots",
    )

    args = parser.parse_args()

    rng = random.Random(args.seed)

    input_root = Path(args.input)
    output_root = Path(args.output)

    if not input_root.is_dir():
        raise FileNotFoundError(
            f"Pasta não encontrada: {input_root}"
        )

    # Localiza automaticamente as gerações.
    generation_dirs = sorted(
        [
            path
            for path in input_root.iterdir()
            if path.is_dir() and path.name.isdigit()
        ],
        key=lambda path: int(path.name),
    )

    if not generation_dirs:
        raise FileNotFoundError(
            "Nenhuma pasta de geração encontrada."
        )

    selected_generations = select_generations(
        generation_dirs,
        args.num_snapshots,
    )

    print(f"Gerações encontradas: {len(generation_dirs)}")
    print(f"Gerações selecionadas: {len(selected_generations)}")
    print(f"Semente aleatória: {args.seed}\n")

    manifest = []

    for generation_dir in selected_generations:

        generation = generation_dir.name

        candidates = find_matching_files(generation_dir)

        if not candidates:
            print(
                f"Geração {generation}: "
                "nenhum par de arquivos encontrado."
            )
            continue

        # Escolhe aleatoriamente indivíduo e execução.
        key, robot_file, object_file = rng.choice(candidates)

        individual_id, run = key

        try:

            robot_positions, robot_angles = read_final_robots(
                robot_file
            )

            object_positions = read_final_objects(
                object_file
            )

            filename = (
                f"generation_{generation}"
                f"_individual_{individual_id}"
                f"_run_{run}.png"
            )

            output_path = output_root / filename

            save_snapshot(
                robot_positions=robot_positions,
                object_positions=object_positions,
                output_path=output_path,
                generation=generation,
                individual_id=individual_id,
                run=run,
            )

            manifest.append({
                "generation": generation,
                "individual_id": individual_id,
                "run": run,
                "robot_file": robot_file.name,
                "object_file": object_file.name,
                "snapshot": filename,
            })

            print(
                f"Geração {generation}: "
                f"indivíduo {individual_id}, run {run}"
            )

        except Exception as error:

            print(
                f"Erro na geração {generation}: {error}"
            )

    # Registra as escolhas aleatórias.
    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest_path = output_root / "selected_samples.csv"

    with manifest_path.open("w", newline="") as file:

        fieldnames = [
            "generation",
            "individual_id",
            "run",
            "robot_file",
            "object_file",
            "snapshot",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(manifest)

    print("\n========== CONCLUÍDO ==========")
    print(f"Imagens geradas: {len(manifest)}")
    print(f"Pasta: {output_root}")
    print(f"Manifesto: {manifest_path}")


if __name__ == "__main__":
    main()
