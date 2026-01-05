export function renderHistory(numbers) {
  const container = document.getElementById("history");
  container.innerHTML = "";
  numbers.forEach(n => {
    const el = document.createElement("div");
    el.className = "history-item";
    el.innerText = n;
    container.appendChild(el);
  });
}

export function renderExplanation(title, data) {
  const box = document.getElementById("explain");
  box.innerHTML = `<h4>${title}</h4>`;
  Object.entries(data).forEach(([k, v]) => {
    box.innerHTML += `
      <p><strong>${k}</strong>: ${v.status}</p>
    `;
  });
}
