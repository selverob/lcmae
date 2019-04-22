"""
This module benchmarks multi-agent evacuation algorithms.

It allows running evacuation planning algorithms on multiple maps and scenarios,
optionally in parallel, and then calculates various statistics about the plans
that were produced.
"""
from __future__ import annotations

from json import dumps
from multiprocessing import Pool
from pathlib import Path
from pprint import pformat
from sys import stderr
from time import process_time_ns
from typing import Any, Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

import lcmae
import expansion
from level import Level, Scenario, AgentType


@dataclass(init=False)
class BenchResult():
    """The result of running a benchmark on a map and scenario"""
    percentiles: Dict[int, float]
    agent_counts: Dict[AgentType, int]
    makespans: Dict[AgentType, int]
    safe_ratios: Dict[AgentType, List[float]]
    paths: List[List[int]]
    planning_time: float
    expansion_time: Optional[float] = None
    expansion_makespan: Optional[int] = None

    def __init__(self, level: Level, paths: List[List[int]], time: int):
        """Create a new BenchResult

        Uses the given arguments to create a new BenchResult with most
        of the members calculated from them.
        """
        self.paths = paths
        self.planning_time = time / 10e9
        st = self.__safety_times(level)
        self.percentiles = self.__percentiles(st)
        per_type_st = self.__per_type_safe_times(st, level.scenario)
        per_type_stats = {typ: (max(times), len(times)) for typ, times in per_type_st.items() if len(times) > 0}
        self.agent_counts = {typ: stats[1] for typ, stats in per_type_stats.items()}
        self.makespans = {typ: stats[0] for typ, stats in per_type_stats.items()}
        self.safe_ratios = {typ: self.__safe_ratio_list(times) for typ, times in per_type_st.items() if len(times) > 0}
        self.planning_time = time / 1e9

    def as_dict(self) -> Dict[str, Any]:
        """Return a simplified dictionary representation of the results"""
        d = {
            "percentiles": self.percentiles,
            "agent_counts": self.__to_type_name_dict(self.agent_counts),
            "makespans": self.__to_type_name_dict(self.makespans),
            "planning_time": self.planning_time
        }
        if self.expansion_time:
            d["expansion_time"] = self.expansion_time
            d["expansion_makespan"] = self.expansion_makespan
        return d

    def __to_type_name_dict(self, d: Dict[AgentType, Any]) -> Dict[str, Any]:
        return {typ.name.lower(): item for typ, item in d.items()}

    def __safety_times(self, level: Level) -> List[int]:
        times = []
        for path in self.paths:
            for i, pos in enumerate(path):
                if level.is_safe(pos):
                    times.append(i)
                    break
        return times

    def __percentiles(self, times: List[int]) -> Dict[int, float]:
        res = {}
        for p in [25, 50, 75, 90, 95, 99, 100]:
            res[p] = np.percentile(times, p)
        return res

    @staticmethod
    def for_case(bench_case: Tuple[Path, Path], run_expansion: bool) -> BenchResult:
        """Benchmark a given test case"""
        print(f"Benchmarking {bench_case[0]} {bench_case[1]}", file=stderr)
        lvl = Level(*bench_case)
        start = process_time_ns()
        paths = lcmae.plan_evacuation(lvl, debug=False)
        stop = process_time_ns()
        result = BenchResult(lvl, paths, stop - start)
        only_retargeting = all(map(lambda a: a.type == AgentType.RETARGETING, lvl.scenario.agents))
        if run_expansion and only_retargeting:
            exp_start = process_time_ns()
            exp_paths = expansion.plan_evacuation(lvl)
            exp_stop = process_time_ns()
            result.expansion_makespan = len(exp_paths[0])
            result.expansion_time = (exp_stop - exp_start) / 1e9
        return result

    def __per_type_safe_times(self, safety_ts: List[int], scen: Scenario) -> Dict[AgentType, List[int]]:
        times: Dict[AgentType, List[int]] = {typ: [] for typ in AgentType}
        for i, t in enumerate(safety_ts):
            times[scen.agents[i].type].append(t)
        return times

    def __safe_ratio_list(self, safety_ts: List[int]) -> List[float]:
        st = safety_ts[:]
        st.sort()
        current_idx = 0
        safe = 0
        res = []
        for t in range(st[-1] + 1):
            while current_idx < len(st) and st[current_idx] == t:
                current_idx += 1
                safe += 1
            res.append(current_idx / len(st))
        return res


@dataclass()
class BenchResults():
    """A container for results of multiple benchmarks"""
    results: Dict[str, BenchResult]

    def as_text(self) -> str:
        """Pretty-print each contained BenchResult into a string"""
        strs = []
        for name, result in self.results.items():
            res = f"=========={name}==========\n"
            res += pformat(result.as_dict())
            strs.append(res)
        return "\n".join(strs)

    def as_json(self) -> str:
        """Return a JSON dictionary with contained results"""
        return dumps({name: result.as_dict() for name, result in self.results.items()})

    @staticmethod
    def for_benchfile(cases: List[Tuple[(Path, Path)]], parallelism: int, run_expansion: bool) -> BenchResults:
        """Run each of the benchmark cases, with `parallelism` cases running in parallel"""
        with Pool(parallelism) as p:
            results = p.starmap(BenchResult.for_case, zip(cases, [run_expansion] * len(cases)))
            return BenchResults({bench_name(*cases[i]): result for i, result in enumerate(results)})


def parse_benchfile(f) -> List[Tuple[Path, Path]]:
    """Parse the given file into benchmark cases.

    On each line in the file, there should be a path to a map,
    a colon and a space-separated list of scenarios which should
    be benchmarked for the map. For example:
    `benchmarks/office.map: benchmarks/office1.scen benchmarks/office2.scen benchmarks/office3.scen`
    """
    benchmarks = []
    for l in f:
        trimmed = l.strip()
        if not trimmed:
            continue
        map_file, scen_files = trimmed.split(":")
        for scen_file in scen_files.strip().split(" "):
            benchmarks.append((Path(map_file), Path(scen_file)))
    return benchmarks


def bench_name(map_file, scen_file) -> str:
    """Return a name for the benchmark, composed of file names of map and scenario without suffixes, separated by a dash"""
    return f"{Path(map_file).stem}-{Path(scen_file).stem}"


def expand_lists(*lists) -> List[List]:
    target_length = max(map(len, lists))
    res = []
    for l in lists:
        res.append(l + [l[-1]] * (target_length - len(l)))
    return res


# def run_benchmarks(benchmarks: List[Tuple[(str, str)]], parallelism: int, run_expansion: bool):
#     results: List[BenchResult] = []
#     with Pool(parallelism) as p:
#         results = p.starmap(BenchResult.for_case, zip(benchmarks, [run_expansion] * len(benchmarks)))
#     names = [bench_name(*t) for t in benchmarks]
#     for name, result in zip(names, results):
#         print(f"===============\n{name}")
#         for k in result.stats:
#             print(f"{k}:\t{result.stats[k]}")
#         print_paths(f"bench_solutions/{name}.sol", result.paths)
#         with open(f"bench_solutions/charts/{name}.csv", "w") as f:
#             print(*[t.name for t in result.ratios], sep=", ", file=f)
#             expanded_ratios = expand_lists(*result.ratios.values())
#             for i in range(len(expanded_ratios[0])):
#                 print(*["{:0.5}".format(float(l[i])) for l in expanded_ratios], sep=", ", file=f)
