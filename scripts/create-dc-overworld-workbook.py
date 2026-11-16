from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape


OUTPUT = Path('dc-overworld-map.xlsx')
COLS, ROWS = 120, 80


def cell(column, row):
    letters = ''
    while column:
        column, remainder = divmod(column - 1, 26)
        letters = chr(65 + remainder) + letters
    return f'{letters}{row}'


def inline(address, value, style):
    return f'<c r="{address}" s="{style}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'


def row_xml(row, values):
    return f'<row r="{row}">{"".join(inline(cell(col, row), value, style) for col, value, style in values)}</row>'


def fill(grid, code, left, top, width, height):
    for y in range(top, top + height):
        for x in range(left, left + width):
            if 0 <= x < COLS and 0 <= y < ROWS:
                grid[y][x] = code


def map_sheet():
    grid = [['GR' for _ in range(COLS)] for _ in range(ROWS)]
    roads = [(0, 2, 120, 4), (0, 18, 120, 4), (46, 32, 74, 4), (0, 69, 120, 4), (20, 0, 4, 22), (34, 0, 4, 22), (46, 0, 4, 36), (64, 0, 4, 36), (76, 0, 4, 80), (90, 0, 4, 80), (104, 0, 4, 80)]
    for x, y, width, height in roads:
        fill(grid, 'RD', x, y, width, height)
    for style, x, y, width, height in [
        ('RH1', 6, 8, 6, 6), ('RH2', 13, 8, 5, 6), ('RH3', 26, 8, 6, 4), ('RH4', 26, 13, 6, 3), ('LR1', 40, 8, 4, 4), ('LR2', 40, 13, 4, 3), ('HTL', 70, 8, 4, 8), ('LR3', 82, 8, 6, 4), ('LR4', 82, 13, 6, 3), ('HR1', 96, 8, 6, 8),
        ('RH1', 6, 24, 6, 6), ('RH2', 13, 24, 5, 6), ('RH3', 26, 24, 6, 6), ('LR1', 40, 24, 4, 6), ('AN1', 52, 24, 6, 6), ('LR2', 70, 24, 4, 6), ('HR1', 82, 24, 6, 6), ('LR3', 82, 38, 6, 4), ('AN1', 24, 38, 6, 4), ('AN2', 31, 38, 6, 4), ('RH1', 22, 63, 6, 5), ('RH2', 30, 63, 6, 5), ('LR4', 60, 63, 6, 5), ('MR1', 68, 63, 6, 5),
    ]:
        fill(grid, style, x, y, width, height)
    landmarks = [('CAP', 96, 52, 8, 6), ('WH', 52, 8, 8, 6), ('WM', 42, 33, 3, 5), ('RP', 16, 44, 12, 20), ('LM', 8, 50, 8, 6), ('SM', 48, 54, 10, 5), ('LC', 101, 52, 7, 5), ('SC', 101, 42, 7, 5), ('CF', 50, 62, 5, 4), ('PR', 68, 42, 6, 4), ('DJ', 30, 51, 2, 2), ('VC', 84, 61, 6, 4)]
    for code, x, y, width, height in landmarks:
        fill(grid, code, x, y, width, height)
    props = [('TR', 14, 34, 4, 3), ('TR', 30, 49, 4, 3), ('TR', 58, 47, 4, 3), ('TR', 74, 51, 4, 3), ('HD', 36, 58, 4, 2), ('FL', 39, 57, 4, 3), ('PL', 57, 49, 3, 2), ('BN', 29, 53, 3, 2), ('BN', 61, 58, 3, 2), ('BR', 72, 44, 3, 2), ('HY', 74, 38, 2, 2), ('SL', 22, 43, 1, 3), ('SL', 39, 44, 1, 3), ('SL', 79, 46, 1, 3), ('TL', 76, 32, 1, 3), ('TL', 90, 32, 1, 3), ('BS', 72, 37, 4, 3), ('VS', 10, 46, 3, 3)]
    for code, x, y, width, height in props:
        fill(grid, code, x, y, width, height)
    styles = {'GR': 4, 'RD': 5, 'CAP': 6, 'WH': 6, 'WM': 6, 'RP': 7, 'LM': 6, 'SM': 6, 'LC': 6, 'SC': 6, 'CF': 6, 'PR': 6, 'DJ': 6, 'VC': 6, 'RH1': 8, 'RH2': 8, 'RH3': 8, 'RH4': 8, 'LR1': 8, 'LR2': 8, 'LR3': 8, 'LR4': 8, 'HR1': 8, 'HTL': 8, 'AN1': 8, 'AN2': 8, 'MR1': 8, 'TR': 9, 'HD': 9, 'FL': 9, 'PL': 9, 'BN': 9, 'BR': 9, 'HY': 9, 'SL': 9, 'TL': 9, 'BS': 9, 'VS': 9}
    rows = [row_xml(1, [(1, 'WASHINGTON, D.C. OVERWORLD MAP', 1)]), row_xml(2, [(1, 'Editable planning grid | 120 columns x 80 rows | Each cell = 48 x 48 px | Edit codes and colors to plan changes.', 2)]), row_xml(4, [(1, 'COLUMN', 3)] + [(col + 2, str(col + 1), 3) for col in range(COLS)])]
    for y in range(ROWS):
        values = [(1, str(y + 1), 3)]
        for x in range(COLS):
            code = grid[y][x]
            values.append((x + 2, code, styles[code]))
        rows.append(row_xml(y + 5, values))
    return ''.join(rows)


def legend_sheet():
    entries = [
        ('GR', 'Grass terrain', 'Base terrain'), ('RD', 'Road', 'Vehicle route'), ('CAP', 'U.S. Capitol / Rotunda', 'Landmark'), ('WH', 'White House', 'Landmark, moved to row 11'), ('WM', 'Washington Monument', 'Landmark, 3 x 5 tiles'), ('RP', 'Reflecting Pool', 'Landmark'), ('LM', 'Lincoln Memorial', 'Landmark'), ('SM', 'Smithsonian Museums', 'Landmark'), ('LC', 'Library of Congress', 'Landmark'), ('SC', 'Supreme Court', 'Landmark'), ('CF', 'Mall Cafe', 'Landmark'), ('PR', 'Press Row', 'Landmark'), ('DJ', 'Duncan Johnson', 'Landmark'), ('VC', 'Visitor Center', 'Landmark'), ('RH1-RH4', 'Rowhouses', 'Regular building art'), ('LR1-LR4', 'Low-rise buildings', 'Regular building art'), ('HR1', 'High-rise building', 'Regular building art'), ('HTL', 'Hotel', 'Regular building art'), ('AN1-AN2', 'Annexes', 'Regular building art'), ('MR1', 'Mid-rise building', 'Regular building art'), ('TR', 'Tree group', 'Prop'), ('HD / FL / PL', 'Hedge, flowers, planter', 'Prop'), ('BN / BR / HY', 'Bench, bike rack, hydrant', 'Prop'), ('SL / TL / BS / VS', 'Streetlamp, traffic light, bus stop, visitor sign', 'Prop'),
    ]
    rows = [row_xml(1, [(1, 'D.C. OVERWORLD MAP LEGEND', 1)]), row_xml(2, [(1, 'Change the Map Grid codes first, then use this legend to update the game implementation.', 2)]), row_xml(4, [(1, 'Code', 3), (2, 'Map element', 3), (3, 'Notes', 3)])]
    rows.extend(row_xml(index, [(1, code, 10), (2, label, 11), (3, notes, 11)]) for index, (code, label, notes) in enumerate(entries, 5))
    return ''.join(rows)


def locations_sheet():
    locations = [('Landmark', 'Map column', 'Map row', 'Width (tiles)', 'Height (tiles)', 'Notes'), ('U.S. Capitol / Rotunda', '99', '58', '8', '6', 'Returns to Rotunda'), ('White House', '55', '11', '8', '6', 'Moved north three tiles'), ('Washington Monument', '43', '38', '3', '5', 'Single landmark footprint'), ('Reflecting Pool', '16', '44', '12', '20', 'West Mall'), ('Lincoln Memorial', '8', '50', '8', '6', 'West Mall'), ('Smithsonian Museums', '48', '54', '10', '5', 'Museum Row'), ('Library of Congress', '101', '52', '7', '5', 'Capitol Hill'), ('Supreme Court', '101', '42', '7', '5', 'Capitol Hill'), ('Mall Cafe', '50', '62', '5', '4', 'Museum Row'), ('Press Row', '68', '42', '6', '4', 'Penn Quarter'), ('Duncan Johnson', '30', '51', '2', '2', 'West Mall'), ('Visitor Center', '84', '61', '6', '4', 'Capitol Hill')]
    rows = [row_xml(1, [(1, 'D.C. LANDMARK PLACEMENT LIST', 1)]), row_xml(2, [(1, 'These are the current gameplay anchors. Update this sheet while planning map changes.', 2)])]
    rows.extend(row_xml(index, [(column, value, 11 if index == 4 else 12) for column, value in enumerate(item, 1)]) for index, item in enumerate(locations, 4))
    return ''.join(rows)


STYLES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="4"><font><sz val="9"/><name val="Aptos"/></font><font><b/><sz val="18"/><color rgb="FFFFFFFF"/><name val="Aptos Display"/></font><font><i/><sz val="10"/><color rgb="FF52606D"/><name val="Aptos"/></font><font><b/><sz val="9"/><color rgb="FFFFFFFF"/><name val="Aptos"/></font></fonts><fills count="10"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF183B56"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF355C7D"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF73966B"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF505A60"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFF0D69A"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF5C9BB5"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFB86949"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF4F7B51"/></patternFill></fill></fills><borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left style="thin"><color rgb="FF506A64"/></left><right style="thin"><color rgb="FF506A64"/></right><top style="thin"><color rgb="FF506A64"/></top><bottom style="thin"><color rgb="FF506A64"/></bottom><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="13"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" applyFont="1" applyFill="1"/><xf numFmtId="0" fontId="2" fillId="0" borderId="0" applyFont="1"/><xf numFmtId="0" fontId="3" fillId="3" borderId="1" applyFont="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="4" borderId="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="5" borderId="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="6" borderId="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="7" borderId="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="8" borderId="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="9" borderId="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center"/></xf><xf numFmtId="0" fontId="3" fillId="4" borderId="1" applyFont="1" applyFill="1" applyBorder="1"/><xf numFmtId="0" fontId="0" fillId="0" borderId="1" applyBorder="1"><alignment wrapText="1"/></xf><xf numFmtId="0" fontId="0" fillId="0" borderId="1" applyBorder="1"/></cellXfs></styleSheet>'''


def sheet_xml(rows, ref, widths, merge_end):
    cols = ''.join(f'<col min="{start}" max="{end}" width="{width}" customWidth="1"/>' for start, end, width in widths)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="{ref}"/><sheetViews><sheetView workbookViewId="0"><pane xSplit="1" ySplit="4" topLeftCell="B5" activePane="bottomRight" state="frozen"/></sheetView></sheetViews><sheetFormatPr defaultRowHeight="15"/><cols>{cols}</cols><sheetData>{rows}</sheetData><mergeCells count="2"><mergeCell ref="A1:{merge_end}1"/><mergeCell ref="A2:{merge_end}2"/></mergeCells></worksheet>'''


def main():
    sheets = [('Map Grid', map_sheet(), 'A1:DQ84', [(1, 1, 8), (2, 121, 5.2)], 'DQ'), ('Legend', legend_sheet(), 'A1:C28', [(1, 1, 16), (2, 2, 34), (3, 3, 38)], 'C'), ('Landmark Locations', locations_sheet(), 'A1:F17', [(1, 1, 28), (2, 5, 16), (6, 6, 36)], 'F')]
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with ZipFile(OUTPUT, 'w', ZIP_DEFLATED) as book:
        overrides = ''.join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1, 4))
        book.writestr('[Content_Types].xml', f'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>{overrides}<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>')
        book.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>')
        book.writestr('docProps/core.xml', f'<?xml version="1.0" encoding="UTF-8"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:creator>Capitol Hill Crawler</dc:creator><dc:title>D.C. Overworld Map</dc:title><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created></cp:coreProperties>')
        book.writestr('xl/workbook.xml', '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Map Grid" sheetId="1" r:id="rId1"/><sheet name="Legend" sheetId="2" r:id="rId2"/><sheet name="Landmark Locations" sheetId="3" r:id="rId3"/></sheets></workbook>')
        book.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        book.writestr('xl/styles.xml', STYLES)
        for index, (_, rows, ref, widths, merge_end) in enumerate(sheets, 1):
            book.writestr(f'xl/worksheets/sheet{index}.xml', sheet_xml(rows, ref, widths, merge_end))
    print(f'Created {OUTPUT}')


if __name__ == '__main__':
    main()
