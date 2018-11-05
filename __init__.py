from map_reader import parse

if __name__ == "__main__":
    f = open("maps/AR0313SR.map")
    g = parse(f)
    print(g.nodes())