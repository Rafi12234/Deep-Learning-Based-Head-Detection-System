import { createContext, useEffect, useState } from 'react';
import { fetchCurrentDetections, fetchDetectionLogs, fetchHealth, startCamera as apiStartCamera, stopCamera as apiStopCamera } from '../services/api';
import { createDetectionSocket } from '../services/websocket';

export const DetectionContext = createContext(null);

export function DetectionProvider({ children }) {
  const [currentDetections, setCurrentDetections] = useState([]);
  const [totalHeads, setTotalHeads] = useState(0);
  const [fps, setFps] = useState(0);
  const [cameraStatus, setCameraStatus] = useState('stopped');
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [detectionHistory, setDetectionHistory] = useState([]);
  const [logs, setLogs] = useState([]);
  const [frameSize, setFrameSize] = useState({ width: 1280, height: 720 });
  const [health, setHealth] = useState(null);

  useEffect(() => {
    let socket;
    const connect = () => {
      socket = createDetectionSocket(import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/detections', {
        onOpen: () => setConnectionStatus('connected'),
        onClose: () => setConnectionStatus('disconnected'),
        onError: () => setConnectionStatus('error'),
        onMessage: data => {
          if (!data || data.type !== 'detection_update') {
            return;
          }
          setCurrentDetections(data.detections || []);
          setTotalHeads(data.total_heads || 0);
          setFps(data.fps || 0);
          setCameraStatus(data.camera_status || 'stopped');
          setFrameSize({ width: data.frame_width || 1280, height: data.frame_height || 720 });
          setDetectionHistory(previous => [...previous.slice(-49), { timestamp: data.timestamp, total_heads: data.total_heads || 0, fps: data.fps || 0 }]);
        },
      });
    };

    fetchHealth().then(setHealth).catch(() => setHealth(null));
    fetchCurrentDetections().then(data => {
      setCurrentDetections(data.detections || []);
      setTotalHeads(data.total_heads || 0);
      setFps(data.fps || 0);
      setCameraStatus(data.camera_status || 'stopped');
      setFrameSize({ width: data.frame_width || 1280, height: data.frame_height || 720 });
    }).catch(() => undefined);
    fetchDetectionLogs({ limit: 10 }).then(data => setLogs(data.items || [])).catch(() => undefined);
    connect();

    return () => socket?.close();
  }, []);

  const startCamera = async payload => {
    const result = await apiStartCamera(payload);
    setCameraStatus(result.status?.includes('started') ? 'running' : cameraStatus);
    return result;
  };

  const stopCamera = async () => {
    const result = await apiStopCamera();
    setCameraStatus('stopped');
    return result;
  };

  const refreshLogs = async () => {
    const data = await fetchDetectionLogs({ limit: 25 });
    setLogs(data.items || []);
  };

  return (
    <DetectionContext.Provider
      value={{
        currentDetections,
        totalHeads,
        fps,
        cameraStatus,
        connectionStatus,
        detectionHistory,
        logs,
        health,
        frameSize,
        startCamera,
        stopCamera,
        refreshLogs,
        setLogs,
      }}
    >
      {children}
    </DetectionContext.Provider>
  );
}
