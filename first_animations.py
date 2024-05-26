from manim import *
import pandas as pd


class CreateCircle(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
        self.play(Create(circle))  # show the circle on screen


class ScatterPlotAnimatedScene(Scene):
    def construct(self):
        # Download data and put in DataFrame
        data_url = "https://raw.githubusercontent.com/thomasnield/machine-learning-demo-data/master/regression/linear_normal.csv"

        df = pd.read_csv(data_url)

        # Animate the creation of Axes
        ax = Axes(x_range=[0, 100, 5], y_range=[-20, 200, 10])
        self.play(Write(ax))

        self.wait()  # wait for 1 second

        # Animate the creation of dots
        dots = [Dot(ax.c2p(x, y), color=BLUE) for x, y in df.values]
        self.play(LaggedStart(*[Write(dot) for dot in dots], lag_ratio=0.05))

        self.wait()  # wait for 1 second


class TriangleAngleProof(Scene):
    def construct(self):
        # Create a triangle
        triangle = Polygon([-2, 0, 0], [2, 0, 0], [0, 2, 0], color=RED)
        self.play(Create(triangle))
        self.wait(0.5)

        # Label the angles
        angle_A = Angle(
            triangle.get_vertices()[1],
            triangle.get_vertices()[0],
            radius=0.5,
        )
        angle_B = Angle(
            triangle.get_vertices()[2],
            triangle.get_vertices()[1],
            radius=0.5,
        )
        angle_C = Angle(
            triangle.get_vertices()[0],
            triangle.get_vertices()[2],
            radius=0.5,
        )
        angle_labels = [MathTex("A"), MathTex("B"), MathTex("C")]
        angle_labels[0].next_to(angle_A, RIGHT)
        angle_labels[1].next_to(angle_B, UP)
        angle_labels[2].next_to(angle_C, LEFT)
        self.play(
            Create(angle_A),
            Create(angle_B),
            Create(angle_C),
            Write(angle_labels[0]),
            Write(angle_labels[1]),
            Write(angle_labels[2]),
        )
        self.wait(1)

        # Extend the sides of the triangle
        extended_sides = [
            Line(triangle.get_vertices()[0], triangle.get_vertices()[0] + UP * 2),
            Line(triangle.get_vertices()[1], triangle.get_vertices()[1] + DOWN * 2),
            Line(triangle.get_vertices()[2], triangle.get_vertices()[2] + LEFT * 2),
        ]
        self.play(
            Create(extended_sides[0]),
            Create(extended_sides[1]),
            Create(extended_sides[2]),
        )
        self.wait(1)

        # Show that the sum of the angles is 180 degrees
        angle_sum = MathTex("A + B + C = 180^\\circ")
        angle_sum.move_to(UP * 2)
        self.play(Write(angle_sum))
        self.wait(2)

        # Clean up
        self.play(
            FadeOut(triangle),
            FadeOut(angle_A),
            FadeOut(angle_B),
            FadeOut(angle_C),
            FadeOut(angle_labels[0]),
            FadeOut(angle_labels[1]),
            FadeOut(angle_labels[2]),
            FadeOut(extended_sides[0]),
            FadeOut(extended_sides[1]),
            FadeOut(extended_sides[2]),
            FadeOut(angle_sum),
        )
