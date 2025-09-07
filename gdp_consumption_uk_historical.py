from manim import *
import numpy as np
import pandas as pd
import os


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

colour_map = {
    "Asia": "#DE5151",
    "North America": XKCD.BUBBLEGUM,
    "South America": XKCD.BRIGHTPURPLE,
    "Africa": XKCD.AMBER,
    "Europe": "#0BB580",
    "Oceania": XKCD.RICHBLUE,
    "G7": "#1099D0",
    "World": "#1099D0",
}

radius_map = {
    "Small": 0.05,
    "Medium": 0.12,
    "Large": 0.20,
}

#################
### Functions ###
#################


def get_gdp_consumption_uk_historical_df() -> pd.DataFrame:
    df = pd.read_csv(cwd + "/data/gdp_consumption_uk_historical.csv")
    return df


def make_axes(
    x_range: list,
    y_range: list,
    x_numbers_to_include: list,
    y_numbers_to_include: list,
    log_x: bool,
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
    if log_x:
        x_axis_config = {
            "numbers_to_include": x_numbers_to_include,
            "scaling": LogBase(custom_labels=True),
        }
    else:
        x_axis_config = {
            "numbers_to_include": x_numbers_to_include,
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
        x_axis_config=x_axis_config,
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


class ConsumptionVsGDP(Scene):

    def construct(self):
        ### Get data
        df = get_gdp_consumption_uk_historical_df()

        ### Generate axes and labels
        ax, x_label, y_label = self.generate_axes(
            x_range=[3, 5, 1],
            y_range=[0, 2, 1],
            x_numbers_to_include=list(range(3, 6, 1)),
            y_numbers_to_include=list(range(0, 3, 1)),
            log_x=True,
            log_y=True,
            animate_axes=True,
            x_axis_label="GDP per Capita ($)",
            y_axis_label="Median Consumption ($/day)",
            font_size=26,
            x_length=12,
            y_length=6,
        )

        ### Create dots for each country in 2023
        gdp_median_dots = self.generate_dots(
            df, ax, "GDP per capita", "Median Income Consumption ($/day)"
        )

        ### Animate dots sequentially
        self.play(
            LaggedStart(*[Create(dot) for dot in gdp_median_dots], lag_ratio=0.05)
        )

        ### Pause at the end to show final result
        self.wait()

        ### Draw dot by dot the sequence for the UK from 1750 to 2012
        ### Reduce opacity of plotted dots to 0.3

        ### Create ValueTracker for year animation
        year_tracker = ValueTracker(1750)

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

        ### Create dynamic UK dot that follows the year tracker
        uk_dynamic_dot = always_redraw(
            lambda: self.create_uk_dot_for_year(df, ax, int(year_tracker.get_value()))
        )

        ### Generate list of dots and add to scene while value tracker changes
        uk_dots_list = []
        uk_df = df.loc[df["Entity"] == "United Kingdom", :]
        for year in range(1750, 2013):
            year_data = uk_df.loc[uk_df["Year"] == year, :]
            if not year_data.empty:
                x_val = year_data["GDP per capita"].values[0]
                y_val = year_data["Median Income Consumption ($/day)"].values[0]
                region = year_data["World regions according to OWID"].values[0]
                size = year_data["Country Size"].values[0]

                uk_dots_list.append(
                    Dot(
                        ax.c2p(x_val, y_val),
                        color=colour_map[region],
                        radius=radius_map[size],
                        fill_opacity=0.3,  # Lower opacity for trail dots
                    )
                )

        ### Add the dynamic dot and year display to scene
        self.add(uk_dynamic_dot, year_text_display)

        ### Animate the year tracker and create trailing dots
        self.play(
            year_tracker.animate.set_value(2012),
            LaggedStart(
                *[Create(d) for d in uk_dots_list],
                lag_ratio=100.0
                / len(uk_dots_list),  # Spread evenly over animation time
                rate_func=rate_functions.linear,
            ),
            run_time=12.0,
            rate_func=rate_functions.linear,
        )
        self.wait()

        ### Remove the dynamic elements before continuing
        self.remove(uk_dynamic_dot, year_text_display)
        self.play(*[Unwrite(d) for d in uk_dots_list], run_time=1.0)

        ### Draw red and green rectangles in bottom left and top right sections of graph
        gdp_median_rect_list = []
        # [(bottom_left, top_right)] <-- [(x_min, y_min), (x_max, y_max)]
        gdp_median_rect_coords = [
            [(1e3, 1e0), (2.4e4, 1.75e1)],  # <-- red
            [(2.4e4, 1.75e1), (1e5, 1e2)],  # <-- green
        ]
        for i, coord_tuples_list in enumerate(gdp_median_rect_coords):
            color = RED if i == 0 else GREEN
            rect = Polygon(
                *[ax.c2p(*i) for i in self.get_rectangle_corners(*coord_tuples_list)],
                color=color,
                fill_color=color,
                fill_opacity=0.6,
            )
            gdp_median_rect_list.append(rect)

        ### Draw rectangles
        self.play(
            *[Create(r) for r in gdp_median_rect_list],
            run_time=1.0,
        )
        self.wait(3)

        ### Undraw rectangles
        self.play(
            *[Unwrite(r) for r in gdp_median_rect_list],
            run_time=1.0,
        )
        self.wait()

        ### Generate dots for GDP and lowest 10% consumption
        gdp_lowest_10_dots = self.generate_dots(
            df, ax, "GDP per capita", "Lowest 10% Income Consumption ($/day)"
        )

        ### Animate transition from GDP vs. median consumption to GDP vs. lowest 10% consumption
        ### And animate title transition

        ### Create new y-axis label for lowest 10% consumption
        lowest_10_y_label = ax.get_y_axis_label(
            Text("Lowest 10% Income Consumption ($/day)", font_size=26, color=BLACK)
        )
        self.play(
            Transform(y_label, lowest_10_y_label),
            *[
                Transform(gdp_median_dots[i], gdp_lowest_10_dots[i])
                for i in range(len(gdp_median_dots))
            ],
            run_time=1.0,
        )
        self.wait()

        ### Draw red and green rectangles in bottom left and top right sections of graph
        gdp_lowest_10_rect_list = []
        gdp_lowest_10_rect_coords = [
            [(1e3, 1e0), (2.65e4, 0.75e1)],  # <-- red
            [(2.65e4, 0.75e1), (1e5, 1e2)],  # <-- green
        ]
        for i, coord_tuples_list in enumerate(gdp_lowest_10_rect_coords):
            color = RED if i == 0 else GREEN
            rect = Polygon(
                *[ax.c2p(*i) for i in self.get_rectangle_corners(*coord_tuples_list)],
                color=color,
                fill_color=color,
                fill_opacity=0.6,
            )
            gdp_lowest_10_rect_list.append(rect)

        ### Draw red and green rectangles
        self.play(
            *[Create(r) for r in gdp_lowest_10_rect_list],
            run_time=1.0,
        )
        self.wait(3)

        ### Undraw rectangles
        self.play(
            *[Unwrite(r) for r in gdp_lowest_10_rect_list],
            run_time=1.0,
        )
        self.wait()

        ### Create ValueTrackers for x-axis range animation
        x_min_tracker = ValueTracker(3)  # Initial x_min (log scale: 10^3 = 1000)
        x_max_tracker = ValueTracker(5)  # Initial x_max (log scale: 10^5 = 100000)

        ### Create new axes with always_redraw for dynamic x-axis range
        new_ax = always_redraw(
            lambda: make_axes(
                x_range=[x_min_tracker.get_value(), x_max_tracker.get_value(), 1],
                y_range=[0, 2, 1],
                x_numbers_to_include=list(
                    range(
                        int(x_min_tracker.get_value()),
                        int(x_max_tracker.get_value()) + 1,
                        1,
                    )
                ),
                y_numbers_to_include=list(range(0, 3, 1)),
                log_x=True,
                log_y=True,
                x_length=12,
                y_length=6,
            )
        )

        ### Create new x-axis label for median consumption
        median_x_label = new_ax.get_x_axis_label(
            Text("Median Income Consumption ($/day)", font_size=26, color=BLACK)
        )

        ### Remove old axes and add new dynamic axes
        self.remove(ax)
        self.add(new_ax)

        ### Create static axes for generating final dot positions (target axes with final range)
        target_ax = make_axes(
            x_range=[0, 2, 1],  # Final x-axis range (log scale: 1 to 100)
            y_range=[0, 2, 1],  # Same y-axis range
            x_numbers_to_include=list(range(0, 3, 1)),
            y_numbers_to_include=list(range(0, 3, 1)),
            log_x=True,
            log_y=True,
            x_length=12,
            y_length=6,
        )

        ### Generate dots for Median consumption vs. Lowest 10% consumption on the target axes
        median_lowest_10_dots = self.generate_dots(
            df,
            target_ax,
            "Median Income Consumption ($/day)",
            "Lowest 10% Income Consumption ($/day)",
        )

        ### Animate the x-axis range transition and label/dots transformation
        self.play(
            x_min_tracker.animate.set_value(0),  # Target x_min (log scale: 10^0 = 1)
            x_max_tracker.animate.set_value(2),  # Target x_max (log scale: 10^2 = 100)
            Transform(x_label, median_x_label),
            *[
                Transform(gdp_median_dots[i], median_lowest_10_dots[i])
                for i in range(len(gdp_median_dots))
            ],
            run_time=2.0,
        )
        self.wait()

        ### Update ax reference to new_ax for subsequent operations
        ax = new_ax

    def get_rectangle_corners(self, bottom_left, top_right):
        return [
            (top_right[0], top_right[1]),
            (bottom_left[0], top_right[1]),
            (bottom_left[0], bottom_left[1]),
            (top_right[0], bottom_left[1]),
        ]

    def create_uk_dot_for_year(self, df: pd.DataFrame, ax: Axes, year: int):
        """Create a single UK dot for a specific year"""
        uk_df = df.loc[df["Entity"] == "United Kingdom", :]
        year_data = uk_df.loc[uk_df["Year"] == year, :]

        if year_data.empty:
            # Return invisible dot if no data for this year
            return Dot(ax.c2p(1000, 1), radius=0.0, fill_opacity=0.0)

        x_val = year_data["GDP per capita"].values[0]
        y_val = year_data["Median Income Consumption ($/day)"].values[0]
        region = year_data["World regions according to OWID"].values[0]
        size = year_data["Country Size"].values[0]

        return Dot(
            ax.c2p(x_val, y_val),
            color=colour_map[region],
            radius=radius_map[size],
            fill_opacity=0.8,
        )

    def generate_dots(
        self,
        df: pd.DataFrame,
        ax: Axes,
        x_col: str,
        y_col: str,
        uk_sequence: bool = False,
    ):
        dots = []
        if uk_sequence:
            uk_df = df.loc[df["Entity"] == "United Kingdom", :]
            for year in range(1750, 2013):
                x_val = uk_df.loc[uk_df["Year"] == year, "GDP per capita"].values[0]
                y_val = uk_df.loc[
                    uk_df["Year"] == year, "Median Income Consumption ($/day)"
                ].values[0]
                region = uk_df.loc[
                    uk_df["Year"] == year, "World regions according to OWID"
                ].values[0]
                size = uk_df.loc[uk_df["Year"] == year, "Country Size"].values[0]
                dots.append(
                    Dot(
                        ax.c2p(x_val, y_val),
                        color=colour_map[region],
                        radius=radius_map[size],
                        fill_opacity=0.8,
                    )
                )
        else:
            countries = df["Entity"].unique()
            excluded_countries = ["Kosovo", "Burundi"]
            for country in countries:
                if country in excluded_countries:
                    continue
                country_df = df.loc[(df["Entity"] == country) & (df["Year"] == 2023), :]
                x_val = country_df[x_col].values[0]
                y_val = country_df[y_col].values[0]

                region = country_df["World regions according to OWID"].values[0]
                size = country_df["Country Size"].values[0]

                if y_val < 1:
                    colour = WHITE
                else:
                    colour = colour_map[region]
                radius = radius_map[size]
                dots.append(
                    Dot(
                        ax.c2p(x_val, y_val),
                        color=colour,
                        radius=radius,
                        fill_opacity=0.8,
                    )
                )
        return dots

    def generate_axes(
        self,
        x_range: list,
        y_range: list,
        x_numbers_to_include: list,
        y_numbers_to_include: list,
        log_x: bool,
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
            log_x=log_x,
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
    df = get_gdp_consumption_uk_historical_df()
    print(df.head())
    pass
