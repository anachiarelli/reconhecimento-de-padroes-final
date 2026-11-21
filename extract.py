import argparse
import csv
import random
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np


# Define os cenários, seus rótulos de classe e os parâmetros visuais de cada simulação.
SCENARIOS = ("grouping", "sorting_groups", "object_clustering")
CLASS_LABEL = {"grouping": 0, "object_clustering": 1, "sorting_groups": 2}

CONFIG = {
    "grouping": {
        "robots": 10,
        "robot_diameter": 7.4,
        "world_size": 316.0,
        "robot_color": "tab:blue",
    },
    "sorting_groups": {
        "robots": 30,
        "robot_diameter": 7.4,
        "world_size": 450.0,
        "robot_color": None,  # As cores vêm do CSV.
    },
    "object_clustering": {
        "robots": 2,
        "objects": 5,
        "robot_diameter": 7.4,
        "object_diameter": 10.0,
        "world_size": 112.0,
        "robot_color": "tab:blue",
        "object_color": "tab:red",
    },
}

# Relaciona os valores RGB encontrados nos CSVs de sorting_groups às cores usadas nas imagens.
SORTING_COLORS = {
    (1, 0, 0): "red",
    (0, 1, 0): "green",
    (0, 0, 1): "blue",
}


# Armazena os caminhos dos arquivos que representam um indivíduo de uma geração.
@dataclass
class Candidate:
    scenario: str
    generation: str
    robot_csv: Path
    object_csv: Path | None = None


# Guarda os dados de um instante escolhido da trajetória: posições, cores e quantidade de cores.
@dataclass
class Snapshot:
    positions: np.ndarray
    colors: list[str]
    num_colors: int
    time_step: int
    object_positions: np.ndarray | None = None


# Lista as pastas de gerações diretamente dentro da pasta do cenário.
def generation_dirs(scenario_dir: Path) -> list[Path]:
    return sorted(
        (path for path in scenario_dir.iterdir()
         if path.is_dir() and path.name.isdigit()),
        key=lambda path: int(path.name),
    )


# Extrai do nome do arquivo o ID do indivíduo e o número da execução para parear robôs e objetos.
def object_file_key(path: Path) -> tuple[int, int] | None:
    """Identifica arquivos correspondentes pelo ID do indivíduo e número da execução."""
    parts = path.stem.split("_")
    if len(parts) < 2 or not parts[0].isdigit():
        return None

    match = re.search(r"(?:run)?(\d+)$", path.stem, re.IGNORECASE)
    return (int(parts[0]), int(match.group(1))) if match else None


# Coleta os indivíduos disponíveis em cada geração. No object_clustering, associa os CSVs
# de robôs e objetos usando o identificador presente nos nomes dos arquivos.
def collect_candidates(scenario_dir: Path, scenario: str) -> list[Candidate]:
    candidates = []

    for generation in generation_dirs(scenario_dir):
        if scenario == "grouping":
            robot_dir = generation / "positions"
        elif scenario == "sorting_groups":
            robot_dir = generation / "positions" / "robots"
        else:
            robot_dir = generation / "positions" / "robots"
            object_dir = generation / "positions" / "objects"
            if not robot_dir.is_dir() or not object_dir.is_dir():
                continue

            def indexed_files(directory: Path) -> dict[tuple[int, int], Path]:
                files = {}
                for path in directory.glob("*.csv"):
                    key = object_file_key(path)
                    if key is not None:
                        files[key] = path
                return files

            robots = indexed_files(robot_dir)
            objects = indexed_files(object_dir)
            for key in sorted(robots.keys() & objects.keys()):
                candidates.append(
                    Candidate(scenario, generation.name, robots[key], objects[key])
                )
            continue

        if robot_dir.is_dir():
            candidates.extend(
                Candidate(scenario, generation.name, path)
                for path in sorted(robot_dir.glob("*.csv"))
                if path.is_file()
            )

    return candidates


# Lê o CSV e mantém as linhas numéricas com a quantidade esperada de valores.
# A chave é o número original da linha, usado para alinhar arquivos temporais.
def read_rows(path: Path, expected_values: int) -> dict[int, np.ndarray]:
    """Lê linhas numéricas válidas, preservando o número físico da linha no CSV."""
    rows = {}
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        for line_number, row in enumerate(csv.reader(file), start=1):
            values = [value.strip() for value in row if value.strip()]
            if not values:
                continue
            try:
                data = np.asarray([float(value) for value in values], dtype=float)
            except ValueError:
                continue
            if data.size == expected_values and np.isfinite(data).all():
                rows[line_number] = data
    return rows


# Escolhe aleatoriamente um instante válido da trajetória e extrai as posições e cores.
# Cada cenário possui um formato próprio de dados nos arquivos CSV.
def read_snapshot(candidate: Candidate, rng: random.Random) -> Snapshot:
    scenario = candidate.scenario
    config = CONFIG[scenario]
    robot_rows = read_rows(candidate.robot_csv, config["robots"] * (
        6 if scenario == "sorting_groups" else 3
    ))

    if scenario == "object_clustering":
        object_rows = read_rows(candidate.object_csv, config["objects"] * 2)
        valid_lines = sorted(robot_rows.keys() & object_rows.keys())
    else:
        object_rows = {}
        valid_lines = sorted(robot_rows)

    line = rng.choice(valid_lines)
    robots = robot_rows[line].reshape(config["robots"], -1)
    positions = robots[:, :2]

    # Define as cores e a quantidade de cores conforme o cenário.
    if scenario == "grouping":
        colors = [config["robot_color"]] * config["robots"]
        num_colors = 1
        object_positions = None

    elif scenario == "sorting_groups":
        colors = []
        distinct_colors = set()
        for rgb in robots[:, 3:6]:
            if rgb.max() > 1.01:
                rgb = rgb / 255.0
            key = tuple(np.rint(np.clip(rgb, 0, 1)).astype(int))
            distinct_colors.add(key)
            colors.append(SORTING_COLORS[key])
        num_colors = len(distinct_colors)
        object_positions = None

    else:
        colors = [config["robot_color"]] * config["robots"]
        num_colors = 2  # Robôs azuis e objetos vermelhos.
        object_positions = object_rows[line].reshape(config["objects"], 2)

    return Snapshot(
        positions=positions,
        colors=colors,
        num_colors=num_colors,
        time_step=line - 1,
        object_positions=object_positions,
    )


# Desenha os robôs e, quando aplicável, os objetos no espaço de simulação e salva a imagem.
def generate_image(snapshot: Snapshot, scenario: str, output: Path) -> None:
    config = CONFIG[scenario]
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, config["world_size"])
    ax.set_ylim(0, config["world_size"])
    ax.set_aspect("equal")
    ax.axis("off")

    robot_linewidth = 0.35 if scenario == "sorting_groups" else 0.8
    robot_alpha = 0.95 if scenario == "sorting_groups" else 0.9

    for (x, y), color in zip(snapshot.positions, snapshot.colors):
        ax.add_patch(Circle(
            (float(x), float(y)),
            radius=config["robot_diameter"] / 2,
            facecolor=color,
            edgecolor="black",
            linewidth=robot_linewidth,
            alpha=robot_alpha,
        ))

    if snapshot.object_positions is not None:
        for x, y in snapshot.object_positions:
            ax.add_patch(Circle(
                (float(x), float(y)),
                radius=config["object_diameter"] / 2,
                facecolor=config["object_color"],
                edgecolor="black",
                linewidth=0.8,
                alpha=0.9,
            ))

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160, bbox_inches="tight", pad_inches=0, facecolor="white")
    plt.close(fig)


# Seleciona, sem reposição, a quantidade configurada de indivíduos de cada cenário
# nas gerações escolhidas e embaralha a ordem final das amostras.
def select_individuals(
    candidates: list[Candidate],
    samples_per_generation: dict[int, int],
    rng: random.Random,
) -> list[Candidate]:
    selected = []

    for scenario in SCENARIOS:
        scenario_candidates = [item for item in candidates if item.scenario == scenario]

        for generation, quantity in samples_per_generation.items():
            pool = [
                item for item in scenario_candidates
                if int(item.generation) == generation
            ]
            selected.extend(rng.sample(pool, quantity))

    rng.shuffle(selected)
    return selected


# Define os caminhos de entrada e saída e os parâmetros de amostragem recebidos pela linha de comando.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seleciona indivíduos, extrai uma amostra temporal e gera imagens/CSVs."
    )
    parser.add_argument("--grouping-root", type=Path, default=Path("output/grouping"))
    parser.add_argument("--sorting-root", type=Path, default=Path("output/sorting_groups"))
    parser.add_argument(
        "--object-clustering-root",
        type=Path,
        default=Path("output/object_clustering"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results"),
    )
    parser.add_argument("--generation-zero-samples", type=int, default=5)
    parser.add_argument("--generation-final-samples", type=int, default=10)
    parser.add_argument("--generation-zero", type=int, default=0)
    parser.add_argument("--generation-final", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


# Coordena o processamento: coleta os indivíduos, seleciona as amostras,
# gera as imagens e exporta as features e os rótulos em CSV.
def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    # Associa cada cenário à pasta onde seus resultados de simulação estão armazenados.
    roots = {
        "grouping": args.grouping_root,
        "sorting_groups": args.sorting_root,
        "object_clustering": args.object_clustering_root,
    }

    # Reúne os indivíduos encontrados em todas as gerações de cada cenário.
    all_candidates = []
    for scenario, root in roots.items():
        candidates = collect_candidates(root, scenario)
        all_candidates.extend(candidates)

    # Seleciona os indivíduos das gerações inicial e final conforme os parâmetros informados.
    selected = select_individuals(
        all_candidates,
        {
            args.generation_zero: args.generation_zero_samples,
            args.generation_final: args.generation_final_samples,
        },
        rng,
    )

    # Prepara a pasta que receberá as imagens geradas.
    image_dir = args.output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    # Armazena separadamente a feature numérica e o rótulo de classe de cada imagem.
    features, labels = [], []

    # Processa cada indivíduo: escolhe um instante, salva a imagem e registra seus dados.
    for index, candidate in enumerate(selected, start=1):
        instance = f"{index:03d}"
        snapshot = read_snapshot(candidate, rng)
        class_label = CLASS_LABEL[candidate.scenario]
        generate_image(
            snapshot,
            candidate.scenario,
            image_dir / f"class_{class_label}" / f"instance_{instance}.png",
        )

        features.append({
            "num_colors": snapshot.num_colors,
        })
        labels.append({
            "instance": instance,
            "class_label": class_label,
        })

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Exporta os dados extraídos. A ordem das linhas corresponde à numeração das imagens.
    for filename, rows, fieldnames in (
        ("features.csv", features, ["num_colors"]),
        ("labels.csv", labels, ["instance", "class_label"]),
    ):
        with (args.output_dir / filename).open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


# Executa o processamento quando o arquivo é chamado diretamente.
if __name__ == "__main__":
    main()
