import { useEffect } from 'react';
import DetectionLogTable from '../components/DetectionLogTable';
import useDetections from '../hooks/useDetections';

export default function DetectionLogs() {
  const { logs, refreshLogs } = useDetections();

  useEffect(() => {
    refreshLogs();
  }, []);

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-3xl p-5">
        <h2 className="text-2xl font-semibold text-white">Detection Logs</h2>
        <p className="mt-2 text-sm text-slate-400">Stored logs from SQLite with head counts, FPS, and frame metadata.</p>
      </div>
      <DetectionLogTable logs={logs} />
    </div>
  );
}
