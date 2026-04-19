import json
import os

MODEL_PATH = "user_preferences.json"

DEFAULT_MODEL = {
    "time_weight": 0.5,
    "distance_weight": 0.5,
    "history": []
}


def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "r") as f:
            return json.load(f)
    return DEFAULT_MODEL.copy()


def save_model(model):
    with open(MODEL_PATH, "w") as f:
        json.dump(model, f, indent=2)


def recommend_route(results, model):

    best_score = float("inf")
    best_algo = None

    for name, result in results.items():

        score = (
            model["time_weight"] * result["total_time_minutes"] +
            model["distance_weight"] * result["total_distance_km"]
        )

        if score < best_score:
            best_score = score
            best_algo = name

    return best_algo


def learn_from_choice(results, chosen_algo):

    model = load_model()
    chosen = results[chosen_algo]

    avg_time = sum(r["total_time_minutes"] for r in results.values()) / len(results)
    avg_dist = sum(r["total_distance_km"] for r in results.values()) / len(results)

    if chosen["total_time_minutes"] < avg_time:
        model["time_weight"] += 0.05

    if chosen["total_distance_km"] < avg_dist:
        model["distance_weight"] += 0.05

    total = model["time_weight"] + model["distance_weight"]

    model["time_weight"] /= total
    model["distance_weight"] /= total

    model["history"].append(chosen_algo)

    save_model(model)

    return model
