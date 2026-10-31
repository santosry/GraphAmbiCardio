"""Firth bias-reduced logistic regression.

The Newton-Raphson and profile-likelihood routines are adapted from
``firthlogist`` 0.5.0 (MIT License, Copyright (c) 2022 Jon Luo,
https://github.com/jzluo/firthlogist), which implements the algorithm of the
R package ``logistf`` (Heinze & Schemper, 2002).

Vendoring keeps the statistical pipeline compatible with NumPy 2 and avoids a
hard dependency on scikit-learn solely for input validation.
"""

from __future__ import annotations

import warnings
from copy import deepcopy
from math import sqrt
from typing import Any

import numpy as np
from scipy.linalg import lapack
from scipy.special import expit
from scipy.stats import chi2, norm

__all__ = ["firth_logit"]


def _firth_newton_raphson(X, y, max_iter, max_stepsize, max_halfstep, tol, mask=None):
    coef = np.zeros(X.shape[1])
    loglike_new = -np.inf
    for iteration in range(1, max_iter + 1):
        preds = expit(X @ coef)
        XW = _get_XW(X, preds, mask)
        fisher_info_mtx = XW.T @ XW
        hat = _hat_diag(XW)
        U_star = np.matmul(X.T, y - preds + np.multiply(hat, 0.5 - preds))
        step_size = np.linalg.lstsq(fisher_info_mtx, U_star, rcond=None)[0]
        mx = np.max(np.abs(step_size)) / max_stepsize
        if mx > 1:
            step_size = step_size / mx
        coef_new = coef + step_size
        preds_new = expit(X @ coef_new)
        loglike = _loglikelihood(X, y, preds)
        loglike_new = _loglikelihood(X, y, preds_new)
        steps = 0
        while loglike < loglike_new:
            step_size *= 0.5
            coef_new = coef + step_size
            preds_new = expit(X @ coef_new)
            loglike_new = _loglikelihood(X, y, preds_new)
            steps += 1
            if steps == max_halfstep:
                warnings.warn("Step-halving failed to converge.", RuntimeWarning, stacklevel=2)
                return coef_new, -loglike_new, iteration
        if iteration > 1 and np.linalg.norm(coef_new - coef) < tol:
            return coef_new, -loglike_new, iteration
        coef += step_size
    warnings.warn(
        "Firth logistic regression failed to converge. Try increasing max_iter.",
        RuntimeWarning,
        stacklevel=2,
    )
    return coef, -loglike_new, max_iter


def _loglikelihood(X, y, preds):
    XW = _get_XW(X, preds)
    fisher_info_mtx = XW.T @ XW
    sign, logdet = np.linalg.slogdet(fisher_info_mtx)
    penalty = 0.5 * logdet if sign > 0 else -np.inf
    return -1 * (np.sum(y * np.log(preds) + (1 - y) * np.log(1 - preds)) + penalty)


def _get_XW(X, preds, mask=None):
    rootW = np.sqrt(preds * (1 - preds))
    XW = rootW[:, np.newaxis] * X
    if mask is not None:
        XW[:, mask] = 0
    return XW


def _get_aug_XW(X, preds, hats):
    rootW = np.sqrt(preds * (1 - preds) * (1 + hats))
    return rootW[:, np.newaxis] * X


def _hat_diag(XW):
    qr, tau, _, _ = lapack.dgeqrf(XW)
    Q, _, _ = lapack.dorgqr(qr, tau)
    return np.einsum("ij,ij->i", Q, Q)


def _bse(X, coefs):
    preds = expit(X @ coefs)
    XW = _get_XW(X, preds)
    fisher_info_mtx = XW.T @ XW
    return np.sqrt(np.diag(np.linalg.pinv(fisher_info_mtx)))


def _penalized_lrt(full_loglik, X, y, max_iter, max_stepsize, max_halfstep, tol, test_vars):
    if test_vars is None:
        indices = range(X.shape[1])
    elif isinstance(test_vars, int):
        indices = [test_vars]
    else:
        indices = sorted(test_vars)
    pvals = []
    for mask in indices:
        _, null_loglik, _ = _firth_newton_raphson(
            X, y, max_iter, max_stepsize, max_halfstep, tol, mask
        )
        pvals.append(_lrt(full_loglik, null_loglik))
    if len(pvals) < X.shape[1]:
        out = np.full(X.shape[1], np.nan)
        for idx, value in zip(indices, pvals):
            out[idx] = value
        return out
    return np.array(pvals)


def _lrt(full_loglik, null_loglik):
    return chi2.sf(2 * (full_loglik - null_loglik), df=1)


def _predict(X, coef):
    preds = expit(X @ coef)
    np.clip(preds, a_min=1e-15, a_max=1 - 1e-15, out=preds)
    return preds


def _profile_likelihood_ci(
    X, y, fitted_coef, full_loglik, max_iter, max_stepsize, max_halfstep, tol, alpha, test_vars
):
    LL0 = full_loglik - chi2.ppf(1 - alpha, 1) / 2
    lower_bound: list[float] = []
    upper_bound: list[float] = []
    if test_vars is None:
        indices = range(fitted_coef.shape[0])
    elif isinstance(test_vars, int):
        indices = [test_vars]
    else:
        indices = sorted(test_vars)
    for side in (-1, 1):
        for coef_idx in indices:
            coef = deepcopy(fitted_coef)
            loglike = -np.inf
            for _ in range(1, max_iter + 1):
                preds = _predict(X, coef)
                loglike = -_loglikelihood(X, y, preds)
                XW = _get_XW(X, preds)
                hat = _hat_diag(XW)
                XW = _get_aug_XW(X, preds, hat)
                fisher_info_mtx = XW.T @ XW
                U_star = np.matmul(X.T, y - preds + np.multiply(hat, 0.5 - preds))
                inv_fisher = np.linalg.pinv(fisher_info_mtx)
                tmp1x1 = U_star @ np.negative(inv_fisher) @ U_star
                under_root = -2 * ((LL0 - loglike) + 0.5 * tmp1x1) / inv_fisher[coef_idx, coef_idx]
                lambda_ = 0 if under_root < 0 else side * sqrt(under_root)
                U_star[coef_idx] += lambda_
                step_size = np.linalg.lstsq(fisher_info_mtx, U_star, rcond=None)[0]
                mx = np.max(np.abs(step_size)) / max_stepsize
                if mx > 1:
                    step_size = step_size / mx
                coef += step_size
                loglike_old = deepcopy(loglike)
                for _ in range(1, max_halfstep + 1):
                    preds = _predict(X, coef)
                    loglike = -_loglikelihood(X, y, preds)
                    if (abs(loglike - LL0) < abs(loglike_old - LL0)) and loglike > LL0:
                        break
                    step_size *= 0.5
                    coef -= step_size
                if abs(loglike - LL0) <= tol:
                    (lower_bound if side == -1 else upper_bound).append(coef[coef_idx])
                    break
            if abs(loglike - LL0) > tol:
                (lower_bound if side == -1 else upper_bound).append(np.nan)
                warnings.warn(
                    "Non-converged profile-likelihood confidence limit.", RuntimeWarning, stacklevel=2
                )
    bounds = np.column_stack([lower_bound, upper_bound])
    if len(lower_bound) < fitted_coef.shape[0]:
        ci = np.full([fitted_coef.shape[0], 2], np.nan)
        for idx, coef_idx in enumerate(indices):
            ci[coef_idx] = bounds[idx]
        return ci
    return bounds


def _wald_ci(coef, bse, alpha):
    return np.column_stack([
        coef + norm.ppf(alpha / 2) * bse,
        coef + norm.ppf(1 - alpha / 2) * bse,
    ])


def _wald_test(coef, bse):
    return chi2.sf(np.square(coef) / np.square(bse), 1)


def firth_logit(
    X: np.ndarray,
    y: np.ndarray,
    *,
    max_iter: int = 50,
    max_stepsize: float = 5.0,
    max_halfstep: int = 25,
    tol: float = 1e-6,
    alpha: float = 0.05,
    wald: bool = False,
    test_vars: int | list[int] | None = None,
) -> dict[str, Any]:
    """Fit a Firth penalised logistic model with an intercept.

    ``X`` must not contain an intercept; a column of ones is appended and the
    returned coefficient vector has the intercept as its last element.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    if X.ndim != 2 or len(y) != X.shape[0]:
        raise ValueError("X must be 2-D and have the same number of rows as y")
    X = np.hstack([X, np.ones((X.shape[0], 1))])
    coef, loglik, n_iter = _firth_newton_raphson(
        X, y, max_iter, max_stepsize, max_halfstep, tol
    )
    bse = _bse(X, coef)
    if wald:
        pvals = _wald_test(coef, bse)
        ci = _wald_ci(coef, bse, alpha)
    else:
        pvals = _penalized_lrt(loglik, X, y, max_iter, max_stepsize, max_halfstep, tol, test_vars)
        ci = _profile_likelihood_ci(
            X, y, coef, loglik, max_iter, max_stepsize, max_halfstep, tol, alpha, test_vars
        )
    return {
        "coef": coef,
        "bse": bse,
        "pvals": pvals,
        "ci": ci,
        "loglik": loglik,
        "n_iter": n_iter,
        "wald": wald,
    }
