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


def generate_refs(dt):
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

    return t, refs


def simulate(elevator, dt, method):
    t, refs = generate_refs(dt)
    elevator.sysd = elevator.sysc.to_discrete(dt, method)
    elevator.x = np.zeros((elevator.x.shape[0], 1))
    elevator.x_hat = np.zeros((elevator.x_hat.shape[0], 1))
    state_rec, ref_rec, u_rec, y_rec = elevator.generate_time_responses(t, refs)

    pos = elevator.extract_row(state_rec, 0)
    if method == "zoh":
        label = "Zero-order hold"
    elif method == "euler":
        label = "Forward Euler"
    elif method == "backward_diff":
        label = "Backward Euler"
    elif method == "bilinear":
        label = "Bilinear transform"
    label += " (T={}s)".format(dt)
    plt.plot(t, pos, label=label)


def main():
    elevator = Elevator(0.1)

    plt.figure(1)
    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    simulate(elevator, 0.1, "zoh")
    simulate(elevator, 0.1, "euler")
    simulate(elevator, 0.1, "backward_diff")
    simulate(elevator, 0.1, "bilinear")
    plt.ylim([-2, 3])
    plt.legend()
    if "--noninteractive" in sys.argv:
        latex.savefig("sampling_simulation_010")

    plt.figure(2)
    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    simulate(elevator, 0.05, "zoh")
    simulate(elevator, 0.05, "euler")
    simulate(elevator, 0.05, "backward_diff")
    simulate(elevator, 0.05, "bilinear")
    plt.ylim([-2, 3])
    plt.legend()
    if "--noninteractive" in sys.argv:
        latex.savefig("sampling_simulation_005")

    plt.figure(3)
    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    simulate(elevator, 0.01, "zoh")
    simulate(elevator, 0.01, "euler")
    simulate(elevator, 0.01, "backward_diff")
    simulate(elevator, 0.01, "bilinear")
    plt.ylim([-0.25, 2])
    plt.legend()
    if "--noninteractive" in sys.argv:
        latex.savefig("sampling_simulation_004")
    else:
        plt.show()


if __name__ == "__main__":
    main()
