from manim import *
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
        dots = []
        for country in df["Entity"].unique():
            if country in ["Kosovo", "Burundi"]:
                continue
            country_df = df.loc[(df["Entity"] == country) & (df["Year"] == 2023), :]
            x_val = country_df["GDP per capita"].values[0]
            y_val = country_df["Median Income Consumption ($/day)"].values[0]

            region = country_df["World regions according to OWID"].values[0]
            size = country_df["Country Size"].values[0]

            colour = colour_map[region]
            radius = radius_map[size]
            dots.append(
                Dot(ax.c2p(x_val, y_val), color=colour, radius=radius, fill_opacity=0.8)
            )

        ### Animate dots sequentially
        self.play(LaggedStart(*[Create(dot) for dot in dots], lag_ratio=0.05))

        ### Pause at the end to show final result
        self.wait(3)

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
