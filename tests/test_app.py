import pytest
from unittest.mock import MagicMock
from app import create_app
from recipe_handler import Recipe, RecipeNotFound, InvalidRecipe

# @pytest.fixture
# def mock_client():
#     mock_handler = MagicMock()
#     # mock_handler.get_recipe_by_id.return_value = Recipe(
#     #     id=1,name="Nachos", ingredients=["chips"], steps=["bake"], tags=["quick"]
#     # )
#     return mock_handler

def test_get_recipe_returns_200_and_json():
    mock_handler = MagicMock()
    mock_handler.get_recipe_by_id.return_value = Recipe(
        id=1,name="Nachos", ingredients=["chips"], steps=["bake"], tags=["quick"]
    )
    app = create_app(mock_handler)
    client = app.test_client()
    response = client.get("/recipes/1")
    assert response.status_code == 200
    assert response.get_json()["name"]=="Nachos"
    mock_handler.get_recipe_by_id.assert_called_once_with(1)

def test_get_recipe_missing_returns_404():
    mock_handler = MagicMock()
    mock_handler.get_recipe_by_id.side_effect = RecipeNotFound("nope")
    app = create_app(mock_handler)
    client = app.test_client()

    response = client.get("/recipes/999999999")

    assert response.status_code == 404
    assert "error" in response.get_json()

# def test_get_recipe():
#     mock_handler = MagicMock()
#     mock_handler.get_recipe.return_value = Recipe(
#         id=1, name="Nachos", ingredients=["chips"], steps=["bake"], tags=["quick"]
#     )
#     app = create_app(mock_handler)
#     client = app.test_client()
#
#     response = client.get("/recipes")
#     assert response.status_code == 200
#     assert response.get_json()["id"] == 1
#     mock_handler.get_recipe.assert_called_once_with(1)


#tests needing completed
# get_recipe happy path (mock returns a Recipe → assert 200 + correct JSON + assert_called_once_with)
# get_recipe missing (mock raises RecipeNotFound → assert 404)
# get_recipes returns a list (mock get_all_recipes.return_value = [recipe1, recipe2] → assert 200 and the JSON is a list of the right length)
# create_recipe happy path (mock add_recipe.return_value a Recipe → POST with client.post("/recipes", json={...}) → assert 201)
# create_recipe invalid (mock add_recipe.side_effect = InvalidRecipe(...) → assert 400)