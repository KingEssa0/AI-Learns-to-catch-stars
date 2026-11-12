from train import state_key


class PolicyVisualizer:
    WIDTH = 460
    ACTIONS = ("Stay", "Left", "Right")

    def __init__(self, pg):
        self.pg = pg
        self.title = pg.font.Font(None, 36)
        self.font = pg.font.Font(None, 24)
        self.small = pg.font.Font(None, 20)
        self.decision = None

    def record(self, table, state, action):
        key = state_key(state)
        values = tuple(table.get(key, (0.0, 0.0, 0.0)))
        self.decision = (state, key, values, action, key in table)

    def draw(self, surface, paused=False, done=False):
        pg = self.pg
        surface.fill((15, 22, 38))
        ink = (234, 241, 255)
        muted = (159, 178, 207)
        green = (102, 230, 170)
        red = (242, 132, 140)
        blue = (118, 179, 249)
        gray = (79, 99, 129)

        def label(text, x, y, color=ink, font=None):
            surface.blit((font or self.font).render(text, True, color), (x, y))

        label("Live agent decisions", 24, 23, ink, self.title)
        label("Catch Stars Q-learning policy", 24, 62, muted)
        if self.decision is None:
            label("Waiting for the first move", 24, 117, muted)
            return

        state, key, values, action, known = self.decision
        label("INPUTS", 24, 125, muted, self.small)
        label("ACTIVE STATE", 177, 125, muted, self.small)
        label("ACTION VALUES", 321, 125, muted, self.small)
        left = [(70, 244), (70, 352)]
        center = (224, 298)
        right = [(322, 205), (322, 298), (322, 391)]
        for point in left:
            pg.draw.line(surface, gray, point, center, 2)

        scale = max(0.01, *(abs(value) for value in values))
        for index, point in enumerate(right):
            value = values[index]
            color = green if value > 0 else red if value < 0 else gray
            width = 1 + round(4 * abs(value) / scale)
            pg.draw.line(surface, color, center, point, width)
            pg.draw.circle(surface, color, point, 9)
            if index == action:
                pg.draw.circle(surface, ink, point, 14, 2)
            label(self.ACTIONS[index], 347, point[1] - 18)
            label(f"{value:+.3f}", 347, point[1] + 6, color, self.small)

        for point in left:
            pg.draw.circle(surface, blue, point, 10)
        pg.draw.circle(surface, blue, center, 14)
        label("Star offset", 24, 204)
        label(f"{state[0]:+.3f}", 24, 264, muted, self.small)
        label("Fall distance", 24, 312)
        label(f"{state[1]:.3f}", 24, 372, muted, self.small)
        label(key, 185, 323, muted, self.small)
        label(f"Chosen move: {self.ACTIONS[action]}", 24, 452, green)
        status = "Round finished" if done else "Paused" if paused else "Showing inputs at the last decision"
        label(status, 24, 487, muted, self.small)
        if not known:
            label("Unseen state. All actions start tied at zero.", 24, 515, muted, self.small)
        label("Space: pause   R: restart   Esc: quit", 24, 560, muted, self.small)
