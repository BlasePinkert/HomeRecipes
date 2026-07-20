from recipe_handler import RecipeHandler, Recipe, RecipeNotFound, InvalidRecipe
import pytest

@pytest.fixture
def handler():
    return RecipeHandler(".data/recipesTest.csv")

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

def test_added_recipe_id_iterated(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler = RecipeHandler(str(csv_file))
    handler.add_recipe("Tacos", ["shells", "beef"], ["cook", "fill"], ["dinner"])
    reloaded = RecipeHandler(str(csv_file))
    assert reloaded.get_recipe_by_id(2).id == 2

    handler.add_recipe("Burgers", ["buns", "beef"], ["cook", "fill"], ["dinner"])
    reloaded = RecipeHandler(str(csv_file))
    assert reloaded.get_recipe_by_id(3).id == 3
    handler.add_recipe("Steak", ["beef"], ["cook"], ["dinner"])
    reloaded = RecipeHandler(str(csv_file))
    assert reloaded.get_recipe_by_id(4).id == 4
    assert reloaded.get_recipe_by_id(3).name == "Burgers"
    assert reloaded.get_recipe_by_id(2).name == "Tacos"
    assert reloaded.get_recipe_by_id(1).name == "Nachos"

def test_recipe_happy_path():
    recipe=Recipe(id=1, name='Scotch on the rocks', ingredients=['scotch', 'ice'], steps=['pour over ice','drink'], tags=['drunk'])
    assert recipe.name == 'Scotch on the rocks'

def test_recipe_name_strip():
    recipe=Recipe(id=1, name='   Scotch on the rocks   ', ingredients=['scotch', 'ice'], steps=['pour over ice','drink'], tags=['drunk'])
    assert recipe.name == 'Scotch on the rocks'

def test_recipe_empty_name():
    with pytest.raises(InvalidRecipe):
        Recipe(id=1, name='   ', ingredients=['scotch', 'ice'], steps=['pour over ice','drink'], tags=['drunk'])

def test_recipe_empty_ing_list():
    with pytest.raises(InvalidRecipe):
        Recipe(id=1, name='Scotch on the rocks', ingredients=[], steps=['pour over ice','drink'], tags=['drunk'])

def test_recipe_empty_ing_string():
    with pytest.raises(InvalidRecipe):
        Recipe(id=1, name='Scotch on the rocks', ingredients=['scotch', ''], steps=['pour over ice','drink'], tags=['drunk'])

def test_recipe_empty_steps_list():
    with pytest.raises(InvalidRecipe):
        Recipe(id=1, name='Scotch on the rocks', ingredients=['scotch','ice'], steps=[], tags=['drunk'])

def test_recipe_empty_step_string():
    with pytest.raises(InvalidRecipe):
        Recipe(id=1, name='Scotch on the rocks', ingredients=['scotch', 'ice'], steps=['','drink'], tags=['drunk'])

def test_recipe_empty_tag_string():
    with pytest.raises(InvalidRecipe):
        Recipe(id=1, name='Scotch on the rocks', ingredients=['scotch', 'ice'], steps=['pour over ice','drink'], tags=[''])

def test_delete_recipe(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n"
        "2,Tacos,chips|cheese,bake it,quick|snack\n"
        "3,Burgers,chips|cheese,bake it,quick|snack\n"
        "4,Steak,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler = RecipeHandler(str(csv_file))
    assert len(handler.get_all_recipes()) == 4
    handler.delete_recipe(3)
    reloaded = RecipeHandler(str(csv_file))
    assert len(reloaded.get_all_recipes()) == 3

def test_delete_recipe_raise(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n"
        "2,Tacos,chips|cheese,bake it,quick|snack\n"
        "3,Burgers,chips|cheese,bake it,quick|snack\n"
        "4,Steak,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler = RecipeHandler(str(csv_file))
    with pytest.raises(RecipeNotFound):
        handler.delete_recipe(999)

def test_middle_delete_followed_by_add_for_correct_id(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n"
        "2,Tacos,chips|cheese,bake it,quick|snack\n"
        "3,Burgers,chips|cheese,bake it,quick|snack\n"
        "4,Steak,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler = RecipeHandler(str(csv_file))
    handler.delete_recipe(2)
    reloaded = RecipeHandler(str(csv_file))
    reloaded.add_recipe("Boogers", ["Boogers", "Snot"], ["cook", "fill"], ["dinner"])
    with pytest.raises(RecipeNotFound):
        reloaded.delete_recipe(2)
    assert reloaded.get_recipe_by_id(5).name == "Boogers"

def test_edit_recipe_with_bad_id(handler):
    with pytest.raises(RecipeNotFound):
        handler.edit_recipe(99999999)

def test_edit_recipe_with_empty_changes(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n"
        "2,Tacos,chips|cheese,bake it,quick|snack\n"
        "3,Burgers,chips|cheese,bake it,quick|snack\n"
        "4,Steak,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler=RecipeHandler(str(csv_file))
    original_recipe = handler.get_recipe_by_id(1)
    empty_updates_recipe = handler.edit_recipe(1)
    assert original_recipe == empty_updates_recipe

def test_edit_recipe_with_all_changes(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n"
        "2,Tacos,chips|cheese,bake it,quick|snack\n"
        "3,Burgers,chips|cheese,bake it,quick|snack\n"
        "4,Steak,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler=RecipeHandler(str(csv_file))
    original_recipe = handler.get_recipe_by_id(3)
    updated_recipe = handler.edit_recipe(3,"BURGERS!",["beef","buns","cheese"],["light grill","form patties","grill 10 minutes or until internal temp is 140"],["grilling","beef", "not healthy"])
    assert original_recipe != updated_recipe
    assert updated_recipe.id == original_recipe.id
    assert updated_recipe.name == "BURGERS!"
    assert updated_recipe.ingredients == ["beef","buns","cheese"]
    assert updated_recipe.steps == ["light grill", "form patties", "grill 10 minutes or until internal temp is 140"]
    assert updated_recipe.tags == ["grilling", "beef","not healthy"]

def test_edit_recipe_ingredients(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n"
        "2,Tacos,chips|cheese,bake it,quick|snack\n"
        "3,Burgers,chips|cheese,bake it,quick|snack\n"
        "4,Steak,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler=RecipeHandler(str(csv_file))
    original_recipe = handler.get_recipe_by_id(3)
    updated_recipe = handler.edit_recipe(3,ingredients=["beef","buns","cheese"])
    assert original_recipe != updated_recipe
    assert original_recipe.id == updated_recipe.id
    assert updated_recipe.name == "Burgers"
    assert updated_recipe.ingredients == ["beef","buns","cheese"]


def test_edit_recipe_steps(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n"
        "2,Tacos,chips|cheese,bake it,quick|snack\n"
        "3,Burgers,chips|cheese,bake it,quick|snack\n"
        "4,Steak,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler=RecipeHandler(str(csv_file))
    original_recipe = handler.get_recipe_by_id(3)
    updated_recipe = handler.edit_recipe(3,steps=["light grill","form patties","grill 10 minutes or until internal temp is 140"])
    assert original_recipe != updated_recipe
    assert original_recipe.id == updated_recipe.id
    assert updated_recipe.name == original_recipe.name
    assert updated_recipe.ingredients == original_recipe.ingredients
    assert updated_recipe.tags == original_recipe.tags
    assert updated_recipe.steps == ["light grill", "form patties", "grill 10 minutes or until internal temp is 140"]


def test_edit_recipe_tags(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n"
        "2,Tacos,chips|cheese,bake it,quick|snack\n"
        "3,Burgers,chips|cheese,bake it,quick|snack\n"
        "4,Steak,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler=RecipeHandler(str(csv_file))
    original_recipe = handler.get_recipe_by_id(3)
    updated_recipe = handler.edit_recipe(3,tags=["grilling","beef", "not healthy"])
    assert original_recipe != updated_recipe
    assert updated_recipe.name == original_recipe.name
    assert updated_recipe.ingredients == original_recipe.ingredients
    assert updated_recipe.steps == original_recipe.steps
    assert updated_recipe.tags == ["grilling", "beef","not healthy"]

def test_edit_recipe_empty_tags(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n"
        "2,Tacos,chips|cheese,bake it,quick|snack\n"
        "3,Burgers,chips|cheese,bake it,quick|snack\n"
        "4,Steak,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler=RecipeHandler(str(csv_file))
    original_recipe = handler.get_recipe_by_id(3)
    updated_recipe = handler.edit_recipe(3,tags=[])
    assert original_recipe != updated_recipe
    assert updated_recipe.name == "Burgers"
    assert updated_recipe.ingredients == ["chips","cheese"]
    assert updated_recipe.steps == original_recipe.steps
    assert updated_recipe.tags == []

def test_edit_recipe_invalid_ingredients_raises(tmp_path):
    csv_file = tmp_path / "recipes.csv"
    csv_file.write_text(
        "id,name,ingredients,steps,tags\n"
        "1,Nachos,chips|cheese,bake it,quick|snack\n",
        encoding="utf-8",
    )
    handler=RecipeHandler(str(csv_file))
    with pytest.raises(InvalidRecipe):
        handler.edit_recipe(1,ingredients=[])
