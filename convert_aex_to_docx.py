#!/usr/bin/env python3
"""
Convert Gemma_4_31B_Deployment_Analysis_AEX.md to .docx format.
Parses markdown tables and headings into proper Word document tables.
Uses only standard library.
"""
import zipfile
import os
import re


def escape(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def p(text, style="Normal", bold=False):
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style != "Normal" else ''
    rpr = '<w:rPr><w:b/></w:rPr>' if bold else ''
    return f'<w:p>{style_xml}<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'


def table_start():
    return '''<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/>
<w:tblBorders>
<w:top w:val="single" w:sz="6" w:color="333333"/>
<w:bottom w:val="single" w:sz="6" w:color="333333"/>
<w:left w:val="single" w:sz="6" w:color="333333"/>
<w:right w:val="single" w:sz="6" w:color="333333"/>
<w:insideH w:val="single" w:sz="4" w:color="666666"/>
<w:insideV w:val="single" w:sz="4" w:color="666666"/>
</w:tblBorders></w:tblPr>'''


def table_end():
    return '</w:tbl>'


def table_row(cells, is_header=False):
    r = '<w:tr>'
    for cell in cells:
        rpr = '<w:rPr><w:b/></w:rPr>' if is_header else ''
        shd = '<w:shd w:val="clear" w:color="auto" w:fill="E3F2FD"/>' if is_header else ''
        r += f'''<w:tc><w:tcPr>{shd}
<w:tcBorders>
<w:top w:val="single" w:sz="4" w:color="666666"/>
<w:bottom w:val="single" w:sz="4" w:color="666666"/>
<w:left w:val="single" w:sz="4" w:color="666666"/>
<w:right w:val="single" w:sz="4" w:color="666666"/>
</w:tcBorders></w:tcPr>
<w:p><w:r>{rpr}<w:t xml:space="preserve">{escape(cell.strip())}</w:t></w:r></w:p></w:tc>'''
    r += '</w:tr>'
    return r


def parse_md_to_docx_body(md_content):
    """Parse markdown content and convert to OOXML body elements."""
    lines = md_content.split('\n')
    body = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Headings
        if line.startswith('# '):
            body.append(p(line[2:].strip(), "Title"))
            i += 1
        elif line.startswith('## '):
            body.append(p(line[3:].strip(), "Heading1"))
            i += 1
        elif line.startswith('### '):
            body.append(p(line[4:].strip(), "Heading2"))
            i += 1
        # Horizontal rule
        elif line.strip() == '---':
            body.append(p(""))
            i += 1
        # Table detection
        elif '|' in line and line.strip().startswith('|'):
            # Collect all table rows
            table_lines = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            
            # Parse table
            if len(table_lines) >= 2:
                body.append(table_start())
                first_row = True
                for tl in table_lines:
                    # Skip separator rows (|---|---|)
                    if re.match(r'^\|[\s\-:]+\|', tl):
                        continue
                    # Parse cells
                    cells = [c.strip() for c in tl.split('|')[1:-1]]
                    if cells:
                        body.append(table_row(cells, is_header=first_row))
                        first_row = False
                body.append(table_end())
                body.append(p(""))
        # Italic/note lines
        elif line.strip().startswith('*') and not line.strip().startswith('**'):
            text = line.strip().strip('*').strip()
            body.append(p(text, "Normal"))
            i += 1
        # Empty lines
        elif line.strip() == '':
            i += 1
        # Regular text
        else:
            body.append(p(line.strip(), "Normal"))
            i += 1
    
    return body


def make_content_types():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''


def make_rels():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''


def make_word_rels():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''


def make_styles():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:pPr><w:jc w:val="center"/><w:spacing w:after="200"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="52"/><w:color w:val="1a237e"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:pPr><w:spacing w:before="360" w:after="120"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="1565c0"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:pPr><w:spacing w:before="240" w:after="80"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="26"/><w:color w:val="1976d2"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:pPr><w:spacing w:after="100" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:sz w:val="22"/><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/></w:rPr>
  </w:style>
</w:styles>'''


def convert_md_to_docx(md_path, docx_path):
    """Convert a markdown file to .docx."""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    body_elements = parse_md_to_docx_body(md_content)
    body_xml = '\n'.join(body_elements)
    
    document = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    {body_xml}
    <w:sectPr>
      <w:pgSz w:w="15840" w:h="12240" w:orient="landscape"/>
      <w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080"/>
    </w:sectPr>
  </w:body>
</w:document>'''
    
    with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', make_content_types())
        zf.writestr('_rels/.rels', make_rels())
        zf.writestr('word/_rels/document.xml.rels', make_word_rels())
        zf.writestr('word/styles.xml', make_styles())
        zf.writestr('word/document.xml', document)
    
    print(f"Converted: {md_path} -> {docx_path}")
    print(f"File size: {os.path.getsize(docx_path):,} bytes")


if __name__ == "__main__":
    md_file = "/projects/sandbox/test/Gemma_4_31B_Deployment_Analysis_AEX.md"
    docx_file = "/projects/sandbox/test/Gemma_4_31B_Deployment_Analysis_AEX.docx"
    convert_md_to_docx(md_file, docx_file)
