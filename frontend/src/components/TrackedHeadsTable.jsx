export default function TrackedHeadsTable({ detections }) {
  return (
    <div className="glass-panel overflow-hidden rounded-3xl">
      <div className="border-b border-white/10 px-5 py-4">
        <h3 className="text-lg font-semibold text-white">Tracked Heads</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-slate-400">
            <tr>
              <th className="px-5 py-3">Label</th>
              <th className="px-5 py-3">Track ID</th>
              <th className="px-5 py-3">Confidence</th>
              <th className="px-5 py-3">Class</th>
            </tr>
          </thead>
          <tbody>
            {detections.map(detection => (
              <tr key={detection.track_id} className="border-t border-white/10 text-slate-200">
                <td className="px-5 py-3 font-medium text-white">{detection.label}</td>
                <td className="px-5 py-3">{detection.track_id}</td>
                <td className="px-5 py-3">{Number(detection.confidence).toFixed(2)}</td>
                <td className="px-5 py-3">{detection.class_name}</td>
              </tr>
            ))}
            {!detections.length && (
              <tr>
                <td className="px-5 py-6 text-slate-400" colSpan="4">No active heads detected.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
