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

        ### Download data and put in DataFrame
        df = get_spending_df()
        filtered_df = df.loc[df["Country"] == "United Kingdom", :].set_index("Year", drop=False)

        ### Generate axes and labels for gdp and spend
        gdp_ax, gdp_x_label, gdp_y_label = self.generate_axes(
            x_range=[1850, 2021, 10],
            y_range=[4000, 40001, 1000],
            x_numbers_to_include=list(range(1860, 2021, 20)),
            y_numbers_to_include=list(range(5000, 40001, 5000)),
            y_axis_label="GDP per capita",
            animate_axes=False,
        )
        spend_ax, spend_x_label, spend_y_label = self.generate_axes(
            x_range=[1850, 2021, 10],
            y_range=[0, 101, 10],
            x_numbers_to_include=list(range(1860, 2021, 20)),
            y_numbers_to_include=list(range(0, 101, 20)),
            y_axis_label="Government Expenditure (%)",
            animate_axes=False,
        )

        ### Group to stack
        gdp_ax_vgroup = VGroup(gdp_ax, gdp_x_label, gdp_y_label)
        spend_ax_vgroup = VGroup(spend_ax, spend_x_label, spend_y_label)

        ### Stack the axes vertically and fit to screen
        stacked_plots_vgroup = VGroup(gdp_ax_vgroup, spend_ax_vgroup)
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
        self.play(Write(gdp_line_graph, rate_func=rate_functions.ease_in_expo))
        self.wait(2)
        self.play(Write(spend_line_graph, rate_func=rate_functions.ease_in_expo))
        self.wait(2)



    def generate_axes(
        self,
        x_range: list,
        y_range: list,
        x_numbers_to_include: list,
        y_numbers_to_include: list,
        animate_axes: bool,
        y_axis_label: str,
    ):
        ax = make_axes(
            x_range=x_range,
            y_range=y_range,
            x_numbers_to_include=x_numbers_to_include,
            y_numbers_to_include=y_numbers_to_include,
        )
        ### Add axis labels
        x_label = ax.get_x_axis_label(Text("Year", font_size=26))
        y_label = ax.get_y_axis_label(Text(y_axis_label, font_size=26))

        if animate_axes:
            ### Animate the creation of Axes
            self.play(Write(ax))
            self.play(Write(x_label))
            self.play(Write(y_label))
            # self.play(Write(line_graph, rate_func=rate_functions.ease_in_expo))
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
