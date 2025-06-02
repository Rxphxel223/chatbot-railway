const itemInput = document.getElementById("itemInput");
const itemList = document.getElementById("itemList");
const recipeOutput = document.getElementById("recipeOutput");

let items = JSON.parse(localStorage.getItem("festival_items")) || [];

function updateUI() {
  itemList.innerHTML = "";
  items.forEach((item, index) => {
    const li = document.createElement("li");
    li.textContent = item + " ";
    const del = document.createElement("button");
    del.textContent = "❌";
    del.onclick = () => removeItem(index);
    li.appendChild(del);
    itemList.appendChild(li);
  });
  localStorage.setItem("festival_items", JSON.stringify(items));
}

function addItem() {
  const value = itemInput.value.trim();
  if (value && !items.includes(value)) {
    items.push(value);
    itemInput.value = "";
    updateUI();
  }
}

function removeItem(index) {
  items.splice(index, 1);
  updateUI();
}

async function generateRecipe() {
  recipeOutput.textContent = "⏳ Rezept wird geladen...";
  const response = await fetch("/api/festival-rezept", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items })
  });

  const data = await response.json();
  recipeOutput.textContent = data.recipe || "❌ Kein Rezept erhalten.";
}

updateUI();
