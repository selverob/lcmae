from pathlib import Path
from sys import argv, stderr
from time import process_time_ns
from typing import Dict, List, Tuple
import numpy as np

from wpashd import plan_evacuation
from level import Level, Scenario


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
    not_panicked_times = [t for i, t in enumerate(safety_ts) if scen.agents[i].type is not Scenario.AgentType.PANICKED]
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


def benchmark(map_file, scen_file) -> Dict[str, float]:
    print(f"Benchmarking {map_file} {scen_file}", file=stderr)
    lvl = Level(map_file, scen_file)
    start = process_time_ns()
    paths = plan_evacuation(lvl, debug=False)
    print_paths(f"bench_solutions/{bench_name(map_file, scen_file)}", paths)
    stop = process_time_ns()
    st = safety_times(lvl, paths)
    result = percentiles(st)
    result["nopanic"] = max_no_panic_t(lvl.scenario, st)
    result["agents"] = len(lvl.scenario.agents)
    result["time"] = (stop - start) / 1e9
    result["died"] = len(paths) - len(st)
    return result


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


def main():
    if len(argv) < 2:
        print("python -m bench <bench scenario list>")
        exit(1)
    benchmarks = []
    with open(argv[1]) as f:
        benchmarks = parse_benchfile(f)
    results = {bench_name(t[0], t[1]): benchmark(t[0], t[1]) for t in benchmarks}
    for scen in results:
        print(f"===============\n{scen}")
        for k in results[scen]:
            print(f"{k}:\t{results[scen][k]}")


if __name__ == "__main__":
    main()
