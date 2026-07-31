import csv
from dataclasses import dataclass, field
import sqlite3


@dataclass
class Recipe:
    id: int
    name: str
    ingredients: list[str]
    steps: list[str]
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        #sanitizing and normalizing data
        self.name = self.name.strip()
        self.ingredients = [item.strip() for item in self.ingredients]
        self.steps = [item.strip() for item in self.steps]
        self.tags = [item.strip() for item in self.tags]

        #Validating sanitized and normalized data
        if not self.name:
            raise InvalidRecipe("Invalid Recipe Name")
        if not self.ingredients: #Checking for an empty list
            raise InvalidRecipe("Recipe needs at least one Ingredient")
        if any(not item for item in self.ingredients): #checking for any element in the list that may be an empty string
            raise InvalidRecipe("Ingredient can't contain empty values")
        if not self.steps: #Checking for an empty list
            raise InvalidRecipe("Recipe needs at least one Step")
        if any(not item for item in self.steps): #checking for any element in the list that may be an empty string
            raise InvalidRecipe("Steps can't contain empty steps")
        if any(not item for item in self.tags): #only checking for empty string tags, as tags can be an empty list
            raise InvalidRecipe("Tags can't contain empty values")

class RecipeNotFound(Exception):
    pass

class InvalidRecipe(Exception):
    pass

class RecipeHandler:
    def __init__(self, db_path):
        self.db_path = db_path
    # def __init__(self, csv_path: str):
    #     self.csv_path = csv_path
    #     self.recipes: dict[int, Recipe] = {}
    #     self._load_from_csv()
    #     self._next_id = max(self.recipes, default=0) + 1

    #
    # def _load_from_csv(self):
    #     with open(self.csv_path, newline='', encoding='utf-8') as recipecsv:
    #         reader = csv.DictReader(recipecsv)
    #
    #         for row in reader:
    #             recipe = Recipe(
    #                 id = int(row["id"]),
    #                 name = row["name"],
    #                 ingredients = row["ingredients"].split('|'),
    #                 steps = row["steps"].split('|'),
    #                 tags = row["tags"].split('|'),
    #             )
    #             self.recipes[recipe.id] = recipe
    #
    # def _write_to_csv(self,recipes):
    #     fieldnames = ['id', 'name', 'ingredients', 'steps', 'tags']
    #     with open(self.csv_path, 'w', newline='', encoding='utf-8') as recipecsv:
    #         writer = csv.DictWriter(recipecsv, fieldnames=fieldnames)
    #         writer.writeheader()
    #         for recipe in recipes:
    #             writer.writerow({
    #                 'id':recipe.id,
    #                 'name': recipe.name,
    #                 'ingredients': '|'.join(recipe.ingredients),
    #                 'steps': '|'.join(recipe.steps),
    #                 'tags':'|'.join(recipe.tags),
    #             })

    def get_recipe_by_id(self, id):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM recipes WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row is None:
                raise RecipeNotFound(f"No recipe with id {id}")
            name = row[0]

            cursor.execute("SELECT name FROM ingredients WHERE recipe_id = ?", (id,))
            ingredients = [r[0] for r in cursor.fetchall()]

            cursor.execute(
                "SELECT directions FROM steps WHERE recipe_id = ? ORDER BY position",
                (id,),
            )
            steps = [r[0] for r in cursor.fetchall()]

            cursor.execute(
                "SELECT tags.name FROM recipe_tags "
                "JOIN tags ON tags.id = recipe_tags.tag_id "
                "WHERE recipe_tags.recipe_id = ?",
                (id,),
            )
            tags = [r[0] for r in cursor.fetchall()]

            return Recipe(id=id, name=name, ingredients=ingredients, steps=steps, tags=tags)
        finally:
            conn.close()

    def get_all_recipes(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM recipes")
            ids = [r[0] for r in cursor.fetchall()]
        finally:
            conn.close()
        return [self.get_recipe_by_id(id) for id in ids]

    # def get_all_recipes(self):
    #     recipe_collection = list(self.recipes.values())
    #     return recipe_collection

    def get_recipes_by_tag(self, tag):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT recipe_tags.recipe_id FROM recipe_tags "
                "JOIN tags ON tags.id = recipe_tags.tag_id "
                "WHERE tags.name = ?",
                (tag,),
            )
            ids = [r[0] for r in cursor.fetchall()]
        finally:
            conn.close()
        return [self.get_recipe_by_id(id) for id in ids]

    def add_recipe(self, name, ingredients, steps, tags):
        #construct new recipe
        #constructing just to throw away, told it's a small code smell
        #to get rid of code smell, pull recipe validation out of post init
        #and into standalone function both data class and handler can call
        Recipe(id=0, name=name, ingredients=ingredients, steps=steps, tags=tags)
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO recipes (name) VALUES (?)", (name,))
            recipe_id = cursor.lastrowid
            for ingredient in ingredients:
                cursor.execute(
                    "INSERT INTO ingredients (recipe_id, name) VALUES (?, ?)",
                    (recipe_id, ingredient),
                )

            for position, step in enumerate(steps):
                cursor.execute(
                    "INSERT INTO steps (recipe_id, position, directions) VALUES (?, ?, ?)",
                    (recipe_id, position, step),
                )
            for tag in tags:
                cursor.execute("SELECT id FROM tags WHERE name = ?",(tag,))
                row = cursor.fetchone()
                if row is not None:
                    tag_id=row[0]
                else:
                    cursor.execute(
                        "INSERT INTO tags (name) VALUES (?)",
                        (tag,))
                    tag_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?,?)",
                    (recipe_id, tag_id),
                )
            conn.commit()
            return Recipe(id=recipe_id, name=name, ingredients=ingredients, steps=steps, tags=tags)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_recipe(self, id):
        to_be_deleted = self.get_recipe_by_id(id)
        conn = sqlite3.connect(self.db_path)

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE from ingredients WHERE recipe_id = ?", (id,))
            cursor.execute("DELETE from steps WHERE recipe_id = ?", (id,))
            cursor.execute("DELETE from recipe_tags WHERE recipe_id = ?", (id,))
            cursor.execute("DELETE from recipes WHERE id = ?", (id,))
            conn.commit()
            return to_be_deleted
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


    def edit_recipe(self, id, name=None, ingredients=None, steps=None, tags=None):
        recipe_to_update = self.get_recipe_by_id(id)
        #if argument not passed and defaulted to None, keep original value, else use new value
        new_name = name if name is not None else recipe_to_update.name
        new_ingredients = ingredients if ingredients is not None else recipe_to_update.ingredients
        new_steps = steps if steps is not None else recipe_to_update.steps
        new_tags = tags if tags is not None else recipe_to_update.tags
        Recipe(
                id = id,
                name = new_name,
                ingredients = new_ingredients,
                steps = new_steps,
                tags = new_tags,
        )

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            if name is not None:
                cursor.execute("UPDATE recipes SET name = ? WHERE id = ?",(name, id))
            if ingredients is not None:
                cursor.execute("DELETE FROM ingredients WHERE recipe_id = ?", (id,))
                for ingredient in ingredients:
                    cursor.execute(
                        "INSERT INTO ingredients (recipe_id, name) VALUES (?, ?)",
                        (id, ingredient)),
            if steps is not None:
                cursor.execute("DELETE FROM steps WHERE recipe_id = ?", (id,))
                for position, step in enumerate(steps):
                    cursor.execute(
                        "INSERT INTO steps (recipe_id, position, directions) VALUES (?, ?, ?)",
                        (id, position, step)),
            if tags is not None:
                cursor.execute("DELETE FROM recipe_tags WHERE recipe_id = ?", (id,))
                for tag in tags:
                    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                    row = cursor.fetchone()
                    if row is not None:
                        tag_id = row[0]
                    else:
                        cursor.execute(
                            "INSERT INTO tags (name) VALUES (?)",
                            (tag,)),
                        tag_id = cursor.lastrowid
                    cursor.execute(
                        "INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?,?)",
                        (id, tag_id)),

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return self.get_recipe_by_id(id)

