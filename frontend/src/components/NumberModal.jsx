import { motion } from "framer-motion";

const WHEEL = [
  0, 32, 15, 19, 4, 21, 2, 25, 17,
  34, 6, 27, 13, 36, 11, 30, 8,
  23, 10, 5, 24, 16, 33, 1,
  20, 14, 31, 9, 22, 18, 29,
  7, 28, 12, 35, 3, 26
];

function getPhysicalNeighbors(number) {
  const idx = WHEEL.indexOf(number);
  if (idx < 0) return [];
  const left = WHEEL[(idx - 1 + WHEEL.length) % WHEEL.length];
  const right = WHEEL[(idx + 1) % WHEEL.length];
  return [left, right];
}

function findHorse(number, horses = []) {
  return horses.find((h) => Array.isArray(h?.pair) && h.pair.includes(number)) || null;
}

function findZone(number, zones = []) {
  const index = zones.findIndex((z) => (z?.numbers || []).includes(number));
  return index >= 0 ? { index, zone: zones[index] } : null;
}

function getPressure(number, neighborsPressure = []) {
  const item = neighborsPressure.find((x) => x?.number === number);
  return item?.pressure ?? 0;
}

export default function NumberModal({ open, onClose, pickedNumber, data }) {
  if (!open) return null;

  const zones = data?.physical_zones || [];
  const horses = data?.horses || [];
  const neighborsPressure = data?.neighbors || [];

  const physicalNeighbors = getPhysicalNeighbors(pickedNumber);
  const horse = findHorse(pickedNumber, horses);
  const zoneInfo = findZone(pickedNumber, zones);

  return (
    <div className="modal-overlay" onMouseDown={onClose}>
      <motion.div
        className="modal"
        initial={{ opacity: 0, y: 14, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.18 }}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="modal-head">
          <h2>
            Detalhes do Giro — <span style={{ color: "var(--gold)" }}>#{pickedNumber}</span>
          </h2>
          <button className="close" onClick={onClose}>Fechar</button>
        </div>

        <div className="modal-body">
          <div className="grid2">
            <div className="card" style={{ boxShadow: "none" }}>
              <div className="card-head">
                <div className="card-title">Vizinhos físicos</div>
                <span className="badge">roleta real</span>
              </div>
              <div className="card-body" style={{ height: "auto", maxHeight: 220 }}>
                {physicalNeighbors.length ? (
                  <>
                    {physicalNeighbors.map((n) => (
                      <div className="kv" key={n}>
                        <span>Número {n}</span>
                        <span style={{ color: "var(--green)", fontWeight: 800 }}>
                          Pressão: {getPressure(n, neighborsPressure)}
                        </span>
                      </div>
                    ))}
                    <div className="muted" style={{ marginTop: 8, fontSize: 12 }}>
                      Pressão vem do backend em <code>neighbors</code>.
                    </div>
                  </>
                ) : (
                  <div className="muted">Número não encontrado no mapa físico</div>
                )}
              </div>
            </div>

            <div className="card" style={{ boxShadow: "none" }}>
              <div className="card-head">
                <div className="card-title">Cavalo (oposição física)</div>
                <span className="badge">wheel</span>
              </div>
              <div className="card-body" style={{ height: "auto", maxHeight: 220 }}>
                {horse?.pair ? (
                  <div style={{ fontSize: 14 }}>
                    Par:{" "}
                    <span className="tag tag-hot">{horse.pair[0]}</span>
                    <span className="tag tag-hot">{horse.pair[1]}</span>
                  </div>
                ) : (
                  <div className="muted">Sem cavalo encontrado</div>
                )}

                <hr className="sep" />

                {zoneInfo ? (
                  <>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                      <strong>
                        Zona {zoneInfo.index + 1} —{" "}
                        <span style={{
                          color: zoneInfo.zone.status?.includes("Quente")
                            ? "var(--gold)"
                            : zoneInfo.zone.status?.includes("Fria")
                            ? "var(--green)"
                            : "var(--text)"
                        }}>
                          {zoneInfo.zone.status || "Neutra"}
                        </span>
                      </strong>
                      <span className="muted">{zoneInfo.zone.hits ?? 0} hits • {zoneInfo.zone.percentage ?? 0}%</span>
                    </div>

                    <div style={{ marginTop: 8 }}>
                      {(zoneInfo.zone.numbers || []).map((n) => (
                        <span key={n} className="tag">{n}</span>
                      ))}
                    </div>

                    {zoneInfo.zone.explanation ? (
                      <div className="muted" style={{ marginTop: 8, fontSize: 12 }}>
                        {zoneInfo.zone.explanation}
                      </div>
                    ) : null}
                  </>
                ) : (
                  <div className="muted">Zona não encontrada</div>
                )}
              </div>
            </div>
          </div>

          <div style={{ marginTop: 12 }} className="muted">
            Clique na timeline para abrir esse modal com detalhes do giro.
          </div>
        </div>
      </motion.div>
    </div>
  );
}
