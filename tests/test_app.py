from operator import truediv

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

def test_get_recipe_by_id():
    mock_handler = MagicMock()
    mock_handler.get_recipe_by_id.return_value = Recipe(
        id=1, name="Nachos", ingredients=["chips"], steps=["bake"], tags=["quick"]
    )
    app = create_app(mock_handler)
    client = app.test_client()

    response = client.get("/recipes/1")
    assert response.status_code == 200
    assert response.get_json()["id"] == 1
    mock_handler.get_recipe_by_id.assert_called_once_with(1)

def test_get_recipe_by_id_missing_recipe():
    mock_handler = MagicMock()
    mock_handler.get_recipe_by_id.side_effect = RecipeNotFound("nope")
    app = create_app(mock_handler)
    client = app.test_client()

    response = client.get("/recipes/999999999")

    assert response.status_code == 404
    assert "error" in response.get_json()

def test_get_recipes_happy_path():
    mock_handler = MagicMock()
    mock_handler.get_all_recipes.return_value = [Recipe(
        id=1, name="Nachos", ingredients=["chips"], steps=["bake"], tags=["quick"]
    ), Recipe(
        id=2, name="Sohcan", ingredients=["spihc"], steps=["ekab"], tags=["kciuq"]
    ) ]

    app = create_app(mock_handler)
    client = app.test_client()

    response = client.get("/recipes")
    assert response.status_code == 200
    assert len(response.get_json()) == 2

def test_get_recipes_by_tag_exist():
    mock_handler = MagicMock()
    mock_handler.get_recipes_by_tag.return_value = [Recipe(
        id=3, name="test", ingredients=["test1"], steps=["teststep"], tags=["testtag"]
    )]
    app = create_app(mock_handler)
    client = app.test_client()
    response = client.get("/recipes?tag=testtag")
    assert response.status_code ==200
    assert len(response.get_json()) == 1
    mock_handler.get_recipes_by_tag.assert_called_once_with("testtag")
    mock_handler.get_all_recipes.assert_not_called()

def test_create_recipe_happy_path():
    mock_handler = MagicMock()
    mock_handler.add_recipe.return_value = Recipe(
        id=1, name="Nachos", ingredients=["chips"], steps=["bake"], tags=["quick"]
    )
    app = create_app(mock_handler)
    client = app.test_client()

    response = client.post("/recipes", json={
        "name": "Nachos",
        "ingredients": ["chips"],
        "steps": ["bake"],
        "tags": ["quick"],
    })

    assert response.status_code == 201
    assert response.get_json()["id"] == 1
    mock_handler.add_recipe.assert_called_once_with(
        "Nachos", ["chips"], ["bake"], ["quick"]
    )

def test_create_invalid_recipe():
    mock_handler = MagicMock()
    mock_handler.add_recipe.side_effect = InvalidRecipe("Invalid Recipe Name")
    app = create_app(mock_handler)
    client = app.test_client()

    response = client.post("/recipes", json={
        "name": "", "ingredients": ["chips"], "steps": ["bake"], "tags": []
    })

    assert response.status_code == 400

def test_delete_recipe():
    mock_handler = MagicMock()
    mock_handler.delete_recipe.return_value = Recipe(
        id=1, name="Nachos", ingredients=["chips"], steps=["bake"], tags=["quick"]
    )
    app = create_app(mock_handler)
    client = app.test_client()

    response = client.delete("/recipes/1")
    assert response.status_code == 200
    mock_handler.delete_recipe.assert_called_once_with(1)

def test_delete_recipe_missing_recipe():
    mock_handler = MagicMock()
    mock_handler.delete_recipe.side_effect = RecipeNotFound("nope")
    app = create_app(mock_handler)
    client = app.test_client()

    response = client.delete("/recipes/1")
    assert response.status_code == 404
    assert "error" in response.get_json()



def test_edit_recipe_missing_id():
    mock_handler = MagicMock()
    mock_handler.edit_recipe.side_effect = RecipeNotFound("nope")
    app = create_app(mock_handler)
    client = app.test_client()

    response = client.patch("/recipes/1", json={"name": "Steve"})
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_edit_recipe_invalid():
    mock_handler = MagicMock()
    mock_handler.edit_recipe.side_effect = InvalidRecipe("Invalid Recipe Name")
    app = create_app(mock_handler)
    client = app.test_client()

    response = client.patch("/recipes/1", json={"name": ""})
    assert response.status_code == 400
    assert "error" in response.get_json()
