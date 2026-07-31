const API_BASE = "http://localhost:5000"
const form = document.getElementById("add-recipe-form")
const editForm = document.getElementById("edit-recipe-form");

let editingRecipeId = null;

async function loadRecipes(){
    const response = await fetch(`${API_BASE}/recipes`);
    const recipes = await response.json();

    const list = document.getElementById("recipe-list");
    list.innerHTML = ""
    for(const recipe of recipes) {
        const item = document.createElement("li");
        item.textContent = recipe.name;

        const editbtn = document.createElement("button");
        editbtn.textContent = "Edit Recipe";

        editbtn.addEventListener("click", () => openEditForm(recipe))

        const delbtn = document.createElement("button");
        delbtn.textContent = "Delete";
        delbtn.addEventListener("click", () => deleteRecipe(recipe.id, recipe.name));

        item.appendChild(editbtn)
        item.appendChild(delbtn);
        list.appendChild(item);

    }
}

function openEditForm(recipe) {
    document.getElementById("edit-name").value = recipe.name;
    document.getElementById("edit-ingredients").value = recipe.ingredients.join(", ");
    document.getElementById("edit-steps").value = recipe.steps.join(", ");
    document.getElementById("edit-tags").value = recipe.tags.join(", ");

    editingRecipeId = recipe.id;                    // remember which recipe we're editing

    document.getElementById("edit-recipe-form").style.display = "block";
}

async function deleteRecipe(id, name){
    const confirmed = confirm(`Delete "${name}"? This cannot be undone.`);
    if(!confirmed){
        return;
    }
    const response = await fetch(`${API_BASE}/recipes/${id}`,{
        method: "DELETE",
    });
    if(response.ok) {
    loadRecipes();
    } else {
        alert("Could Not Delete Recipe")
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault(); //stop page reload here

    //read input
    const name = document.getElementById("name").value;
    const ingredients = document.getElementById("ingredients").value;
    const steps = document.getElementById("steps").value;
    const tags = document.getElementById("tags").value;

    //convert comma sep'd string to array
    const recipeData = {
        name: name,
        ingredients: ingredients.split(",").map(s => s.trim()),
        steps: steps.split(",").map(s => s.trim()),
        tags: tags.split(",").map(s => s.trim()),
    };
    //send
    const response = await fetch(`${API_BASE}/recipes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(recipeData),
    });
    if (response.ok) {
        loadRecipes();
    } else {
        alert("That's an invalid recipe");
    }
    });

editForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const recipeData ={
        name: document.getElementById("edit-name").value,
        ingredients: document.getElementById("edit-ingredients").value.split(",").map(s => s.trim()),
        steps: document.getElementById("edit-steps").value.split(",").map(s => s.trim()),
        tags: document.getElementById("edit-tags").value.split(",").map(s => s.trim()),
    }
    const response = await fetch(`${API_BASE}/recipes/${editingRecipeId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(recipeData),
    });

        if (response.ok) {
        editForm.style.display = "none";        // hide the form
        loadRecipes();                          // re-render with the edit
    } else {
        const err = await response.json();
        alert(err.error);                       // show the API's error message
    }
});


loadRecipes()

