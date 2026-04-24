export function formatTime(value) {
  if (!value) return '-';
  return new Date(value).toLocaleString();
}
