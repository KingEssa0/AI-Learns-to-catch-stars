import random


class CatchStars:
    WIDTH = 480
    HEIGHT = 600
    FPS = 60
    BASKET_WIDTH = 84
    BASKET_Y = 550
    BASKET_SPEED = 7
    STAR_RADIUS = 10
    STAR_SPEED = 5
    MAX_MISSES = 3

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.reset()

    def _spawn_star(self):
        self.star_x = self.rng.randint(self.STAR_RADIUS, self.WIDTH - self.STAR_RADIUS)
        self.star_y = -self.STAR_RADIUS

    def reset(self, seed=None):
        if seed is not None:
            self.rng.seed(seed)
        self.basket_x = self.WIDTH / 2
        self.score = 0
        self.misses = 0
        self.done = False
        self._spawn_star()
        return self.get_state()

    def get_state(self):
        offset = self.star_x - self.basket_x
        distance = self.BASKET_Y - self.star_y
        return (offset / self.WIDTH, distance / self.HEIGHT)

    def step(self, action):
        if action not in (0, 1, 2):
            raise ValueError("Use 0 to stay, 1 to move left, or 2 to move right")
        if self.done:
            raise RuntimeError("Call reset() before stepping again")

        direction = (0, -1, 1)[action]
        half_width = self.BASKET_WIDTH / 2
        self.basket_x += direction * self.BASKET_SPEED
        self.basket_x = max(half_width, min(self.WIDTH - half_width, self.basket_x))
        self.star_y += self.STAR_SPEED

        reward = 0
        if self.star_y + self.STAR_RADIUS >= self.BASKET_Y:
            if abs(self.star_x - self.basket_x) <= half_width + self.STAR_RADIUS:
                self.score += 1
                reward = 1
            else:
                self.misses += 1
                reward = -1
            self.done = self.misses >= self.MAX_MISSES
            if not self.done:
                self._spawn_star()

        info = {"score": self.score, "misses": self.misses}
        return self.get_state(), reward, self.done, info


def draw(game, pg, screen, font):
    screen.fill((20, 24, 52))
    left = round(game.basket_x - game.BASKET_WIDTH / 2)
    basket = (left, game.BASKET_Y, game.BASKET_WIDTH, 22)
    pg.draw.rect(screen, (107, 205, 241), basket, border_radius=6)

    x = round(game.star_x)
    y = round(game.star_y)
    points = [(x, y - 12), (x + 5, y - 4), (x + 12, y), (x + 5, y + 4), (x, y + 12), (x - 5, y + 4), (x - 12, y), (x - 5, y - 4)]
    pg.draw.polygon(screen, (255, 218, 94), points)

    white = (244, 245, 255)
    score = font.render(f"Score: {game.score}    Misses: {game.misses}/{game.MAX_MISSES}", True, white)
    screen.blit(score, (18, 18))
    if game.done:
        message = font.render("Game over. Press R to restart.", True, white)
    else:
        message = font.render("Left and right arrows to move", True, white)
    screen.blit(message, message.get_rect(center=(game.WIDTH // 2, game.HEIGHT - 15)))
    pg.display.flip()


def main():
    import pygame as pg

    pg.init()
    game = CatchStars()
    screen = pg.display.set_mode((game.WIDTH, game.HEIGHT))
    pg.display.set_caption("Catch the Falling Stars")
    clock = pg.time.Clock()
    font = pg.font.Font(None, 28)

    try:
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
                    if event.key == pg.K_r:
                        game.reset()

            if not game.done:
                keys = pg.key.get_pressed()
                action = 0
                if keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
                    action = 1
                elif keys[pg.K_RIGHT] and not keys[pg.K_LEFT]:
                    action = 2
                game.step(action)

            draw(game, pg, screen, font)
            clock.tick(game.FPS)
    finally:
        pg.quit()


if __name__ == "__main__":
    main()
