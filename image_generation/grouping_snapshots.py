
import csv
import random
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path("output/grouping")
OUTPUT_DIR = Path("results/grouping/snapshots")

NUM_ROBOTS = 10
DIAMETER_ROBOT = 7.4
WORLD_SIZE = 316

NUM_SNAPSHOTS = 50
SEED = 42

ROBOT_COLOR = "tab:blue"

ROBOT_COLORS = {
    (1, 0, 0): "#e74c3c",
    (0, 1, 0): "#2ecc71",
    (0, 0, 1): "#3498db",
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
            return datetime.fromtimestamp(path.stat().st_mtime)

    return max(executions, key=execution_date)


# ============================================================
# LEITURA DO ESTADO FINAL
# ============================================================

def read_final_positions(csv_path):

    last_row = None

    with csv_path.open("r", newline="") as file:
        reader = csv.reader(file)

        for row in reader:

            try:
                values = [
                    float(value.strip())
                    for value in row
                    if value.strip()
                ]
            except ValueError:
                continue

            if values:
                last_row = values

    if last_row is None:
        raise ValueError("Nenhum dado numérico encontrado.")

    data = np.asarray(last_row, dtype=float)

    if not np.isfinite(data).all():
        raise ValueError("Valores inválidos.")

    if len(data) == NUM_ROBOTS * 3:

        data = data.reshape(NUM_ROBOTS, 3)

        positions = data[:, :2]
        colors = [ROBOT_COLOR] * NUM_ROBOTS

    elif len(data) == NUM_ROBOTS * 6:

        data = data.reshape(NUM_ROBOTS, 6)

        positions = data[:, :2]

        colors = [
            ROBOT_COLORS.get(
                tuple(int(round(v)) for v in rgb),
                "gray"
            )
            for rgb in data[:, 3:6]
        ]

    else:
        raise ValueError(
            f"Esperados {NUM_ROBOTS * 3} ou "
            f"{NUM_ROBOTS * 6} valores; "
            f"encontrados {len(data)}."
        )

    return positions, colors


# ============================================================
# GERAÇÃO DA IMAGEM
# ============================================================

def save_snapshot(positions, colors, output_path):

    fig, ax = plt.subplots(figsize=(8, 8))

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.set_xlim(0, WORLD_SIZE)
    ax.set_ylim(0, WORLD_SIZE)
    ax.set_aspect("equal")

    ax.axis("off")

    for (x, y), color in zip(positions, colors):

        circle = Circle(
            (x, y),
            radius=DIAMETER_ROBOT / 2,
            facecolor=color,
            edgecolor="black",
            linewidth=0.8,
            alpha=0.9,
        )

        ax.add_patch(circle)

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
        positions_dir = generation_dir / "positions"

        if not positions_dir.is_dir():
            print(f"Geração {generation}: positions não encontrada.")
            continue

        candidates = sorted(
            path for path in positions_dir.iterdir()
            if path.is_file()
        )

        if not candidates:
            print(f"Geração {generation}: nenhum arquivo encontrado.")
            continue

        csv_path = rng.choice(candidates)

        try:

            positions, colors = read_final_positions(csv_path)

            output_filename = f"generation_{generation}.png"
            output_path = OUTPUT_DIR / output_filename

            save_snapshot(
                positions,
                colors,
                output_path,
            )

            generated += 1

            print(f"Geração {generation}: OK")

        except Exception as error:

            print(f"Geração {generation}: erro - {error}")

    print("\n========== CONCLUÍDO ==========")
    print(f"Imagens geradas: {generated}")
    print(f"Destino: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
