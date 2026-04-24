import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from '../components/Layout';
import Dashboard from '../pages/Dashboard';
import CameraMonitor from '../pages/CameraMonitor';
import DetectionLogs from '../pages/DetectionLogs';
import Settings from '../pages/Settings';

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/camera" element={<CameraMonitor />} />
        <Route path="/logs" element={<DetectionLogs />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
