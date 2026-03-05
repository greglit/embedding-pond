from __future__ import annotations

# pyright: ignore

import manim as m  # type: ignore


class ClipEmbeddings(m.Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"

        title_color = "#1F2937"
        box_stroke = "#CBD5E1"
        arrow_color = "#64748B"
        text_encoder_fill = "#DDD6FE"
        image_encoder_fill = "#BBF7D0"
        embedding_fill = "#F8FAFC"
        link_color = "#94A3B8"

        text_box = m.RoundedRectangle(
            corner_radius=0.15, width=2.1, height=0.7, stroke_color=box_stroke
        )
        text_label = m.Text("Text", font_size=28, color=title_color)
        text_group = m.VGroup(text_box, text_label).move_to(m.LEFT * 5.1 + m.UP * 1.5)

        image_box = m.RoundedRectangle(
            corner_radius=0.15, width=2.1, height=0.7, stroke_color=box_stroke
        )
        image_label = m.Text("Bild", font_size=28, color=title_color)
        image_group = m.VGroup(image_box, image_label).move_to(
            m.LEFT * 5.1 + m.DOWN * 1.5
        )

        text_encoder_box = m.RoundedRectangle(
            corner_radius=0.2, width=2.4, height=1.6, stroke_color=box_stroke
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
            "Text\nEncoder", font_size=22, color=title_color, line_spacing=0.8
        )
        text_encoder = m.VGroup(
            text_encoder_box, text_encoder_core, text_encoder_label
        ).move_to(m.LEFT * 1.6 + m.UP * 1.5)

        image_encoder_box = m.RoundedRectangle(
            corner_radius=0.2, width=2.4, height=1.6, stroke_color=box_stroke
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
            "Image\nEncoder", font_size=22, color=title_color, line_spacing=0.8
        )
        image_encoder = m.VGroup(
            image_encoder_box, image_encoder_core, image_encoder_label
        ).move_to(m.LEFT * 1.6 + m.DOWN * 1.5)

        text_embedding_box = m.RoundedRectangle(
            corner_radius=0.18,
            width=3.4,
            height=0.9,
            stroke_color=box_stroke,
            fill_color=embedding_fill,
            fill_opacity=1,
        )
        text_embedding_label = m.Text(
            "Embeddingwerte als Liste", font_size=20, color=title_color
        )
        text_embedding_group = m.VGroup(
            text_embedding_box, text_embedding_label
        ).move_to(m.RIGHT * 4.2 + m.UP * 1.5)

        image_embedding_box = m.RoundedRectangle(
            corner_radius=0.18,
            width=3.4,
            height=0.9,
            stroke_color=box_stroke,
            fill_color=embedding_fill,
            fill_opacity=1,
        )
        image_embedding_label = m.Text(
            "Embeddingwerte als Liste", font_size=20, color=title_color
        )
        image_embedding_group = m.VGroup(
            image_embedding_box, image_embedding_label
        ).move_to(m.RIGHT * 4.2 + m.DOWN * 1.5)

        shared_text_box = m.RoundedRectangle(
            corner_radius=0.14, width=2.6, height=0.8, stroke_color=box_stroke
        )
        shared_text_label = m.Text("Selber Zahlenraum", font_size=22, color=title_color)
        shared_text = m.VGroup(shared_text_box, shared_text_label).move_to(
            m.RIGHT * 4.2
        )

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
            text_encoder.get_right(),
            text_embedding_group.get_left(),
            color=arrow_color,
            stroke_width=3,
        )
        image_encoder_to_embed = m.Arrow(
            image_encoder.get_right(),
            image_embedding_group.get_left(),
            color=arrow_color,
            stroke_width=3,
        )

        shared_to_text = m.Arrow(
            shared_text.get_top(),
            text_embedding_group.get_bottom(),
            color=link_color,
            stroke_width=2,
        )
        shared_to_image = m.Arrow(
            shared_text.get_bottom(),
            image_embedding_group.get_top(),
            color=link_color,
            stroke_width=2,
        )

        self.add(
            text_group,
            image_group,
            text_encoder,
            image_encoder,
            text_embedding_group,
            image_embedding_group,
            shared_text,
        )

        self.play(m.Create(text_to_encoder), run_time=0.7)
        self.play(m.Create(text_encoder_to_embed), run_time=0.7)

        text_values = m.VGroup(
            *[
                m.Text(val, font_size=20, color=title_color)
                for val in ["[0.42", "-1.03", "0.77", "2.11", "-0.58", "…]"]
            ]
        )
        text_values.arrange(m.RIGHT, buff=0.15)
        text_values.move_to(text_embedding_group)
        text_values.shift(m.DOWN * 0.1)

        for val in text_values:
            self.play(m.FadeIn(val, shift=m.UP * 0.1), run_time=0.3)

        self.play(m.Create(image_to_encoder), run_time=0.7)
        self.play(m.Create(image_encoder_to_embed), run_time=0.7)

        image_values = m.VGroup(
            *[
                m.Text(val, font_size=20, color=title_color)
                for val in ["[0.39", "-1.07", "0.72", "2.05", "-0.61", "…]"]
            ]
        )
        image_values.arrange(m.RIGHT, buff=0.15)
        image_values.move_to(image_embedding_group)
        image_values.shift(m.DOWN * 0.1)

        for val in image_values:
            self.play(m.FadeIn(val, shift=m.UP * 0.1), run_time=0.3)

        self.play(m.FadeIn(shared_text_label, shift=m.UP * 0.1), run_time=0.3)
        self.play(m.Create(shared_to_text), m.Create(shared_to_image), run_time=0.7)

        self.wait(1)
