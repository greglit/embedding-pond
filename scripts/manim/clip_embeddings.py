from __future__ import annotations

import shutil
from pathlib import Path

# pyright: ignore

import manim as m  # type: ignore


class ClipEmbeddings(m.Scene):
    def construct(self):
        m.config.disable_caching = True
        self.camera.background_color = "#FFFFFF"
        self.camera.frame_width = 12.0
        self.camera.frame_height = 6.75

        title_color = "#1F2937"
        box_stroke = "#CBD5E1"
        arrow_color = "#64748B"
        text_encoder_fill = "#DDD6FE"
        image_encoder_fill = "#BBF7D0"
        embedding_fill = "#F8FAFC"
        link_color = "#94A3B8"
        font_family = "Avenir"

        text_box = m.RoundedRectangle(
            corner_radius=0.15, width=2.1, height=0.7, stroke_color=box_stroke
        )
        text_label = m.Text("Text", font_size=28, color=title_color, font=font_family)
        text_group = m.VGroup(text_box, text_label).move_to(m.LEFT * 4.5 + m.UP * 1.2)

        image_box = m.RoundedRectangle(
            corner_radius=0.15, width=2.1, height=0.7, stroke_color=box_stroke
        )
        image_label = m.Text("Image", font_size=28, color=title_color, font=font_family)
        image_group = m.VGroup(image_box, image_label).move_to(
            m.LEFT * 4.5 + m.DOWN * 1.2
        )

        text_encoder_core = m.Polygon(
            [-0.7, 0.6, 0],
            [0.7, 0.35, 0],
            [0.7, -0.35, 0],
            [-0.7, -0.6, 0],
            fill_color=text_encoder_fill,
            fill_opacity=1,
            stroke_width=0,
        )
        text_encoder_label = m.Text(
            "Text\nEncoder",
            font_size=22,
            color=title_color,
            line_spacing=0.8,
            font=font_family,
        )
        text_encoder = m.VGroup(text_encoder_core, text_encoder_label).move_to(
            m.LEFT * 1.1 + m.UP * 1.2
        )

        image_encoder_core = m.Polygon(
            [-0.7, 0.6, 0],
            [0.7, 0.35, 0],
            [0.7, -0.35, 0],
            [-0.7, -0.6, 0],
            fill_color=image_encoder_fill,
            fill_opacity=1,
            stroke_width=0,
        )
        image_encoder_label = m.Text(
            "Image\nEncoder",
            font_size=22,
            color=title_color,
            line_spacing=0.8,
            font=font_family,
        )
        image_encoder = m.VGroup(image_encoder_core, image_encoder_label).move_to(
            m.LEFT * 1.1 + m.DOWN * 1.2
        )

        text_embedding_anchor = m.Dot(
            point=m.RIGHT * 3.3 + m.UP * 1.2,
            radius=0,
            fill_opacity=0,
            stroke_opacity=0,
        )

        image_embedding_anchor = m.Dot(
            point=m.RIGHT * 3.3 + m.DOWN * 1.2,
            radius=0,
            fill_opacity=0,
            stroke_opacity=0,
        )

        shared_text_label = m.Text(
            "Shared embedding space",
            font_size=22,
            color=title_color,
            font=font_family,
        )
        shared_text_label.move_to(m.RIGHT * 3.3)

        shared_box = m.RoundedRectangle(
            corner_radius=0.2,
            width=4.6,
            height=4.1,
            stroke_color=box_stroke,
        ).move_to(m.RIGHT * 3.3)

        text_embed_target = shared_box.get_left() + m.RIGHT * 0.1 + m.UP * 1.2
        image_embed_target = shared_box.get_left() + m.RIGHT * 0.1 + m.DOWN * 1.2

        text_to_encoder = m.Arrow(
            text_group.get_right(),
            text_encoder.get_left(),
            color=arrow_color,
            stroke_width=3,
        )
        image_to_encoder = m.Arrow(
            image_group.get_right(),
            image_encoder.get_left(),
            color=arrow_color,
            stroke_width=3,
        )
        text_encoder_to_embed = m.Arrow(
            text_encoder_core.get_right(),
            text_embed_target,
            color=arrow_color,
            stroke_width=3,
        )
        image_encoder_to_embed = m.Arrow(
            image_encoder_core.get_right(),
            image_embed_target,
            color=arrow_color,
            stroke_width=3,
        )

        self.add(text_group, image_group, text_encoder, image_encoder)

        self.play(m.Create(text_to_encoder), run_time=0.225)
        self.play(m.Create(text_encoder_to_embed), run_time=0.225)

        text_values = m.VGroup(
            *[
                m.Text(val, font_size=20, color=title_color, font=font_family)
                for val in ["[0.42", "-1.03", "0.77", "2.11", "-0.58", "…]"]
            ]
        )
        text_values.arrange(m.RIGHT, buff=0.15)
        text_values.move_to(text_embedding_anchor)

        for idx, val in enumerate(text_values):
            self.play(m.FadeIn(val, shift=m.UP * 0.1), run_time=0.1)
            if idx == 1:
                self.play(m.Create(image_to_encoder), run_time=0.225)

        self.play(m.Create(image_encoder_to_embed), run_time=0.225)

        image_values = m.VGroup(
            *[
                m.Text(val, font_size=20, color=title_color, font=font_family)
                for val in ["[0.39", "-1.07", "0.72", "2.05", "-0.61", "…]"]
            ]
        )
        image_values.arrange(m.RIGHT, buff=0.15)
        image_values.move_to(image_embedding_anchor)

        for val in image_values:
            self.play(m.FadeIn(val, shift=m.UP * 0.1), run_time=0.1)

        self.play(m.FadeIn(shared_text_label, shift=m.UP * 0.1), run_time=0.1)
        self.play(m.Create(shared_box), run_time=0.175)

        self.wait(0.25)


def cleanup_manim_artifacts(scene_name: str = "ClipEmbeddings") -> None:
    media_dir = Path(m.config.media_dir)
    partial_dir = (
        media_dir
        / "videos"
        / "clip_embeddings"
        / "1080p60"
        / "partial_movie_files"
        / scene_name
    )
    if partial_dir.exists():
        shutil.rmtree(partial_dir)

    for cache_dir in (media_dir / "texts", media_dir / "images"):
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
