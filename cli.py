"""A module which provides a unified CLI to all the functionality.

This module serves as a single entry point for a user. It exposes a CLI
which can be use to call the different commands and set their properties.

This CLI replaces `__main__.py` files scattered around the project with
a single, unified interface for running everything.
"""
from typing import List

import click

import bench


def print_paths(filename: str, paths: List[List[int]]):
    """Print the given agent paths into a file, in the format used by all the tools"""
    with open(filename, "w") as f:
        for path in paths:
            num_strings = ["{:02d}".format(n) for n in path]
            print(*num_strings, file=f)


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
@click.argument("map")
@click.argument("scenario")
def plan():
    "Create an evacuation plan for a map and a scenario"
    pass


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
def benchmark(benchfile, processes, format, flow):
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


@cli.command()
def gui():
    """Show a GUI for plan visualization and editing."""
    pass


if __name__ == "__main__":
    cli()
