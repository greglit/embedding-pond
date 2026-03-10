from __future__ import annotations

import math
import shutil
from pathlib import Path

import manim as m


class WaterlilyRender(m.Scene):
    def construct(self):
        m.config.disable_caching = True
        self.camera.background_color = "#FFFFFF"
        self.camera.frame_width = 12.0
        self.camera.frame_height = 6.75

        title_color = "#1F2937"
        accent_color = "#FADAE8"
        outline_color = "#B94A7A"
        arrow_color = "#64748B"
        font_family = "Avenir"

        embedding_values = [
            0.42,
            -1.03,
            0.77,
            2.11,
            -0.58,
            1.24,
            -0.12,
            0.96,
            -1.31,
            0.33,
            1.08,
            -0.74,
            0.51,
            -0.22,
            1.43,
            0.05,
            -0.92,
            0.68,
            1.27,
            -0.47,
            0.18,
            -0.66,
            0.89,
            -1.12,
            0.72,
            0.31,
            -0.84,
            1.02,
            -0.36,
            0.59,
            -0.15,
            1.19,
            -0.73,
            0.27,
            0.94,
            -0.41,
            1.11,
            -0.63,
            0.08,
            1.36,
            -0.98,
            0.44,
            0.86,
            -0.29,
            1.05,
            -0.57,
            0.12,
            1.21,
            -0.88,
            0.64,
            0.24,
            -0.79,
            1.09,
            -0.52,
            0.03,
            1.28,
            -1.07,
            0.47,
            0.75,
            -0.33,
        ]

        display_values = [
            int(round(abs(value) * 10)) % 10 for value in embedding_values
        ]
        bracket_left = m.Text("[", font=font_family, font_size=28, color=title_color)
        bracket_right = m.Text("]", font=font_family, font_size=28, color=title_color)
        value_texts = m.VGroup(
            bracket_left,
            *[
                m.Text(f"{value}", font=font_family, font_size=22, color=title_color)
                for value in display_values
            ],
            bracket_right,
        )
        value_texts.arrange_in_grid(rows=5, cols=13, buff=0.12)

        embedding_group = value_texts
        embedding_group.move_to(m.LEFT * 5.4 + m.UP * 2.4, aligned_edge=m.UP + m.LEFT)

        center = m.ORIGIN + m.RIGHT * 1.6
        inner_radius = 1.05
        outer_radius = 2.25

        min_val = min(embedding_values)
        max_val = max(embedding_values)
        value_range = max_val - min_val or 1

        points = []
        for index, value in enumerate(embedding_values):
            angle = math.pi / 2 - (index / len(embedding_values)) * math.tau
            normalized = (value - min_val) / value_range
            radius = inner_radius + normalized * (outer_radius - inner_radius)
            points.append(
                center
                + m.RIGHT * math.cos(angle) * radius
                + m.UP * math.sin(angle) * radius
            )

        lily_shape = m.VMobject()
        lily_shape.set_points_smoothly(points + [points[0]])
        lily_shape.set_fill(color="#FFFFFF", opacity=0)
        lily_shape.set_stroke(color=outline_color, width=0)

        self.add(embedding_group)

        point_dots = m.VGroup()
        line_segments = m.VGroup()
        radius_lines = m.VGroup()
        center_dot = m.Dot(point=center, radius=0.05, color=outline_color)

        self.play(m.FadeIn(embedding_group), run_time=0.35)
        self.play(m.FadeIn(center_dot, scale=0.8), run_time=0.15)

        value_items = list(value_texts)[1:-1]
        for index, (value_text, point) in enumerate(zip(value_items, points)):
            dot = m.Dot(point=point, radius=0.045, color=accent_color)
            radius_line = m.Line(center, point, color=arrow_color, stroke_width=1.6)
            radius_lines.add(radius_line)
            point_dots.add(dot)
            self.play(
                m.AnimationGroup(
                    m.FadeOut(
                        value_text,
                        shift=(point - value_text.get_center()) * 0.15,
                    ),
                    m.FadeIn(dot, scale=0.8),
                    m.Create(radius_line),
                    lag_ratio=0,
                ),
                run_time=0.08,
            )
        self.play(m.FadeOut(bracket_left), m.FadeOut(bracket_right), run_time=0.08)
        for index in range(1, len(points)):
            segment = m.Line(
                points[index - 1], points[index], color=arrow_color, stroke_width=2
            )
            line_segments.add(segment)

        closing_segment = m.Line(
            points[-1], points[0], color=arrow_color, stroke_width=2
        )
        line_segments.add(closing_segment)

        self.play(
            m.LaggedStart(
                *[m.Create(segment) for segment in line_segments],
                lag_ratio=0.02,
                run_time=0.35,
            ),
            m.Create(lily_shape.set_stroke(color=outline_color, width=2.2)),
            run_time=0.35,
        )
        self.play(
            m.FadeOut(point_dots),
            m.FadeOut(line_segments),
            m.FadeOut(radius_lines),
            m.FadeOut(center_dot),
            run_time=0.25,
        )
        self.play(
            lily_shape.animate.set_fill(color=accent_color, opacity=1), run_time=0.55
        )

        seed_dots = m.VGroup(
            m.Dot(point=center + m.RIGHT * 0.14, radius=0.0765, color="#F9E79F"),
            m.Dot(
                point=center + m.LEFT * 0.12 + m.UP * 0.08,
                radius=0.0765,
                color="#F9E79F",
            ),
            m.Dot(point=center + m.DOWN * 0.12, radius=0.0765, color="#F9E79F"),
        )
        self.play(m.FadeIn(seed_dots, scale=0.8), run_time=0.2)

        self.wait(0.3)


def cleanup_manim_artifacts(scene_name: str = "WaterlilyRender") -> None:
    media_dir = Path(m.config.media_dir)
    partial_dir = (
        media_dir
        / "videos"
        / "waterlily_render"
        / "1080p60"
        / "partial_movie_files"
        / scene_name
    )
    if partial_dir.exists():
        shutil.rmtree(partial_dir)

    for cache_dir in (media_dir / "texts", media_dir / "images"):
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
