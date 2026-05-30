import { useState } from 'react';
import { getApiBaseUrl, getWebSocketUrl } from '../services/api';

export default function Settings() {
  const [apiUrl, setApiUrl] = useState(getApiBaseUrl());
  const [wsUrl, setWsUrl] = useState(getWebSocketUrl());
  const [confidence, setConfidence] = useState('0.35');
  const [cameraSource, setCameraSource] = useState('0');

  return (
    <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
      <div className="glass-panel rounded-3xl p-6">
        <h2 className="text-2xl font-semibold text-white">Settings</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <label className="space-y-2 text-sm text-slate-300"><span>Backend API URL</span><input className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none" value={apiUrl} onChange={event => setApiUrl(event.target.value)} /></label>
          <label className="space-y-2 text-sm text-slate-300"><span>WebSocket URL</span><input className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none" value={wsUrl} onChange={event => setWsUrl(event.target.value)} /></label>
          <label className="space-y-2 text-sm text-slate-300"><span>Confidence Threshold</span><input className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none" value={confidence} onChange={event => setConfidence(event.target.value)} /></label>
          <label className="space-y-2 text-sm text-slate-300"><span>Camera Source</span><input className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none" value={cameraSource} onChange={event => setCameraSource(event.target.value)} /></label>
        </div>
      </div>

      <div className="space-y-4">
        <div className="glass-panel rounded-3xl p-5">
          <h3 className="font-semibold text-white">Model Info</h3>
          <p className="mt-2 text-sm text-slate-400">Recommended trained model location: backend/models/head_detector.pt</p>
        </div>
        <div className="glass-panel rounded-3xl p-5">
          <h3 className="font-semibold text-white">Tracker Info</h3>
          <p className="mt-2 text-sm text-slate-400">Default tracker: ByteTrack. BoT-SORT can be enabled later from backend settings.</p>
        </div>
      </div>
    </div>
  );
}
