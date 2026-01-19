import { useEffect, useState } from "react";

export default function LiveWheel() {
  const [url, setUrl] = useState(() => localStorage.getItem("live_url") || "");
  const [draft, setDraft] = useState(url);

  useEffect(() => {
    localStorage.setItem("live_url", url);
  }, [url]);

  return (
    <div className="panel live">
      <div className="live-top">
        <input
          className="input"
          placeholder="Cole a URL do iframe/stream ao vivo (opcional)"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <button className="btn btn-ghost" onClick={() => setUrl(draft)}>
          Aplicar
        </button>
      </div>

      <div className="iframe-wrap">
        {url ? (
          <iframe className="iframe" src={url} title="Roleta ao vivo" allow="autoplay; fullscreen" />
        ) : (
          <div style={{ padding: 14, color: "rgba(232,240,234,.65)", fontSize: 13 }}>
            Cole uma URL de embed/iframe do provedor de roleta ao vivo (se você tiver).
            <br />
            O painel de análise funciona mesmo sem isso.
          </div>
        )}
      </div>
    </div>
  );
}
