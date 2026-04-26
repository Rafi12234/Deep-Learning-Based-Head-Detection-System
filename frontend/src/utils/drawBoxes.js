export function drawBoxes(canvas, detections, frameSize) {
  if (!canvas || !frameSize.width || !frameSize.height) {
    return;
  }

  const context = canvas.getContext('2d');
  if (!context) return;

  const rect = canvas.getBoundingClientRect();
  const scaleX = rect.width / frameSize.width;
  const scaleY = rect.height / frameSize.height;
  const pixelRatio = window.devicePixelRatio || 1;

  canvas.width = rect.width * pixelRatio;
  canvas.height = rect.height * pixelRatio;
  context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  context.clearRect(0, 0, rect.width, rect.height);

  detections.forEach(detection => {
    const {
      bbox,
      label,
      confidence,
      direction,
      risk_status: riskStatus = 'normal',
      side_look_duration_seconds: sideLookDuration = 0,
      suspicious_side_look_count: suspiciousCount = 0,
      potential_unethical: potentialUnethical = false,
    } = detection;
    const x = bbox.x1 * scaleX;
    const y = bbox.y1 * scaleY;
    const width = (bbox.x2 - bbox.x1) * scaleX;
    const height = (bbox.y2 - bbox.y1) * scaleY;

    const isSuspicious = riskStatus === 'suspicious';
    const strokeColor = potentialUnethical ? '#dc2626' : (isSuspicious ? '#f59e0b' : '#ef4444');
    context.strokeStyle = strokeColor;
    context.lineWidth = 2;
    context.strokeRect(x, y, width, height);

    const directionTag = direction || 'Forward';
    let riskTag = '';
    if (potentialUnethical) {
      riskTag = `UNETHICAL? x${suspiciousCount}`;
    } else if (isSuspicious) {
      riskTag = `SUSPICIOUS ${sideLookDuration.toFixed(1)}s x${suspiciousCount}`;
    }

    const textBase = `${label} ${directionTag} ${(confidence * 100).toFixed(0)}%`;
    const text = riskTag ? `${textBase} ${riskTag}` : textBase;
    context.font = '600 12px Space Grotesk, sans-serif';
    const textWidth = context.measureText(text).width + 16;
    context.fillStyle = potentialUnethical
      ? 'rgba(220, 38, 38, 0.95)'
      : (isSuspicious ? 'rgba(245, 158, 11, 0.95)' : 'rgba(239, 68, 68, 0.95)');
    context.fillRect(x, Math.max(0, y - 24), textWidth, 20);
    context.fillStyle = '#fff';
    context.fillText(text, x + 8, Math.max(14, y - 10));
  });
}
