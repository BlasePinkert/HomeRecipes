from flask import Flask, jsonify, request
from dataclasses import asdict
from recipe_handler import RecipeHandler, RecipeNotFound, InvalidRecipe
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "recipes.csv"

app = Flask(__name__)
handler = RecipeHandler(str(DATA_FILE))


@app.route("/")
def home():
    return "HomeRecipes is running"

@app.route("/recipes/<int:id>")
def get_recipe(id):
    try:
        recipe = handler.get_recipe_by_id(id)
        return jsonify(asdict(recipe))
    except RecipeNotFound:
        return jsonify({"error": f"No Recipe with id {id}"}), 404

@app.route("/recipes")
#/recipes
#/recipes?tag=<value>
def get_recipes():
    tag = request.args.get("tag")
    if tag is None:
        recipe_collection = handler.get_all_recipes()
    else:
        recipe_collection = handler.get_recipes_by_tag(tag)

    recipe_dicts=[asdict(r) for r in recipe_collection]
    return jsonify(recipe_dicts)

@app.route("/recipes", methods=["POST"])
def add_recipe():
    data = request.get_json()
    try:
        recipe = handler.add_recipe(
            data["name"],
            data["ingredients"],
            data["steps"],
            data["tags"],
        )
        return jsonify(asdict(recipe)), 201

    except InvalidRecipe as e:
        return jsonify({"error": str(e)}),400
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}),400

@app.route("/recipes/<int:id>", methods=["DELETE"])
def delete_recipe(id):
    try:
        recipe = handler.delete_recipe(id)
        return jsonify(asdict(recipe)), 200
    except RecipeNotFound:
        return jsonify({"error": f"No recipe with id {id}"}), 404

@app.route("/recipes/<int:id>", methods=["PATCH"])
def edit_recipe(id):
    data = request.get_json()
    try:
        recipe = handler.edit_recipe(
            id,
            name=data.get("name"),
            ingredients=data.get("ingredients"),
            steps=data.get("steps"),
            tags=data.get("tags"),
        )
        return jsonify(asdict(recipe)), 200
    except RecipeNotFound as e:
        return jsonify({"error": str(e)}), 404
    except InvalidRecipe as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)