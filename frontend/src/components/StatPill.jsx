export default function StatPill({ label, value, tone="green" }){
  const color = tone === "gold" ? "var(--gold)" : "var(--green)";
  const border = tone === "gold" ? "rgba(255,204,102,.35)" : "rgba(0,225,138,.35)";
  return (
    <span className="pill">
      <span className="l">{label}</span>
      <span className="v">{value}</span>
      <style>{`
        .pill{
          display:inline-flex;
          align-items:center;
          gap:8px;
          padding: 7px 10px;
          border-radius: 999px;
          border: 1px solid ${border};
          background: rgba(255,255,255,.06);
          font-size: 11px;
          white-space:nowrap;
        }
        .l{ color: var(--muted); }
        .v{ color: ${color}; font-weight: 800; }
      `}</style>
    </span>
  );
}
