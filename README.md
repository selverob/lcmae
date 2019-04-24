# Evacuation Simulator

This is an implementation of the algorithms described in the "Evacuation
Planning Based on Local Cooperative Path Finding Techniques" bachelor thesis at
the Faculty of Information Technologies of Czech Technical University.

It's capable of planning an evacuation using either the LC-MAE algorithm or a
max-flow based one and of visualizing it.

## Installation

### (Optional) Activate Virtualenv

This is not required but it will help your system not to get polluted with
simulator's dependencies.

- Change into the directory in which this README is located
- Run `python -m venv .`
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
It will plan the evacuation (using LV-MAE by default) and show you the visualization
GUI with the plans loaded automatically.

# GUI commands
GUI is controlled with mouse and keyboard. Left mouse button adds objects of a
given type to the map, right mouse button removes them. Keyboard buttons control
what object is added to the map or removed from it:

|   Key   | Function                                    |
|:-------:|---------------------------------------------|
|    w    | Draw walls                                  |
|    d    | Draw danger                                 |
|    r    | Draw retargeting agents                     |
|    f    | Draw closest-frontier agents                |
|    s    | Draw static agents                          |
|    p    | Draw panicked agents                        |
|    h    | Print coordinates of clicked-on squares     |
|    m    | Save map and scenario                       |
|  Space  | Animate the plan passed on the command line |

Modified maps and scenarios are always saved into files called `out.map` and
`out.scen` in the current directory.