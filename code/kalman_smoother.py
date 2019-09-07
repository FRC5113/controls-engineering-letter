#!/usr/bin/env python3

# Avoid needing display if plots aren't being shown
import sys

if "--noninteractive" in sys.argv:
    import matplotlib as mpl

    mpl.use("svg")
    import utils.latex as latex

import matplotlib.pyplot as plt
import numpy as np

plt.rc("text", usetex=True)


def main():
    # x_1: robot position measured from corner
    # x_2: robot velocity with positive direction toward wall
    # x_3: wall position measured from corner
    xhat = np.array([[0.0], [0.0], [0.0]])

    # y_1: measurement of distance from robot to corner
    # y_2: measurement of distance from robot to wall
    y = np.genfromtxt("kalman_robot.csv", delimiter=",")

    # fmt: off
    A = np.array([[1, 1, 0],
                  [0, 1, 0],
                  [0, 0, 1]])
    gamma = np.array([[0],
                      [0.1],
                      [0]])

    Q = np.array([[1]])
    R = np.array([[10, 0],
                  [0, 10]])

    P = np.zeros((3, 3))
    K = np.zeros((3, 2))
    H = np.array([[1, 0, 0],
                  [-1, 0, 1]])
    # fmt: on

    # Initialize matrix storage
    xhat_pre_rec = np.zeros((3, 1, y.shape[1]))
    xhat_post_rec = np.zeros((3, 1, y.shape[1]))
    P_pre_rec = np.zeros((3, 3, y.shape[1]))
    P_post_rec = np.zeros((3, 3, y.shape[1]))
    xhat_smooth_rec = np.zeros((3, 1, y.shape[1]))
    P_smooth_rec = np.zeros((3, 3, y.shape[1]))
    t = [0] * (y.shape[1])

    # Forward Kalman filter

    # Set up initial conditions for first measurement
    xhat[0] = y[0, 0]
    xhat[1] = 0.2
    xhat[2] = y[0, 0] + y[1, 0]
    # fmt: off
    P = np.array([[10, 0, 10],
                  [0, 1, 0],
                  [10, 0, 20]])
    # fmt: on

    xhat_pre_rec[:, :, 1] = xhat
    P_pre_rec[:, :, 1] = P
    xhat_post_rec[:, :, 1] = xhat
    P_post_rec[:, :, 1] = P
    t[1] = 1

    for k in range(2, 100):
        # Predict
        xhat = A @ xhat
        P = A @ P @ A.T + gamma @ Q @ gamma.T

        xhat_pre_rec[:, :, k] = xhat
        P_pre_rec[:, :, k] = P

        # Update
        K = P @ H.T @ np.linalg.inv(H @ P @ H.T + R)
        xhat += K @ (y[:, k : k + 1] - H @ xhat)
        P = (np.eye(3, 3) - K @ H) @ P

        xhat_post_rec[:, :, k] = xhat
        P_post_rec[:, :, k] = P
        t[k] = k

    # Kalman smoother

    # Last estimate is already optional, so add it to the record
    xhat_smooth_rec[:, :, -1] = xhat_post_rec[:, :, -1]
    P_smooth_rec[:, :, -1] = P_post_rec[:, :, -1]

    for k in range(y.shape[1] - 2, 0, -1):
        K = P_post_rec[:, :, k] @ A.T @ np.linalg.inv(P_pre_rec[:, :, k + 1])
        xhat = xhat_post_rec[:, :, k] + K @ (
            xhat_smooth_rec[:, :, k + 1] - xhat_pre_rec[:, :, k + 1]
        )
        P = P_post_rec[:, :, k] + K @ (P - P_pre_rec[:, :, k + 1]) @ K.T

        xhat_smooth_rec[:, :, k] = xhat
        P_smooth_rec[:, :, k] = P

    # Robot position
    plt.figure(1)
    plt.xlabel("Time (s)")
    plt.ylabel("Position (cm)")
    plt.plot(t[1:], xhat_post_rec[0, 0, 1:], label="Kalman filter")
    plt.plot(t[1:], xhat_smooth_rec[0, 0, 1:], label="Kalman smoother")
    plt.legend()
    if "--noninteractive" in sys.argv:
        latex.savefig("kalman_smoother_robot_pos")

    # Robot velocity
    plt.figure(2)
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (cm/s)")
    plt.plot(t[1:], xhat_post_rec[1, 0, 1:], label="Kalman filter")
    plt.plot(t[1:], xhat_smooth_rec[1, 0, 1:], label="Kalman smoother")
    plt.legend()
    if "--noninteractive" in sys.argv:
        latex.savefig("kalman_smoother_robot_vel")

    # Wall position
    plt.figure(3)
    plt.xlabel("Time (s)")
    plt.ylabel("Wall position (cm)")
    plt.plot(t[1:], xhat_post_rec[2, 0, 1:], label="Kalman filter")
    plt.plot(t[1:], xhat_smooth_rec[2, 0, 1:], label="Kalman smoother")
    plt.legend()
    if "--noninteractive" in sys.argv:
        latex.savefig("kalman_smoother_wall_pos")

    # Robot position variance
    plt.figure(4)
    plt.xlabel("Time (s)")
    plt.ylabel("Robot position variance ($cm^2$)")
    plt.plot(t[1:], P_post_rec[1, 1, 1:], label="Kalman filter")
    plt.plot(t[1:], P_smooth_rec[1, 1, 1:], label="Kalman smoother")
    plt.legend()
    if "--noninteractive" in sys.argv:
        latex.savefig("kalman_smoother_robot_pos_variance")
    else:
        plt.show()


if __name__ == "__main__":
    main()
