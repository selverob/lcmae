import pandas as pd
import pathlib as pl
from typing import Iterator, List, Tuple
from itertools import groupby
from os import listdir
from sys import argv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


AGENT_COLORS = {
    "RETARGETING": "green",
    "CLOSEST_FRONTIER": "blue",
    "STATIC": "orange",
    "PANICKED": "red"
}

LINE_STYLES = ['solid', 'dashed', 'dashdot', 'dotted']


def to_percentages(df: pd.DataFrame) -> pd.DataFrame:
    new_df = pd.DataFrame(columns=df.columns)
    for col in df.columns:
        new_df[col] = df[col] * 100
    return new_df


def make_plot(title: str, df: pd.DataFrame):
    plt.figure()
    for col in df:
        plt.plot(df[col], color=AGENT_COLORS[col.strip()])
        plt.title(title)
        plt.xlabel("Time")
        plt.ylabel("Safe agents")
        plt.yticks(range(0, 101, 10))
        plt.grid(True)
        plt.legend()


def chart_groups(elems: Iterator[pl.PurePath]) -> List[Tuple[str, List[pl.PurePath]]]:
    res = []
    filtered = filter(lambda p: p.suffix == ".csv", elems)
    for m, charts in groupby(filtered, lambda s: s.name.split(".")[0]):
        res.append((m, list(charts)))
    return res


def single_run_plot(path: pl.PurePath, percentages: pd.DataFrame):
    with PdfPages(path.with_suffix(".pdf")) as pp:
        make_plot(path.stem.replace("-", " "), percentages)
        pp.savefig()
        plt.close()


def group_plot(path: pl.PurePath, stems: List[str], percentages: List[pd.DataFrame]):
    plt.figure()
    plt.title(path.stem)
    plt.xlabel("Time")
    plt.ylabel("Safe agents (%)")
    plt.yticks(range(0, 101, 10))
    plt.grid(True)
    with PdfPages(path) as pp:
        for i, df in enumerate(percentages):
            for col in df:
                line_name = stems[i].split("_")[-1].split(".")[0]
                data = list(df[col])
                plt.plot(data[:data.index(100) + 1],
                         color=AGENT_COLORS[col.strip()],
                         label=f"{line_name} - {col.strip().lower()}",
                         linestyle=LINE_STYLES[i % len(LINE_STYLES)])
        plt.legend()
        pp.savefig()
        plt.close()


def process_group(group: Tuple[str, List[pl.PurePath]]):
    percentages = [to_percentages(pd.read_csv(p)) for p in group[1]]
    for path, percentage in zip(group[1], percentages):
        single_run_plot(path, percentage)
    group_plot(group[1][0].with_name(f"{group[0]}.pdf"), [p.stem for p in group[1]], percentages)


if __name__ == "__main__":
    dir_path = pl.PurePath(argv[1])
    file_paths = map(dir_path.joinpath, listdir(dir_path))
    groups = chart_groups(file_paths)
    for g in groups:
        process_group(g)
