import argparse
import json
import random
from pathlib import Path

from catch_stars import CatchStars, draw
from train import choose_action


def load_model(path):
    model = json.loads(path.read_text(encoding="utf-8"))
    repeat = model["action_repeat"]
    table = model["q_table"]
    if type(repeat) is not int or repeat < 1 or not isinstance(table, dict) or not table:
        raise ValueError("Invalid model. Run train.py to create a new one.")
    return table, repeat


def main():
    parser = argparse.ArgumentParser(description="Watch the trained Catch Stars agent.")
    parser.add_argument("--model", type=Path, default=Path(__file__).with_name("q_table.json"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    try:
        table, repeat = load_model(args.model)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(f"Could not load {args.model}. Run python3 train.py first. {error}")

    import pygame as pg

    pg.init()
    try:
        game = CatchStars(seed=args.seed)
        rng = random.Random(args.seed)
        screen = pg.display.set_mode((game.WIDTH, game.HEIGHT))
        pg.display.set_caption("Catch Stars — Watch the Trained Agent")
        clock = pg.time.Clock()
        font = pg.font.Font(None, 28)
        action = 0
        frames_left = 0
        paused = False

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
                    if event.key == pg.K_SPACE:
                        paused = not paused
                    if event.key == pg.K_r:
                        game.reset()
                        frames_left = 0
                        paused = False

            if not paused and not game.done:
                if frames_left == 0:
                    action = choose_action(table, game.get_state(), rng)
                    frames_left = repeat
                _, reward, _, _ = game.step(action)
                frames_left -= 1
                if reward:
                    frames_left = 0

            draw(game, pg, screen, font)
            clock.tick(game.FPS)
    finally:
        pg.quit()


if __name__ == "__main__":
    main()
