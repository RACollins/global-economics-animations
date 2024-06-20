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
    ### Convert to K$s
    df["GDP per capita (OWiD)"] = df["GDP per capita (OWiD)"].div(1000)
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

        ### Load data and put in DataFrame
        df = get_spending_df()
        filtered_df = df.loc[df["Country"] == "United Kingdom", :].set_index("Year", drop=False)

        ### Generate axes and labels for gdp and spend
        gdp_ax, gdp_x_label, gdp_y_label = self.generate_axes(
            x_range=[1850, 2021, 10],
            y_range=[4, 40, 1],
            x_numbers_to_include=list(range(1860, 2021, 20)),
            y_numbers_to_include=list(range(5, 40, 5)),
            x_axis_label="Year",
            y_axis_label="GDP per capita (kUSD)",
            animate_axes=False,
        )
        spend_ax, spend_x_label, spend_y_label = self.generate_axes(
            x_range=[1850, 2021, 10],
            y_range=[0, 101, 10],
            x_numbers_to_include=list(range(1860, 2021, 20)),
            y_numbers_to_include=list(range(0, 100, 20)),
            x_axis_label="Year",
            y_axis_label="Government Expenditure (%)",
            animate_axes=False,
        )

        ### Group to stack
        gdp_ax_vgroup = VGroup(gdp_ax, gdp_x_label, gdp_y_label)
        spend_ax_vgroup = VGroup(spend_ax, spend_x_label, spend_y_label)

        ### Stack the axes vertically and fit to screen
        stacked_plots_vgroup = VGroup(spend_ax_vgroup, gdp_ax_vgroup)
        stacked_plots_vgroup.arrange(UP, buff=1).scale_to_fit_height(6)
        
        ### Generate line plots and draw
        gdp_line_graph = gdp_ax.plot_line_graph(
            x_values=filtered_df["Year"],
            y_values=filtered_df["GDP per capita (OWiD)"],
            line_color=PURE_GREEN,
            add_vertex_dots=False,
        )
        spend_line_graph = spend_ax.plot_line_graph(
            x_values=filtered_df["Year"],
            y_values=filtered_df["Government Expenditure (IMF & Wiki)"],
            line_color=PURE_GREEN,
            add_vertex_dots=False,
        )

        ### Draw plots
        self.play(
            LaggedStart(
                Write(spend_line_graph, rate_func=rate_functions.ease_in_quad),
                Write(gdp_line_graph, rate_func=rate_functions.ease_in_quad),
                lag_ratio=0.25,
                run_time=6.5,
            )
        )
        self.wait()

        ### Move plots to left
        stacked_plots_vgroup += gdp_line_graph
        stacked_plots_vgroup += spend_line_graph
        self.play(stacked_plots_vgroup.animate.shift(LEFT*4.33))

        """ ### Draw composite axes to right
        comp_ax, comp_x_label, comp_y_label = self.generate_axes(
            x_range=[0, 81, 10],
            y_range=[-81, 81, 10],
            x_numbers_to_include=list(range(0, 81, 20)),
            y_numbers_to_include=list(range(-80, 81, 20)),
            x_axis_label="Average Government Expenditure (%)",
            y_axis_label="Increase in GDP per capita (%)",
            animate_axes=True,
        ) """

        ### Declare ValueTrackers and start it at lower values
        lower_vt = ValueTracker(1850)
        upper_vt = ValueTracker(1855)

        ### Create the line that connects the both graphs
        lower_projecting_line = always_redraw(
            lambda: DashedLine(
                color=YELLOW,
                end=gdp_ax.c2p(lower_vt.get_value(), 40),
                start=spend_ax.c2p(lower_vt.get_value(), 0),
            )
        )
        upper_projecting_line = always_redraw(
            lambda: DashedLine(
                color=YELLOW,
                end=gdp_ax.c2p(upper_vt.get_value(), 40),
                start=spend_ax.c2p(upper_vt.get_value(), 0),
            )
        )

        ### Write the projected lines to the scene
        self.play(
            Write(lower_projecting_line),
            Write(upper_projecting_line)
            )
        self.wait()

        ### Animate the value trackers incrementally
        for i in range(2020-1855):
            self.play(lower_vt.animate.set_value(1850+i), upper_vt.animate.set_value(1855+i), run_time=0.1)


    def generate_axes(
        self,
        x_range: list,
        y_range: list,
        x_numbers_to_include: list,
        y_numbers_to_include: list,
        animate_axes: bool,
        x_axis_label: str,
        y_axis_label: str,
    ):
        ax = make_axes(
            x_range=x_range,
            y_range=y_range,
            x_numbers_to_include=x_numbers_to_include,
            y_numbers_to_include=y_numbers_to_include,
        )
        ### Add axis labels
        x_label = ax.get_x_axis_label(Text(x_axis_label, font_size=26))
        y_label = ax.get_y_axis_label(Text(y_axis_label, font_size=26))

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
    """ df = get_spending_df()
    #filtered_df = df.loc[df["Country"] == "United Kingdom", :].reset_index(drop=True)
    filtered_df = df.reset_index(drop=True).sort_values(by=["GDP per capita (OWiD)"])
    print(filtered_df) """
    pass
