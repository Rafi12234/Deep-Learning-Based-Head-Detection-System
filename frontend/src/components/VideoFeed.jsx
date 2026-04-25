import DetectionCanvas from './DetectionCanvas';

export default function VideoFeed({ streamUrl, detections, frameSize }) {
  return (
    <div
      className="relative mx-auto w-full max-w-6xl overflow-hidden rounded-3xl border border-white/10 bg-slate-950 shadow-glow"
      style={{ aspectRatio: `${frameSize.width} / ${frameSize.height}`, maxHeight: '72vh' }}
    >
      <img alt="Live camera stream" className="h-full w-full object-cover" src={streamUrl} />
      <DetectionCanvas detections={detections} frameSize={frameSize} />
      <div className="absolute left-4 top-4 rounded-full bg-black/50 px-3 py-1 text-sm text-white">Live Stream</div>
    </div>
  );
}
