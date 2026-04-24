export default function HeadCountCard({ value, label = 'Total Visible Heads' }) {
  return (
    <div className="glass-panel rounded-3xl p-5 shadow-glow">
      <p className="text-sm text-slate-400">{label}</p>
      <div className="mt-3 text-4xl font-bold text-white">{value}</div>
    </div>
  );
}
