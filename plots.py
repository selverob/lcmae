"""This module generates PDF plots for benchmark results and their groups on different maps."""
from itertools import groupby
from math import ceil
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.cm import get_cmap
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import pathlib as pl

from bench import BenchResults
from level import AgentType

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


def make_plot(title: str, safe_ratios: Dict[AgentType, List[float]]):
    """Generate a plot for a single BenchResult"""
    plt.figure()
    for typ, ratios in safe_ratios.items():
        plt.plot([x * 100 for x in ratios], color=AGENT_COLORS[typ.name])
        plt.title(title)
        plt.xlabel("Time")
        plt.ylabel("Safe agents")
        plt.yticks(range(0, 101, 10))
        plt.grid(True)
        plt.legend()


def chart_groups(result_names: List[str]) -> List[Tuple[str, List[str]]]:
    """Group results according to the map they belong to"""
    res = []
    result_names.sort()
    for m, charts in groupby(result_names, lambda name: name.split("-")[0]):
        res.append((m, list(charts)))
    return res


def group_plot(axis: plt.Axes, title: str, names: List[str], ratios: List[Dict[AgentType, List[float]]]):
    """Generate a joint plot for a benchmark result group on `axis`"""
    axis.set_title(title)
    axis.set_xlabel("Čas")
    axis.set_ylabel("Agenty v bezpečí (%)")
    axis.set_yticks(range(0, 101, 10))
    axis.grid(True)
    legend: Tuple[List[plt.Line2D], List[str]] = ([], [])
    dark = get_cmap("Dark2")
    for i, rs in enumerate(ratios):
        line_name = names[i].split("_")[-1]
        for (j, typ) in enumerate(rs):
            data = list(map(lambda x: x * 100, rs[typ]))
            xdata = data[:data.index(100) + 1]
            axis.plot(xdata,
                      color=dark(i),
                      linestyle=AGENT_STYLES[typ.name],
                      linewidth=2)
            if j == 0:
                legend_line = plt.Line2D(xdata,
                                         range(0, len(xdata)),
                                         color=dark(i),
                                         linestyle="solid")
                legend[0].append(legend_line)
                legend[1].append(line_name)
    axis.legend(*legend, loc=4, fontsize="large")


def process_group(destination: pl.Path, results: BenchResults, group: Tuple[str, List[str]], group_axis: plt.Axes):
    """Generate and save plots for each of the benchmark results and add a joint plot for the group to `group_axis`"""
    for bench_name in group[1]:
        with PdfPages(destination.joinpath(f"{bench_name}.pdf")) as pp:
            make_plot(bench_name, results.results[bench_name].safe_ratios)
            pp.savefig()
            plt.close()
    group_plot(group_axis, group[0], group[1], [results.results[name].safe_ratios for name in group[1]])


def generate_plots(results: BenchResults, destination: pl.Path):
    """Generate agent safety plots for given benchmark results and save them as PDFs to a given destination"""
    plt.rcParams["font.family"] = "Latin Modern Roman"
    groups = chart_groups(list(results.results.keys()))
    group_fig, group_axes = plt.subplots(ncols=2,
                                         nrows=ceil(len(groups) / 2),
                                         figsize=(8, 8),
                                         tight_layout=True,
                                         sharey=True)
    for g, axis in zip(groups, group_axes.flatten()):
        process_group(destination, results, g, axis)
    with PdfPages(destination.joinpath("summary.pdf")) as pp:
        pp.savefig(group_fig)
