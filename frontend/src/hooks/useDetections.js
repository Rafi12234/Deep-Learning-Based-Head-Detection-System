import { useContext } from 'react';
import { DetectionContext } from '../context/DetectionContext';

export default function useDetections() {
  return useContext(DetectionContext);
}
