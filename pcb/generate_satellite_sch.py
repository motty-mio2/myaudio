import uuid
import re
import os

def gen_uuid():
    return str(uuid.uuid4())

def extract_symbol_body(lib_path, sym_name):
    with open(lib_path, 'r', encoding='utf-8') as f:
        content = f.read()
    start_tag = f'(symbol "{sym_name}"'
    idx = content.find(start_tag)
    if idx == -1:
        raise ValueError(f"Symbol {sym_name} not found in {lib_path}")
    depth = 0
    for i in range(idx, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return content[idx:i+1]
    raise ValueError(f"Unmatched parenthesis for {sym_name}")

# Prepare satellite.kicad_pro
pro_content = '''{
  "board": {
    "design_settings": {
      "defaults": {},
      "diff_pair_dimensions": [],
      "drc_exclusions": [],
      "rules": {},
      "track_widths": [],
      "via_dimensions": []
    }
  },
  "boards": [],
  "libraries": {
    "pinned_footprint_libs": [],
    "pinned_symbol_libs": []
  },
  "meta": {
    "filename": "satellite.kicad_pro",
    "version": 1
  },
  "net_settings": {
    "classes": [],
    "meta": {
      "version": 0
    }
  },
  "pcbnew": {
    "page_layout_descr_file": ""
  },
  "sheets": [],
  "text_variables": {}
}'''

with open('pcb/satellite/satellite.kicad_pro', 'w', encoding='utf-8') as f:
    f.write(pro_content)

print("satellite.kicad_pro written")
