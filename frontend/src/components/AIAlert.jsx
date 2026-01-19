export default function AIAlert({ alerts = [] }) {
  if (!alerts || alerts.length === 0) {
    return <div className="muted">Nenhum alerta</div>;
  }

  return (
    <div>
      {alerts.map((a, i) => (
        <div key={i} className="kv">
          <span>{typeof a === "string" ? a : a?.message || "Alerta"}</span>
          <span style={{ color: "var(--danger)", fontWeight: 800 }}>!</span>
        </div>
      ))}
    </div>
  );
}
