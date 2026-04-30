import useDetections from '../hooks/useDetections';

export default function Navbar() {
  const { connectionStatus, cameraStatus, totalHeads } = useDetections();

  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4 px-4 py-4 md:px-6">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Real-time monitoring</p>
          <h2 className="text-xl font-semibold text-white">AI Head Counting CCTV</h2>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-sm">
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-slate-200">WebSocket: {connectionStatus}</span>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-slate-200">Camera: {cameraStatus}</span>
          <span className="rounded-full border border-sky-400/30 bg-sky-500/10 px-3 py-1 text-sky-100">Heads: {totalHeads}</span>
          
        </div>
      </div>
    </header>
  );
}
