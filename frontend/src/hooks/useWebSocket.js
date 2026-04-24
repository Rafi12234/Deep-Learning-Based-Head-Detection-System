import { useEffect, useState } from 'react';
import { createDetectionSocket } from '../services/websocket';

export default function useWebSocket(url, onMessage) {
  const [status, setStatus] = useState('disconnected');

  useEffect(() => {
    const socket = createDetectionSocket(url, {
      onOpen: () => setStatus('connected'),
      onClose: () => setStatus('disconnected'),
      onError: () => setStatus('error'),
      onMessage,
    });

    return () => socket.close();
  }, [url, onMessage]);

  return status;
}
