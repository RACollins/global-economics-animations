from manim import *
import pandas as pd
import os
from utils import add_line_of_best_fit, add_moving_average


###################
### Definitions ###
###################

cwd = os.getcwd()

#################
### Functions ###
#################


def get_labour_value_in_bread_df() -> pd.DataFrame:
    # Read the original data
    df = pd.read_csv(cwd + "/data/labour_value_in_bread.csv")
    complete_years = pd.DataFrame({"Year": range(1200, 2021)})
    df = pd.merge(complete_years, df, on="Year", how="left")
    df["Hr Rate bread (kg)"] = df["Hr Rate bread (kg)"].interpolate(method="quadratic")

    df = add_line_of_best_fit(df, "Year", "Hr Rate bread (kg)", 10)
    df = add_moving_average(df, "Year", "Hr Rate bread (kg)", 20)
    return df


def make_axes(
    x_range: list,
    y_range: list,
    x_numbers_to_include: list,
    y_numbers_to_include: list,
    log_y: bool,
    x_length: int,
    y_length: int,
):
    if log_y:
        y_axis_config = {
            "numbers_to_include": y_numbers_to_include,
            "scaling": LogBase(custom_labels=True),
        }
    else:
        y_axis_config = {
            "numbers_to_include": y_numbers_to_include,
        }
    ax = Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_length,
        y_length=y_length,
        axis_config={
            "color": WHITE,  # <- not needed if backgroud colour is default BLACK
            "include_tip": False,
            "include_numbers": True,
            "decimal_number_config": {
                "num_decimal_places": 0,
                "group_with_commas": False,  # <- This removes the comma delimitation
            },
        },
        x_axis_config={"numbers_to_include": x_numbers_to_include},
        y_axis_config=y_axis_config,
    )
    return ax


###############
### Classes ###
###############

#############
### Scene ###
#############


class LabourValueInBreadScene(Scene):

    def construct(self):
        ### Get data
        df = get_labour_value_in_bread_df()

        ### Generate axes and labels for gdp and spend
        ax, x_label, y_label = self.generate_axes(
            x_range=[1200, 2020, 50],
            y_range=[0, 7, 1],
            x_numbers_to_include=list(range(1200, 2020, 100)),
            y_numbers_to_include=list(range(0, 7, 1)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="Labour Value in Bread (kg/h)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["moving_average"],
            line_color=XKCD.SANDBROWN,
            add_vertex_dots=False,
            stroke_width=2,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()

    def generate_axes(
        self,
        x_range: list,
        y_range: list,
        x_numbers_to_include: list,
        y_numbers_to_include: list,
        log_y: bool,
        animate_axes: bool,
        x_axis_label: str,
        y_axis_label: str,
        font_size: int,
        x_length: int,
        y_length: int,
        position: float = None,
        scale: float = None,
    ) -> tuple:
        ax = make_axes(
            x_range=x_range,
            y_range=y_range,
            x_numbers_to_include=x_numbers_to_include,
            y_numbers_to_include=y_numbers_to_include,
            log_y=log_y,
            x_length=x_length,
            y_length=y_length,
        )

        if position:
            ax = ax.move_to(RIGHT * position)
        if scale:
            ax = ax.scale(scale)

        ### Add axis labels
        x_label = ax.get_x_axis_label(Text(x_axis_label, font_size=font_size))
        y_label = ax.get_y_axis_label(Text(y_axis_label, font_size=font_size))

        if animate_axes:
            ### Animate the creation of Axes
            self.play(Write(ax))
            self.play(Write(x_label))
            self.play(Write(y_label))
            # self.play(Write(title))
            self.wait()  # wait for 1 second
        else:
            ### Just generate without animation
            self.add(ax)
            self.add(x_label)
            self.add(y_label)
            # self.add(line_graph)

        return ax, x_label, y_label


if __name__ == "__main__":
    df = get_labour_value_in_bread_df()
    print(df)
    pass
