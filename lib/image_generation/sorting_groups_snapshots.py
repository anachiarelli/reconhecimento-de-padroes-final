
import csv
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path("output/sorting_groups")
OUTPUT_DIR = Path("results/sorting_groups/snapshots")

NUM_ROBOTS = 30
DIAMETER_ROBOT = 10.0
WORLD_SIZE = 450

NUM_SNAPSHOTS = 50
SEED = 42

COLORS = {
    (1, 0, 0): "red",
    (0, 1, 0): "green",
    (0, 0, 1): "blue",
}


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
# LEITURA DO ESTADO FINAL
# ============================================================

def read_final_positions(csv_path):

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
                numeric = [float(v) for v in values]
            except ValueError:
                continue

            last_row = numeric

    if last_row is None:
        raise ValueError(
            f"Nenhuma linha numérica em {csv_path.name}"
        )

    expected = NUM_ROBOTS * 6

    if len(last_row) != expected:
        raise ValueError(
            f"{csv_path.name}: esperados {expected} valores, "
            f"encontrados {len(last_row)}."
        )

    data = np.asarray(last_row, dtype=float)

    if not np.isfinite(data).all():
        raise ValueError("Valores inválidos.")

    data = data.reshape(NUM_ROBOTS, 6)

    robots = []

    for x, y, angle, r, g, b in data:

        rgb = np.array([r, g, b], dtype=float)

        # Aceita RGB entre 0-1 ou 0-255.
        if rgb.max() > 1.01:
            rgb = rgb / 255.0

        rgb = np.clip(rgb, 0, 1)

        color_key = tuple(
            np.round(rgb).astype(int)
        )

        if color_key not in COLORS:
            raise ValueError(
                f"Cor RGB não reconhecida: {rgb}"
            )

        robots.append({
            "x": x,
            "y": y,
            "color": COLORS[color_key],
        })

    return robots


# ============================================================
# GERAÇÃO DA IMAGEM
# ============================================================

def save_snapshot(robots, output_path):

    fig, ax = plt.subplots(figsize=(8, 8))

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.set_xlim(0, WORLD_SIZE)
    ax.set_ylim(0, WORLD_SIZE)
    ax.set_aspect("equal")

    ax.axis("off")

    ax.set_position([0, 0, 1, 1])

    for robot in robots:

        circle = Circle(
            (robot["x"], robot["y"]),
            radius=DIAMETER_ROBOT / 2,
            facecolor=robot["color"],
            edgecolor="black",
            linewidth=0.35,
            alpha=0.95,
        )

        ax.add_patch(circle)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=160,
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

        robots_dir = (
            generation_dir / "positions" / "robots"
        )

        if not robots_dir.is_dir():
            print(
                f"Geração {generation}: "
                "pasta robots não encontrada."
            )
            continue

        candidates = sorted(
            path for path in robots_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".csv"
        )

        if not candidates:
            print(
                f"Geração {generation}: "
                "nenhum CSV encontrado."
            )
            continue

        # Seleciona aleatoriamente um indivíduo.
        csv_path = rng.choice(candidates)

        try:

            robots = read_final_positions(csv_path)

            output_path = (
                OUTPUT_DIR / f"generation_{generation}.png"
            )

            save_snapshot(
                robots,
                output_path,
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
