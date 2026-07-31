from recipe_handler import RecipeHandler, Recipe, RecipeNotFound, InvalidRecipe
from pathlib import Path
import pytest
import sqlite3

SCHEMA = Path(__file__).parent.parent / "schema.sql"

@pytest.fixture
def seeded_handler(tmp_path):
    db_path = tmp_path / "test.db"
    #create schema in the fresh temp db
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA.read_text())
    conn.commit()
    conn.close()
    recipe_handler = RecipeHandler(str(db_path))
    recipes =[
        recipe_handler.add_recipe("Nachos Supreme",["testIng"],["testStep"],["testTag"]),
        recipe_handler.add_recipe("Spaghetti Bolognese", ["testIng"], ["testStep"], ["testTag","comfort"]),
        recipe_handler.add_recipe("Grilled Cheese", ["testIng"], ["testStep"], ["testTag","comfort"]),
        recipe_handler.add_recipe("Burgers",["testIng"],["testStep"],["testTag"])
    ]
    return recipe_handler, recipes

@pytest.fixture
def empty_handler(tmp_path):
    db_path = tmp_path / "test.db"
    #create schema in the fresh temp db
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA.read_text())
    conn.commit()
    conn.close()
    return RecipeHandler(str(db_path))


# def test_loads_all_recipes(handler):
#     recipes = handler.get_all_recipes()
#     assert len(recipes) == 5

def test_get_recipe_by_id(empty_handler):
    created = empty_handler.add_recipe("Blargh",["testIng"],["testStep"],["testTag"])
    recipe = empty_handler.get_recipe_by_id(created.id)
    assert recipe.name == "Blargh"


def test_get_recipe_by_id_no_recipe(seeded_handler):
    handler, recipes = seeded_handler
    with pytest.raises(RecipeNotFound):
        handler.get_recipe_by_id(999)

def test_get_recipes_by_tag(seeded_handler):
    handler, recipes = seeded_handler
    comfort = "comfort"
    results = handler.get_recipes_by_tag(comfort)
    assert all("comfort" in r.tags for r in results)
    names = {r.name for r in results}
    assert names == {"Spaghetti Bolognese", "Grilled Cheese"}

def test_get_recipes_by_tag_nonexistent_tag(seeded_handler):
    handler, recipes = seeded_handler
    loremipsum = "lorem ipsum"
    recipe_collection = handler.get_recipes_by_tag(loremipsum)
    assert recipe_collection == []

def test_add_recipe_persists_across_handlers(empty_handler, tmp_path):
    created = empty_handler.add_recipe("Tacos", ["shells"], ["cook"], ["dinner"])
    # a completely fresh handler on the same db file — proves it hit disk, not just this connection
    fresh = RecipeHandler(empty_handler.db_path)
    assert fresh.get_recipe_by_id(created.id).name == "Tacos"

def test_added_recipe_id_iterated(empty_handler):
    created1 =  empty_handler.add_recipe("tacos", ["shells", "beef"], ["cook", "fill"], ["dinner"])
    recipe1 = empty_handler.get_recipe_by_id(created1.id)
    created2 = empty_handler.add_recipe("burritos", ["shells", "beef"], ["cook", "fill"], ["dinner"])
    recipe2 = empty_handler.get_recipe_by_id(created2.id)
    assert recipe2.name == "burritos"
    assert recipe1.name == "tacos"


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


def test_delete_recipe(seeded_handler):
    handler, recipes = seeded_handler
    conn = sqlite3.connect(handler.db_path)
    target = recipes[2]
    start_count = len(handler.get_all_recipes())

    handler.delete_recipe(target.id)
    leftover = conn.execute("SELECT COUNT(*) FROM ingredients WHERE recipe_id = ?", (target.id,)).fetchone()[0]
    # the target is actually gone
    with pytest.raises(RecipeNotFound):
        handler.get_recipe_by_id(target.id)
    # count dropped by exactly one
    assert len(handler.get_all_recipes()) == start_count - 1
    # a recipe we didn't touch survived
    survivors = {r.name for r in handler.get_all_recipes()}
    assert recipes[0].name in survivors
    conn.close()
    assert leftover == 0

def test_delete_recipe_missing_raises(seeded_handler):
    handler, _ = seeded_handler
    with pytest.raises(RecipeNotFound):
        handler.delete_recipe(999999)

def test_middle_delete_followed_by_add_for_correct_id(seeded_handler):
    handler, recipes = seeded_handler
    target = recipes[1]

    handler.delete_recipe(target.id)
    created = handler.add_recipe("Boogers", ["Boogers", "Snot"], ["cook", "fill"], ["dinner"])

    with pytest.raises(RecipeNotFound):
        handler.delete_recipe(2)
    assert handler.get_recipe_by_id(created.id).name == "Boogers"

def test_edit_recipe_with_bad_id(seeded_handler):
    handler, recipes = seeded_handler
    with pytest.raises(RecipeNotFound):
        handler.edit_recipe(99999999)

def test_edit_recipe_with_empty_changes(seeded_handler):
    handler, recipes = seeded_handler
    original_recipe = handler.get_recipe_by_id(1)
    empty_updates_recipe = handler.edit_recipe(1)
    assert original_recipe == empty_updates_recipe

def test_edit_recipe_with_all_changes(seeded_handler):
    handler, recipes = seeded_handler

    original_recipe = handler.get_recipe_by_id(4)
    updated_recipe = handler.edit_recipe(4,"BURGERS!",["beef","buns","cheese"],["light grill","form patties","grill 10 minutes or until internal temp is 140"],["grilling","beef", "not healthy"])
    assert original_recipe != updated_recipe
    assert updated_recipe.id == original_recipe.id
    assert updated_recipe.name == "BURGERS!"
    assert updated_recipe.ingredients == ["beef","buns","cheese"]
    assert updated_recipe.steps == ["light grill", "form patties", "grill 10 minutes or until internal temp is 140"]
    assert updated_recipe.tags == ["grilling", "beef","not healthy"]

def test_edit_recipe_ingredients(seeded_handler):
    handler, recipes = seeded_handler

    original_recipe = handler.get_recipe_by_id(4)
    updated_recipe = handler.edit_recipe(4,ingredients=["beef","buns","cheese"])
    assert original_recipe != updated_recipe
    assert original_recipe.id == updated_recipe.id
    assert updated_recipe.name == "Burgers"
    assert updated_recipe.ingredients == ["beef","buns","cheese"]


def test_edit_recipe_steps(seeded_handler):
    handler, recipes = seeded_handler

    original_recipe = handler.get_recipe_by_id(4)
    updated_recipe = handler.edit_recipe(4,steps=["light grill","form patties","grill 10 minutes or until internal temp is 140"])
    assert original_recipe != updated_recipe
    assert original_recipe.id == updated_recipe.id
    assert updated_recipe.name == original_recipe.name
    assert updated_recipe.ingredients == original_recipe.ingredients
    assert updated_recipe.tags == original_recipe.tags
    assert updated_recipe.steps == ["light grill", "form patties", "grill 10 minutes or until internal temp is 140"]


def test_edit_recipe_tags(seeded_handler):
    handler, recipes = seeded_handler
    original_recipe = handler.get_recipe_by_id(4)
    updated_recipe = handler.edit_recipe(4,tags=["grilling","beef", "not healthy"])
    assert original_recipe != updated_recipe
    assert updated_recipe.name == original_recipe.name
    assert updated_recipe.ingredients == original_recipe.ingredients
    assert updated_recipe.steps == original_recipe.steps
    assert updated_recipe.tags == ["grilling", "beef","not healthy"]

def test_edit_recipe_empty_tags(seeded_handler):
    handler, recipes = seeded_handler
    original_recipe = handler.get_recipe_by_id(4)
    updated_recipe = handler.edit_recipe(4,tags=[])
    assert original_recipe != updated_recipe
    assert updated_recipe.name == "Burgers"
    assert updated_recipe.steps == original_recipe.steps
    assert updated_recipe.tags == []

def test_edit_recipe_invalid_ingredients_raises(seeded_handler):
    handler, recipes = seeded_handler
    with pytest.raises(InvalidRecipe):
        handler.edit_recipe(1,ingredients=[])
