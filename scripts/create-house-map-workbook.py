from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape


OUTPUT = Path('house-of-representatives-map.xlsx')
TILE = 48


def cell(column, row):
    letters = ''
    while column:
        column, remainder = divmod(column - 1, 26)
        letters = chr(65 + remainder) + letters
    return f'{letters}{row}'


def inline(value, style=None):
    style_attribute = f' s="{style}"' if style is not None else ''
    return f'<c r="{value[0]}"{style_attribute} t="inlineStr"><is><t>{escape(str(value[1]))}</t></is></c>'


def number(address, value, style=None):
    style_attribute = f' s="{style}"' if style is not None else ''
    return f'<c r="{address}"{style_attribute}><v>{value}</v></c>'


def row_xml(row_number, values):
    cells = []
    for column, value, style in values:
        cells.append(inline((cell(column, row_number), value), style))
    return f'<row r="{row_number}">{"".join(cells)}</row>'


def overview_sheet():
    # Styles: title, subtitle, header, chamber, caucus, cloakroom, connector,
    # committee, hallway, door, prop, table-heading, table-body, note.
    rows = [
        row_xml(1, [(1, 'HOUSE OF REPRESENTATIVES - GRAPHICS MAP', 1)]),
        row_xml(2, [(1, 'Editable planning workbook | Source: src/World.svelte | Grid: 48 px per tile', 2)]),
        row_xml(4, [(1, 'MAP OVERVIEW (each cell = 48 x 48 px)', 3)]),
    ]
    for row in range(5, 26):
        values = []
        for column in range(1, 25):
            label = ''
            style = 12
            if 6 <= row <= 15 and 6 <= column <= 19:
                style = 4
            if 7 <= row <= 11 and 2 <= column <= 3:
                style = 5
            if 7 <= row <= 11 and 22 <= column <= 23:
                style = 5
            if 7 <= row <= 15 and column == 4:
                style = 6
            if 7 <= row <= 15 and column == 21:
                style = 6
            if 16 <= row <= 17 and 11 <= column <= 14:
                style = 7
            if row == 18 and 8 <= column <= 17:
                style = 8
            if row == 20 and 3 <= column <= 22:
                style = 9
            if (column, row) == (12, 5): label, style = 'PUBLIC GALLERY', 10
            if (column, row) == (12, 6): label, style = "SPEAKER'S ROSTRUM", 10
            if (column, row) == (12, 10): label, style = 'HOUSE CHAMBER', 10
            if (column, row) == (2, 9): label, style = 'WEST CAUCUS', 10
            if (column, row) == (23, 9): label, style = 'EAST CAUCUS', 10
            if (column, row) == (4, 8): label, style = 'WEST CLOAKROOM', 10
            if (column, row) == (21, 8): label, style = 'EAST CLOAKROOM', 10
            if (column, row) == (12, 16): label, style = 'CONNECTOR', 10
            if (column, row) == (12, 18): label, style = 'COMMITTEE MARKUP', 10
            if (column, row) == (12, 20): label, style = 'ROTUNDA HALLWAY', 10
            if (column, row) == (12, 21): label, style = 'EXIT TO D.C.', 10
            values.append((column, label, style))
        rows.append(row_xml(row, values))

    rows.extend([
        row_xml(28, [(1, 'EDITABLE ASSET / ZONE LIST', 3)]),
        row_xml(29, [(1, 'Zone', 11), (2, 'Map bounds in pixels', 11), (3, 'Entry / purpose', 11), (4, 'Graphics notes', 11)]),
    ])
    zones = [
        ('Main House Chamber', 'x 1920-7248; y 144-1344', 'Primary playable space', 'Public gallery, Speaker rostrum, 180 desks, legislators'),
        ('West Caucus', 'x 192-1104; y 240-720', 'Enter only from House', 'Side room; west upper door connection'),
        ('East Caucus', 'x 8016-8976; y 240-720', 'Enter only from House', 'Side room; east upper door connection'),
        ('West Cloakroom', 'x 1296-1728; y 240-1344', 'Enter only from House', 'Side room; two House door connections'),
        ('East Cloakroom', 'x 7392-7824; y 240-1344', 'Enter only from House', 'Side room; two House door connections'),
        ('Committee Connector', 'x 4320-4848; y 1344-1584', 'House to committee route', 'Short vertical connection'),
        ('Committee Markup', 'x 3408-5808; y 1584-1728', 'House-linked route', 'Committee encounter route'),
        ('Rotunda Hallway', 'x 528-8688; y 1776-1872', 'House exit route', 'Rotunda Hall access and Exit to D.C.'),
    ]
    for offset, zone in enumerate(zones, 30):
        rows.append(row_xml(offset, [(1, zone[0], 13), (2, zone[1], 13), (3, zone[2], 13), (4, zone[3], 13)]))
    return ''.join(rows)


def side_rooms_sheet():
    rows = [
        row_xml(1, [(1, 'HOUSE-ONLY SIDE ROOMS', 1)]),
        row_xml(2, [(1, 'All four rooms below can be entered only from the House map.', 2)]),
        row_xml(4, [(1, 'Room', 11), (2, 'House map bounds (px)', 11), (3, 'Door locations on House map (px)', 11), (4, 'Room contents / graphics cues', 11), (5, 'Room-specific staff role', 11), (6, 'Scout targets', 11)]),
    ]
    rooms = [
        ('West Caucus', 'x 192-1104; y 240-720', 'West upper door: x 1104-1920; y 480-576', 'Reference shelf; coats; caucus table; chairs; 3 caucus members', 'Caucus Researcher', 'Priya Anand; Diane Okafor'),
        ('East Caucus', 'x 8016-8976; y 240-720', 'East upper door: x 7248-8016; y 480-576', 'Reference shelf; coats; caucus table; chairs; 3 caucus members', 'District Aide', 'Selena Marsh; Robin Yates'),
        ('West Cloakroom', 'x 1296-1728; y 240-1344', 'West upper: x 1104-1920; y 480-576 | West lower: x 1728-1920; y 960-1056', 'Reference shelf; coats; work table; chairs', 'Cloakroom Staffer', 'Hank Delgado; Gus Whitfield'),
        ('East Cloakroom', 'x 7392-7824; y 240-1344', 'East upper: x 7248-8016; y 480-576 | East lower: x 7248-7392; y 960-1056', 'Reference shelf; coats; work table; chairs', 'Message Board Intern', 'Naomi Cho; Cyrus Boone'),
    ]
    for row, room in enumerate(rooms, 5):
        rows.append(row_xml(row, [(column, value, 13) for column, value in enumerate(room, 1)]))
    rows.extend([
        row_xml(11, [(1, 'ROOM INTERIOR BUILD (separate playable room)', 3)]),
        row_xml(12, [(1, 'Interior grid', 11), (2, 'Player start', 11), (3, 'Reference material', 11), (4, 'Staff position', 11), (5, 'Return zone', 11)]),
        row_xml(13, [(1, '1000 x 800 px; 50 px tiles', 13), (2, '500, 700', 13), (3, '200, 300', 13), (4, '800, 300', 13), (5, 'bottom edge: y >= 700', 13)]),
    ])
    return ''.join(rows)


def assets_sheet():
    rows = [
        row_xml(1, [(1, 'HOUSE MAP GRAPHICS CHECKLIST', 1)]),
        row_xml(2, [(1, 'Use this sheet to track replacements or refinements while preserving map purpose and navigation.', 2)]),
        row_xml(4, [(1, 'Area', 11), (2, 'Asset or detail', 11), (3, 'Current implementation', 11), (4, 'Status', 11), (5, 'Notes / replacement path', 11)]),
    ]
    assets = [
        ('Chamber', 'Public gallery', 'Labeled band at north of chamber', 'To refine', ''),
        ('Chamber', "Speaker's rostrum", 'Labeled focal point below gallery', 'To refine', ''),
        ('Chamber', 'Representative desks', '180 desk markers in 36 columns x 5 rows', 'To refine', ''),
        ('Chamber', 'Background legislators', '34 walking sprite placements', 'To refine', 'public/assets/sprites/'),
        ('Chamber', 'Floor papers', 'Interactive study prop', 'To refine', ''),
        ('Chamber', 'Vote ledger', 'Interactive study prop', 'To refine', ''),
        ('Chamber', 'Briefing table', 'Interactive study prop', 'To refine', ''),
        ('Cloakrooms', 'Study boards', 'West and east boards; hallway floor notes', 'To refine', ''),
        ('Side rooms', 'Reference shelf', 'Study-find prop in each side room', 'To refine', ''),
        ('Side rooms', 'Coat rack / coats', 'Interior prop in each side room', 'To refine', ''),
        ('Side rooms', 'Table and chairs', 'Caucus table or work table plus chairs', 'To refine', ''),
        ('Routes', 'Doors and labels', 'Four House-to-side-room doors', 'To refine', 'Keep entry points readable'),
        ('Routes', 'Committee connector and hallway', 'South exit from chamber', 'To refine', ''),
    ]
    for row, asset in enumerate(assets, 5):
        rows.append(row_xml(row, [(column, value, 13) for column, value in enumerate(asset, 1)]))
    return ''.join(rows)


STYLES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="4"><font><sz val="10"/><name val="Aptos"/></font><font><b/><sz val="18"/><color rgb="FFFFFFFF"/><name val="Aptos Display"/></font><font><i/><sz val="10"/><color rgb="FF52606D"/><name val="Aptos"/></font><font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Aptos"/></font></fonts>
<fills count="13"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF183B56"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFF1F5F9"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFBDE3F5"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFC7E9D4"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFF8D7A8"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE5D0F0"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFC9C9"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFD4D4D4"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF355C7D"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FF274C77"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFFFFF"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border><border><left style="thin"><color rgb="FF94A3B8"/></left><right style="thin"><color rgb="FF94A3B8"/></right><top style="thin"><color rgb="FF94A3B8"/></top><bottom style="thin"><color rgb="FF94A3B8"/></bottom><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="14"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" applyFont="1" applyFill="1"><alignment horizontal="left" vertical="center"/></xf><xf numFmtId="0" fontId="2" fillId="0" borderId="0" applyFont="1"><alignment horizontal="left" vertical="center"/></xf><xf numFmtId="0" fontId="3" fillId="11" borderId="0" applyFont="1" applyFill="1"><alignment horizontal="left" vertical="center"/></xf><xf numFmtId="0" fontId="0" fillId="4" borderId="1" applyFill="1" applyBorder="1"/><xf numFmtId="0" fontId="0" fillId="5" borderId="1" applyFill="1" applyBorder="1"/><xf numFmtId="0" fontId="0" fillId="6" borderId="1" applyFill="1" applyBorder="1"/><xf numFmtId="0" fontId="0" fillId="7" borderId="1" applyFill="1" applyBorder="1"/><xf numFmtId="0" fontId="0" fillId="8" borderId="1" applyFill="1" applyBorder="1"/><xf numFmtId="0" fontId="0" fillId="9" borderId="1" applyFill="1" applyBorder="1"/><xf numFmtId="0" fontId="3" fillId="10" borderId="1" applyFont="1" applyFill="1" applyBorder="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf><xf numFmtId="0" fontId="3" fillId="11" borderId="1" applyFont="1" applyFill="1" applyBorder="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf><xf numFmtId="0" fontId="0" fillId="12" borderId="1" applyFill="1" applyBorder="1"/><xf numFmtId="0" fontId="0" fillId="12" borderId="1" applyFill="1" applyBorder="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs>
</styleSheet>'''


def sheet_xml(rows, dimensions, widths, freeze=None):
    columns = ''.join(f'<col min="{minimum}" max="{maximum}" width="{width}" customWidth="1"/>' for minimum, maximum, width in widths)
    pane = f'<pane ySplit="{freeze}" topLeftCell="A{freeze + 1}" activePane="bottomLeft" state="frozen"/>' if freeze else ''
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="{dimensions}"/><sheetViews><sheetView workbookViewId="0">{pane}</sheetView></sheetViews><sheetFormatPr defaultRowHeight="15"/><cols>{columns}</cols><sheetData>{rows}</sheetData><mergeCells count="2"><mergeCell ref="A1:F1"/><mergeCell ref="A2:F2"/></mergeCells></worksheet>'''


def main():
    sheets = [
        ('House Map Overview', overview_sheet(), 'A1:X37', [(1, 24, 17)], 4),
        ('House-Only Side Rooms', side_rooms_sheet(), 'A1:F13', [(1, 1, 22), (2, 3, 34), (4, 4, 48), (5, 6, 28)], 4),
        ('Graphics Checklist', assets_sheet(), 'A1:E17', [(1, 1, 18), (2, 2, 27), (3, 3, 40), (4, 4, 14), (5, 5, 36)], 4),
    ]
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    workbook_sheets = ''.join(f'<sheet name="{name}" sheetId="{index}" r:id="rId{index}"/>' for index, (name, _, _, _, _) in enumerate(sheets, 1))
    workbook_rels = ''.join(f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{index}.xml"/>' for index in range(1, 4))
    content_sheets = ''.join(f'<Override PartName="/xl/worksheets/sheet{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for index in range(1, 4))
    with ZipFile(OUTPUT, 'w', ZIP_DEFLATED) as workbook:
        workbook.writestr('[Content_Types].xml', f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>{content_sheets}<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>''')
        workbook.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>''')
        workbook.writestr('docProps/core.xml', f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:creator>Capitol Hill Crawler</dc:creator><dc:title>House of Representatives Map</dc:title><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>''')
        workbook.writestr('docProps/app.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Excel</Application><Sheets>3</Sheets></Properties>''')
        workbook.writestr('xl/workbook.xml', f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><bookViews><workbookView activeTab="0"/></bookViews><sheets>{workbook_sheets}</sheets></workbook>''')
        workbook.writestr('xl/_rels/workbook.xml.rels', f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{workbook_rels}<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>''')
        workbook.writestr('xl/styles.xml', STYLES)
        for index, (_, rows, dimensions, widths, freeze) in enumerate(sheets, 1):
            workbook.writestr(f'xl/worksheets/sheet{index}.xml', sheet_xml(rows, dimensions, widths, freeze))
    print(f'Created {OUTPUT}')


if __name__ == '__main__':
    main()
