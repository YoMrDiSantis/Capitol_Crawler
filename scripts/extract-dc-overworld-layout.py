from collections import defaultdict
import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET


SOURCE = Path('DC Overworld Map Singles/dc-overworld-map.xlsx')
OUTPUT = Path('src/dc-overworld-layout.ts')
NAMESPACE = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
COLS, ROWS = 120, 80


def coordinates(reference):
    letters = ''.join(character for character in reference if character.isalpha())
    column = 0
    for character in letters:
        column = column * 26 + ord(character) - 64
    return column - 2, int(''.join(character for character in reference if character.isdigit())) - 5


def components(grid, code):
    remaining = {(column, row) for row in range(ROWS) for column in range(COLS) if grid[row][column] == code}
    output = []
    while remaining:
        pending = [remaining.pop()]
        component = []
        while pending:
            column, row = pending.pop()
            component.append((column, row))
            for neighbor in ((column + 1, row), (column - 1, row), (column, row + 1), (column, row - 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    pending.append(neighbor)
        left = min(column for column, _ in component)
        top = min(row for _, row in component)
        output.append((left, top, max(column for column, _ in component) - left + 1, max(row for _, row in component) - top + 1))
    return sorted(output, key=lambda item: (item[1], item[0]))


def main():
    with ZipFile(SOURCE) as workbook:
        strings = [''.join(node.itertext()) for node in ET.fromstring(workbook.read('xl/sharedStrings.xml')).findall('x:si', NAMESPACE)]
        sheet = ET.fromstring(workbook.read('xl/worksheets/sheet1.xml'))
    grid = [['GR' for _ in range(COLS)] for _ in range(ROWS)]
    for node in sheet.findall('.//x:sheetData/x:row/x:c', NAMESPACE):
        column, row = coordinates(node.attrib['r'])
        if column < 0 or row < 0:
            continue
        value = node.findtext('x:v', default='', namespaces=NAMESPACE)
        grid[row][column] = strings[int(value)] if node.attrib.get('t') == 's' else value

    codes = sorted({value for row in grid for value in row} - {'GR', 'RD', 'PR'})
    groups = {code: components(grid, code) for code in codes}
    press_or_river = components(grid, 'PR')
    groups['PR'] = [rect for rect in press_or_river if rect[0] != 110]
    road_cells = [(column, row) for row in range(ROWS) for column in range(COLS) if grid[row][column] == 'RD']
    river_cells = [(column, row) for row in range(ROWS) for column in range(COLS) if grid[row][column] == 'PR' and column >= 110]
    output = [
        '// Generated from DC Overworld Map Singles/dc-overworld-map.xlsx. Do not edit by hand.',
        'export type DcMapRect = { code: string; col: number; row: number; width: number; height: number };',
        f'export const dcRoadTiles: readonly [number, number][] = {json.dumps(road_cells)};',
        f'export const dcRiverTiles: readonly [number, number][] = {json.dumps(river_cells)};',
        f'const dcMapRectData: [string, number, number, number, number][] = {json.dumps([[code, *rect] for code in [*codes, "PR"] for rect in groups[code]])};',
        'export const dcMapRects: readonly DcMapRect[] = dcMapRectData.map(([code, col, row, width, height]) => ({ code, col, row, width, height }));',
    ]
    OUTPUT.write_text('\n'.join(output) + '\n')
    print(f'Created {OUTPUT}')


if __name__ == '__main__':
    main()
