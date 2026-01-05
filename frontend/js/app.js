import { API_BASE } from "./config.js";
import { renderHistory, renderExplanation } from "./ui.js";
import { sendOCR } from "./ocr.js";

async function loadInitial() {
  const res = await fetch(`${API_BASE}/analyze`);
  const data = await res.json();
  renderHistory(data.history);
  renderExplanation("Terminais", data.terminals);
}

document.getElementById("sendOCR").onclick = async () => {
  const file = document.getElementById("ocrFile").files[0];
  const data = await sendOCR(file);
  renderHistory(data.history);
};

loadInitial();
