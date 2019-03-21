import pandas as pd
import pathlib as pl
from os import listdir
from sys import argv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def to_percentages(df: pd.DataFrame):
    for col in df.columns:
        df[col] = df[col] * 100


def make_plot(title: str, df: pd.DataFrame):
    plt.figure()
    for col in df:
        plt.plot(df[col])
        plt.title(title)
        plt.xlabel("Time")
        plt.ylabel("Safe agents")
        plt.yticks(range(0, 101, 10))
        plt.grid(True)
        plt.legend()


dir_path = pl.PurePath(argv[1])
for file in listdir(dir_path):
    file_path = dir_path.joinpath(file)
    if file_path.suffix == ".csv":
        df = pd.read_csv(file_path)
        to_percentages(df)
        with PdfPages(file_path.with_suffix(".pdf")) as pp:
            make_plot(file_path.stem.replace("-", " "), df)
            pp.savefig()
