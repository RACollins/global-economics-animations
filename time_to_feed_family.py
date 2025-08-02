from manim import *
import pandas as pd
import os

###################
### Definitions ###
###################

### Set WHITE background
config.background_color = WHITE

### Set default color for common objects to BLACK
Line.set_default(color=BLACK)
Text.set_default(color=BLACK)
Axes.set_default(color=BLACK)
Dot.set_default(color=BLACK)

cwd = os.getcwd()

#################
### Functions ###
#################


def get_time_to_feed_family_df() -> pd.DataFrame:
    """Simple utility function to read the time to feed family data with yearly interpolation"""
    df = pd.read_csv(cwd + "/data/time_to_feed_family.csv")

    # Create complete year range from min to max year
    min_year = df["Year"].min()
    max_year = df["Year"].max()
    complete_years = pd.DataFrame({"Year": range(min_year, max_year + 1)})

    # Merge and interpolate missing values
    df_complete = pd.merge(complete_years, df, on="Year", how="left")
    df_complete["Time to feed family (Hours)"] = df_complete[
        "Time to feed family (Hours)"
    ].interpolate(method="quadratic")

    return df_complete


class LineGraphAxis(object):
    def __init__(self, x_min, x_max, y_max, x_step=None, y_step=None):
        self._x_min = x_min
        self._x_max = ValueTracker(x_max)
        self._y_max = y_max
        self.x_step = x_step or max(1, (x_max - x_min) // 10)
        self.y_step = y_step or max(1, y_max // 10)
        self.ax = self.make_graph()

    @property
    def x_max(self):
        return self._x_max.get_value()

    def make_axis(self):
        x_max_val = self._x_max.get_value()
        ax = Axes(
            x_range=[self._x_min, x_max_val, self.x_step],
            y_range=[0, self._y_max, self.y_step],
            axis_config={
                "color": BLACK,
                "include_tip": False,
                "include_numbers": True,
                "decimal_number_config": {
                    "num_decimal_places": 0,
                    "group_with_commas": False,
                },
            },
            x_axis_config={
                "numbers_to_include": np.arange(
                    self._x_min, x_max_val + 1, self.x_step
                ),
            },
            y_axis_config={
                "numbers_to_include": np.arange(0, self._y_max + 1, self.y_step),
            },
        )
        # Add coordinates and make them visible
        ax.add_coordinates()
        ax.coordinate_labels[0].set_color(BLACK)
        ax.coordinate_labels[1].set_color(BLACK)
        return ax

    def make_graph(self):
        ax = self.make_axis()

        def become_ax(mob):
            old_ax = mob
            new_ax = self.make_axis()
            old_ax.become(new_ax)

            # Copy additional properties that are not
            # copied with .become()
            old_ax.x_axis.x_range = new_ax.x_axis.x_range
            old_ax.x_axis.scaling = new_ax.x_axis.scaling
            old_ax.y_axis.x_range = new_ax.y_axis.x_range
            old_ax.y_axis.scaling = new_ax.y_axis.scaling

        ax.add_updater(become_ax)
        return ax

    def update_x_max(self, x_max):
        return self._x_max.animate.set_value(x_max)


class LineGraphLine(object):
    def __init__(self, ax, x_start, y_start):
        self.ax = ax
        self.x_points = [x_start]
        self.y_points = [y_start]
        self.line = self.plot_line()

        # From add_batch
        self.new_x_batch = None
        self.new_y_batch = None
        self.segment_batch = None

    def make_line(self):
        # Take the saved points and build a line graph connecting them.
        line = VGroup()

        if len(self.x_points) > 1:
            points = [self.ax.c2p(x, y) for x, y in zip(self.x_points, self.y_points)]
            line.set_points_as_corners(points)
            line.set_stroke(color=GRAY, width=2)

        return line

    def plot_line(self):
        # Make the line and add an updater, which will keep the
        # points in sync with the axis.
        line = self.make_line()

        def line_updater(mob):
            mob.become(self.make_line())

        line.add_updater(line_updater)

        return line

    def add_batch(self, x_batch, y_batch):
        # Create line segments for a batch of points
        # Save the points to temporary values so they can be
        # added to the array when save_batch() is called.
        self.new_x_batch = x_batch
        self.new_y_batch = y_batch

        # Create all the line segments for this batch
        segments = VGroup()

        # Start from the last existing point
        prev_x = self.x_points[-1]
        prev_y = self.y_points[-1]

        for x, y in zip(x_batch, y_batch):
            start = self.ax.c2p(prev_x, prev_y)
            end = self.ax.c2p(x, y)
            segment = Line(start, end, color=GRAY, stroke_width=2)
            segments.add(segment)

            # Update previous point for next segment
            prev_x = x
            prev_y = y

        self.segment_batch = segments
        return segments

    def save_batch(self):
        # Save the batch points to the array and
        # return the segments so they can be
        # removed from the scene.
        self.x_points.extend(self.new_x_batch)
        self.y_points.extend(self.new_y_batch)
        return self.segment_batch


class AnimatedScatterPlot(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Define batch configuration - can be easily modified
        self.batch_config = {
            "batch1": [1200, 1320],
            "batch2": [1321, 1420],
            "batch3": [1421, 1520],
            "batch4": [1521, 1820],
            "batch5": [1821, 2000],
            "batch6": [2001, 2020],
        }

    def construct(self):
        # Load data
        df = get_time_to_feed_family_df()

        # Get the data ranges
        x_data = df["Year"].values
        y_data = df["Time to feed family (Hours)"].values

        # Calculate ranges
        x_min = x_data[0]  # Starting year
        first_batch_end = self.batch_config["batch1"][1]
        initial_x_max = first_batch_end  # Show first batch initially
        y_max = max(y_data) * 1.1  # Add 10% padding

        # Create axis with initial range - adjust step sizes based on data
        x_step = 100  # Use even 100-year steps
        y_step = max(1, int(y_max // 8))  # Reasonable y-axis step
        lga = LineGraphAxis(x_min, initial_x_max, y_max, x_step=x_step, y_step=y_step)

        # Add axis labels using proper method for visibility
        x_label = lga.ax.get_x_axis_label(Text("Year", font_size=28, color=BLACK))
        y_label = lga.ax.get_y_axis_label(
            Text("Time to Feed Family (Hours)", font_size=28, color=BLACK)
        )

        # Create a line starting at the first data point
        lgl = LineGraphLine(lga.ax, x_data[0], y_data[0])

        # Add everything to scene (no dots)
        self.add(lga.ax, lgl.line, x_label, y_label)

        # Animate adding points in batches
        for batch_name, (start_year, end_year) in self.batch_config.items():
            # Get data for this batch (excluding the starting point which is already added)
            batch_mask = (x_data >= start_year) & (x_data <= end_year)
            if batch_name == "batch1":
                # For first batch, exclude the starting point
                batch_mask = batch_mask & (x_data > x_data[0])

            batch_x = x_data[batch_mask]
            batch_y = y_data[batch_mask]

            if len(batch_x) == 0:
                continue

            # Check if we need to expand the axis
            batch_max_x = batch_x[-1]
            if batch_max_x > lga.x_max * 0.9:
                new_x_max = min(
                    batch_max_x * 1.1, x_data[-1] * 1.05
                )  # Don't overshoot final data
                self.play(lga.update_x_max(new_x_max), run_time=1.0)

            # Animate creation of the batch line segments
            new_segments = lgl.add_batch(batch_x, batch_y)
            self.play(Create(new_segments), run_time=1.5)

            # Save the points and remove temporary segments
            temp_segments = lgl.save_batch()
            self.remove(temp_segments)

            # Force line update by becoming the updated line
            lgl.line.become(lgl.make_line())

        self.wait(2)


if __name__ == "__main__":
    # Test runner - uncomment to render
    # from manim import tempconfig
    # with tempconfig({"quality": "low_quality", "disable_caching": True}):
    #     AnimatedScatterPlot().render(preview=True)
    pass
