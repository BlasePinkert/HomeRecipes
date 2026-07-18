import csv
from dataclasses import dataclass, field

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
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.recipes: dict[int, Recipe] = {}
        self._load_from_csv()
        self._next_id = max(self.recipes, default=0) + 1


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

#TODO address latent bug where id creation doesn't follow intended behavior if I delete max id recipe, followed by a recipe write, the new write after the delete of max id recipe will reuse that id
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
        # list(self.recipes.values() is what's currently in memory
        # [recipe] is the newly minted recipe from above
        recipes_to_add = list(self.recipes.values()) + [recipe]
        # new recipe is not currently committed to our source of truth in memory, but is prepped to be have full file written to csv
        # writing to csv
        self._write_to_csv(recipes_to_add)
        #now that write is done, grab back into memory from disk and iterate next_id
        self.recipes[recipe.id] = recipe
        self._next_id += 1
        return recipe

    def delete_recipe(self, id):

        if id not in self.recipes:
            raise RecipeNotFound(f"no recipe with id: {id}")

        to_be_deleted = self.recipes[id]
        remaining_recipes = [recipe for recipe in  self.recipes.values() if recipe.id != id]

        self._write_to_csv(remaining_recipes)
        del self.recipes[id]
        return to_be_deleted





