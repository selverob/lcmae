# Evacuation Simulator

This is an implementation of the algorithms described in the "Evacuation
Planning Based on Local Cooperative Path Finding Techniques" bachelor thesis at
the Faculty of Information Technologies of Czech Technical University.

It's capable of planning an evacuation using either the LC-MAE algorithm or a
max-flow based one and of visualizing it.

## Note

This code was produced as part of a research project (my bachelor thesis). As
such, it's not in an ideal shape, since focus was on iteration and testing
different approaches. I'd love to get the time to improve it (or just rewrite it
completely in a more performant way), but, unfortunately, that has not
materialized yet. Don't judge me too harshly.

This research has been supported by GAČR - the Czech Science Foundation, grant
registration number 19-17966S.

## Installation

### Prerequisites

There is nothing that would stop `evacsim` from running on Windows but it has
never been tested so it's safest to run it on Linux.

To run evacsim, you need to have Python 3.7 installed. The GUI requires Python's
Tkinter library and evacsim will not start without it. Some distros (most
famously, Ubuntu and Debian) package the Tk portions of Python separately so you
need to find the correct package to install, if you don't already have it.

On Ubuntu, the package with Tkinter is called `python3-tk`.

### (Optional) Activate Virtualenv

This is not required but it will help your system not to get polluted with
simulator's dependencies.

- Change into the directory in which this README is located
- Run `python3.7 -m venv .`
- Run `source bin/activate` (if you are using a POSIX-compatible shell)

### Install the simulator
- Run `pip install .`

After finishing this process, you should have a binary called `evacsim`
on your PATH.

# Running

If you just start `evacsim`, it should print all the information about its
command-line interface. You can use `plan` to generate evacuation plans for maps
and scenarios and `check` to check them for validity (especially useful if
you're extending the simulator with new features).

For the simplest experience, use `evacsim plan --visualize <MAP> <SCENARIO>`.
It will plan the evacuation (using LC-MAE by default) and show you the visualization
GUI with the plan loaded automatically.

# GUI commands
GUI is started with `evacsim gui` and controlled with mouse and keyboard. Left
mouse button adds objects of a given type to the map, right mouse button removes
them. Keyboard buttons control what object is added to the map or removed from
it:

|   Key   | Function                                            |
|:-------:|-----------------------------------------------------|
|    w    | Draw walls                                          |
|    d    | Draw danger                                         |
|    r    | Draw retargeting agents                             |
|    f    | Draw closest-frontier agents                        |
|    s    | Draw static agents (second click sets their target) |
|    p    | Draw panicked agents                                |
|    h    | Print coordinates of clicked-on squares             |
|    m    | Save map and scenario                               |
|  Space  | Animate the plan passed on the command line         |

Modified maps and scenarios are always saved into files called `out.map` and
`out.scen` in the current directory.

# Project structure
The subdirectories in this project contain:

 - `evacsim`: The code of evacsim itself
 - `bench_suite`: Maps and scenarios used to test evacsim's performance
 - `maps`: Some of the maps used for testing and an empty map and scenario
 - `bench_solutions`: Empty directory prepared for solutions and plots
  generated by the benchmarking module
