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

        #################
        ### Functions ###
        #################

        ### Load data for line graphs and put in DataFrame
        line_graphs_df = get_spend_gdp_df()
        uk_line_graphs_df = line_graphs_df.loc[line_graphs_df["Country"] == "United Kingdom", :].set_index("Year", drop=False)

if __name__ == "__main__":
    df = get_spend_gdp_df().sort_values(by=["GDP per capita (OWiD)"], ascending=False)
    # filtered_df = df.loc[df["Country"] == "United Kingdom", :].reset_index(drop=True)
    print(df.head(40))
    pass