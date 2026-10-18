import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import reiplotlib as rpl


def test_offscreen_outlier_and_crossing():
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2, 20], [1, 2, 3, 15])
    ax.set_xlim(0, 1.5)
    rpl.autoscale_y(ax, margin=0)
    assert np.allclose(ax.get_ylim(), (1, 2.5))
    plt.close(fig)


def test_shared_errors_manual_and_watch():
    fig, axes = plt.subplots(1, 2, sharey=True)
    axes[0].errorbar([1, 20], [2, 50], yerr=[.5, 3], fmt='none')
    axes[1].scatter([1, 20], [4, 60])
    for ax in axes:
        ax.set_xlim(0, 2)
    rpl.autoscale_y(axes[0], margin=0, watch=True)
    assert np.allclose(axes[0].get_ylim(), (1.5, 4))
    axes[1].set_xlim(19, 21)
    assert np.allclose(axes[0].get_ylim(), (1.5, 60))
    axes[0].set_ylim(0, 10)
    axes[1].set_xlim(0, 2)
    rpl.autoscale_y(axes[0])
    assert axes[0].get_ylim() == (0, 10)
    plt.close(fig)


def test_log_clipping_and_vertical_guide():
    fig, ax = plt.subplots()
    ax.set(xscale='log', yscale='log', xlim=(1, 10))
    ax.plot([1, 100], [1, 100])
    ax.axvline(3)
    rpl.autoscale_y(ax, margin=0)
    assert np.allclose(ax.get_ylim(), (1, 10))
    plt.close(fig)


def test_adaptive_errorbars_preserve_original_extents():
    fig, ax = plt.subplots()
    rpl.errorbar(ax, [1, 20], [2, 50], yerr=[.01, 30], min_error_size=100, fmt='o')
    ax.set_xlim(0, 2)
    fig.canvas.draw()
    rpl.autoscale_y(ax, margin=0)
    assert np.allclose(ax.get_ylim(), (1.99, 2.01))
    plt.close(fig)
