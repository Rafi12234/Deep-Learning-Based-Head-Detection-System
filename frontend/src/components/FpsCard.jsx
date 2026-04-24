export default function FpsCard({ value }) {
  return (
    <div className="glass-panel rounded-3xl p-5">
      <p className="text-sm text-slate-400">Current FPS</p>
      <div className="mt-3 text-3xl font-semibold text-emerald-300">{Number(value || 0).toFixed(1)}</div>
    </div>
  );
}
