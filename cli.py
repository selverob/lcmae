#! /usr/bin/env python3
"""A module which provides a unified CLI to all the functionality.

This module serves as a single entry point for a user. It exposes a CLI
which can be use to call the different commands and set their properties.

This CLI replaces `__main__.py` files scattered around the project with
a single, unified interface for running everything.
"""
from typing import List
import pathlib as pl
from sys import stderr

import click

import bench
import plots
import lcmae
import expansion
from level import Level


def paths_to_str(paths: List[List[int]]) -> str:
    """Create a string with given paths printed in a readable format"""
    lines = []
    for path in paths:
        nums = ["{:02d}".format(n) for n in path]
        lines.append(" ".join(nums))
    return "\n".join(lines)


def write_paths(filename: str, paths: List[List[int]]):
    """Write the given agent paths into a file, in the format used by all the tools"""
    with open(filename, "w") as f:
        print(paths_to_str(paths), file=f)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--algorithm",
              type=click.Choice(("lcmae", "flow")),
              default="lcmae",
              help="Algorithm to use when planning")
@click.option("--visualize/--no-visualize",
              default=False,
              help="Start visualization after creating the plan")
@click.option("--debug/--no-debug",
              default=False,
              help="Print planning algorithm's debug output")
@click.argument("map_path",
                type=click.Path(exists=True, dir_okay=False))
@click.argument("scenario_path",
                type=click.Path(exists=True, dir_okay=False))
def plan(map_path, scenario_path, algorithm, visualize, debug):
    "Create an evacuation plan for a map and a scenario"
    lvl = Level(map_path, scenario_path)
    if not lvl.frontier:
        print("No passage to safety exists!", file=stderr)
        exit(2)
    paths: List[List[int]] = []
    if algorithm == "lcmae":
        paths = lcmae.plan_evacuation(lvl, debug=debug)
    else:
        paths = expansion.plan_evacuation(lvl, debug=debug)
    paths = lcmae.plan_evacuation(lvl) if algorithm == "lcmae" else expansion.plan_evacuation(lvl)
    print(paths_to_str(paths))


@cli.command()
@click.argument("benchfile", type=click.File("r"))
@click.option("-p", "--processes",
              type=click.INT,
              help="Number of processors to use while benchmarking")
@click.option("-f", "--format",
              type=click.Choice(("text", "json")),
              help="Benchmark results format")
@click.option("--flow/--no-flow",
              default=False,
              help="Also run the network flow algorithm on eligible scenarios")
@click.option("-p", "--plot-dest", 'plot_dest',
              type=click.Path(exists=True, file_okay=False),
              help="Directory into which agent safety plots should be saved")
@click.option("-d", "--path-dest", 'path_dest',
              type=click.Path(exists=True, file_okay=False),
              help="Directory into which evacuation plan paths should be saved")
def benchmark(benchfile, processes, format, flow, plot_dest, path_dest):
    """Evaluate benchmark algorithms' performance

    Plans evacuations for multiple maps and scenarios (optionally in parallel)
    and then displays stats about them.

    By default, all processor cores on the system will be used to speed up
    benchmarking.

    When the --flow option is passed, the network flow algorithm is ran on
    some of the scenarios and its results are reported. This only works on
    scenarios which only have retargeting agents.

    CAUTION: The network flow algorithm may take up massive amounts of memory.
    """
    bench_cases = bench.parse_benchfile(benchfile)
    results = bench.BenchResults.for_benchfile(bench_cases, processes, flow)
    if format == "text":
        print(results.as_test())
    else:
        print(results.as_json())
    if plot_dest:
        plots.generate_plots(results, pl.Path(plot_dest))
    if path_dest:
        path = pl.Path(path_dest)
        for name, result in results.results.items():
            write_paths(path.joinpath(f"{name}.out"), result.paths)


@cli.command()
def gui():
    """Show a GUI for plan visualization and editing."""
    pass


if __name__ == "__main__":
    cli()
