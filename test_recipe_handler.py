from recipe_handler import RecipeHandler, RecipeNotFound
import pytest

def test_loads_all_recipes():
    handler =RecipeHandler("recipesTest.csv")
    recipes = handler.get_all_recipes()
    assert len(recipes) == 5

def test_get_recipe_by_id():
    handler = RecipeHandler("recipesTest.csv")
    recipe = handler.get_recipe_by_id(1)
    assert recipe.name == "Nachos Supreme"

def test_get_recipe_by_id_no_recipe():
    handler = RecipeHandler("recipesTest.csv")
    with pytest.raises(RecipeNotFound):
        recipe = handler.get_recipe_by_id(999)

def test_get_recipes_by_tag():
    comfort = "comfort"
    handler = RecipeHandler("recipesTest.csv")
    recipe_collection = handler.get_recipes_by_tag(comfort)
    assert len(recipe_collection) == 2

def test_get_recipes_by_tag_nonexistent_tag():
    loremipsum = "lorem ipsum"
    handler = RecipeHandler("recipesTest.csv")
    recipe_collection = handler.get_recipes_by_tag(loremipsum)
    assert recipe_collection == []