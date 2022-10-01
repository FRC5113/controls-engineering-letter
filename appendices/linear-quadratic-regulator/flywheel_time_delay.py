#!/usr/bin/env python3

"""Simulates flywheel velocity control with a time delay."""

import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import fractional_matrix_power
from scipy.signal import StateSpace

from bookutil import latex
from bookutil.systems import Flywheel

if "--noninteractive" in sys.argv:
    mpl.use("svg")
plt.rc("text", usetex=True)

DT = 0.001
DELAY = 0.08


class FlywheelTimeDelay(Flywheel):
    """An frccontrol system representing a flywheel with a time delay."""

    def __init__(self, dt, latency_comp=False):
        """Flywheel subsystem.

        Keyword arguments:
        dt -- time between model/controller updates
        latency_comp -- True if the controller gain should be latency-compensated
        """
        self.latency_comp = latency_comp

        Flywheel.__init__(self, dt)

    # pragma pylint: disable=signature-differs
    def create_model(self, states, inputs):
        Kv = 0.011
        Ka = 0.005515

        A = np.array([[-Kv / Ka]])
        B = np.array([[1.0 / Ka]])
        C = np.array([[1]])
        D = np.array([[0]])

        return StateSpace(A, B, C, D)

    def design_controller_observer(self):
        self.design_two_state_feedforward()
        self.design_lqr([80], [12])

        q_vel = 700
        r_vel = 50
        self.design_kalman_filter([q_vel], [r_vel])

        self.ubuf = []
        for _ in range(int(DELAY / DT)):
            self.ubuf.append(np.zeros((1, 1)))

        if self.latency_comp:
            self.K = self.K @ fractional_matrix_power(
                self.sysd.A - self.sysd.B @ self.K, DELAY / DT
            )

    def update_controller(self, next_r):
        u = self.K @ (self.r - self.x_hat)
        if self.f:
            rdot = (next_r - self.r) / self.dt
            uff = self.Kff @ (rdot - self.f(self.r, np.zeros(self.u.shape)))
        else:
            uff = self.Kff @ (next_r - self.sysd.A @ self.r)
        self.r = next_r
        self.u = np.clip(u + uff, self.u_min, self.u_max)
        self.ubuf.append(self.u)
        self.u = self.ubuf.pop(0)


def main():
    """Entry point."""
    # Set up graphing
    l0 = 0.1
    l1 = l0 + 5.0
    l2 = l1 + 0.1
    ts = np.arange(0, l2 + 5.0, DT)

    refs = []

    # Generate references for simulation
    for t in ts:
        if t < l0:
            r = np.array([[0]])
        elif t < l1:
            r = np.array([[510]])
        else:
            r = np.array([[0]])
        refs.append(r)

    flywheel = FlywheelTimeDelay(DT)
    x_rec, ref_rec, u_rec, _ = flywheel.generate_time_responses(refs)
    latex.plot_time_responses(flywheel, ts, x_rec, ref_rec, u_rec, 2)
    if "--noninteractive" in sys.argv:
        latex.savefig("flywheel_time_delay_no_comp")

    flywheel = FlywheelTimeDelay(DT, latency_comp=True)
    x_rec, ref_rec, u_rec, _ = flywheel.generate_time_responses(refs)
    latex.plot_time_responses(flywheel, ts, x_rec, ref_rec, u_rec, 8)
    if "--noninteractive" in sys.argv:
        latex.savefig("flywheel_time_delay_comp")
    else:
        plt.show()


if __name__ == "__main__":
    main()
