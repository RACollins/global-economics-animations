from manim import *
import numpy as np
import pandas as pd
import os
from utils import add_line_of_best_fit, add_moving_average, convert_to_moving_average


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


def get_multi_chart_data() -> pd.DataFrame:
    # Read the original data
    df = pd.read_csv(cwd + "/data/multi_chart_data.csv")
    complete_years = pd.DataFrame({"Year": range(1200, 2021)})
    df = pd.merge(complete_years, df, on="Year", how="left")
    for col in df.columns:
        if col == "Year":
            continue
        df[col] = df[col].interpolate(method="quadratic")
        df = convert_to_moving_average(df, "Year", col, 10)

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


def generate_axes(
    scene,
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
        scene.play(Write(ax))
        scene.play(Write(x_label))
        scene.play(Write(y_label))
        scene.wait()  # wait for 1 second
    else:
        ### Just generate without animation
        scene.add(ax)
        scene.add(x_label)
        scene.add(y_label)

    return ax, x_label, y_label


###############
### Classes ###
###############

##############
### Scenes ###
##############


class GDP1300to1500(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1300
        end_year = 1500
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Generate axes and labels for gdp and spend
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 50],
            y_range=[0, 5, 1],
            x_numbers_to_include=list(range(start_year, end_year, 50)),
            y_numbers_to_include=list(range(0, 5, 1)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="Real GDP (£B)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["Real GDP (£B)"],
            line_color=XKCD.BLUE,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class Pop1300to1500(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1300
        end_year = 1500
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Convert pop to millions
        df["Population (England)"] = df["Population (England)"] / 1000000

        ### Generate axes and labels for gdp and spend
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 50],
            y_range=[0, 5, 1],
            x_numbers_to_include=list(range(start_year, end_year, 50)),
            y_numbers_to_include=list(range(0, 5, 1)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="Population (millions)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["Population (England)"],
            line_color=XKCD.RED,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class GDPperCapita1300to1500(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1300
        end_year = 1500
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Generate axes and labels for gdp and spend
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 50],
            y_range=[0, 1500, 200],
            x_numbers_to_include=list(range(start_year, end_year, 50)),
            y_numbers_to_include=list(range(0, 1500, 200)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="GDP Per Person (£)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["GDP Per Person"],
            line_color=XKCD.BLUE,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class GDPperCapita1800to2000(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1800
        end_year = 2020
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Generate axes and labels for gdp and spend
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 50],
            y_range=[3, 5, 1],
            x_numbers_to_include=list(range(start_year, end_year, 50)),
            y_numbers_to_include=list(range(3, 6, 1)),
            log_y=True,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="GDP Per Person (£)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["GDP Per Person"],
            line_color=XKCD.BLUE,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class ValueInBread1800to2000(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1800
        end_year = 2000
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Generate axes and labels for gdp and spend
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 50],
            y_range=[0, 6, 1],
            x_numbers_to_include=list(range(start_year, end_year, 50)),
            y_numbers_to_include=list(range(0, 6, 1)),
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
            y_values=df["Labour Value in Bread (kg/h)"],
            line_color=XKCD.SANDBROWN,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class Population1800to2000(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1800
        end_year = 2000
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Convert pop to millions
        df["Population (England)"] = df["Population (England)"] / 1000000

        ### Generate axes and labels for gdp and spend
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 50],
            y_range=[0, 50, 10],
            x_numbers_to_include=list(range(start_year, end_year, 50)),
            y_numbers_to_include=list(range(0, 50, 10)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="Population (England) (millions)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["Population (England)"],
            line_color=XKCD.BLUE,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class WeatYield1200to2000(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1200
        end_year = 2000
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Generate axes and labels
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 100],
            y_range=[0, 7000, 1000],
            x_numbers_to_include=list(range(start_year, end_year, 200)),
            y_numbers_to_include=list(range(0, 7001, 1000)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="Wheat Yield (Tonnes per 2000 acres)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["Weat yield (Tonnes per 2000 acres)"],
            line_color=XKCD.GOLDENROD,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class MenInAgriculture1200to2000(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1200
        end_year = 2000
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Convert percentage from decimal to percentage scale
        df["Percentage of Men in Agriculture"] = (
            df["Percentage of Men in Agriculture"] * 100
        )

        ### Generate axes and labels
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 100],
            y_range=[0, 100, 10],
            x_numbers_to_include=list(range(start_year, end_year, 200)),
            y_numbers_to_include=list(range(0, 101, 20)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="Percentage of Men in Agriculture (%)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["Percentage of Men in Agriculture"],
            line_color=XKCD.RED,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class MenInAgricultureTotal1800to2000(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1800
        end_year = 2000
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Generate axes and labels
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 50],
            y_range=[0, 4000, 500],
            x_numbers_to_include=list(range(start_year, end_year, 50)),
            y_numbers_to_include=list(range(0, 4001, 500)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="Men in Agriculture",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["Men in Agriculture"],
            line_color=XKCD.RED,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class DayWages1300to1400(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1300
        end_year = 1400
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Generate axes and labels
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 50],
            y_range=[0, 18, 2],
            x_numbers_to_include=list(range(start_year, end_year, 50)),
            y_numbers_to_include=list(range(0, 18, 2)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="Day Wages (£)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["Labour Day Wages (2025-£)"],
            line_color=XKCD.RED,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class DayWages1800to2000(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1800
        end_year = 2000
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Generate axes and labels
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[start_year, end_year, 50],
            y_range=[0, 70, 10],
            x_numbers_to_include=list(range(start_year, end_year, 50)),
            y_numbers_to_include=list(range(0, 70, 10)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Year",
            y_axis_label="Day Wages (£)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Generate line plots and draw
        line_graph = ax.plot_line_graph(
            x_values=df["Year"],
            y_values=df["Labour Day Wages (2025-£)"],
            line_color=XKCD.RED,
            add_vertex_dots=False,
            stroke_width=3,
        )

        ### Draw plots
        self.play(
            Write(line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad)
        )
        self.wait()


class GDPPerPersonVsValueInBread1800to2000(Scene):

    def construct(self):
        ### Get data
        df = get_multi_chart_data()

        ### Limit to time range
        start_year = 1800
        end_year = 2000
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Remove rows with missing data for either variable
        df = df.dropna(subset=["GDP Per Person", "Labour Value in Bread (kg/h)"])

        ### Sort by year to ensure chronological order
        df = df.sort_values("Year").reset_index(drop=True)

        ### Filter to only every 10 years
        df = df[df["Year"] % 10 == 0]

        ### Determine axis ranges based on data
        x_min, x_max = df["GDP Per Person"].min(), df["GDP Per Person"].max()
        y_min, y_max = (
            df["Labour Value in Bread (kg/h)"].min(),
            df["Labour Value in Bread (kg/h)"].max(),
        )

        # Add padding to ranges
        x_padding = (x_max - x_min) * 0.1
        y_padding = (y_max - y_min) * 0.1

        x_range = [x_min - x_padding, x_max + x_padding]
        y_range = [y_min - y_padding, y_max + y_padding]

        ### Generate axes and labels
        ax, x_label, y_label = generate_axes(
            scene=self,
            x_range=[0, 25000, 5000],
            y_range=[0, 6, 1],
            x_numbers_to_include=list(range(0, 25001, 5000)),
            y_numbers_to_include=list(range(0, 6, 1)),
            log_y=False,
            animate_axes=True,
            x_axis_label="GDP Per Person (£)",
            y_axis_label="Labour Value in Bread (kg/h)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Create dots for each year
        dots = []
        years = []
        for i in range(len(df)):
            year = df.iloc[i]["Year"]
            x_val = df.iloc[i]["GDP Per Person"]
            y_val = df.iloc[i]["Labour Value in Bread (kg/h)"]

            dot = Dot(
                ax.c2p(x_val, y_val), color=XKCD.BLUE, radius=0.08, fill_opacity=0.8
            )
            dots.append(dot)
            years.append(year)

        ### Animate dots sequentially from 1800 to 2000
        self.play(LaggedStart(*[Create(dot) for dot in dots], lag_ratio=0.2))

        # Pause at the end to show final result
        self.wait(3)


if __name__ == "__main__":
    df = get_multi_chart_data()
    print(df.loc[df["Year"] >= 2000])
    pass
