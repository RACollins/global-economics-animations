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


def make_axes(
    x_range: list,
    y_range: list,
    x_numbers_to_include: list,
    y_numbers_to_include: list,
    x_length: int,
    y_length: int,
):
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
        y_axis_config={"numbers_to_include": y_numbers_to_include},
    )
    return ax


###############
### Classes ###
###############


#############
### Scene ###
#############

q_0 = 3000
class Test(Scene):
    def construct(self):
        y_min, y_max = ValueTracker(0), ValueTracker(6000)
        y_tick_step = ValueTracker(2000)
        ax = always_redraw(lambda: Axes(
            x_range=[0, 60, 15],
            y_range=[y_min.get_value(), y_max.get_value(), y_tick_step.get_value()],
            tips=False,
            axis_config={"include_numbers": True}
        ))

        #base_flow_line = ax.plot(lambda t: q_0*t/60, color="blue")
        x_values = list(range(0, 61, 15))
        base_flow_line = ax.plot_line_graph(
            x_values=x_values,
            y_values=[q_0*x/60 for x in x_values],
            line_color=BLUE,
            add_vertex_dots=False,
        )

        self.add(ax)
        self.play(Create(base_flow_line))
        self.wait(3)

        #base_flow_line_xfrm = always_redraw(lambda: ax.plot(lambda t: 0, color="blue"))
        #base_flow_line_xfrm = ax.plot(lambda t: t*0, color="blue")
        base_flow_line_xfrm = ax.plot_line_graph(
            x_values=x_values,
            y_values=[0 for x in x_values],
            line_color=BLUE,
            add_vertex_dots=False,
        )
        self.play(Transform(base_flow_line, base_flow_line_xfrm))
        
        v_group = VGroup(ax, base_flow_line_xfrm)
        self.wait(2)

        self.play(y_min.animate.set_value(-300),
                  y_max.animate.set_value(300),
                  y_tick_step.animate.set_value(100))

        self.wait(5)

class SpendingVsGrowthAnimatedScene(Scene):

    def construct(self):

        ### Load data for line graphs and put in DataFrame
        line_graphs_df = get_spend_gdp_df()
        uk_line_graphs_df = line_graphs_df.loc[line_graphs_df["Country"] == "United Kingdom", :].set_index("Year", drop=False)
        de_line_graphs_df = line_graphs_df.loc[line_graphs_df["Country"] == "Germany", :].set_index("Year", drop=False)

        ### Load data for scatter plot
        scatter_df = get_avg_spend_change_gdp_df()
        uk_scatter_df = scatter_df.loc[scatter_df["Country"] == "United Kingdom", :]
        de_scatter_df = scatter_df.loc[scatter_df["Country"] == "Germany", :]

        ### Generate axes and labels for gdp and spend
        gdp_ax, gdp_x_label, gdp_y_label = self.generate_axes(
            x_range=[1850, 2021, 10],
            y_range=[4, 40, 1],
            x_numbers_to_include=list(range(1860, 2021, 20)),
            y_numbers_to_include=list(range(5, 40, 5)),
            animate_axes=False,
            x_axis_label="Year",
            y_axis_label="GDP per capita (kUSD)",
            font_size=26, 
            x_length=12,
            y_length=6,
        )
        spend_ax, spend_x_label, spend_y_label = self.generate_axes(
            x_range=[1850, 2021, 10],
            y_range=[0, 101, 10],
            x_numbers_to_include=list(range(1860, 2021, 20)),
            y_numbers_to_include=list(range(0, 100, 20)),
            animate_axes=False,
            x_axis_label="Year",
            y_axis_label="Government Expenditure (%)",
            font_size=26, 
            x_length=12,
            y_length=6,
        )

        ### Group to stack
        gdp_ax_vgroup = VGroup(gdp_ax, gdp_x_label, gdp_y_label)
        spend_ax_vgroup = VGroup(spend_ax, spend_x_label, spend_y_label)

        ### Stack the axes vertically and fit to screen
        stacked_plots_vgroup = VGroup(spend_ax_vgroup, gdp_ax_vgroup)
        stacked_plots_vgroup.arrange(UP, buff=1).scale_to_fit_height(6)
        
        ### Generate line plots and draw
        gdp_line_graph = gdp_ax.plot_line_graph(
            x_values=uk_line_graphs_df["Year"],
            y_values=uk_line_graphs_df["GDP per capita (OWiD)"],
            line_color=PURE_GREEN,
            add_vertex_dots=False,
        )
        spend_line_graph = spend_ax.plot_line_graph(
            x_values=uk_line_graphs_df["Year"],
            y_values=uk_line_graphs_df["Government Expenditure (IMF & Wiki)"],
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

        ### Add line plots to stacked vgroups and move to left
        stacked_plots_vgroup += gdp_line_graph
        stacked_plots_vgroup += spend_line_graph
        self.play(stacked_plots_vgroup.animate.shift(LEFT*4.33))

        ### Draw composite axes to right
        comp_ax, comp_x_label, comp_y_label = self.generate_axes(
            x_range=[0, 81, 10],
            y_range=[-81, 81, 10],
            x_numbers_to_include=list(range(0, 81, 20)),
            y_numbers_to_include=list(range(-80, 81, 20)),
            animate_axes=True,
            x_axis_label="Average Government Expenditure (%)",
            y_axis_label="Increase in GDP per capita (%)",
            font_size=14, 
            x_length=14,
            y_length=12,
            position=2.0,
            scale=0.5,
        )

        ### Declare ValueTrackers and start it at 1936
        initial_start_year = 1936
        initial_end_year = 1941
        lower_vt = ValueTracker(initial_start_year)
        upper_vt = ValueTracker(initial_end_year)

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
        ### Define point corresponding to demo calculation
        demo_dot = always_redraw(
            lambda: Dot(
                comp_ax.coords_to_point(
                    *self.years_to_coords(
                        uk_scatter_df,
                        round(lower_vt.get_value()),
                        round(upper_vt.get_value()),
                    )
                ),
                color=PURE_GREEN,
                radius=0.05,
                fill_opacity=0.85,
            )
        )

        ### Write the projected lines and demo point to the scene
        self.play(
            Write(lower_projecting_line, run_time=1.0),
            Write(upper_projecting_line, run_time=1.0),
            Write(demo_dot, run_time=1.0),
            )
        self.wait()

        ### Two further demo points by changing value trackers
        self.play(lower_vt.animate.set_value(1979), upper_vt.animate.set_value(1984), run_time=2.5)
        self.wait(1)
        self.play(lower_vt.animate.set_value(1916), upper_vt.animate.set_value(1921), run_time=3.5)
        self.wait(1)
        self.play(lower_vt.animate.set_value(1850), upper_vt.animate.set_value(1855), run_time=2.5)


        ### Animate the value trackers incrementally
        for i in range(2019-1855):
            self.play(lower_vt.animate.increment_value(1), upper_vt.animate.increment_value(1), run_time=0.05)
            self.add(
                Dot(
                    comp_ax.coords_to_point(
                        *self.years_to_coords(
                            uk_scatter_df,
                            round(lower_vt.get_value()),
                            round(upper_vt.get_value()),
                        )
                    ),
                    color=PURE_GREEN,
                    radius=0.05,
                    fill_opacity=0.5,
                )
            )

    def years_to_coords(
            self,
            df: pd.DataFrame,
            start_year: int,
            end_year: int
    ) -> list[float, float]:
        coords = df.loc[
            (df["start_year"] == start_year) & (df["end_year"] == end_year),
            ["Average Government Expenditure as % of GDP", "Percentage change in GDP per capita USD"]
        ].values[0]
        return coords

    def generate_axes(
        self,
        x_range: list,
        y_range: list,
        x_numbers_to_include: list,
        y_numbers_to_include: list,
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
            x_length=x_length,
            y_length=y_length,
        )

        if position:
            ax = ax.move_to(RIGHT*position)
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
    """ df = get_avg_spend_change_gdp_df()
    filtered_df = df.loc[df["Country"] == "United Kingdom", :].reset_index(drop=True)
    print(filtered_df) """
    pass
