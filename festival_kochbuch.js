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
  try {
    const response = await fetch("/api/festival-rezept", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items })
    });

    const text = await response.text(); // <-- kein .json(), wir lesen erstmal Text

    let data;
    try {
      data = JSON.parse(text);
    } catch (jsonErr) {
      recipeOutput.textContent = "❌ Serverfehler: Keine gültige JSON-Antwort erhalten.\n\n" + text;
      console.error("❌ Ungültige JSON-Antwort:", text);
      return;
    }

    recipeOutput.textContent = data.recipe || "❌ Kein Rezept erhalten.";

  } catch (err) {
    recipeOutput.textContent = "❌ Fehler beim Abrufen des Rezepts.";
    console.error(err);
  }
}

  const data = await response.json();
  recipeOutput.textContent = data.recipe || "❌ Kein Rezept erhalten.";
}

updateUI();
