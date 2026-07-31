
from app import create_app
from recipe_handler import RecipeHandler
from pathlib import Path

#DATA_FILE = Path(__file__).parent / "data" / "recipes.csv"
handler = RecipeHandler("data/recipes.db")


if __name__ == '__main__':
    #DATA_FILE
    handler
    app = create_app(handler)
    app.run(debug=True)
