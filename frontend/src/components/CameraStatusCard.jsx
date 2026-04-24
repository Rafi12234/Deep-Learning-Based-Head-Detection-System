export default function CameraStatusCard({ value }) {
  const tone = value === 'running' ? 'bg-emerald-500/15 text-emerald-200' : value === 'disconnected' ? 'bg-amber-500/15 text-amber-200' : 'bg-slate-500/15 text-slate-200';

  return (
    <div className="glass-panel rounded-3xl p-5">
      <p className="text-sm text-slate-400">Camera Status</p>
      <div className={`mt-3 inline-flex rounded-full px-3 py-1 text-sm font-medium ${tone}`}>{value}</div>
    </div>
  );
}
