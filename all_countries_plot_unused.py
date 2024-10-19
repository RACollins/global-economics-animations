"""### Add all country lines to left plots
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

### Generate line plots randomly
random_line_plots = np.random.choice(
    [Write(slg) for k, slg in spend_lines_dict.items()] + [Write(gdplg) for k, gdplg in gdp_lines_dict.items()],
    (len(all_countries)-len(excluded_countries))*2,  #<-- ignoring excluded countries
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

### Generate dict of region average lines
avg_gdp_lines_dict, avg_spend_lines_dict = {}, {}
for region, colour in colour_map.items():
    country = region + "_avg"
    average_lines_graph_df = (avg_line_graphs_df
                                .loc[avg_line_graphs_df["Region"] == region, :]
                                .set_index("Year", drop=False))
    
    avg_gdp_lines_dict[region] = gdp_ax.plot_line_graph(
        x_values=average_lines_graph_df["Year"],
        y_values=average_lines_graph_df["GDP per capita (OWiD)"],
        line_color=colour_map[region],
        add_vertex_dots=False,
        stroke_width=1,
    )
    avg_spend_lines_dict[region] = spend_ax.plot_line_graph(
        x_values=average_lines_graph_df["Year"],
        y_values=average_lines_graph_df["Government Expenditure (IMF & Wiki)"],
        line_color=colour_map[region],
        add_vertex_dots=False,
        stroke_width=1,
    )

### Transform lines to weighted region average lines
to_avg_transforms = []
for country in all_countries:
    if country in excluded_countries:
        continue
    region = line_graphs_df.loc[line_graphs_df["Country"] == country, "Region"].values[0]
    to_avg_transforms.append(
        Transform(gdp_lines_dict[country], avg_gdp_lines_dict[region])
    )
    to_avg_transforms.append(
        Transform(spend_lines_dict[country], avg_spend_lines_dict[region])
    )
self.play(
    *to_avg_transforms,
    run_time=1,
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

### Generate dict of dots for all region averages
avg_region_dots_dict = {}
for region, colour in colour_map.items():
    region_scatter_df = (
        rgn_avg_scatter_df.loc[rgn_avg_scatter_df["Region"] == region, :]
    )
    dots_list = []
    for lower_bound in list(range(1850, 2015)):
        upper_bound = lower_bound + 5
        try:
            coords = self.years_to_coords(
                region_scatter_df,
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
                color=colour,
                radius=0.05,
                fill_opacity=alpha,
            )
        )
    avg_region_dots_dict[region] = dots_list

### Create initial dots
initial_dots = [Write(dots_list[0], run_time=1.0) for region, dots_list in avg_region_dots_dict.items()]

### Write the projected lines and initial dots to the scene
self.play(
    Write(lower_projecting_line, run_time=1.0),
    Write(upper_projecting_line, run_time=1.0),
    *initial_dots,
    )
self.wait()

### Animate vertical lines and plot dots on right scatter graph
### Will take long time to render!
### But maybe not so long after the switch to region averages
lagged_start_list = [
    LaggedStart(
        *[Create(d) for d in dots_list],
        lag_ratio=5.0,
        rate_func=rate_functions.linear,
    ) for region, dots_list in avg_region_dots_dict.items()
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
    )"""