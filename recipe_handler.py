import csv
from dataclasses import dataclass, field

@dataclass
class Recipe:
    id: int
    name: str
    ingredients: list[str]
    steps: list[str]
    tags: list[str] = field(default_factory=list)

class RecipeNotFound(Exception):
    pass

class RecipeHandler:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.recipes: dict[int, Recipe] = {}
        self._load_from_csv()
        self._next_id = max(self.recipes, default=0) + 1
        self._write_to_csv()

    def _load_from_csv(self):
        with open(self.csv_path, newline='', encoding='utf-8') as recipecsv:
            reader = csv.DictReader(recipecsv)

            for row in reader:
                recipe = Recipe(
                    id = int(row["id"]),
                    name = row["name"],
                    ingredients = row["ingredients"].split('|'),
                    steps = row["steps"].split('|'),
                    tags = row["tags"].split('|'),
                )
                self.recipes[recipe.id] = recipe

    def _write_to_csv(self,recipes):
        fieldnames = ['id', 'name', 'ingredients', 'steps', 'tags']
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as recipecsv:
            writer = csv.DictWriter(recipecsv, fieldnames=fieldnames)
            writer.writeheader()
            for recipe in recipes:
                writer.writerow({
                    'id':recipe.id,
                    'name': recipe.name,
                    'ingredients': '|'.join(recipe.ingredients),
                    'steps': '|'.join(recipe.steps),
                    'tags':'|'.join(recipe.tags),
                })

    def get_recipe_by_id(self,id):
        if id in self.recipes:
            return self.recipes[id]
        else:
            raise RecipeNotFound(f"No Recipe with id {id}")

    def get_all_recipes(self):
        recipe_collection = list(self.recipes.values())
        return recipe_collection

    # def get_recipes_by_tag(self, tag):
    #     return [recipe for recipe in self.recipes.values() if tag in recipe.tags]
    def get_recipes_by_tag(self, tag):
        recipe_collection = []
        for recipe in self.recipes.values():
            if tag in recipe.tags:
                recipe_collection.append(recipe)
        return recipe_collection

    def add_recipe(self, name, ingredients, steps, tags):
        #construct new recipe
        recipe = Recipe(
            #Mint new id with _next_id
                id = self._next_id,
                name = name,
                ingredients = ingredients,
                steps = steps,
                tags = tags,
        )
        #write to CSV

        ####

        #wait to add and iterate self._next_id until after the write finishes
        self.recipes[recipe.id] = recipe
        self._next_id += 1
        return recipe


