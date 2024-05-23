from manim import *
import pandas as pd
import os


class DataPoint(Dot):
    def __init__(self, point: list | np.ndarray, x: float, y: float, color, **kwargs):
        super().__init__(point=point, radius=0.15, color=color, **kwargs)
        self.x = x
        self.y = y


def make_axes():
    ax = Axes(
        x_range=[0, 100, 10],
        y_range=[-20, 200, 10],
        x_axis_config={
            "include_tip": True,
            "include_numbers": True,
        },
        y_axis_config={
            "include_tip": False,
            "include_numbers": True,
        },
    )
    return ax


class SalariesScatterPlotAnimatedScene(Scene):
    def construct(self):
        # Download data and put in DataFrame
        data_url = "https://raw.githubusercontent.com/thomasnield/machine-learning-demo-data/master/regression/linear_normal.csv"

        df = pd.read_csv(data_url)

        # Animate the creation of Axes
        ax = make_axes()
        self.play(Write(ax))

        self.wait()  # wait for 1 second

        # Animate the creation of dots
        dots = [Dot(ax.c2p(x, y), color=BLUE) for x, y in df.values]
        self.play(LaggedStart(*[Write(dot) for dot in dots], lag_ratio=0.05))

        self.wait()  # wait for 1 second

class LogScalingExample(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 10, 1],
            y_range=[-2, 6, 1],
            tips=False,
            axis_config={"include_numbers": True},
            y_axis_config={"scaling": LogBase(custom_labels=True)},
        )

        # x_min must be > 0 because log is undefined at 0.
        graph = ax.plot(lambda x: x ** 2, x_range=[0.001, 10], use_smoothing=False)
        self.add(ax, graph)