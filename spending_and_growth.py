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

def make_axes():
    ax = Axes(
        x_range=[1850, 2020, 20],
        y_range=[0, 100, 10],
        axis_config={
            "color": WHITE,   # <- not needed if backgroud colour is default BLACK
            "include_tip": False,
            "include_numbers": True
        },
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
       #self.generate_timeseries_plot(animate_axes=True)
        self.generate_line_plot(animate_axes=True)
        self.wait(2)
    
    def generate_line_plot(self, animate_axes: bool):
        ### Download data and put in DataFrame
        df = get_spending_df()
        filtered_df = df.loc[df["Country"] == "United Kingdom", :].set_index("Year", drop=False)
        ax = make_axes()
        ### Add axis labels
        x_label = ax.get_x_axis_label(Text("Year", font_size=26))
        y_label = ax.get_y_axis_label(Text("Government Expenditure (%)", font_size=26))

        line_graph = ax.plot_line_graph(
            x_values = filtered_df["Year"],
            y_values = filtered_df["Government Expenditure (IMF & Wiki)"],
            line_color=PURE_GREEN,
            add_vertex_dots=False,
        )

        if animate_axes:
            ### Animate the creation of Axes
            self.play(Write(ax))
            self.play(Write(x_label))
            self.play(Write(y_label))
            self.play(Write(line_graph, rate_func=rate_functions.ease_in_expo))
            #self.play(Write(title))
            self.wait()  # wait for 1 second

        return ax

    def generate_timeseries_plot(self, animate_axes: bool):
        ### Download data and put in DataFrame
        df = get_spending_df()
        filtered_df = df.loc[df["Country"] == "United Kingdom", :].set_index("Year", drop=False)
        ax = make_axes()
        ### Add axis labels
        x_label = ax.get_x_axis_label(Text("Year", font_size=26))
        y_label = ax.get_y_axis_label(Text("Government Expenditure (%)", font_size=26))
        ### Add title
        #title = Text(r"{}".format(" ".join([s.capitalize() for s in job.split("_")])), font_size=30)
        #title.to_edge(UP)
        ts = ax.plot(
            lambda x: filtered_df.loc[x, "Government Expenditure (IMF & Wiki)"],
            x_range=[1850, 2020, 1],
            color=PURE_GREEN,
            )
        
        if animate_axes:
            ### Animate the creation of Axes
            self.play(Write(ax))
            self.play(Write(x_label))
            self.play(Write(y_label))
            self.play(Write(ts, rate_func=rate_functions.ease_in_expo))
            #self.play(Write(title))
            self.wait()  # wait for 1 second

        return ax


if __name__ == "__main__":
    """ df = get_spending_df()
    filtered_df = df.loc[df["Country"] == "United Kingdom", :].reset_index(drop=True)
    print(filtered_df) """
    pass
