import pandas as pd
import pathlib as pl
from typing import Iterator, List, Tuple
from itertools import groupby
from os import listdir
from sys import argv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.cm import get_cmap


AGENT_COLORS = {
    "RETARGETING": "green",
    "CLOSEST_FRONTIER": "blue",
    "STATIC": "orange",
    "PANICKED": "red"
}

AGENT_STYLES = {
    "RETARGETING": "dashed",
    "CLOSEST_FRONTIER": "solid",
    "STATIC": "dotted",
    "PANICKED": "dashdot"
}


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
    filtered = [p for p in elems if p.suffix == ".csv"]
    filtered.sort()
    for m, charts in groupby(filtered, lambda s: s.name.split(".")[0]):
        res.append((m, list(charts)))
    return res


def single_run_plot(path: pl.PurePath, percentages: pd.DataFrame):
    with PdfPages(path.with_suffix(".pdf")) as pp:
        make_plot(path.stem.replace("-", " "), percentages)
        pp.savefig()
        plt.close()


def group_plot(axis: plt.Axes, title: str, stems: List[str], percentages: List[pd.DataFrame]):
    axis.set_title(title)
    axis.set_xlabel("Čas")
    axis.set_ylabel("Agenty v bezpečí (%)")
    axis.set_yticks(range(0, 101, 10))
    axis.grid(True)
    legend: Tuple[List[plt.Line2D], List[str]] = ([], [])
    dark = get_cmap("Dark2")
    for i, df in enumerate(percentages):
        line_name = stems[i].split("_")[-1].split(".")[0]
        for (j, col) in enumerate(df):
            data = list(df[col])
            xdata = data[:data.index(100) + 1]
            axis.plot(xdata,
                      color=dark(i),
                      linestyle=AGENT_STYLES[col.strip()],
                      linewidth=2)
            if j == 0:
                legend_line = plt.Line2D(xdata,
                                         range(0, len(xdata)),
                                         color=dark(i),
                                         linestyle="solid")
                legend[0].append(legend_line)
                legend[1].append(line_name)
    axis.legend(*legend, loc=4, fontsize="large")


def process_group(group: Tuple[str, List[pl.PurePath]], group_axis: plt.Axes):
    percentages = [to_percentages(pd.read_csv(p)) for p in group[1]]
    for path, percentage in zip(group[1], percentages):
        single_run_plot(path, percentage)
    group_plot(group_axis, group[0], [p.stem for p in group[1]], percentages)


if __name__ == "__main__":
    plt.rcParams["font.family"] = "Latin Modern Roman"
    dir_path = pl.PurePath(argv[1])
    file_paths = map(dir_path.joinpath, listdir(dir_path))
    groups = chart_groups(file_paths)
    group_fig, group_axes = plt.subplots(ncols=2,
                                         nrows=len(groups) // 2,
                                         figsize=(8, 8),
                                         tight_layout=True,
                                         sharey=True)
    for g, axis in zip(groups, group_axes.flatten()):
        process_group(g, axis)
    with PdfPages(dir_path.with_name("summary.pdf")) as pp:
        pp.savefig(group_fig)
