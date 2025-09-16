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


def get_gdp_and_wages_df() -> pd.DataFrame:
    # Read the original data
    df = pd.read_csv(cwd + "/data/gdp_per_capita_vs_weekly_wages.csv")
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


###############
### Classes ###
###############

##############
### Scenes ###
##############


class GDPPerPersonVsWeeklyWages1800to2000(Scene):

    def construct(self):
        ### Get data
        df = get_gdp_and_wages_df()

        ### Limit to time range
        start_year = 1800
        end_year = 2000
        df = df.loc[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        ### Remove rows with missing data for either variable
        df = df.dropna(
            subset=[
                "GDP /Person rolling average",
                "Real Average Weekly Wages (Bank of England (2017))",
            ]
        )

        ### Sort by year to ensure chronological order
        df = df.sort_values("Year").reset_index(drop=True)

        ### Keep all years for smooth animation (remove the 5-year filtering)
        # The original data already has interpolation built in from get_gdp_and_wages_df()
        # which creates values for every year and applies moving averages

        ### Determine axis ranges based on data
        x_min, x_max = (
            df["GDP /Person rolling average"].min(),
            df["GDP /Person rolling average"].max(),
        )
        y_min, y_max = (
            df["Real Average Weekly Wages (Bank of England (2017))"].min(),
            df["Real Average Weekly Wages (Bank of England (2017))"].max(),
        )

        # Add padding to ranges
        x_padding = (x_max - x_min) * 0.1
        y_padding = (y_max - y_min) * 0.1

        x_range = [x_min - x_padding, x_max + x_padding]
        y_range = [y_min - y_padding, y_max + y_padding]

        ### Generate axes and labels
        ax, x_label, y_label = self.generate_axes(
            x_range=[0, 25000, 5000],
            y_range=[0, 500, 100],
            x_numbers_to_include=list(range(0, 25001, 5000)),
            y_numbers_to_include=list(range(0, 501, 100)),
            log_y=False,
            animate_axes=True,
            x_axis_label="GDP Per Person (£)",
            y_axis_label="Weekly Wages (£)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Create ValueTracker for year animation
        year_tracker = ValueTracker(1800)

        ### Create year display in bottom right corner using absolute positioning
        year_text_display = always_redraw(
            lambda: Text(
                f"{int(year_tracker.get_value())}",
                font_size=24,
                color=BLACK,
            ).move_to(
                [5, -1.5, 0]
            )  # Absolute position in bottom right
        )

        ### Create dynamic line that updates based on year_tracker
        def get_filtered_data(current_year):
            """Filter data up to current year and interpolate for smooth animation"""
            # Get all data up to the current year
            filtered_df = df[df["Year"] <= current_year].copy()

            if len(filtered_df) < 1:  # Need at least 1 point
                return [], []

            # If current_year is not a whole number, interpolate the current point
            if current_year != int(current_year) and current_year < end_year:
                current_year_int = int(current_year)
                next_year = current_year_int + 1

                # Find the data for current and next year
                current_data = df[df["Year"] == current_year_int]
                next_data = df[df["Year"] == next_year]

                if not current_data.empty and not next_data.empty:
                    # Interpolate between current and next year
                    fraction = current_year - current_year_int

                    interp_gdp = (
                        current_data.iloc[0]["GDP /Person rolling average"]
                        * (1 - fraction)
                        + next_data.iloc[0]["GDP /Person rolling average"] * fraction
                    )
                    interp_wage = (
                        current_data.iloc[0][
                            "Real Average Weekly Wages (Bank of England (2017))"
                        ]
                        * (1 - fraction)
                        + next_data.iloc[0][
                            "Real Average Weekly Wages (Bank of England (2017))"
                        ]
                        * fraction
                    )

                    # Add the interpolated point
                    interp_row = pd.DataFrame(
                        {
                            "Year": [current_year],
                            "GDP /Person rolling average": [interp_gdp],
                            "Real Average Weekly Wages (Bank of England (2017))": [
                                interp_wage
                            ],
                        }
                    )
                    filtered_df = pd.concat(
                        [filtered_df, interp_row], ignore_index=True
                    )

            if len(filtered_df) < 2:  # Need at least 2 points for a line
                return [], []

            return (
                filtered_df["GDP /Person rolling average"].tolist(),
                filtered_df[
                    "Real Average Weekly Wages (Bank of England (2017))"
                ].tolist(),
            )

        ### Create the dynamic line graph
        dynamic_line = always_redraw(
            lambda: (
                ax.plot_line_graph(
                    *get_filtered_data(year_tracker.get_value()),
                    line_color=XKCD.BLUE,
                    add_vertex_dots=False,
                    stroke_width=3,
                )
                if get_filtered_data(year_tracker.get_value())[0]
                else VGroup()
            )
        )

        ### Add the year display and dynamic line to the scene
        self.add(year_text_display, dynamic_line)

        ### Animate the year tracker from 1800 to 2000 with smooth interpolation
        # Use a longer duration for smoother animation
        self.play(
            year_tracker.animate.set_value(2000),
            run_time=10,  # Increased from 8 to allow more granular updates
            rate_func=rate_functions.linear,
        )

        ### Wait at the end to show the complete result
        self.wait(2)

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
        x_label = ax.get_x_axis_label(
            Text(x_axis_label, font_size=font_size, color=BLACK)
        )
        y_label = ax.get_y_axis_label(
            Text(y_axis_label, font_size=font_size, color=BLACK)
        )

        if animate_axes:
            ### Animate the creation of Axes
            self.play(Write(ax))
            self.play(Write(x_label))
            self.play(Write(y_label))
            self.wait()  # wait for 1 second
        else:
            ### Just generate without animation
            self.add(ax)
            self.add(x_label)
            self.add(y_label)

        return ax, x_label, y_label


if __name__ == "__main__":
    df = get_gdp_and_wages_df()
    print(df.loc[df["Year"] >= 2000])
    pass
