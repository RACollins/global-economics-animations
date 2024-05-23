from manim import *
import pandas as pd


class CreateCircle(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
        self.play(Create(circle))  # show the circle on screen


class ScatterPlotAnimatedScene(Scene):
    def construct(self):
        # Download data and put in DataFrame
        data_url = "https://raw.githubusercontent.com/thomasnield/machine-learning-demo-data/master/regression/linear_normal.csv"

        df = pd.read_csv(data_url)

        # Animate the creation of Axes
        ax = Axes(x_range=[0, 100, 5], y_range=[-20, 200, 10])
        self.play(Write(ax))

        self.wait()  # wait for 1 second

        # Animate the creation of dots
        dots = [Dot(ax.c2p(x, y), color=BLUE) for x, y in df.values]
        self.play(LaggedStart(*[Write(dot) for dot in dots], lag_ratio=0.05))

        self.wait()  # wait for 1 second
