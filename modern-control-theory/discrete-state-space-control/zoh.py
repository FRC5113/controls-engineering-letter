#!/usr/bin/env python3

# Avoid needing display if plots aren't being shown
import sys

if "--noninteractive" in sys.argv:
    import matplotlib as mpl

    mpl.use("svg")
    import bookutil.latex as latex

import matplotlib.pyplot as plt
import numpy as np

from bookutil.systems import Elevator

plt.rc("text", usetex=True)


def generate_zoh(data, dt, sample_period):
    """Generates zero-order hold of data set.

    Keyword arguments:
    data -- array of position data
    dt -- dt of original data samples
    sample_period -- desired time between samples in zero-order hold
    """
    y = []
    count = 0
    val = 0
    for i in range(len(data)):
        count += 1
        if count >= sample_period / dt:
            val = data[i]
            count = 0
        y.append(val)
    return y


def main():
    dt = 0.005
    sample_period = 0.1
    elevator = Elevator(dt)

    # Set up graphing
    l0 = 0.1
    l1 = l0 + 5.0
    l2 = l1 + 0.1
    l3 = l2 + 1.0
    t = np.arange(0, l3, dt)

    refs = []

    # Generate references for simulation
    for i in range(len(t)):
        if t[i] < l0:
            r = np.array([[0.0], [0.0]])
        elif t[i] < l1:
            r = np.array([[1.524], [0.0]])
        else:
            r = np.array([[0.0], [0.0]])
        refs.append(r)

    state_rec, ref_rec, u_rec, y_rec = elevator.generate_time_responses(t, refs)
    pos = elevator.extract_row(state_rec, 0)

    plt.figure(1)
    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    plt.plot(t, pos, label="Continuous")
    y = generate_zoh(pos, dt, sample_period)
    plt.plot(t, y, label="Zero-order hold (T={}s)".format(sample_period))
    plt.legend()
    if "--noninteractive" in sys.argv:
        latex.savefig("zoh")
    else:
        plt.show()


if __name__ == "__main__":
    main()
