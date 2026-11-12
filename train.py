import argparse
import json
import random
from pathlib import Path

from catch_stars import CatchStars


ACTION_REPEAT = 5
LEARNING_RATE = 0.2
DISCOUNT = 0.97


def state_key(state):
    offset, distance = state
    return f"{round(offset * 24)},{round(distance * 12)}"


def choose_action(table, state, rng, epsilon=0.0):
    if rng.random() < epsilon:
        return rng.randrange(3)
    values = table.get(state_key(state), [0.0, 0.0, 0.0])
    best = max(values)
    return rng.choice([action for action, value in enumerate(values) if value == best])


def advance(game, action):
    for _ in range(ACTION_REPEAT):
        state, reward, done, _ = game.step(action)
        if reward or done:
            break
    return state, reward


def train(episodes, seed):
    rng = random.Random(seed)
    game = CatchStars(seed=seed)
    table = {}
    for episode in range(episodes):
        state = game.reset()
        epsilon = max(0.05, 0.8 * (1 - episode / episodes))
        while True:
            action = choose_action(table, state, rng, epsilon)
            next_state, reward = advance(game, action)
            values = table.setdefault(state_key(state), [0.0, 0.0, 0.0])
            target = reward
            if not reward:
                progress = abs(state[0]) - abs(next_state[0])
                future = max(table.get(state_key(next_state), [0.0, 0.0, 0.0]))
                target = 0.5 * progress + DISCOUNT * future
            values[action] += LEARNING_RATE * (target - values[action])
            if reward:
                break
            state = next_state
    return table


def catch_rate(table, seed, trials=200, epsilon=0.0):
    game = CatchStars(seed=seed)
    rng = random.Random(seed)
    catches = 0
    for _ in range(trials):
        state = game.reset()
        while True:
            action = choose_action(table, state, rng, epsilon)
            state, reward = advance(game, action)
            if reward:
                catches += int(reward == 1)
                break
    return catches / trials


def main():
    parser = argparse.ArgumentParser(description="Train a Q-learning agent to catch falling stars.")
    parser.add_argument("--episodes", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("q_table.json"))
    args = parser.parse_args()
    if args.episodes < 1:
        parser.error("--episodes must be at least 1")

    table = train(args.episodes, args.seed)
    evaluation_seed = args.seed + 100000
    baseline = catch_rate({}, evaluation_seed, epsilon=1.0)
    trained = catch_rate(table, evaluation_seed)
    model = {"action_repeat": ACTION_REPEAT, "q_table": table}
    args.output.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
    print(f"Random catch rate: {baseline:.1%}")
    print(f"Trained catch rate: {trained:.1%}")
    print(f"Saved {len(table)} learned states to {args.output}")


if __name__ == "__main__":
    main()
