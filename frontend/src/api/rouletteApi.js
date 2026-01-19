const API_URL =
  import.meta.env.VITE_API_URL || "https://roulette-ai-mvp-production.up.railway.app";

/**
 * Envia 1 giro por vez (como seu backend espera):
 * POST /add-spin?number=14
 */
export async function addSpin(number, historyLimit = 50) {
  const url = `${API_URL}/add-spin?number=${encodeURIComponent(
    number
  )}&history_limit=${encodeURIComponent(historyLimit)}`;

  const response = await fetch(url, { method: "POST" });

  if (!response.ok) {
    let payload = null;
    try {
      payload = await response.json();
    } catch {
      // ignore
    }
    console.error("Backend error:", response.status, payload);
    throw new Error(payload?.detail?.[0]?.msg || payload?.message || "Erro ao comunicar com o backend");
  }

  return response.json();
}
