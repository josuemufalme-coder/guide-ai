import re
def body_span(xml):
    a = xml.index('<w:body>') + len('<w:body>')
    b = xml.index('</w:body>')
    return a, b

TAG = re.compile(r'<(/?)w:p(\b[^>]*?)(/?)>')

def top_paragraphs(xml):
    """Return list of (start,end) byte spans of top-level <w:p> inside <w:body>."""
    a, b = body_span(xml)
    spans, depth, start = [], 0, None
    for m in TAG.finditer(xml, a, b):
        closing, attrs, selfclose = m.group(1), m.group(2), m.group(3)
        if closing:
            depth -= 1
            if depth == 0:
                spans.append((start, m.end()))
                start = None
        elif selfclose:
            if depth == 0:
                spans.append((m.start(), m.end()))
        else:
            if depth == 0:
                start = m.start()
            depth += 1
    return spans

def text_of(frag):
    return ''.join(re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', frag, re.S))

RTAG = re.compile(r'<(/?)w:r(\b[^>]*?)(/?)>')

def top_runs(frag):
    """(start,end) spans of top-level <w:r> inside a paragraph fragment."""
    spans, depth, start = [], 0, None
    for m in RTAG.finditer(frag):
        closing, selfclose = m.group(1), m.group(3)
        if closing:
            depth -= 1
            if depth == 0:
                spans.append((start, m.end()))
        elif selfclose:
            if depth == 0:
                spans.append((m.start(), m.end()))
        else:
            if depth == 0:
                start = m.start()
            depth += 1
    return spans
