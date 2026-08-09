
from app import create_app
from recipe_handler import RecipeHandler
from pathlib import Path
from user_handler import UserHandler

DB_PATH = Path(__file__).parent / "data" / "recipes.db"

if __name__ == '__main__':
    recipe_handler = RecipeHandler(str(DB_PATH))
    user_handler = UserHandler(str(DB_PATH))
    app = create_app(recipe_handler, user_handler)
    app.run(debug=True)
