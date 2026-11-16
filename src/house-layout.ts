export type HousePropType =
  | 'desk'
  | 'chair'
  | 'table'
  | 'lectern'
  | 'bookshelf'
  | 'bench'
  | 'statue'
  | 'display-case'
  | 'message-board'
  | 'paper-table'
  | 'carpet'
  | 'column';

export type HouseProp = {
  id: string;
  type: HousePropType;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  mirrored?: boolean;
};

export type HouseLayout = {
  version: 1;
  hideBuiltInDesks: boolean;
  props: HouseProp[];
};

export const HOUSE_LAYOUT_KEY = 'capitol-hill-crawler-house-layout-v1';
export const housePropLabels: Record<HousePropType, string> = {
  desk: 'House desk',
  chair: 'Chair',
  table: 'Committee table',
  lectern: 'Lectern',
  bookshelf: 'Bookshelf',
  bench: 'Bench',
  statue: 'Statue',
  'display-case': 'Display case',
  'message-board': 'Message board',
  'paper-table': 'Paper table',
  carpet: 'Carpet section',
  column: 'Column'
};

export const housePropTypes = Object.keys(housePropLabels) as HousePropType[];

export const defaultHouseLayout: HouseLayout = {
  version: 1,
  hideBuiltInDesks: false,
  props: []
};

export function isHouseLayout(value: unknown): value is HouseLayout {
  if (!value || typeof value !== 'object') return false;
  const layout = value as Partial<HouseLayout>;
  return layout.version === 1
    && typeof layout.hideBuiltInDesks === 'boolean'
    && Array.isArray(layout.props)
    && layout.props.every((prop) => prop
      && typeof prop.id === 'string'
      && housePropTypes.includes(prop.type as HousePropType)
      && [prop.x, prop.y, prop.width, prop.height, prop.rotation].every((number) => typeof number === 'number' && Number.isFinite(number)));
}
