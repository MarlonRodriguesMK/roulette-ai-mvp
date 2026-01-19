export default function Heatmap({ zones = [] }) {
  return (
    <div>
      {zones.length === 0 ? (
        <div className="muted">Sem dados</div>
      ) : (
        zones.map((z, i) => {
          const status = z.status || "Neutra";
          const isHot = status.includes("Quente");
          const isCold = status.includes("Fria");
          return (
            <div key={i} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                <strong style={{ color: isHot ? "var(--gold)" : isCold ? "var(--green)" : "var(--text)" }}>
                  Zona {i + 1} — {status}
                </strong>
                <span className="muted">{z.hits ?? 0} hits • {z.percentage ?? 0}%</span>
              </div>

              <div style={{ marginTop: 6 }}>
                {(z.numbers || []).map((n) => (
                  <span
                    key={n}
                    className={`tag ${isHot ? "tag-hot" : isCold ? "tag-cold" : ""}`}
                  >
                    {n}
                  </span>
                ))}
              </div>

              {z.explanation ? <div className="muted" style={{ marginTop: 6, fontSize: 12 }}>{z.explanation}</div> : null}
            </div>
          );
        })
      )}
    </div>
  );
}
