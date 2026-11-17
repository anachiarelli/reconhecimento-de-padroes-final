
#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


# ============================================================
# CONFIGURAÇÕES DO CENÁRIO
# ============================================================

NUM_ROBOTS = 30
DIAMETER_ROBOT = 10.0
WORLD_SIZE = 450

COLORS = {
    (1, 0, 0): "red",
    (0, 1, 0): "green",
    (0, 0, 1): "blue",
}


# ============================================================
# LEITURA DOS DADOS
# ============================================================

def read_fitness(generation_dir):
    """Lê os valores de fitness da geração."""

    fitness_file = generation_dir / "fitness.csv"

    if not fitness_file.is_file():
        return []

    fitnesses = []

    with fitness_file.open("r") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                fitnesses.append(float(line) * 100)
            except ValueError:
                fitnesses.append(np.nan)

    return fitnesses


def read_final_positions(pos_file):
    """
    Lê a última linha do CSV.

    Cada robô possui:
        x, y, angle, r, g, b

    Total esperado:
        30 * 6 = 180 valores.
    """

    final_values = None

    with pos_file.open("r", newline="") as file:
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
                numeric = [float(value) for value in values]
            except ValueError:
                continue

            final_values = numeric

    if final_values is None:
        raise ValueError("Nenhuma linha numérica encontrada.")

    expected = NUM_ROBOTS * 6

    if len(final_values) != expected:
        raise ValueError(
            f"Esperados {expected} valores, "
            f"encontrados {len(final_values)}."
        )

    data = np.asarray(final_values).reshape(NUM_ROBOTS, 6)

    robots = []

    for robot in data:

        x, y, angle, r, g, b = robot

        rgb = np.array([r, g, b], dtype=float)

        # Aceita RGB entre 0-1 ou 0-255.
        if rgb.max() > 1.01:
            rgb = rgb / 255.0

        rgb = np.clip(rgb, 0, 1)

        # Identifica a cor predominante.
        color_key = tuple(
            int(value == rgb.max())
            for value in rgb
        )

        # Para RGB exatamente primário.
        if tuple(np.round(rgb).astype(int)) in COLORS:
            color_key = tuple(
                np.round(rgb).astype(int)
            )

        if color_key not in COLORS:
            raise ValueError(f"Cor RGB não reconhecida: {rgb}")

        robots.append({
            "x": x,
            "y": y,
            "angle": angle,
            "rgb": rgb,
            "color": COLORS[color_key],
        })

    return robots


# ============================================================
# IDENTIFICAÇÃO DOS INDIVÍDUOS
# ============================================================

def get_individual_id(filename):
    """
    Extrai o ID do indivíduo.

    Exemplo:
        003_genotype_0.csv -> 3
    """

    try:
        return int(filename.split("_")[0])
    except (ValueError, IndexError):
        return None


def get_run(filename):
    """Extrai o número da execução no final do nome."""

    try:
        return int(Path(filename).stem.split("_")[-1])
    except ValueError:
        return None


# ============================================================
# DESENHO DE UMA SIMULAÇÃO
# ============================================================

def draw_simulation(ax, robots, fitness=None):

    ax.set_xlim(0, WORLD_SIZE)
    ax.set_ylim(0, WORLD_SIZE)
    ax.set_aspect("equal")

    ax.set_xticks([])
    ax.set_yticks([])

    ax.grid(False)

    if fitness is None or np.isnan(fitness):
        title = "Fitness: n/a"
    else:
        title = f"Fitness: {fitness:.2f}"

    ax.set_title(title, fontsize=9, pad=4)

    for robot in robots:

        circle = Circle(
            (robot["x"], robot["y"]),
            DIAMETER_ROBOT / 2,
            facecolor=robot["color"],
            edgecolor="black",
            linewidth=0.35,
            alpha=0.95,
        )

        ax.add_patch(circle)


# ============================================================
# GERAÇÃO DA GRADE
# ============================================================

def make_generation_grid(
    output_base,
    generation,
    out_dir,
    rows=8,
    cols=5,
):

    generation_dir = output_base / generation

    robots_dir = (
        generation_dir / "positions" / "robots"
    )

    if not robots_dir.is_dir():
        print(f"Diretório não encontrado: {robots_dir}")
        return

    # --------------------------------------------------------
    # Arquivos da execução 0
    # --------------------------------------------------------

    robot_files = [
        path
        for path in robots_dir.glob("*.csv")
        if get_run(path.name) == 0
    ]

    if not robot_files:
        print(f"Nenhum arquivo da execução 0 em {robots_dir}")
        return

    # --------------------------------------------------------
    # Associação entre indivíduo e fitness
    # --------------------------------------------------------

    fitnesses = read_fitness(generation_dir)

    individuals = []

    for path in robot_files:

        individual_id = get_individual_id(path.name)

        if individual_id is None:
            continue

        if individual_id < len(fitnesses):
            fitness = fitnesses[individual_id]
        else:
            fitness = np.nan

        individuals.append({
            "id": individual_id,
            "path": path,
            "fitness": fitness,
        })

    # Ordena por fitness decrescente.
    # Valores NaN ficam no final.

    individuals.sort(
        key=lambda item: (
            np.isnan(item["fitness"]),
            -item["fitness"]
            if not np.isnan(item["fitness"])
            else 0,
        )
    )

    # Seleciona os melhores indivíduos.
    max_individuals = rows * cols
    selected = individuals[:max_individuals]

    if not selected:
        print(f"Nenhum indivíduo válido na geração {generation}")
        return

    # --------------------------------------------------------
    # Criação da figura
    # --------------------------------------------------------

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(cols * 2.2, rows * 2.2),
        dpi=120,
    )

    axes = np.asarray(axes).flatten()

    fig.suptitle(
        f"Sorting Groups - Generation {generation}",
        fontsize=15,
        y=0.995,
    )

    fig.subplots_adjust(
        left=0.03,
        right=0.97,
        top=0.96,
        bottom=0.03,
        wspace=0.12,
        hspace=0.25,
    )

    # --------------------------------------------------------
    # Desenho dos indivíduos
    # --------------------------------------------------------

    for index, ax in enumerate(axes):

        if index < len(selected):

            individual = selected[index]

            try:
                robots = read_final_positions(
                    individual["path"]
                )

                draw_simulation(
                    ax,
                    robots,
                    individual["fitness"],
                )

                ax.text(
                    0.03,
                    0.03,
                    f"ID: {individual['id']}",
                    transform=ax.transAxes,
                    fontsize=7,
                    color="black",
                )

            except Exception as error:

                ax.set_title(
                    f"Erro no indivíduo {individual['id']}",
                    fontsize=8,
                )

                ax.text(
                    0.5,
                    0.5,
                    str(error),
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                    fontsize=6,
                    wrap=True,
                )

        else:
            ax.axis("off")

    # --------------------------------------------------------
    # Legenda das cores
    # --------------------------------------------------------

    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D(
            [0], [0],
            marker="o",
            color="w",
            label="Vermelho",
            markerfacecolor="red",
            markeredgecolor="black",
            markersize=8,
        ),
        Line2D(
            [0], [0],
            marker="o",
            color="w",
            label="Verde",
            markerfacecolor="green",
            markeredgecolor="black",
            markersize=8,
        ),
        Line2D(
            [0], [0],
            marker="o",
            color="w",
            label="Azul",
            markerfacecolor="blue",
            markeredgecolor="black",
            markersize=8,
        ),
    ]

    fig.legend(
        handles=legend_elements,
        loc="lower center",
        ncol=3,
        fontsize=9,
        bbox_to_anchor=(0.5, -0.005),
    )

    # --------------------------------------------------------
    # Salvar
    # --------------------------------------------------------

    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        out_dir / f"sorting_groups_{generation}.png"
    )

    fig.savefig(
        output_path,
        dpi=120,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Imagem salva: {output_path}")


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Gera snapshots do cenário sorting_groups."
    )

    parser.add_argument(
        "--output-base",
        required=True,
        help="Diretório raiz das gerações de sorting_groups.",
    )

    parser.add_argument(
        "--generations",
        default="000,002,005,010,020,030,040,060,080,100",
        help="Gerações separadas por vírgula.",
    )

    parser.add_argument(
        "--out-dir",
        default="results/sorting_groups/snapshots",
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=8,
    )

    parser.add_argument(
        "--cols",
        type=int,
        default=5,
    )

    args = parser.parse_args()

    output_base = Path(args.output_base)
    out_dir = Path(args.out_dir)

    generations = [
        generation.strip()
        for generation in args.generations.split(",")
        if generation.strip()
    ]

    for generation in generations:

        make_generation_grid(
            output_base=output_base,
            generation=generation,
            out_dir=out_dir,
            rows=args.rows,
            cols=args.cols,
        )


if __name__ == "__main__":
    main()
