import { motion } from "framer-motion";

export default function Timeline({ history = [], onPick, picked }) {
  const last = history.length ? history[history.length - 1] : null;

  return (
    <div className="panel">
      <div className="timeline">
        {history.length === 0 ? (
          <span className="muted">Sem histórico ainda</span>
        ) : (
          history.slice(-50).map((n, idx) => {
            const isLast = idx === history.slice(-50).length - 1;
            const isPicked = picked?.index === idx;
            return (
              <motion.div
                key={`${idx}-${n}`}
                className={`chip ${isLast ? "chip-last" : ""}`}
                onClick={() => onPick({ number: n, index: idx })}
                whileHover={{ y: -1 }}
                style={{
                  outline: isPicked ? "2px solid rgba(0,255,157,.35)" : "none",
                }}
                title="Clique para detalhes"
              >
                {n}
              </motion.div>
            );
          })
        )}
      </div>
      {last !== null ? (
        <div style={{ padding: "0 12px 10px", color: "rgba(232,240,234,.75)", fontSize: 12 }}>
          Último giro: <span style={{ color: "var(--gold)", fontWeight: 800 }}>{last}</span>
        </div>
      ) : null}
    </div>
  );
}
