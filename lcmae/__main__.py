import cProfile
from sys import stderr, argv
from lcmae import plan_evacuation
from level import Level

def main():
    map_path, scen_path = argv[1], argv[2]
    lvl = Level(map_path, scen_path)
    if not lvl.frontier:
        print("No passage to safety exists!", file=stderr)
        exit(2)
    paths = plan_evacuation(lvl)
    for agent_id, path in enumerate(paths):
        num_strings = ["{:02d}".format(n) for n in path]
        print(*num_strings)
        if path[-1] in lvl.scenario.danger:
            print("Agent", agent_id, "could not evacuate. He dead.",
                  file=stderr)


if __name__ == "__main__":
    main()
    #cProfile.run("main()")
