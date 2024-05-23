from manim import *
import pandas as pd
import os

#################
### Functions ###
#################


def get_salaries_df(job):
    cwd = os.getcwd()
    df = pd.read_csv(cwd + "/data/{}.csv".format(job), index_col=0)
    return df


def make_axes(df):
    max_y = df.loc[:, "Median_USD"].max()

    ax = Axes(
        x_range=[0, 140e3, 10e3],
        y_range=[0, max_y, 10e3],
        axis_config={
            "include_tip": True,
            "include_numbers": False,
        },
    )
    return ax


###############
### Classes ###
###############


class DataPoint(Dot):
    def __init__(self, point: list | np.ndarray, x: float, y: float, color, **kwargs):
        super().__init__(point=point, radius=0.1, color=color, fill_opacity=0.8, **kwargs)
        self.x = x
        self.y = y


#############
### Scene ###
#############


class SalariesScatterPlotAnimatedScene(Scene):
    def construct(self):
        # Download data and put in DataFrame
        df = get_salaries_df(job="nurse")

        # Animate the creation of Axes
        ax = make_axes(df)
        self.play(Write(ax))

        self.wait()  # wait for 1 second

        # Animate the creation of dots
        dots = []
        colour_map = {
            "Asia": PURE_RED,
            "Americas": PINK,
            "Africa": YELLOW,
            "Europe": PURE_GREEN,
            "Oceania": PURE_BLUE,
        }
        for i in range(df.shape[0]):
            x, y = df.loc[i, ["GDP_per_capita_USD", "Median_USD"]].values
            colour = colour_map[df.loc[i, ["Region"]].values[0]]
            dots.append(DataPoint(point=ax.c2p(x, y), x=x, y=y, color=colour))
        """ dots = [
            DataPoint(point=ax.c2p(x, y), x=x, y=y, color=BLUE)
            for x, y in df.loc[:, ["GDP_per_capita_USD", "Median_USD"]].values
        ] """
        self.play(LaggedStart(*[Write(dot) for dot in dots], lag_ratio=0.05))

        self.wait()  # wait for 1 second


if __name__ == "__main__":
    """df = get_salaries_df(job="nurse")
    print(df)"""
    pass
