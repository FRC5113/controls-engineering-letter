#!/usr/bin/env python3

# Avoid needing display if plots aren't being shown
import sys

if "--noninteractive" in sys.argv:
    import matplotlib as mpl

    mpl.use("svg")
    import bookutil.latex as latex

import math
import matplotlib.pyplot as plt
import numpy as np

plt.rc("text", usetex=True)


def main():
    xlim = [0, 3]
    x = np.arange(xlim[0], xlim[1], 0.001)
    plt.xlim(xlim)

    y1 = np.sin(2 * math.pi * x)
    plt.plot(x, y1, label="Signal at $1$ Hz")

    y2 = np.sin(2 * math.pi * x / 2 + math.pi / 4)
    plt.plot(x, y2, color="k", linestyle="--", label="Signal at $2$ Hz")

    # Draw intersection points
    idx = np.argwhere(np.diff(np.sign(y1 - y2)) != 0)
    plt.plot(x[idx], y1[idx], "ko", label="Samples at $3$ Hz")

    plt.xlabel("$t$")
    plt.ylabel("$f(t)$")
    plt.legend()

    if "--noninteractive" in sys.argv:
        latex.savefig("nyquist")
    else:
        plt.show()


if __name__ == "__main__":
    main()
