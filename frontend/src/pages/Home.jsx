import React, { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { addSpin } from "../api/rouletteApi";

import Card from "../components/Card";
import Timeline from "../components/Timeline";
import NumberModal from "../components/NumberModal";
import Heatmap from "../components/Heatmap";
import AIAlert from "../components/AIAlert";
import LiveWheel from "../components/LiveWheel";

export default function Home() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [data, setData] = useState(null);

  const [picked, setPicked] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const history = data?.history || [];
  const numbersMap = data?.numbers || {};
  const zones = data?.physical_zones || [];
  const neighbors = data?.neighbors || [];
  const horses = data?.horses || [];
  const absences = data?.absences || { numbers: [], zones: [], horses: [] };
  const strategies = data?.strategies || [];
  const alerts = data?.alerts || [];

  const numbersSorted = useMemo(() => {
    const entries = Object.entries(numbersMap || {});
    entries.sort((a, b) => (b[1] ?? 0) - (a[1] ?? 0));
    return entries;
  }, [numbersMap]);

  async function handleSpin() {
    setErr("");
    const trimmed = input.trim();

    if (!trimmed) return;

    const n = Number(trimmed);
    if (Number.isNaN(n) || n < 0 || n > 36) {
      setErr("Digite um número válido de 0 a 36.");
      return;
    }

    setLoading(true);
    try {
      const resp = await addSpin(n, 50);
      setData(resp);
      setInput("");
    } catch (e) {
      setErr(e?.message || "Erro ao comunicar com o backend");
    } finally {
      setLoading(false);
    }
  }

  function onPick(p) {
    setPicked(p);
    setModalOpen(true);
  }

  return (
    <div className="app-shell">
      <div className="topbar">
        <div className="brand">
          <h1>ROULETTE AI — V2 Premium</h1>
          <small>cassino • painéis • análise em tempo real (via seu backend)</small>
        </div>
        <div className="pill">
          <span>Status:</span>{" "}
          <strong style={{ color: data?.status === "ok" ? "var(--green)" : "var(--gold)" }}>
            {data?.status || "offline"}
          </strong>
        </div>
      </div>

      <div className="layout">
        {/* Linha 1: Live + Input */}
        <div className="row" style={{ height: "min(44vh, 420px)" }}>
          <div className="panel" style={{ flex: 1.4, display: "flex", flexDirection: "column" }}>
            <div className="input-wrap">
              <input
                className="input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Digite um número de 0 a 36 e aperte Enter"
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleSpin();
                }}
                inputMode="numeric"
              />
              <button className="btn" onClick={handleSpin} disabled={loading}>
                {loading ? "Analisando..." : "Giro"}
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => {
                  setData(null);
                  setErr("");
                  setInput("");
                }}
                disabled={loading}
                title="Limpa painel local (não apaga histórico do backend)"
              >
                Limpar
              </button>
            </div>

            {err ? (
              <div style={{ padding: "0 12px 12px", color: "var(--danger)", fontWeight: 700, fontSize: 13 }}>
                {err}
              </div>
            ) : (
              <div style={{ padding: "0 12px 12px", color: "rgba(232,240,234,.65)", fontSize: 12 }}>
                Dica: clique na timeline para abrir detalhes do giro (vizinhos físicos + cavalo + zona).
              </div>
            )}

            <Timeline history={history} onPick={onPick} picked={picked} />
          </div>

          <div style={{ flex: 1 }}>
            <LiveWheel />
          </div>
        </div>

        {/* Linha 2: Cards */}
        <div className="panel" style={{ height: "calc(100% - min(44vh, 420px) - 24px)" }}>
          <div className="cards">
            <Card title="📊 Histórico" badge={`${history.length}/50`}>
              {history.length ? (
                <div style={{ lineHeight: 1.8 }}>
                  {history.slice(-50).map((n, i) => (
                    <span key={`${i}-${n}`} className="tag" onClick={() => onPick({ number: n, index: i })} style={{ cursor: "pointer" }}>
                      {n}
                    </span>
                  ))}
                </div>
              ) : (
                <div className="muted">Sem histórico ainda</div>
              )}
            </Card>

            <Card title="🎯 Frequência (numbers)" badge={`${numbersSorted.length}`}>
              {numbersSorted.length ? (
                numbersSorted.slice(0, 18).map(([num, hits]) => (
                  <div className="kv" key={num}>
                    <span>Número {num}</span>
                    <span style={{ color: "var(--gold)", fontWeight: 900 }}>{hits}x</span>
                  </div>
                ))
              ) : (
                <div className="muted">Sem dados</div>
              )}
              {numbersSorted.length > 18 ? <div className="muted" style={{ marginTop: 8, fontSize: 12 }}>Mostrando top 18</div> : null}
            </Card>

            <Card title="🧭 Heatmap por Zonas" badge={`${zones.length}`}>
              <Heatmap zones={zones} />
            </Card>

            <Card title="👥 Vizinhos (pressão)" badge={`${neighbors.length}`}>
              {neighbors.length ? (
                neighbors.slice(0, 20).map((v, i) => (
                  <div className="kv" key={`${v.number}-${i}`}>
                    <span>Número {v.number}</span>
                    <span style={{ color: "var(--green)", fontWeight: 900 }}>{v.pressure}</span>
                  </div>
                ))
              ) : (
                <div className="muted">Sem dados</div>
              )}
              {neighbors.length > 20 ? <div className="muted" style={{ marginTop: 8, fontSize: 12 }}>Mostrando top 20</div> : null}
            </Card>

            <Card title="🐎 Cavalos" badge={`${horses.length}`}>
              {horses.length ? (
                horses.map((h, i) => (
                  <div className="kv" key={i}>
                    <span>Par</span>
                    <span style={{ color: "var(--gold)", fontWeight: 900 }}>
                      {h?.pair?.[0]} — {h?.pair?.[1]}
                    </span>
                  </div>
                ))
              ) : (
                <div className="muted">Sem dados</div>
              )}
            </Card>

            <Card title="❄️ Ausências" badge={`${(absences?.numbers || []).length}`}>
              <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>Números ausentes</div>
              <div style={{ lineHeight: 1.8 }}>
                {(absences?.numbers || []).slice(0, 36).map((n) => (
                  <span key={n} className="tag tag-cold">{n}</span>
                ))}
              </div>

              <hr className="sep" />

              <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>Zonas ausentes</div>
              {(absences?.zones || []).length ? (
                (absences.zones || []).map((z, i) => (
                  <div key={i} style={{ marginBottom: 10 }}>
                    <strong style={{ color: "var(--green)" }}>{z.status || "❄️ Fria"}</strong>
                    <div className="muted" style={{ fontSize: 12 }}>hits: {z.hits ?? 0} • {z.percentage ?? 0}%</div>
                    <div style={{ marginTop: 6 }}>
                      {(z.numbers || []).map((n) => <span key={n} className="tag">{n}</span>)}
                    </div>
                  </div>
                ))
              ) : (
                <div className="muted">Nenhuma zona ausente</div>
              )}
            </Card>

            <Card title="📈 Estratégias" badge={`${strategies.length}`}>
              {strategies.length ? (
                strategies.map((s, i) => (
                  <div key={i} className="kv">
                    <span>{s?.name || "Strategy"}</span>
                    <span className="muted">hits: {s?.stats?.hits ?? 0}</span>
                  </div>
                ))
              ) : (
                <div className="muted">Nenhuma no momento</div>
              )}
            </Card>

            <Card title="🚨 Alertas" badge={`${alerts.length}`}>
              <AIAlert alerts={alerts} />
            </Card>
          </div>
        </div>
      </div>

      <NumberModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        pickedNumber={picked?.number}
        data={data}
      />
    </div>
  );
}
