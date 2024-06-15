from manim import *
import pandas as pd
import os

###################
### Definitions ###
###################

colour_map = {
    "Asia": PURE_RED,
    "Americas": PINK,
    "Africa": YELLOW,
    "Europe": PURE_GREEN,
    "Oceania": PURE_BLUE,
}

#################
### Functions ###
#################


def get_spending_df() -> pd.DataFrame:
    cwd = os.getcwd()
    df = (
        pd.read_csv(cwd + "/data/spending_vs_gdp_per_capita.csv")
        .drop(columns=["Unnamed: 0"])
        .sort_values(["Country", "Year"])
    )
    return df


def add_radius_col(
    df: pd.DataFrame, lowest_radius: float, highest_radius: float
) -> pd.DataFrame:
    df["radius"] = (df["Population"] - df["Population"].min()) / (
        df["Population"].max() - df["Population"].min()
    ) * (highest_radius - lowest_radius) + lowest_radius
    return df


def make_axes(
    x_range: list, y_range: list, x_numbers_to_include: list, y_numbers_to_include: list
):
    ax = Axes(
        x_range=x_range,
        y_range=y_range,
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
        y_axis_config={"numbers_to_include": y_numbers_to_include},
    )
    return ax


###############
### Classes ###
###############


#############
### Scene ###
#############


class SpendingVsGrowthAnimatedScene(Scene):
    def construct(self):
        """self.generate_timeseries_plot(
            country="United Kingdom",
            x_range=[1850, 2021, 10],
            y_range=[0, 100, 10],
            numbers_to_exclude=list(range(1850, 2020, 20)),
            y_axis_label="Government Expenditure (%)",
            col_to_plot="Government Expenditure (IMF & Wiki)",
            animate_axes=True,
        )"""
        plot_vgroup = self.generate_line_plot(
            country="United Kingdom",
            x_range=[1850, 2021, 10],
            y_range=[4000, 40001, 1000],
            x_numbers_to_include=list(range(1860, 2021, 20)),
            y_numbers_to_include=list(range(5000, 40001, 5000)),
            y_axis_label="GDP per capita",
            col_to_plot="GDP per capita (OWiD)",
            animate_axes=True,
        )
        self.wait(2)
        """ self.play(ApplyMethod(plot_vgroup.scale, 0.25),
                  ApplyMethod(plot_vgroup.move_to, UP * 3 + LEFT * 5)) """
        shift_scale = plot_vgroup.animate  
        self.play(shift_scale.shift([-4.25, 2.5, 0]), shift_scale.scale(0.33))  

    def generate_line_plot(
        self,
        country: str,
        x_range: list,
        y_range: list,
        x_numbers_to_include: list,
        y_numbers_to_include: list,
        animate_axes: bool,
        y_axis_label: str,
        col_to_plot: str,
    ):
        ### Download data and put in DataFrame
        df = get_spending_df()
        filtered_df = df.loc[df["Country"] == country, :].set_index("Year", drop=False)
        ax = make_axes(
            x_range=x_range,
            y_range=y_range,
            x_numbers_to_include=x_numbers_to_include,
            y_numbers_to_include=y_numbers_to_include,
        )
        ### Add axis labels
        x_label = ax.get_x_axis_label(Text("Year", font_size=26))
        y_label = ax.get_y_axis_label(Text(y_axis_label, font_size=26))

        line_graph = ax.plot_line_graph(
            x_values=filtered_df["Year"],
            y_values=filtered_df[col_to_plot],
            line_color=PURE_GREEN,
            add_vertex_dots=False,
        )

        if animate_axes:
            ### Animate the creation of Axes
            self.play(Write(ax))
            self.play(Write(x_label))
            self.play(Write(y_label))
            self.play(Write(line_graph, rate_func=rate_functions.ease_in_expo))
            # self.play(Write(title))
            self.wait()  # wait for 1 second
        else:
            ### Just generate without animation
            self.add(ax)
            self.add(x_label)
            self.add(y_label)
            self.add(line_graph)

        return VGroup(ax, line_graph, x_label, y_label)

    def generate_timeseries_plot(
        self,
        country: str,
        x_range: list,
        y_range: list,
        numbers_to_exclude: list,
        animate_axes: bool,
        y_axis_label: str,
        col_to_plot: str,
    ):
        ### Download data and put in DataFrame
        df = get_spending_df()
        filtered_df = df.loc[df["Country"] == country, :].set_index("Year", drop=False)
        ax = make_axes(
            x_range=x_range, y_range=y_range, numbers_to_exclude=numbers_to_exclude
        )
        ### Add axis labels
        x_label = ax.get_x_axis_label(Text("Year", font_size=26))
        y_label = ax.get_y_axis_label(Text(y_axis_label, font_size=26))
        ### Add title
        # title = Text(r"{}".format(" ".join([s.capitalize() for s in job.split("_")])), font_size=30)
        # title.to_edge(UP)
        ts = ax.plot(
            lambda x: filtered_df.loc[x, col_to_plot],
            x_range=[1850, 2020, 1],
            color=PURE_GREEN,
        )

        if animate_axes:
            ### Animate the creation of Axes
            self.play(Write(ax))
            self.play(Write(x_label))
            self.play(Write(y_label))
            self.play(Write(ts, rate_func=rate_functions.ease_in_expo))
            # self.play(Write(title))
            self.wait()  # wait for 1 second

        return ax


if __name__ == "__main__":
    """ df = get_spending_df()
    #filtered_df = df.loc[df["Country"] == "United Kingdom", :].reset_index(drop=True)
    filtered_df = df.reset_index(drop=True).sort_values(by=["GDP per capita (OWiD)"])
    print(filtered_df) """
    pass
