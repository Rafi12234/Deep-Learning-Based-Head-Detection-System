import { useState } from 'react';
import { formatTime } from '../utils/formatTime';

export default function DetectionLogTable({ logs }) {
  const [selected, setSelected] = useState(null);

  return (
    
    <div className="glass-panel overflow-hidden rounded-3xl">
      <div className="border-b border-white/10 px-5 py-4">
        <h3 className="text-lg font-semibold text-white">Detection Logs</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          
          <thead className="text-slate-400">
            <tr>
              
              <th className="px-5  py-3">Timestamp</th>
              <th className="px-5 py-3">Heads</th>
              <th className="px-5 py-3">FPS</th>
              <th className="px-5 py-3">Camera ID</th>
              <th className="px-5 py-3">Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id} className="border-t border-white/10 text-slate-200">
                <td className="px-5 py-3">{formatTime(log.timestamp)}</td>
                <td className="px-5 py-3">{log.total_heads}</td>
                <td className="px-5 py-3">{Number(log.fps).toFixed(2)}</td>
                <td className="px-5 py-3">{log.camera_id}</td>
                <td className="px-5 py-3">
                  <button className="rounded-full bg-sky-500/15 px-3 py-1 text-sky-100" onClick={() => setSelected(log)} type="button">
                    View JSON
                  </button>
                </td>
              </tr>
            ))}
            {!logs.length && (
              <tr>
                <td className="px-5 py-6 text-slate-400" colSpan="5">No logs yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {selected && (
        <div className="border-t border-white/10 p-5">
          <div className="mb-3 flex items-center justify-between">
            <h4 className="font-semibold text-white">Detection JSON</h4>
            <button className="text-sm text-slate-300" type="button" onClick={() => setSelected(null)}>Close</button>
          </div>
          <pre className="max-h-80 overflow-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-200">{JSON.stringify(selected.detections_json, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
