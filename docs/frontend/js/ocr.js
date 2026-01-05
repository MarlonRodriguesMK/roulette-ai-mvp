import { API_BASE } from "./config.js";

export async function sendOCR(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/send-history`, {
    method: "POST",
    body: form
  });

  return res.json();
}
