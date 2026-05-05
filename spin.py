from manim import *
import numpy as np

class SpinCoatedWafer2D(Scene):
    def construct(self):
        self.camera.background_color = BLACK

        a, b = 3.0, 1.3
        center = ORIGIN

        wafer = Ellipse(width=2*a, height=2*b).move_to(center)
        wafer.set_fill(GRAY_E, opacity=1)
        wafer.set_stroke(WHITE, width=4)

        # Resist (delayed)
        resist = Ellipse(width=1.0, height=0.45).move_to(center)
        resist.set_fill(RED, opacity=0.0)
        resist.set_stroke(width=0)

        # Helpers
        def ept(rx, ry, t):
            return center + np.array([rx*np.cos(t), ry*np.sin(t), 0.0])

        def etan(rx, ry, t):
            return np.array([-rx*np.sin(t), ry*np.cos(t), 0.0])

        # Arrows behind wafer
        rx, ry = a + 1.25, b + 0.9

        def curved_arrow(t0, t1, stroke_w=3):
            arc = ParametricFunction(lambda t: ept(rx, ry, t), t_range=[t0, t1])
            arc.set_stroke(WHITE, width=stroke_w)

            end = ept(rx, ry, t1)
            tan = etan(rx, ry, t1)

            tip = Triangle().scale(0.12).set_fill(WHITE, 1).set_stroke(width=0)
            tip.move_to(end)
            tip.rotate(angle_of_vector(tan) - PI/2)
            return VGroup(arc, tip)

        arrows = VGroup(
            curved_arrow(0.30*PI, 0.75*PI, stroke_w=3),
            curved_arrow(1.30*PI, 1.75*PI, stroke_w=3),
        ).set_opacity(0.85)

        # ---- Spin drivers ----
        theta = ValueTracker(0.0)
        spin_rate = ValueTracker(TAU * 1.2)  # start slower

        # CRITICAL: add trackers to the scene so their updaters run
        self.add(theta, spin_rate)

        theta.add_updater(lambda m, dt: m.increment_value(spin_rate.get_value() * dt))

        notch = always_redraw(lambda: self._notch(a, b, theta.get_value(), center))
        radial = always_redraw(lambda: self._radial_line(a, b, theta.get_value(), center))

        # Clipped-looking highlight that rotates (no boolean ops)
        highlight = always_redraw(lambda: self._soft_highlight(a, b, theta.get_value(), center))

        # Draw order
        self.add(wafer, highlight, resist, notch)

        # Spin-up (ramp RPM)
        self.play(spin_rate.animate.set_value(TAU * 3.0), run_time=1.2)

        # Resist appears later
        self.play(resist.animate.set_opacity(0.85), run_time=0.35)
        self.wait(0.1)

        # Spread while spinning
        self.play(resist.animate.scale(4.5).set_opacity(0.25), run_time=3, rate_func=linear)
        self.wait(0.8)

        #theta.clear_updaters()

    def _notch(self, a, b, t, center):
        pos = center + np.array([a*np.cos(t), b*np.sin(t), 0.0])
        tan = np.array([-a*np.sin(t), b*np.cos(t), 0.0])
        ang = angle_of_vector(tan)

        n = Triangle().scale(0.12).set_fill(YELLOW, 1).set_stroke(width=0)
        n.move_to(pos)
        n.rotate(ang)
        return n

    def _radial_line(self, a, b, t, center):
        """
        Short rim tick that rotates (spin cue) without drawing a long line
        through the wafer.
        """
        r_outer = 0.98
        r_inner = 0.85

        p_outer = center + np.array([r_outer*a*np.cos(t), r_outer*b*np.sin(t), 0.0])
        p_inner = center + np.array([r_inner*a*np.cos(t), r_inner*b*np.sin(t), 0.0])

        return Line(p_inner, p_outer).set_stroke(WHITE, width=2, opacity=0.35)


    def _soft_highlight(self, a, b, t, center):
        """
        Highlight band guaranteed to stay inside the ellipse for any angle.
        We create the band in a coordinate frame rotated by -(t + base_angle),
        clip it to the ellipse there, then rotate the finished band back.
        """
        base_angle = 25 * DEGREES

        # Band parameters in the band's own frame
        y0 = 0.10
        half_thick = 0.16
        n_lines = 30

        # Rotation that defines the band orientation
        phi = t + base_angle

        def alpha_profile(u):
            return 0.12 * np.exp(-3.0 * (u ** 2))

        band = VGroup()

        # Build in band-frame coordinates (x', y')
        for i in range(n_lines):
            u = -1 + 2 * (i / (n_lines - 1))
            y_prime = y0 + u * half_thick

            # For each scanline in band frame, find where it intersects the ellipse.
            # Using substitution with rotation:
            # x = x' cosφ - y' sinφ
            # y = x' sinφ + y' cosφ
            # Plug into (x/a)^2 + (y/b)^2 = 1 gives quadratic in x'.
            c = np.cos(phi)
            s = np.sin(phi)

            A = (c*c)/(a*a) + (s*s)/(b*b)
            B = 2 * y_prime * c * s * (1/(b*b) - 1/(a*a))
            C = (y_prime*y_prime) * ((s*s)/(a*a) + (c*c)/(b*b)) - 1

            disc = B*B - 4*A*C
            if disc <= 0:
                continue

            x1 = (-B - np.sqrt(disc)) / (2*A)
            x2 = (-B + np.sqrt(disc)) / (2*A)

            # Endpoints in world coordinates
            p1 = center + np.array([x1*c - y_prime*s, x1*s + y_prime*c, 0.0])
            p2 = center + np.array([x2*c - y_prime*s, x2*s + y_prime*c, 0.0])

            seg = Line(p1, p2)
            seg.set_stroke(WHITE, width=6, opacity=alpha_profile(u))
            band.add(seg)

        return band
