from manim import *
import numpy as np

class PhotolithographyStretched(Scene):

    def make_label(self, text, size=28):
        return Text(text, font_size=size, color=WHITE)

    def construct(self):
        self.camera.background_color = BLACK

        # ----------------------------
        # Helpers: make parallelogram
        # ----------------------------
        def parallelogram(w, h, skew, **kwargs):
            """
            w: width, h: height, skew: x-shift applied to the top edge
            Returns a Polygon shaped like a parallelogram.
            """
            pts = [
                np.array([-w/2, -h/2, 0]),
                np.array([ w/2, -h/2, 0]),
                np.array([ w/2 + skew,  h/2, 0]),
                np.array([-w/2 + skew,  h/2, 0]),
            ]
            return Polygon(*pts, **kwargs)

        # Scene layout
        tray_pos = DOWN * 1.1
        wafer_pos = tray_pos + UP * 0.35 + RIGHT * 0.70
        mask_pos  = tray_pos + UP * 1.10 + LEFT * 0.20
        source_pos = UP * 2.6

        # ----------------------------
        # Tray (skewed)
        # ----------------------------
        tray = parallelogram(7.2, 2.7, skew=1.6)
        tray.set_fill(GRAY_D, opacity=0.45)
        tray.set_stroke(WHITE, width=2, opacity=0.6)
        tray.move_to(tray_pos)

        tray_inner = parallelogram(6.6, 2.1, skew=1.45)
        tray_inner.set_fill(BLACK, opacity=0.35)
        tray_inner.set_stroke(width=0)
        tray_inner.move_to(tray_pos)

        tray_label = self.make_label("Wafer Tray", 26)
        tray_label.next_to(tray, DOWN, buff=0.25)

        tray_group = VGroup(tray, tray_inner, tray_label)


        # ----------------------------
        # Wafer (squashed ellipse = "tilt")
        # ----------------------------
        wafer = Ellipse(width=4.8, height=1.7)
        wafer.set_fill(GRAY_E, opacity=1)
        wafer.set_stroke(WHITE, width=3)
        wafer.move_to(wafer_pos)

        # simple sheen (optional)
        wafer_sheen = Ellipse(width=4.3, height=1.45)
        wafer_sheen.set_fill(WHITE, opacity=0.07)
        wafer_sheen.set_stroke(width=0)
        wafer_sheen.move_to(wafer_pos + UP*0.05)

        wafer_label = self.make_label("Silicon Wafer", 26)
        wafer_label.next_to(wafer, RIGHT, buff=0.35)

        wafer_group = VGroup(wafer, wafer_sheen, wafer_label)


        # ----------------------------
        # Mask (skewed, semi-transparent)
        # ----------------------------
        mask = parallelogram(5.7, 1.6, skew=1.3)
        mask.set_fill(GRAY_C, opacity=0.15)
        mask.set_stroke(WHITE, width=2, opacity=0.55)
        mask.move_to(mask_pos)

        # faint pattern lines on mask
        mask_lines = VGroup()
        for k in range(7):
            y = interpolate(-0.55, 0.55, k/6)
            # lines aligned with the parallelogram’s "tilt": give them same skew
            l = Line(
                np.array([-2.6, y, 0]),
                np.array([ 2.6, y, 0]),
            )
            l.shift(RIGHT * (1.3 * (y / 0.8)))  # tiny proportional skew
            mask_lines.add(l)
        mask_lines.set_stroke(WHITE, width=1, opacity=0.20)
        mask_lines.move_to(mask_pos)

        # mask label group
        mask_label = self.make_label("Mask", 26)
        mask_label.next_to(mask, LEFT, buff=0.35)

        mask_group = VGroup(mask, mask_lines, mask_label)


        # ----------------------------
        # UV source + cone
        # ----------------------------
        bulb = Circle(radius=0.32)
        bulb.set_fill("#b8a3ff", opacity=0.95)
        bulb.set_stroke(WHITE, width=2, opacity=0.8)
        bulb.move_to(source_pos)

        bulb_glow = Circle(radius=0.75)
        bulb_glow.set_fill("#7f7fff", opacity=0.12)
        bulb_glow.set_stroke(width=0)
        bulb_glow.move_to(source_pos)

        # UV lamp label
        lamp_label = self.make_label("UV Light Source", 24)
        lamp_label.next_to(bulb, UP, buff=0.25)
    
        lamp_group = VGroup(bulb, bulb_glow, lamp_label)


        # Cone aimed at the mask region
        cone = Polygon(
            source_pos + DOWN*0.35 + LEFT*0.18,
            source_pos + DOWN*0.35 + RIGHT*0.18,
            mask_pos + RIGHT*2.25 + DOWN*0.05,
            mask_pos + LEFT*2.25 + DOWN*0.05,
        )
        cone.set_fill("#7f7fff", opacity=0.10)
        cone.set_stroke(width=0)
        cone.set_opacity(0.0)  # off at start

        # ----------------------------
        # Vertical-ish rays (animated DOWN)
        # ----------------------------
        ray_phase = ValueTracker(0.0)

        def make_rays():
            rays = VGroup()
            # rays across the cone width
            xs = np.linspace(-2.0, 2.0, 9)
            for i, x in enumerate(xs):
                # endpoints: from just under bulb to just above mask
                top = source_pos + DOWN*0.55 + RIGHT*(0.55*x/2.0)
                bot = mask_pos + UP*0.10 + RIGHT*(1.10*x/2.0)

                # animate by sliding a little “pulse” downward using phase
                shift = 0.25 * np.sin(ray_phase.get_value() + i*0.6)
                seg = Line(top + DOWN*shift, bot + DOWN*shift)
                seg.set_stroke("#7f7fff", width=2, opacity=0.25)
                rays.add(seg)

            return rays

        rays = always_redraw(make_rays)
        rays.set_opacity(0.0)  # off at start

        # ----------------------------
        # Animate: tray -> wafer drop -> mask drop -> light on
        # ----------------------------
        self.play(FadeIn(tray_group, shift=DOWN*0.2), run_time=0.8)


        wafer_group.move_to(UP*3.0)
        self.play(FadeIn(wafer_group), run_time=0.1)
        self.play(
            wafer_group.animate.move_to(wafer_pos),
            run_time=1.0,
            rate_func=rate_functions.ease_out_bounce
        )


        mask_group.move_to(UP*3.0)
        self.play(FadeIn(mask_group), run_time=0.3)
        self.play(
            mask_group.animate.move_to(mask_pos),
            run_time=0.8,
            rate_func=smooth
        )


        # Light on
        self.add(cone, rays)
        self.play(FadeIn(lamp_group, scale=0.8), run_time=0.5)
        self.play(cone.animate.set_opacity(1.0), rays.animate.set_opacity(1.0), run_time=0.35)

        # Animate rays (downward pulsing)
        self.play(ray_phase.animate.increment_value(10*TAU), run_time=3.0, rate_func=linear)

        # Light off
        self.play(cone.animate.set_opacity(0.0), rays.animate.set_opacity(0.0), run_time=0.4)


        self.wait(0.3)
