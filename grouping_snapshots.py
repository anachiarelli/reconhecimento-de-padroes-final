
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

NUM_ROBOTS = 10
DIAMETER_ROBOT = 7.4
WORLD_SIZE = 316

ROBOT_COLOR = "tab:blue"

FILENAME_PATTERN = re.compile(
    r"^(?P<prefix>[^_]+)_(?P<genotype>[01]+)_(?P<run>\d+)\.csv$",
    re.IGNORECASE,
)


# ============================================================
# IDENTIFICAÇÃO DOS ARQUIVOS
# ============================================================

def parse_filename(filename):
    """
    Identifica geração, genótipo e execução.

    Exemplo:
    000_1110111111101101111000000000111110011110_0.csv
    """

    match = FILENAME_PATTERN.match(filename)

    if match:
        return {
            "prefix": match.group("prefix"),
            "genotype": match.group("genotype"),
            "run": int(match.group("run")),
        }

    return {
        "prefix": None,
        "genotype": None,
        "run": None,
    }


# ============================================================
# LEITURA DO ESTADO FINAL
# ============================================================

def read_final_positions(csv_path):
    """
    Lê somente a última linha numérica do CSV.

    Cada robô possui três valores:
    x, y e ângulo.
    """

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
                numeric_values = [float(value) for value in values]
            except ValueError:
                continue

            last_row = numeric_values

    if last_row is None:
        raise ValueError(
            f"Arquivo vazio ou sem dados numéricos: {csv_path.name}"
        )

    expected_values = NUM_ROBOTS * 3

    if len(last_row) != expected_values:
        raise ValueError(
            f"{csv_path.name}: esperados {expected_values} valores "
            f"({NUM_ROBOTS} robôs x 3), "
            f"encontrados {len(last_row)}."
        )

    data = np.asarray(last_row, dtype=float)

    if not np.isfinite(data).all():
        raise ValueError(
            f"Valores inválidos no arquivo {csv_path.name}"
        )

    data = data.reshape(NUM_ROBOTS, 3)

    positions = data[:, :2]
    angles = data[:, 2]

    return positions, angles


# ============================================================
# VISUALIZAÇÃO
# ============================================================

def save_snapshot(
    positions,
    output_path,
    generation,
    genotype,
    run,
):

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.set_xlim(0, WORLD_SIZE)
    ax.set_ylim(0, WORLD_SIZE)
    ax.set_aspect("equal")

    ax.set_title(
        f"Grouping | Generation {generation}\n"
        f"Genotype={genotype} | Run={run}",
        fontsize=11,
    )

    ax.set_xlabel("x")
    ax.set_ylabel("y")

    for i, (x, y) in enumerate(positions):

        circle = Circle(
            (x, y),
            radius=DIAMETER_ROBOT / 2,
            facecolor=ROBOT_COLOR,
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

    if num_snapshots <= 0:
        raise ValueError(
            "A quantidade de snapshots deve ser maior que zero."
        )

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
        description=(
            "Gera snapshots aleatórios do cenário grouping."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Pasta output/grouping/{data}.",
    )

    parser.add_argument(
        "--num-snapshots",
        type=int,
        default=50,
        help="Quantidade de gerações selecionadas.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semente para seleção aleatória.",
    )

    parser.add_argument(
        "--output",
        default="results/grouping/snapshots",
        help="Pasta de destino das imagens.",
    )

    args = parser.parse_args()

    rng = random.Random(args.seed)

    input_root = Path(args.input)
    output_root = Path(args.output)

    if not input_root.is_dir():
        raise FileNotFoundError(
            f"Pasta não encontrada: {input_root}"
        )

    # Localiza as pastas de geração.
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
        positions_dir = generation_dir / "positions"

        if not positions_dir.is_dir():
            print(
                f"Geração {generation}: pasta positions não encontrada."
            )
            continue

        # Cada CSV representa um indivíduo em uma execução.
        candidates = sorted(
            positions_dir.glob("*.csv")
        )

        if not candidates:
            print(
                f"Geração {generation}: nenhum CSV encontrado."
            )
            continue

        # Seleção aleatória de um indivíduo e uma execução.
        csv_path = rng.choice(candidates)

        metadata = parse_filename(csv_path.name)

        genotype = metadata["genotype"] or "unknown"
        run = metadata["run"]

        print(
            f"Geração {generation}: {csv_path.name}"
        )

        try:

            positions, angles = read_final_positions(csv_path)

            output_filename = (
                f"generation_{generation}_"
                f"{csv_path.stem}.png"
            )

            output_path = output_root / output_filename

            save_snapshot(
                positions=positions,
                output_path=output_path,
                generation=generation,
                genotype=genotype,
                run=run,
            )

            manifest.append({
                "generation": generation,
                "filename": csv_path.name,
                "genotype": genotype,
                "run": run,
                "snapshot": output_filename,
            })

        except Exception as error:

            print(
                f"Erro na geração {generation}: {error}"
            )

    # Registra as escolhas para reproduzir a amostragem.
    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest_path = output_root / "selected_samples.csv"

    with manifest_path.open("w", newline="") as file:

        fieldnames = [
            "generation",
            "filename",
            "genotype",
            "run",
            "snapshot",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(manifest)

    print("\n========== CONCLUÍDO ==========")
    print(f"Snapshots gerados: {len(manifest)}")
    print(f"Pasta: {output_root}")
    print(f"Manifesto: {manifest_path}")


if __name__ == "__main__":
    main()
