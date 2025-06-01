from manim import *
import pandas as pd
import os
from utils import add_line_of_best_fit, add_moving_average


###################
### Definitions ###
###################

### Uncomment when switching to WHITE background
config.background_color = WHITE

### Set default color for common objects
Line.set_default(color=BLACK)
Text.set_default(color=BLACK)
Axes.set_default(color=BLACK)

cwd = os.getcwd()

#################
### Functions ###
#################


def get_g7_debt_df(start_year: int, end_year: int) -> pd.DataFrame:
    df = pd.read_csv(cwd + "/data/imf_gross_public_debt_20240924_inverted.csv").drop(
        columns=["Unnamed: 0"]
    )
    # Filter to G7 countries
    g7_df = df[
        df["Country"].isin(
            [
                "United States",
                "Canada",
                "United Kingdom",
                "France",
                "Germany",
                "Italy",
                "Japan",
            ]
        )
    ]

    # Group by Year and calculate the average debt across G7 countries
    g7_avg_df = g7_df.groupby("Year")["Public debt (% of GDP)"].mean().reset_index()
    g7_avg_df = g7_avg_df[g7_avg_df["Year"] >= start_year]
    g7_avg_df = g7_avg_df[g7_avg_df["Year"] <= end_year]

    g7_avg_df = add_line_of_best_fit(g7_avg_df, "Year", "Public debt (% of GDP)", 10)
    g7_avg_df = add_moving_average(g7_avg_df, "Year", "Public debt (% of GDP)", 5)
    return g7_avg_df


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
            "color": BLACK,  # <- not needed if backgroud colour is default BLACK
            "include_tip": False,
            "include_numbers": True,
            "decimal_number_config": {
                "num_decimal_places": 0,
                "group_with_commas": False,  # <- This removes the comma delimitation
            },
        },
        x_axis_config={
            "numbers_to_include": x_numbers_to_include,
        },
        y_axis_config=y_axis_config,
    )
    ax.add_coordinates()
    ax.coordinate_labels[0].set_color(BLACK)
    ax.coordinate_labels[1].set_color(BLACK)
    return ax


###############
### Classes ###
###############

#############
### Scene ###
#############


class G7DebtScene(Scene):

    def construct(self):
        start_year = 1970
        end_year = 2023
        ### Get data
        df = get_g7_debt_df(start_year, end_year)

        ### Generate axes and labels for gdp and spend
        ax, x_label, y_label = self.generate_axes(
            x_range=[start_year, end_year, 5],
            y_range=[0, 150, 20],
            x_numbers_to_include=list(range(start_year, end_year, 10)),
            y_numbers_to_include=list(range(0, 160, 20)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="G7 Average Public Debt (% of GDP)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["moving_average"],
            line_color=XKCD.AZURE,
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
        x_label = ax.get_x_axis_label(Text(x_axis_label, font_size=font_size, color=BLACK))
        y_label = ax.get_y_axis_label(Text(y_axis_label, font_size=font_size, color=BLACK))

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
    df = get_g7_debt_df(1970, 2023)
    print(df)
    pass
