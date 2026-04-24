import { NavLink } from 'react-router-dom';

const linkClass = ({ isActive }) =>
  `block rounded-xl px-4 py-3 text-sm transition ${isActive ? 'bg-sky-500/20 text-sky-200 border border-sky-500/30' : 'text-slate-300 hover:bg-white/5 hover:text-white'}`;

export default function Sidebar() {
  return (
    <aside className="hidden w-72 border-r border-white/10 bg-slate-950/90 px-4 py-6 lg:block">
      <div className="mb-8 rounded-3xl border border-white/10 bg-gradient-to-br from-sky-500/20 to-orange-500/10 p-5 shadow-glow">
        <p className="text-xs uppercase tracking-[0.35em] text-sky-200/70">AI CCTV</p>
        <h1 className="mt-2 text-2xl font-bold leading-tight">Head Counting System</h1>
        <p className="mt-2 text-sm text-slate-300">Live heads, stable IDs, and camera analytics.</p>
      </div>

      <nav className="space-y-2">
        <NavLink className={linkClass} to="/">Dashboard</NavLink>
        <NavLink className={linkClass} to="/camera">Camera Monitor</NavLink>
        <NavLink className={linkClass} to="/logs">Detection Logs</NavLink>
        <NavLink className={linkClass} to="/settings">Settings</NavLink>
      </nav>

      <div className="mt-8 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
        <p className="font-medium text-white">Model path</p>
        <p className="mt-1 break-all">backend/models/head_detector.pt</p>
      </div>
    </aside>
  );
}
