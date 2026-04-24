import VideoFeed from '../components/VideoFeed';
import TrackedHeadsTable from '../components/TrackedHeadsTable';
import useDetections from '../hooks/useDetections';
import { getApiBaseUrl } from '../services/api';

export default function CameraMonitor() {
  const { currentDetections, totalHeads, fps, cameraStatus, connectionStatus, frameSize, startCamera, stopCamera } = useDetections();

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-4">
        <div className="glass-panel rounded-3xl p-5"><p className="text-sm text-slate-400">Total Heads</p><p className="mt-2 text-4xl font-bold text-white">{totalHeads}</p></div>
        <div className="glass-panel rounded-3xl p-5"><p className="text-sm text-slate-400">FPS</p><p className="mt-2 text-3xl font-bold text-emerald-300">{Number(fps).toFixed(1)}</p></div>
        <div className="glass-panel rounded-3xl p-5"><p className="text-sm text-slate-400">Camera</p><p className="mt-2 text-2xl font-semibold text-white">{cameraStatus}</p></div>
        <div className="glass-panel rounded-3xl p-5"><p className="text-sm text-slate-400">Socket</p><p className="mt-2 text-2xl font-semibold text-white">{connectionStatus}</p></div>
      </div>

      <div className="flex flex-wrap gap-3">
        <button className="rounded-full bg-emerald-500 px-5 py-2 font-medium text-slate-950" onClick={() => startCamera({ source: '0' })} type="button">Start Camera</button>
        <button className="rounded-full bg-rose-500 px-5 py-2 font-medium text-white" onClick={stopCamera} type="button">Stop Camera</button>
        <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300">Stream: {getApiBaseUrl()}/api/camera/stream</div>
      </div>

      <VideoFeed detections={currentDetections} frameSize={frameSize} streamUrl={`${getApiBaseUrl()}/api/camera/stream`} />
      <TrackedHeadsTable detections={currentDetections} />
    </div>
  );
}
