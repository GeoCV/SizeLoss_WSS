#!/usr/bin/env python3.6

import argparse
from typing import List
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from utils import map_, colors


def run(args: argparse.Namespace) -> None:
    assert len(args.folders) <= len(colors)

    if len(args.columns) > 1:
        raise NotImplementedError("Only 1 columns at a time is handled for now")

    paths: List[Path] = [Path(f, args.filename) for f in args.folders]
    arrays: List[np.ndarray] = map_(np.load, paths)
    metric_name: str = paths[0].stem

    assert len(set(a.shape for a in arrays)) == 1  # All arrays should have the same shape
    if len(arrays[0].shape) == 2:
        arrays = map_(lambda a: a[..., np.newaxis], arrays)  # Add an extra dimension for column selection

    fig = plt.figure(figsize=(14, 9))
    ax = fig.gca()
    ax.set_ylim([0, 1])
    # ax.set_xlim([0, len(args.folders) + 1])
    ax.set_xlabel(metric_name)
    ax.set_ylabel("Percentage")
    ax.grid(True, axis='y')
    ax.set_title(f"{metric_name} moustaches")

    # bins = np.linspace(0, 1, args.nbins)
    for i, (a, c, p) in enumerate(zip(arrays, colors, paths)):
        for k in args.columns:
            mean_a = a[..., k].mean(axis=1)
            best_epoch: int = np.argmax(mean_a)

            # values = a[args.epc, :, k]
            values = a[best_epoch, :, k]

            ax.boxplot(values, positions=[i + 1], manage_xticks=False, showmeans=True, meanline=True, whis=[5, 95])
            print(f"{p.parent.stem:10}: min {values.min():.03f} 25{np.percentile(values, 25):.03f} "
                  + f"avg {values.mean():.03f} 75 {np.percentile(values, 75):.03f} max {values.max():.03f} at epc {best_epoch}")
    # ax.legend()

    ax.set_xticklabels([""] + map_(lambda p: p.parent.stem, paths))
    ax.set_xticks(np.mgrid[0:len(args.folders) + 1])
    ax.set_yticks(np.mgrid[0:1.1:.1])

    fig.tight_layout()
    if args.savefig:
        fig.savefig(args.savefig)

    if not args.headless:
        plt.show()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Plot data over time')
    parser.add_argument('--folders', type=str, required=True, nargs='+', help="The folders containing the file")
    parser.add_argument('--filename', type=str, required=True)
    parser.add_argument('--columns', type=int, nargs='+', default=0, help="Which columns of the third axis to plot")
    parser.add_argument("--savefig", type=str, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--nbins", type=int, default=100)
    parser.add_argument("--epc", type=int, required=True)
    args = parser.parse_args()

    print(args)

    return args


if __name__ == "__main__":
    run(get_args())
