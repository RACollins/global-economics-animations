from manim import *
import pandas as pd
import os

###################
### Definitions ###
###################


cwd = os.getcwd()
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

def get_spend_gdp_df() -> pd.DataFrame:
    df = (
        pd.read_csv(cwd + "/data/spending_and_gdp_per_capita.csv")
        .drop(columns=["Unnamed: 0"])
        .sort_values(["Country", "Year"])
    )
    ### Convert to K$s
    df["GDP per capita (OWiD)"] = df["GDP per capita (OWiD)"].div(1000)
    return df


def get_avg_spend_change_gdp_df() -> pd.DataFrame:
    df = (
        pd.read_csv(cwd + "/data/average_spend_vs_change_in_gdp.csv")
        .drop(columns=["Unnamed: 0"])
    )
    return df

def add_radius_col(
    df: pd.DataFrame, lowest_radius: float, highest_radius: float
) -> pd.DataFrame:
    df["radius"] = (df["Population"] - df["Population"].min()) / (
        df["Population"].max() - df["Population"].min()
    ) * (highest_radius - lowest_radius) + lowest_radius
    return df



###############
### Classes ###
###############


#############
### Scene ###
#############


class SpendingAnimatedScene(Scene):

    def construct(self):
        ###################
        ### Definitions ###
        ###################

        x_min = ValueTracker(1850)

        #########################
        ### Functions & Scene ###
        #########################

        ### Load data for line graphs and put in DataFrame
        line_graphs_df = get_spend_gdp_df()
        uk_line_graphs_df = line_graphs_df.loc[line_graphs_df["Country"] == "United Kingdom", :].set_index("Year", drop=False)

        ### Make axis function and generate
        def make_ax():
            ax = Axes(
                 x_range=[x_min.get_value(), 2021, 10],
                 y_range=[0, 101, 10],
                 x_length=12,
                 y_length=6,
                 axis_config={
                      "color": WHITE,  # <- not needed if backgroud colour is default BLACK
                      "include_tip": False,
                      "include_numbers": False,
                      "decimal_number_config": {
                           "num_decimal_places": 0,
                           "group_with_commas": False,  # <- This removes the comma delimitation
                        },
                    },
                    x_axis_config={"numbers_to_include": list(range(1860, 2021, 20))},
                    y_axis_config={"numbers_to_include": list(range(0, 100, 20))},
            )
            return ax
        ax = make_ax()
        
        ### Define axis updater function and add to axis object
        def axis_updater(mob):
            old_ax = mob
            new_ax = make_ax()
            old_ax.become(new_ax)
            old_ax.x_axis.x_range = new_ax.x_axis.x_range
            old_ax.x_axis.scaling = new_ax.x_axis.scaling
            old_ax.y_axis.x_range = new_ax.y_axis.x_range
            old_ax.y_axis.scaling = new_ax.y_axis.scaling
        ax.add_updater(axis_updater)

        ### Make line function and generate line object
        line = ax.plot_line_graph(
            x_values=uk_line_graphs_df["Year"],
            y_values=uk_line_graphs_df["Government Expenditure (IMF & Wiki)"],
            line_color=PURE_GREEN,
            add_vertex_dots=False,
        )
        
        ### Define line updater function and add to line object
        def line_updater(mob):
            mob.become(
                ax.plot_line_graph(
                    x_values=uk_line_graphs_df["Year"],
                    y_values=uk_line_graphs_df["Government Expenditure (IMF & Wiki)"],
                    line_color=PURE_GREEN,
                    add_vertex_dots=False,
                )
            )
        line.add_updater(line_updater, index=1)
        
        ### Moment of truth!
        self.add(ax, line)
        self.play(x_min.animate.set_value(1991), run_time=5)

if __name__ == "__main__":
    """ df = get_spend_gdp_df().sort_values(by=["GDP per capita (OWiD)"], ascending=False)
    # filtered_df = df.loc[df["Country"] == "United Kingdom", :].reset_index(drop=True)
    print(df.head(40)) """
    pass