export default function WheelEmbed({ src }){
  return (
    <div className="wheel">
      {src ? (
        <iframe
          src={src}
          title="Roleta ao vivo"
          frameBorder="0"
          allow="autoplay; encrypted-media"
        />
      ) : (
        <div className="placeholder">
          Configure o link da roleta ao vivo no <b>Home.jsx</b>
        </div>
      )}

      <style>{`
        .wheel{
          flex:1;
          min-height:0;
          border-radius: var(--radius2);
          border: 1px solid var(--stroke);
          background: rgba(255,255,255,.05);
          box-shadow: var(--shadow);
          backdrop-filter: blur(10px);
          overflow:hidden;
          position:relative;
        }
        iframe{
          width:100%;
          height:100%;
        }
        .placeholder{
          height:100%;
          display:flex;
          align-items:center;
          justify-content:center;
          color: var(--muted);
          padding: 12px;
          text-align:center;
        }
      `}</style>
    </div>
  );
}
