import { useMemo } from 'react';
import CameraStatusCard from '../components/CameraStatusCard';
import HeadCountCard from '../components/HeadCountCard';
import FpsCard from '../components/FpsCard';
import StatsChart from '../components/StatsChart';
import DetectionLogTable from '../components/DetectionLogTable';
import useDetections from '../hooks/useDetections';

export default function Dashboard() {
  const { totalHeads, fps, cameraStatus, detectionHistory, logs, health } = useDetections();

  const summaryCards = useMemo(() => [
    <HeadCountCard key="heads" value={totalHeads} />,
    <FpsCard key="fps" value={fps} />,
    <CameraStatusCard key="status" value={cameraStatus} />,
  ], [totalHeads, fps, cameraStatus]);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">{summaryCards}</div>

      <div className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
        <StatsChart data={detectionHistory} />
        <div className="glass-panel rounded-3xl p-5">
          <h3 className="text-lg font-semibold text-white">System Health</h3>
          <div className="mt-4 space-y-3 text-sm text-slate-300">
            <div className="flex items-center justify-between"><span>Backend</span><span className="text-emerald-300">{health?.status || 'unknown'}</span></div>
            <div className="flex items-center justify-between"><span>Model loaded</span><span>{health?.model_loaded ? 'yes' : 'no'}</span></div>
            <div className="flex items-center justify-between"><span>Database</span><span>{health?.database_connected ? 'connected' : 'offline'}</span></div>
            <div className="flex items-center justify-between"><span>Recent logs</span><span>{logs.length}</span></div>
          </div>
        </div>
      </div>

      <DetectionLogTable logs={logs} />
    </div>
  );
}
