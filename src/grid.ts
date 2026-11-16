export function snapToGrid(value: number, tileSize: number) {
  return Math.round(value / tileSize) * tileSize;
}

export function clampGridPosition(value: number, minimum: number, maximum: number, tileSize: number) {
  return Math.max(minimum, Math.min(maximum, snapToGrid(value, tileSize)));
}
