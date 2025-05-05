from manim import *
import pandas as pd
import os
import numpy as np
from utils import (
    get_scatter_df,
    create_country_group,
    add_binned_columns,
    add_kmeans_clusters,
)

### Uncomment when switching to WHITE background
config.background_color = WHITE

### Set default color for common objects
Line.set_default(color=BLACK)
Text.set_default(color=BLACK)
Axes.set_default(color=BLACK)

np.random.seed(37)

###################
### Definitions ###
###################

cwd = os.getcwd()
colour_map = {
    "Asia": XKCD.FADEDRED,
    "Americas": XKCD.BUBBLEGUM,
    "Africa": XKCD.AMBER,
    "Europe": XKCD.ALGAEGREEN,
    "Oceania": XKCD.RICHBLUE,
    "G7": XKCD.AZURE,
    "World": XKCD.AZURE,
}

### Between 10s
""" bin_groups = {
    5.0: [0.0, 10.0],
    15.0: [10.0, 20.0],
    25.0: [20.0, 30.0],
    35.0: [30.0, 40.0],
    45.0: [40.0, 50.0],
} """

### On 10s
bin_groups = {
    0.0: [0.0, 5.0],
    10.0: [5.0, 15.0],
    20.0: [15.0, 25.0],
    30.0: [25.0, 35.0],
    40.0: [35.0, 45.0],
    50.0: [45.0, 50.0],
}

#################
### Functions ###
#################


### Line graphs
def get_spend_gdp_df() -> pd.DataFrame:
    df = (
        pd.read_csv(cwd + "/data/spending_and_gdp_per_capita.csv")
        .drop(columns=["Unnamed: 0"])
        .sort_values(["Country", "Year"])
    )
    return df


def get_spend_gdp_debt_adjusted_df() -> pd.DataFrame:
    df = pd.read_csv(
        cwd + "/data/spending_and_gdp_per_capita_debt_adjusted.csv"
    ).sort_values(["Country", "Year"])
    return df


def get_region_avg_spend_gdp_df() -> pd.DataFrame:
    df = pd.read_csv(
        cwd + "/data/region_average_spending_and_gdp_per_capita.csv"
    ).sort_values(["Country", "Year"])
    return df


def get_region_avg_spend_gdp_debt_adjusted_df() -> pd.DataFrame:
    df = pd.read_csv(
        cwd + "/data/region_average_spending_and_gdp_per_capita_debt_adjusted.csv"
    ).sort_values(["Country", "Year"])
    return df


### Scatter graphs
def get_avg_spend_avg_change_gdp_df() -> pd.DataFrame:
    df = pd.read_csv(cwd + "/data/average_spend_vs_average_change_in_gdp.csv").drop(
        columns=["Unnamed: 0"]
    )
    return df


def get_avg_spend_avg_change_gdp_debt_adjusted_df() -> pd.DataFrame:
    df = pd.read_csv(
        cwd + "/data/average_spend_vs_average_change_in_gdp_debt_adjusted.csv"
    ).drop(columns=["Unnamed: 0"])
    return df


def get_avg_spend_ann_change_gdp_df() -> pd.DataFrame:
    df = pd.read_csv(cwd + "/data/average_spend_vs_annualized_change_in_gdp.csv").drop(
        columns=["Unnamed: 0"]
    )
    return df


def get_avg_spend_ann_change_gdp_debt_adjusted_df() -> pd.DataFrame:
    df = pd.read_csv(
        cwd + "/data/average_spend_vs_annualized_change_in_gdp_debt_adjusted.csv"
    ).drop(columns=["Unnamed: 0"])
    return df


def get_rgn_avg_spend_rgn_avg_change_gdp_df() -> pd.DataFrame:
    df = pd.read_csv(
        cwd + "/data/region_average_spend_vs_region_average_change_in_gdp.csv"
    ).drop(columns=["Unnamed: 0"])
    return df


def get_rgn_avg_spend_rgn_avg_change_gdp_debt_adjusted_df() -> pd.DataFrame:
    df = pd.read_csv(
        cwd
        + "/data/region_average_spend_vs_region_average_change_in_gdp_debt_adjusted.csv"
    ).drop(columns=["Unnamed: 0"])
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

#############
### Scene ###
#############


class SpendingVsGrowthAnimatedScene(Scene):

    def construct(self):
        ### Demo country
        demo_country = "United Kingdom"
        focus_countries = ["United States", "Japan", "G7"]
        excluded_countries = [
            "Kuwait",
            "Qatar",
            "Equatorial Guinea",
            "Bulgaria",
            "Azerbaijan",
            "Hungary",
            "Angola",
        ]

        ### Load data for line graphs and put in DataFrame
        line_graphs_df = get_spend_gdp_df()
        line_graphs_debt_adjusted_df = get_spend_gdp_debt_adjusted_df()
        uk_line_graphs_debt_adjusted_df = line_graphs_debt_adjusted_df.loc[
            line_graphs_debt_adjusted_df["Country"] == demo_country, :
        ].set_index("Year", drop=False)
        ### Don't bother calculating, just import from dashboard data
        """ avg_line_graphs_df = make_region_avg_df(line_graphs_df, weight_pop=True)
        avg_line_graphs_debt_adjusted_df = make_region_avg_df(line_graphs_debt_adjusted_df, weight_pop=True) """
        ### Don't even do that, because we're not doing all Euopean countries now
        """ avg_line_graphs_df = get_region_avg_spend_gdp_df()
        avg_line_graphs_debt_adjusted_df = get_region_avg_spend_gdp_debt_adjusted_df() """
        ### Add G7 countriesto the line graph data
        g7_countries = [
            "United States",
            "Canada",
            "United Kingdom",
            "Germany",
            "France",
            "Italy",
            "Japan",
        ]
        new_country_names = ["G7"]
        new_region_names = ["World"]
        for i, country_list in enumerate([g7_countries]):
            line_graphs_df = create_country_group(
                line_graphs_df,
                countries=country_list,
                new_country_name=new_country_names[i],
                new_region_name=new_region_names[i],
                weight_pop=True,
            )
            line_graphs_debt_adjusted_df = create_country_group(
                line_graphs_debt_adjusted_df,
                countries=country_list,
                new_country_name=new_country_names[i],
                new_region_name=new_region_names[i],
                weight_pop=True,
            )

        ### Load data for scatter plot
        scatter_df = get_avg_spend_ann_change_gdp_df()
        uk_scatter_df = scatter_df.loc[scatter_df["Country"] == demo_country, :]
        scatter_debt_adjusted_df = get_avg_spend_ann_change_gdp_debt_adjusted_df()
        uk_scatter_debt_adjusted_df = scatter_debt_adjusted_df.loc[
            scatter_debt_adjusted_df["Country"] == demo_country, :
        ]
        ### Calculate scatter data for G7
        rgn_avg_scatter_df = get_scatter_df(
            line_graphs_df, long_range=[1850, 2022], sub_period=5
        )
        rgn_avg_debt_adjusted_scatter_df = get_scatter_df(
            line_graphs_debt_adjusted_df, long_range=[1850, 2022], sub_period=5
        )

        ### Colour mapping dict
        country_to_colour_map = make_country_to_colour_map(scatter_df)

        ### Generate axes and labels for gdp and spend
        gdp_ax, gdp_x_label, gdp_y_label = self.generate_axes(
            x_range=[1840, 2023, 20],
            y_range=[3, 5, 1],
            x_numbers_to_include=list(range(1860, 2023, 20)),
            y_numbers_to_include=list(range(3, 6, 1)),
            log_y=True,
            animate_axes=False,
            x_axis_label="Year",
            y_axis_label="GDP per capita (USD)",
            font_size=26,
            x_length=12,
            y_length=6,
        )
        spend_ax, spend_x_label, spend_y_label = self.generate_axes(
            x_range=[1840, 2023, 20],
            y_range=[0, 101, 10],
            x_numbers_to_include=list(range(1860, 2023, 20)),
            y_numbers_to_include=list(range(0, 100, 20)),
            log_y=False,
            animate_axes=False,
            x_axis_label="Year",
            y_axis_label="Gover nment Expenditure (%)",
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
            x_values=uk_line_graphs_debt_adjusted_df["Year"],
            y_values=uk_line_graphs_debt_adjusted_df["GDP per capita (OWiD)"],
            line_color=country_to_colour_map[demo_country],
            add_vertex_dots=False,
            stroke_width=2,
        )
        spend_line_graph = spend_ax.plot_line_graph(
            x_values=uk_line_graphs_debt_adjusted_df["Year"],
            y_values=uk_line_graphs_debt_adjusted_df[
                "Government Expenditure (IMF, Wiki, Statistica)"
            ],
            line_color=country_to_colour_map[demo_country],
            add_vertex_dots=False,
            stroke_width=2,
        )

        # Create the "United Kingdom" text
        uk_text = Text("United Kingdom", font_size=14, color=BLACK)
        uk_text.move_to(gdp_ax.c2p(2010, 1e5))  # Adjusted to top right of gdp_ax

        ### Draw plots and text
        self.play(
            Write(
                spend_line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad
            ),
            Write(gdp_line_graph, run_time=6.5, rate_func=rate_functions.ease_in_quad),
            Write(uk_text, run_time=1.0),
        )
        self.wait()

        ### Add line plots and text to stacked vgroups and move to left
        stacked_plots_vgroup += gdp_line_graph
        stacked_plots_vgroup += spend_line_graph
        stacked_plots_vgroup += uk_text
        self.play(stacked_plots_vgroup.animate.shift(LEFT * 4.33))

        ### Draw composite axes to right
        comp_ax, comp_x_label, comp_y_label = self.generate_axes(
            x_range=[0, 81, 10],
            y_range=[-11, 16, 5],
            x_numbers_to_include=list(range(0, 81, 10)),
            y_numbers_to_include=list(range(-10, 16, 5)),
            log_y=False,
            animate_axes=True,
            x_axis_label="Average Gover nment Expenditure (%)",
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
                color=XKCD.YELLOW,
                end=gdp_ax.c2p(lower_vt.get_value(), 100e3),
                start=spend_ax.c2p(lower_vt.get_value(), 0),
            )
        )
        upper_projecting_line = always_redraw(
            lambda: DashedLine(
                color=XKCD.YELLOW,
                end=gdp_ax.c2p(upper_vt.get_value(), 100e3),
                start=spend_ax.c2p(upper_vt.get_value(), 0),
            )
        )
        ### Define point corresponding to demo calculation
        demo_dot = always_redraw(
            lambda: Dot(
                comp_ax.coords_to_point(
                    *self.years_to_coords(
                        uk_scatter_debt_adjusted_df,
                        round(lower_vt.get_value()),
                        round(upper_vt.get_value()),
                    )
                ),
                color=country_to_colour_map[demo_country],
                radius=0.05,
                fill_opacity=0.85,
            )
        )
        ### Create year range display
        year_text_range = always_redraw(
            lambda: Text(
                f"{int(lower_vt.get_value())} - {int(upper_vt.get_value())}",
                font_size=14,
                color=BLACK,
            ).move_to(
                comp_ax.c2p(70, -10)
            )  # Position in bottom right corner
        )

        ### Write the projected lines and demo point to the scene
        self.play(
            Write(lower_projecting_line, run_time=1.0),
            Write(upper_projecting_line, run_time=1.0),
            Write(demo_dot, run_time=1.0),
            Write(year_text_range, run_time=1.0),
        )
        self.wait()

        ### Two further demo points by changing value trackers
        self.play(
            lower_vt.animate.set_value(1979),
            upper_vt.animate.set_value(1984),
            run_time=1.75,
        )
        self.wait(1)
        self.play(
            lower_vt.animate.set_value(1916),
            upper_vt.animate.set_value(1921),
            run_time=2.75,
        )
        self.wait(1)
        self.play(
            lower_vt.animate.set_value(1850),
            upper_vt.animate.set_value(1855),
            run_time=1.75,
        )

        ### Generate list of dots and add to scene while value tracker changes
        demo_dots_list = []
        for lower_bound in list(range(1850, 2018)):
            upper_bound = lower_bound + 5
            demo_dots_list.append(
                Dot(
                    comp_ax.coords_to_point(
                        *self.years_to_coords(
                            uk_scatter_debt_adjusted_df,
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
            lower_vt.animate.set_value(2017),
            upper_vt.animate.set_value(2022),
            LaggedStart(
                *[Create(d) for d in demo_dots_list],
                lag_ratio=5.0,
                rate_func=rate_functions.linear,
            ),
            run_time=15.0,
            rate_func=rate_functions.linear,
        )

        ### Unwrite the projected lines and demo point from the scene
        self.play(
            Unwrite(lower_projecting_line, run_time=1.0),
            Unwrite(upper_projecting_line, run_time=1.0),
            Unwrite(demo_dot, run_time=1.0),
        )
        self.wait()

        ### Remove UK lines, dots and text
        self.play(
            Unwrite(spend_line_graph),
            Unwrite(gdp_line_graph),
            Unwrite(uk_text),
            *[Unwrite(d) for d in demo_dots_list],
            run_time=1,
        )
        self.wait()

        ### Do the same animation for selected countries
        for fc, focus_country in enumerate(focus_countries):
            if focus_country in ["G7"]:
                fc_scatter_debt_adjusted_df = rgn_avg_debt_adjusted_scatter_df.copy()
                cmap = colour_map
            else:
                fc_scatter_debt_adjusted_df = scatter_debt_adjusted_df.copy()
                cmap = country_to_colour_map

            fc_line_graphs_debt_adjusted_df = line_graphs_debt_adjusted_df.copy()

            ### Create dfs for line plots
            fc_line_graphs_debt_adjusted_df = fc_line_graphs_debt_adjusted_df.loc[
                fc_line_graphs_debt_adjusted_df["Country"] == focus_country, :
            ].set_index("Year", drop=False)

            ### Create dfs for scatter plots
            fc_scatter_debt_adjusted_df = fc_scatter_debt_adjusted_df.loc[
                fc_scatter_debt_adjusted_df["Country"] == focus_country, :
            ]

            ### Generate line plots and draw
            gdp_line_graph = gdp_ax.plot_line_graph(
                x_values=fc_line_graphs_debt_adjusted_df["Year"],
                y_values=fc_line_graphs_debt_adjusted_df["GDP per capita (OWiD)"],
                line_color=cmap[focus_country],
                add_vertex_dots=False,
                stroke_width=2,
            )
            spend_line_graph = spend_ax.plot_line_graph(
                x_values=fc_line_graphs_debt_adjusted_df["Year"],
                y_values=fc_line_graphs_debt_adjusted_df[
                    "Government Expenditure (IMF, Wiki, Statistica)"
                ],
                line_color=cmap[focus_country],
                add_vertex_dots=False,
                stroke_width=2,
            )

            # Create the "Focus Country" text
            fc_text = Text(focus_country, font_size=14, color=BLACK)
            fc_text.move_to(gdp_ax.c2p(2012, 1e5))  # Adjusted to top right of gdp_ax

            ### Draw plots and text
            draw_country_lines_randomly = True
            if focus_country == "G7" and draw_country_lines_randomly:
                ### Draw all country lines on left plots
                gdp_lines_dict, spend_lines_dict = {}, {}
                for country in g7_countries:
                    if country in excluded_countries:
                        continue
                    country_lines_graph_df = line_graphs_debt_adjusted_df.loc[
                        line_graphs_debt_adjusted_df["Country"] == country, :
                    ].set_index("Year", drop=False)

                    gdp_lines_dict[country] = gdp_ax.plot_line_graph(
                        x_values=country_lines_graph_df["Year"],
                        y_values=country_lines_graph_df["GDP per capita (OWiD)"],
                        line_color=country_to_colour_map[country],
                        add_vertex_dots=False,
                        stroke_width=1,
                    )
                    spend_lines_dict[country] = spend_ax.plot_line_graph(
                        x_values=country_lines_graph_df["Year"],
                        y_values=country_lines_graph_df[
                            "Government Expenditure (IMF, Wiki, Statistica)"
                        ],
                        line_color=country_to_colour_map[country],
                        add_vertex_dots=False,
                        stroke_width=1,
                    )

                ### Generate line plots randomly
                random_line_plots = np.random.choice(
                    [Write(slg) for k, slg in spend_lines_dict.items()]
                    + [Write(gdplg) for k, gdplg in gdp_lines_dict.items()],
                    len(g7_countries) * 2,  # <-- one for each gdp and spend line
                    replace=False,
                )

                ### Plot lines
                self.play(
                    LaggedStart(
                        *random_line_plots,
                        lag_ratio=0.0,
                        run_time=2.5,
                        rate_func=rate_functions.smooth,
                    ),
                    Write(fc_text, run_time=1.0),
                )
                self.wait()

                ### Transform random lines to weighted mean line
                to_avg_transforms = []
                for country in g7_countries:
                    if country in excluded_countries:
                        continue
                    to_avg_transforms.append(
                        Transform(gdp_lines_dict[country], gdp_line_graph)
                    )
                    to_avg_transforms.append(
                        Transform(spend_lines_dict[country], spend_line_graph)
                    )
                self.play(
                    *to_avg_transforms,
                    run_time=1,
                )
                self.wait()
            else:
                self.play(
                    Write(
                        spend_line_graph,
                        run_time=2.5,
                        rate_func=rate_functions.ease_in_quad,
                    ),
                    Write(
                        gdp_line_graph,
                        run_time=2.5,
                        rate_func=rate_functions.ease_in_quad,
                    ),
                    Write(fc_text, run_time=1.0),
                )
                self.wait()

            ### Declare ValueTrackers and start it at 1880 for Japan, G7 and 1850 for others
            initial_start_year = 1880 if focus_country in ["Japan", "G7"] else 1850
            initial_end_year = 1885 if focus_country in ["Japan", "G7"] else 1855
            lower_vt = ValueTracker(initial_start_year)
            upper_vt = ValueTracker(initial_end_year)

            ### Create the line that connects the both graphs
            lower_projecting_line = always_redraw(
                lambda: DashedLine(
                    color=XKCD.YELLOW,
                    end=gdp_ax.c2p(lower_vt.get_value(), 10e4),
                    start=spend_ax.c2p(lower_vt.get_value(), 0),
                )
            )
            upper_projecting_line = always_redraw(
                lambda: DashedLine(
                    color=XKCD.YELLOW,
                    end=gdp_ax.c2p(upper_vt.get_value(), 10e4),
                    start=spend_ax.c2p(upper_vt.get_value(), 0),
                )
            )
            ### Define point corresponding to demo calculation
            demo_dot = always_redraw(
                lambda: Dot(
                    comp_ax.coords_to_point(
                        *self.years_to_coords(
                            fc_scatter_debt_adjusted_df,
                            round(lower_vt.get_value()),
                            round(upper_vt.get_value()),
                        )
                    ),
                    color=cmap[focus_country],
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

            ### Generate list of dots and add to scene while value tracker changes
            demo_dots_list = []
            for lower_bound in list(range(initial_start_year, 2018)):
                upper_bound = lower_bound + 5
                demo_dots_list.append(
                    Dot(
                        comp_ax.coords_to_point(
                            *self.years_to_coords(
                                fc_scatter_debt_adjusted_df,
                                lower_bound,
                                upper_bound,
                            )
                        ),
                        color=cmap[focus_country],
                        radius=0.05,
                        fill_opacity=0.3,
                    )
                )
            self.play(
                lower_vt.animate.set_value(2017),
                upper_vt.animate.set_value(2022),
                LaggedStart(
                    *[Create(d) for d in demo_dots_list],
                    lag_ratio=5.0,
                    rate_func=rate_functions.linear,
                ),
                run_time=15.5,
                rate_func=rate_functions.linear,
            )

            ### Unwrite the projected lines and demo point from the scene
            self.play(
                Unwrite(lower_projecting_line, run_time=1.0),
                Unwrite(upper_projecting_line, run_time=1.0),
                Unwrite(demo_dot, run_time=1.0),
            )
            self.wait()

            ### Remove Focus Country's lines, dots and text if not final country
            if fc != len(focus_countries) - 1:
                self.play(
                    Unwrite(spend_line_graph),
                    Unwrite(gdp_line_graph),
                    Unwrite(fc_text),
                    *[Unwrite(d) for d in demo_dots_list],
                    run_time=1,
                )
                self.wait()

        ### Remove war years from scatter plot
        war_years = [y for y in range(1909, 1918)] + [y for y in range(1934, 1945)]
        war_year_indices = [
            i
            for i, y in enumerate(fc_scatter_debt_adjusted_df["start_year"])
            if y in war_years
        ]
        demo_dots_war_years = [
            demo_dots_list[war_year_index] for war_year_index in war_year_indices
        ]

        ### Draw black rectangles around line graphs for war years
        rect_list = []
        gdp_coord_tuples_list = [
            [(1909, 3e3), (1923, 1e5)],
            [(1934, 3e3), (1950, 1e5)],
        ]
        spend_coord_tuples_list = [
            [(1909, 3), (1923, 100)],
            [(1934, 3), (1950, 100)],
        ]
        for i, coord_tuples_list in enumerate(
            gdp_coord_tuples_list + spend_coord_tuples_list
        ):
            if i <= 1:
                ax = gdp_ax
            else:
                ax = spend_ax
            rect = Polygon(
                *[ax.c2p(*i) for i in self.get_rectangle_corners(*coord_tuples_list)],
                color=WHITE,
                fill_color=WHITE,
                fill_opacity=1.0,
            )
            rect_list.append(rect)

        ### "Remove" war years from all plots
        self.play(
            *[Create(r) for r in rect_list],
            *[Unwrite(d) for d in demo_dots_war_years],
            run_time=1.0,
        )
        self.wait()

        ### Remove war years from dots list and scatter dataframe
        demo_dots_minus_war_years = [
            demo_dots_list[i]
            for i in range(len(demo_dots_list))
            if i not in war_year_indices
        ]
        fc_scatter_debt_adjusted_df = fc_scatter_debt_adjusted_df.reset_index(
            drop=True
        ).drop(war_year_indices)

        ### Add clustering results to dataframe
        fc_scatter_debt_adjusted_df = add_kmeans_clusters(
            fc_scatter_debt_adjusted_df, n_clusters=5
        )

        ### Transform current scatter plot to centroid scatter plot
        centroid_dots_list = []
        seen_coords = []
        for lower_bound in list(range(initial_start_year, 2018)):
            if lower_bound in war_years:
                continue
            upper_bound = lower_bound + 5
            coords = self.years_to_coords(
                fc_scatter_debt_adjusted_df,
                lower_bound,
                upper_bound,
                which_data="centroid",
            )
            coords_tuple = tuple(coords)  # Convert numpy array to tuple
            if coords_tuple not in seen_coords:
                seen_coords.append(coords_tuple)
                fill_opacity = 0.75
            else:
                fill_opacity = 0.0
            centroid_dots_list.append(
                Dot(
                    comp_ax.coords_to_point(*coords),
                    color=colour_map[focus_country],
                    radius=0.05,
                    fill_opacity=fill_opacity,
                )
            )

        ### Finally, animate the transformations
        self.play(
            *[
                ReplacementTransform(d, centroid_dots_list[i])
                for i, d in enumerate(demo_dots_minus_war_years)
            ],
            run_time=1,
        )
        self.wait(2)

    def get_rectangle_corners(self, bottom_left, top_right):
        return [
            (top_right[0], top_right[1]),
            (bottom_left[0], top_right[1]),
            (bottom_left[0], bottom_left[1]),
            (top_right[0], bottom_left[1]),
        ]

    def years_to_coords(
        self, df: pd.DataFrame, start_year: int, end_year: int, which_data: str = None
    ) -> list[float, float]:
        if abs(end_year - start_year) != 5:
            end_year = start_year + 5
        if which_data == "centroid":
            col_names = ["centroid_x", "centroid_y"]
        else:
            col_names = [
                "Average Government Expenditure as % of GDP",
                "Annualized percentage change in GDP per capita USD",
            ]
        result = df.loc[
            (df["start_year"] == start_year) & (df["end_year"] == end_year),
            col_names,
        ]
        if result.empty:
            raise ValueError(
                f"No data found for start_year={start_year} and end_year={end_year}"
            )
        coords = result.values[0]
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
            ax = ax.move_to(RIGHT * position)
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
    df = get_spend_gdp_debt_adjusted_df()
    countries = [
        "United Kingdom",
        "United States",
        "Japan",
        "Germany",
        "France",
        "Canada",
        "Italy",
    ]
    new_country_name = "G7"
    new_region_name = "World"
    new_df = create_country_group(
        df, countries, new_country_name, new_region_name, weight_pop=True
    )
    scatter_df = get_scatter_df(new_df, long_range=[1850, 2019], sub_period=5)
    print(scatter_df.loc[scatter_df["Country"] == "G7", :].head(15))
    war_years = [y for y in range(1909, 1918)] + [y for y in range(1934, 1945)]
    cluster_result = add_kmeans_clusters(scatter_df, n_clusters=5)
    print(cluster_result.loc[cluster_result["Country"] == "G7", :].head(15))
    pass
