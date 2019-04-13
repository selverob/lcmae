from collections import namedtuple
from multiprocessing import Pool
from pathlib import Path
from sys import argv, stderr
from time import process_time_ns
from typing import Dict, List, Tuple
import numpy as np

import wpashd
import expansion
from level import Level, Scenario, AgentType


def bench_name(map_file, scen_file) -> str:
    return f"{Path(map_file).name}-{Path(scen_file).name}"


def safety_times(level: Level, paths: List[List[int]]) -> List[int]:
    times = []
    for path in paths:
        for i, pos in enumerate(path):
            if level.is_safe(pos):
                times.append(i)
                break
    return times


def max_no_panic_t(scen: Scenario, safety_ts: List[int]) -> int:
    not_panicked_times = [t for i, t in enumerate(safety_ts) if scen.agents[i].type is not AgentType.PANICKED]
    return max(not_panicked_times)


def percentiles(times: List[int]) -> Dict[str, float]:
    res = {}
    for p in [25, 50, 75, 90, 95, 99, 100]:
        res[str(p)] = np.percentile(times, p)
    return res


def print_paths(filename, paths):
    with open(filename, "w") as f:
        for path in paths:
            num_strings = ["{:02d}".format(n) for n in path]
            print(*num_strings, file=f)


def per_type_safety_times(safety_ts: List[int], scen: Scenario) -> Dict[AgentType, List[int]]:
    times: Dict[AgentType, List[int]] = {typ: [] for typ in AgentType}
    for i, t in enumerate(safety_ts):
        times[scen.agents[i].type].append(t)
    return times


def per_type_averages(safety_ts: Dict[AgentType, List[int]]) -> Dict[AgentType, float]:
    return {typ: sum(ts) / len(ts) for typ, ts in safety_ts.items() if len(ts) > 0}


def safe_ratio_list(safety_ts: List[int]) -> List[float]:
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


BenchResult = namedtuple("BenchResult", "stats paths ratios")


def benchmark(benchspec: Tuple[str, str]) -> BenchResult:
    print(f"Benchmarking {benchspec[0]} {benchspec[1]}", file=stderr)
    lvl = Level(*benchspec)
    start = process_time_ns()
    paths = wpashd.plan_evacuation(lvl, debug=False)
    stop = process_time_ns()
    st = safety_times(lvl, paths)
    stats = percentiles(st)
    type_safety_times = per_type_safety_times(st, lvl.scenario)
    for typ, avg in per_type_averages(type_safety_times).items():
        stats[typ.name] = avg
    # Done here because we cannot use lambdas in multiprocessing maps
    benchmark_expansion = "-e" in argv
    if benchmark_expansion and all(map(lambda a: a.type == AgentType.RETARGETING, lvl.scenario.agents)):
        exp_start = process_time_ns()
        exp_paths = expansion.plan_evacuation(lvl)
        exp_stop = process_time_ns()
        stats["expansion"] = len(exp_paths[0])
        stats["expansion_time"] = (exp_stop - exp_start) / 1e9
    stats["nopanic"] = max_no_panic_t(lvl.scenario, st)
    stats["agents"] = len(lvl.scenario.agents)
    stats["time"] = (stop - start) / 1e9
    stats["died"] = len(paths) - len(st)
    return BenchResult(stats, paths, {typ: safe_ratio_list(st) for typ, st in type_safety_times.items() if len(st) > 0})


def parse_benchfile(f) -> List[Tuple[str, str]]:
    benchmarks = []
    for l in f:
        trimmed = l.strip()
        if not trimmed:
            continue
        map_file, scen_files = trimmed.split(":")
        for scen_file in scen_files.strip().split(" "):
            benchmarks.append((map_file, scen_file))
    return benchmarks


def expand_lists(*lists) -> List[List]:
    target_length = max(map(len, lists))
    res = []
    for l in lists:
        res.append(l + [l[-1]] * (target_length - len(l)))
    return res


def main():
    if len(argv) < 2:
        print("python -m bench <bench scenario list>")
        exit(1)
    benchmarks = []
    with open(argv[1]) as f:
        benchmarks = parse_benchfile(f)
    results = []
    with Pool(None) as p:
        results = p.map(benchmark, benchmarks)
    names = [bench_name(*t) for t in benchmarks]
    for name, result in zip(names, results):
        print(f"===============\n{name}")
        for k in result.stats:
            print(f"{k}:\t{result.stats[k]}")
        print_paths(f"bench_solutions/{name}.sol", result.paths)
        with open(f"bench_solutions/charts/{name}.csv", "w") as f:
            print(*[t.name for t in result.ratios], sep=", ", file=f)
            expanded_ratios = expand_lists(*result.ratios.values())
            for i in range(len(expanded_ratios[0])):
                print(*["{:0.5}".format(float(l[i])) for l in expanded_ratios], sep=", ", file=f)


if __name__ == "__main__":
    main()
