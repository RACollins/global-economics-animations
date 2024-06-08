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

jobs = ["all_jobs", "bricklayer", "doctor", "nurse"]

#################
### Functions ###
#################


def get_salaries_df(job: str) -> pd.DataFrame:
    cwd = os.getcwd()
    df = pd.read_csv(cwd + "/data/{}.csv".format(job), index_col=0)
    return df


def add_radius_col(
    df: pd.DataFrame, lowest_radius: float, highest_radius: float
) -> pd.DataFrame:
    df["radius"] = (df["Population"] - df["Population"].min()) / (
        df["Population"].max() - df["Population"].min()
    ) * (highest_radius - lowest_radius) + lowest_radius
    return df

def convert_k_cols(df: pd.DataFrame, cols_to_convert: str|list) -> pd.DataFrame:
    df[cols_to_convert] /= 1000
    return df


def make_axes():
    ax = Axes(
        x_range=[3, 5.2, 1],
        y_range=[3, 6.1, 1],
        axis_config={
            "color": WHITE,   # <- not needed if backgroud colour is default BLACK
            "include_tip": True,
            "include_numbers": True,
            "scaling": LogBase(custom_labels=True),
        },
    )
    return ax


###############
### Classes ###
###############


#############
### Scene ###
#############


class SalariesScatterPlotAnimatedScene(Scene):
    def construct(self):
        axes_dict, dots_dict, titles_dict = self.generate_data_dicts(jobs=jobs)
        self.generate_play_transforms(jobs=jobs, data_dicts=(axes_dict, dots_dict, titles_dict))
        self.wait(2)
        

    def generate_play_transforms(self, jobs: list, data_dicts: tuple):
        axes_dict, dots_dict, titles_dict = data_dicts
        
        for j in range(len(jobs)-1):
            axes_transforms, dots_transforms, titles_transforms = [], [], []
            axes_transforms.append(Transform(axes_dict[jobs[0]], axes_dict[jobs[j+1]]))
            titles_transforms.append(Transform(titles_dict[jobs[0]], titles_dict[jobs[j+1]]))
            for d, dot in enumerate(dots_dict[jobs[j+1]]):
                dots_transforms.append(Transform(dots_dict[jobs[0]][d], dots_dict[jobs[j+1]][d]))
            self.play(*axes_transforms,
                      *dots_transforms,
                      *titles_transforms)
            self.wait(3.5)
        return None
    
    def generate_data_dicts(self, jobs: list):
        axes_dict, dots_dict, titles_dict = {}, {}, {}
        for j, job in enumerate(jobs):
            animate_axes, animate_dots = (True, True) if j == 0 else (False, False)
            ax, dots, title = self.generate_plot(job=job, animate_axes=animate_axes, animate_dots=animate_dots)
            axes_dict[job], dots_dict[job], titles_dict[job] = ax, dots, title
        return axes_dict, dots_dict, titles_dict
    
    def generate_plot(self, job: str, animate_axes: bool, animate_dots: bool):
        ### Download data and put in DataFrame
        df = get_salaries_df(job=job)
        df = add_radius_col(df, lowest_radius=0.05, highest_radius=0.85)
        pay_col = "Mean_USD" if job == "all_jobs" else "Median_USD"
        ax = make_axes()
        ### Add axis labels
        x_label = ax.get_x_axis_label(Text("GDP per Capita (USD)", font_size=26))
        y_label = ax.get_y_axis_label(Text("Average Salary (USD)", font_size=26))
        ### Add title
        title = Text(r"{}".format(" ".join([s.capitalize() for s in job.split("_")])), font_size=30)
        title.to_edge(UP)

        if animate_axes:
            ### Animate the creation of Axes
            self.play(Write(ax))
            self.play(Write(x_label))
            self.play(Write(y_label))
            self.play(Write(title))
            self.wait()  # wait for 1 second
        
        dots = []
        for i in range(df.shape[0]):
            x, y = df.loc[i, ["GDP_per_capita_USD", pay_col]].values
            colour = colour_map[df.loc[i, ["Region"]].values[0]]
            radius = df.loc[i, ["radius"]].values[0]
            dots.append(Dot(ax.c2p(x, y), color=colour, radius=radius, fill_opacity=0.65))

        if animate_dots:
            ### Animate the creation of dots
            self.play(LaggedStart(*[Write(dot) for dot in dots], lag_ratio=0.05))
            self.wait()  # wait for 1 second

        return ax, dots, title


if __name__ == "__main__":
    """ df = get_salaries_df(job="nurse")
    df = add_radius_col(df, lowest_radius=0.05, highest_radius=1.0)
    print(df) """
    pass
