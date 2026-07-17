from recipe_handler import RecipeHandler, RecipeNotFound
import pytest

@pytest.fixture
def handler():
    return RecipeHandler("recipesTest.csv")

def test_loads_all_recipes(handler):
    recipes = handler.get_all_recipes()
    assert len(recipes) == 5

def test_get_recipe_by_id(handler):
    recipe = handler.get_recipe_by_id(1)
    assert recipe.name == "Nachos Supreme"

def test_get_recipe_by_id_no_recipe(handler):
    with pytest.raises(RecipeNotFound):
        handler.get_recipe_by_id(999)

def test_get_recipes_by_tag(handler):
    comfort = "comfort"
    results = handler.get_recipes_by_tag(comfort)
    assert all("comfort" in r.tags for r in results)
    names = {r.name for r in results}
    assert names == {"Spaghetti Bolognese", "Grilled Cheese"}

def test_get_recipes_by_tag_nonexistent_tag(handler):
    loremipsum = "lorem ipsum"
    recipe_collection = handler.get_recipes_by_tag(loremipsum)
    assert recipe_collection == []

    def test_add_recipe_persists(tmp_path):
        csv_file = tmp_path / "recipes.csv"
        csv_file.write_text(
            "id,name,ingredients,steps,tags\n"
            "1,Nachos,chips|cheese,bake it,quick|snack\n",
            encoding="utf-8",
        )
        handler = RecipeHandler(str(csv_file))
        handler.add_recipe("Tacos", ["shells", "beef"], ["cook", "fill"], ["dinner"])

        #reload
        reloaded = RecipeHandler(str(csv_file))
        assert len(reloaded.get_all_recipes()) == 2
        assert reloaded.get_recipe_by_id(2).name == "Tacos"