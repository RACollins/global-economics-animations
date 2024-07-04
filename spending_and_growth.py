from manim import *
import pandas as pd
import os
import random
np.random.seed(37)

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
    #df["GDP per capita (OWiD)"] = df["GDP per capita (OWiD)"].div(1000)
    return df


def get_avg_spend_change_gdp_df() -> pd.DataFrame:
    df = (
        pd.read_csv(cwd + "/data/average_spend_vs_change_in_gdp.csv")
        .drop(columns=["Unnamed: 0"])
    )
    return df

def get_avg_spend_avg_change_gdp_df() -> pd.DataFrame:
    df = (
        pd.read_csv(cwd + "/data/average_spend_vs_average_change_in_gdp.csv")
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

def make_country_to_colour_map(df: pd.DataFrame) -> dict:
    df_copy = df.copy()
    df_copy["colour"] = df_copy["Region"].map(colour_map)
    country_to_colour_map = dict(zip(df_copy["Country"], df_copy["colour"]))
    return country_to_colour_map


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
        y_axis_config={
            "numbers_to_include": y_numbers_to_include,
            "scaling": LogBase(custom_labels=True)
        }
    else:
        y_axis_config={"numbers_to_include": y_numbers_to_include}
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
        y_axis_config=y_axis_config,
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
        ### Demo country
        demo_country = "United Kingdom"
        excluded_countries = [
            "Kuwait",
            "Qatar",
            "Equatorial Guinea",
            "Bulgaria",
            "Azerbaijan",
            "Hungary",
            "Qatar",
            "Angola"
        ]

        ### Load data for line graphs and put in DataFrame
        line_graphs_df = get_spend_gdp_df()
        uk_line_graphs_df = line_graphs_df.loc[line_graphs_df["Country"] == demo_country, :].set_index("Year", drop=False)

        ### Load data for scatter plot
        scatter_df = get_avg_spend_avg_change_gdp_df()
        uk_scatter_df = scatter_df.loc[scatter_df["Country"] == demo_country, :]

        ### Colour mapping dict
        country_to_colour_map = make_country_to_colour_map(scatter_df)

        ### Generate axes and labels for gdp and spend
        gdp_ax, gdp_x_label, gdp_y_label = self.generate_axes(
            x_range=[1850, 2021, 10],
            y_range=[2, 5.1, 1],
            x_numbers_to_include=list(range(1860, 2021, 20)),
            y_numbers_to_include=list(range(2, 6, 1)),
            log_y=True,
            animate_axes=False,
            x_axis_label="Year",
            y_axis_label="GDP per capita (USD)",
            font_size=26, 
            x_length=12,
            y_length=6,
        )
        spend_ax, spend_x_label, spend_y_label = self.generate_axes(
            x_range=[1850, 2021, 10],
            y_range=[0, 101, 10],
            x_numbers_to_include=list(range(1860, 2021, 20)),
            y_numbers_to_include=list(range(0, 100, 20)),
            log_y=False,
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
            line_color=country_to_colour_map[demo_country],
            add_vertex_dots=False,
            stroke_width=2,
        )
        spend_line_graph = spend_ax.plot_line_graph(
            x_values=uk_line_graphs_df["Year"],
            y_values=uk_line_graphs_df["Government Expenditure (IMF & Wiki)"],
            line_color=country_to_colour_map[demo_country],
            add_vertex_dots=False,
            stroke_width=2,
        )

        ### Draw plots
        self.play(
            LaggedStart(
                Write(spend_line_graph),
                Write(gdp_line_graph),
                lag_ratio=0.25,
                run_time=6.5,
                rate_func=rate_functions.ease_in_quad,
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
            y_range=[-16, 31, 5],
            x_numbers_to_include=list(range(0, 81, 10)),
            y_numbers_to_include=list(range(-15, 31, 5)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Average Government Expenditure (%)",
            y_axis_label="Average change in GDP per capita (%)",
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
                end=gdp_ax.c2p(lower_vt.get_value(), 10e4),
                start=spend_ax.c2p(lower_vt.get_value(), 0),
            )
        )
        upper_projecting_line = always_redraw(
            lambda: DashedLine(
                color=YELLOW,
                end=gdp_ax.c2p(upper_vt.get_value(), 10e4),
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
                color=country_to_colour_map[demo_country],
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

        ### Uncomment for real video, although probably not needed now!
        """ ### Animate the value trackers incrementally
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
                    color=country_to_colour_map[demo_country],
                    radius=0.05,
                    fill_opacity=0.5,
                )
            ) """
        
        ### Generate list of dots and add to scene while value tracker changes
        demo_dots_list = []
        for lower_bound in list(range(1850, 2015)):
            upper_bound = lower_bound + 5
            demo_dots_list.append(
                Dot(
                    comp_ax.coords_to_point(
                        *self.years_to_coords(
                            uk_scatter_df,
                            lower_bound,
                            upper_bound,
                        )
                    ),
                    color=country_to_colour_map[demo_country],
                    radius=0.05,
                    fill_opacity=0.3,
                )
            )
        self.play(
            lower_vt.animate.set_value(2014),
            upper_vt.animate.set_value(2019),
            LaggedStart(
                *[Create(d) for d in demo_dots_list],
                lag_ratio=5.0,
                rate_func=rate_functions.linear,
            ),
            run_time=15.0,
            rate_func=rate_functions.linear
        )
        
        ### Unwrite the projected lines and demo point from the scene
        self.play(
            Unwrite(lower_projecting_line, run_time=1.0),
            Unwrite(upper_projecting_line, run_time=1.0),
            Unwrite(demo_dot, run_time=1.0),
            )
        
        ### Find countries within graph limits
        all_countries = np.union1d(scatter_df["Country"].unique(), line_graphs_df["Country"].unique())

        ### Draw all country lines on left plots
        gdp_lines_dict, spend_lines_dict = {}, {}
        for country in all_countries:
            if country in excluded_countries:
                continue
            country_lines_graph_df = (line_graphs_df
                                      .loc[line_graphs_df["Country"] == country, :]
                                      .set_index("Year", drop=False))
            
            gdp_lines_dict[country] = gdp_ax.plot_line_graph(
                x_values=country_lines_graph_df["Year"],
                y_values=country_lines_graph_df["GDP per capita (OWiD)"],
                line_color=country_to_colour_map[country],
                add_vertex_dots=False,
                stroke_width=1,
            )
            spend_lines_dict[country] = spend_ax.plot_line_graph(
                x_values=country_lines_graph_df["Year"],
                y_values=country_lines_graph_df["Government Expenditure (IMF & Wiki)"],
                line_color=country_to_colour_map[country],
                add_vertex_dots=False,
                stroke_width=1,
            )
        
        ### Transform UK line to thinner line
        self.play(
            Transform(spend_line_graph, spend_lines_dict[demo_country]),
            Transform(gdp_line_graph, gdp_lines_dict[demo_country]),
            run_time=1,
        )
        self.wait()

        ### Generate line plots randomly
        random_line_plots = np.random.choice(
            [Write(slg) for k, slg in spend_lines_dict.items()] + [Write(gdplg) for k, gdplg in gdp_lines_dict.items()],
            (len(all_countries)-len(excluded_countries))*2, # <- ignoring excluded countries
            replace=False,
        )

        ### Plot lines
        self.play(
            LaggedStart(
                *random_line_plots,
                lag_ratio=0.05,
                run_time=6.5,
                rate_func=rate_functions.smooth
            )
        )
        self.wait()

        ### Re-declare ValueTrackers and start it at 1850
        initial_start_year = 1850
        initial_end_year = 1855
        lower_vt = ValueTracker(initial_start_year)
        upper_vt = ValueTracker(initial_end_year)

        ### Create the line that connects the both graphs, again!
        lower_projecting_line = always_redraw(
            lambda: DashedLine(
                color=YELLOW,
                end=gdp_ax.c2p(lower_vt.get_value(), 10e4),
                start=spend_ax.c2p(lower_vt.get_value(), 0),
            )
        )
        upper_projecting_line = always_redraw(
            lambda: DashedLine(
                color=YELLOW,
                end=gdp_ax.c2p(upper_vt.get_value(), 10e4),
                start=spend_ax.c2p(upper_vt.get_value(), 0),
            )
        )

        ### Generate dict of dots for all countries
        country_dots_dict = {}
        for country in all_countries:
            if country in excluded_countries or country == "United Kingdom":
                continue
            country_scatter_df = scatter_df.loc[scatter_df["Country"] == country, :]
            dots_list = []
            for lower_bound in list(range(1850, 2015)):
                upper_bound = lower_bound + 5
                try:
                    coords = self.years_to_coords(
                        country_scatter_df,
                        lower_bound,
                        upper_bound,
                    )
                    alpha = 0.3
                except IndexError:
                    coords = [0.0, 0.0]
                    alpha = 0.0
                    #continue
                dots_list.append(
                    Dot(
                        comp_ax.coords_to_point(*coords),
                        color=country_to_colour_map[country],
                        radius=0.05,
                        fill_opacity=alpha,
                    )
                )
            country_dots_dict[country] = dots_list

        ### Create initial dots
        initial_dots = [Write(dots_list[0], run_time=1.0) for country, dots_list in country_dots_dict.items()]

        ### Write the projected lines and initial dots to the scene
        self.play(
            Write(lower_projecting_line, run_time=1.0),
            Write(upper_projecting_line, run_time=1.0),
            *initial_dots,
            )
        self.wait()
        
        ### Animate vertical lines and plot dots on right scatter graph
        ### Will take long time to render!
        lagged_start_list = [
            LaggedStart(
                *[Create(d) for d in dots_list],
                lag_ratio=5.0,
                rate_func=rate_functions.linear,
            ) for country, dots_list in country_dots_dict.items()
        ]
        self.play(
            lower_vt.animate.set_value(2014),
            upper_vt.animate.set_value(2019),
            *lagged_start_list,
            run_time=15.0,
            rate_func=rate_functions.linear
        )

        ### Unwrite the projected lines
        self.play(
            Unwrite(lower_projecting_line, run_time=1.0),
            Unwrite(upper_projecting_line, run_time=1.0),
            )

        

    def years_to_coords(
            self,
            df: pd.DataFrame,
            start_year: int,
            end_year: int
    ) -> list[float, float]:
        coords = df.loc[
            (df["start_year"] == start_year) & (df["end_year"] == end_year),
            ["Average Government Expenditure as % of GDP", "Average percentage change in GDP per capita USD"]
        ].values[0]
        return coords

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
