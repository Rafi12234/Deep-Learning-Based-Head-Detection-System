import { useEffect, useRef } from 'react';
import { drawBoxes } from '../utils/drawBoxes';

export default function DetectionCanvas({ detections, frameSize }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    drawBoxes(canvasRef.current, detections, frameSize);
    
  }, [detections, frameSize]);
  

  return <canvas ref={canvasRef} className="pointer-events-none absolute inset-0 h-full w-full" />;
}
