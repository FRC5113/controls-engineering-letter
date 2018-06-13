import control as cnt
import numpy as np
import scipy as sp


def kalman(sys, Q, R):
    """Solves for the steady state kalman gain and covariance matricies.

    Keyword arguments:
    sys -- discrete state-space model
    Q -- the model uncertantity
    R -- the measurement uncertainty

    Returns:
    Kalman gain, covariance.
    """
    I = np.matrix(np.eye(Q.shape[0]))
    Z = np.matrix(np.zeros(Q.shape[0]))
    n = sys.A.shape[0]
    m = sys.C.shape[0]

    observability_rank = np.linalg.matrix_rank(cnt.obsv(sys.A, sys.C))
    if observability_rank != n:
        print('warning: Observability of %d != %d, unobservable state',
              observability_rank, n)

    # Compute the steady state covariance matrix.
    P_prior = sp.linalg.solve_discrete_are(a=sys.A.T, b=sys.C.T, q=Q, r=R)
    S = sys.C * P_prior * sys.C.T + R
    K = np.linalg.lstsq(S.T, (P_prior * sys.C.T).T, rcond=None)[0].T
    P = (I - K * sys.C) * P_prior

    return K, P