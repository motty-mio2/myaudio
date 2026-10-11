import uuid
import re
import math
import subprocess

def u():
    return str(uuid.uuid4())

def sym_to_sch(sym_x, sym_y, pin_x, pin_y, rot=0):
    rad = math.radians(rot)
    rx = pin_x * math.cos(rad) - pin_y * math.sin(rad)
    ry = pin_x * math.sin(rad) + pin_y * math.cos(rad)
    return round(sym_x + rx, 2), round(sym_y - ry, 2)

def get_sym_def(lib_path, sym_name, new_name=None):
    with open(lib_path, 'r', encoding='utf-8') as f:
        c = f.read()
    tag = f'(symbol "{sym_name}"'
    idx = c.find(tag)
    if idx == -1:
        raise ValueError(f"Symbol {sym_name} not found in {lib_path}")
    depth = 0
    for i in range(idx, len(c)):
        if c[i] == '(':
            depth += 1
        elif c[i] == ')':
            depth -= 1
            if depth == 0:
                sym_body = c[idx:i+1]
                break
    if new_name:
        sym_body = re.sub(r'\(symbol "' + re.escape(sym_name) + r'"', f'(symbol "{new_name}"', sym_body, count=1)
        sub_prefix = new_name.split(':')[-1]
        sym_body = re.sub(r'\(symbol "' + re.escape(sym_name) + r'_', f'(symbol "{sub_prefix}_', sym_body)
    return sym_body

def parse_pins(sym_body):
    pins = {}
    for m in re.finditer(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(name\s+\"([^\"]*)\".*?\(number\s+\"([^\"]+)\"', sym_body, re.DOTALL):
        x, y, rot, name, num = m.groups()
        pins[num] = {'x': float(x), 'y': float(y), 'rot': float(rot), 'name': name}
    return pins

rj45_def = get_sym_def('/usr/share/kicad/symbols/Connector.kicad_sym', '8P8C', 'Connector:8P8C')
enc_def = get_sym_def('/usr/share/kicad/symbols/Device.kicad_sym', 'RotaryEncoder_Switch', 'Device:RotaryEncoder_Switch')
sw_def = get_sym_def('/usr/share/kicad/symbols/Switch.kicad_sym', 'SW_Push', 'Switch:SW_Push')
led_def = get_sym_def('/usr/share/kicad/symbols/Device.kicad_sym', 'LED', 'Device:LED')
r_def = get_sym_def('/usr/share/kicad/symbols/Device.kicad_sym', 'R', 'Device:R')
gnd_def = get_sym_def('/usr/share/kicad/symbols/power.kicad_sym', 'GND', 'power:GND')
pwr_flag_def = get_sym_def('/usr/share/kicad/symbols/power.kicad_sym', 'PWR_FLAG', 'power:PWR_FLAG')

rj45_pins = parse_pins(rj45_def)
enc_pins = parse_pins(enc_def)
sw_pins = parse_pins(sw_def)
led_pins = parse_pins(led_def)
r_pins = parse_pins(r_def)
gnd_pins = parse_pins(gnd_def)
pwr_flag_pins = parse_pins(pwr_flag_def)

sch_uuid = u()

sch_text = f"""(kicad_sch
\t(version 20260306)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid {sch_uuid})
\t(paper "A4")
\t(title_block
\t\t(title "Satellite Control Unit")
\t\t(company "Desk Audio Controller")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{rj45_def}
{enc_def}
{sw_def}
{led_def}
{r_def}
{gnd_def}
{pwr_flag_def}
\t)
"""

def add_wire(x1, y1, x2, y2):
    return f"""\t(wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f}))
\t\t(stroke (width 0) (type solid))
\t\t(uuid {u()})
\t)\n"""

def add_label(name, x, y, rot=0):
    return f"""\t(label "{name}" (at {x:.2f} {y:.2f} {rot}) (fields_autoplaced)
\t\t(effects (font (size 1.27 1.27)) (justify {"right bottom" if rot==180 else "left bottom"}))
\t\t(uuid {u()})
\t)\n"""

def add_gnd(x, y):
    g_u = u()
    return f"""\t(symbol (lib_id "power:GND") (at {x:.2f} {y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {g_u})
\t\t(property "Reference" f"#PWR{g_u[:4]}" (at {x:.2f} {y+3.81:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Value" "GND" (at {x:.2f} {y+2.54:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Footprint" "" (at {x:.2f} {y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Datasheet" "" (at {x:.2f} {y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(pin "1" (uuid {u()}))
\t\t(instances
\t\t\t(project "satellite"
\t\t\t\t(path "/{sch_uuid}"
\t\t\t\t\t(reference "#PWR{g_u[:4]}") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)\n"""

# J1: RJ45 at (50.8, 88.9, 0)
j1_x, j1_y = 50.8, 88.9
j1_uuid = u()
sch_text += f"""
\t(symbol (lib_id "Connector:8P8C") (at {j1_x:.2f} {j1_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {j1_uuid})
\t\t(property "Reference" "J1" (at {j1_x:.2f} {j1_y-15.24:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "RJ45_8P8C" (at {j1_x:.2f} {j1_y-12.7:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "Connector_RJ:RJ45_Amphenol_RJHSE5380" (at {j1_x:.2f} {j1_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Datasheet" "~" (at {j1_x:.2f} {j1_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
"""
for pin_num in ["1", "2", "3", "4", "5", "6", "7", "8"]:
    sch_text += f'\t\t(pin "{pin_num}" (uuid {u()}))\n'
sch_text += f"""\t\t(instances
\t\t\t(project "satellite"
\t\t\t\t(path "/{sch_uuid}"
\t\t\t\t\t(reference "J1") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)\n"""

j1_pin_nets = {
    "1": ("GND", None),
    "2": ("NC", None),
    "3": ("ENC_A", "ENC_A"),
    "4": ("ENC_B", "ENC_B"),
    "5": ("ENC_SW", "ENC_SW"),
    "6": ("TOGGLE_SW", "TOGGLE_SW"),
    "7": ("LED_SPK", "LED_SPK"),
    "8": ("LED_HP", "LED_HP"),
}

for pin_num, (net_name, label_name) in j1_pin_nets.items():
    p = rj45_pins[pin_num]
    px, py = sym_to_sch(j1_x, j1_y, p['x'], p['y'], 0)
    tx = px + 5.08
    if label_name:
        sch_text += add_wire(px, py, tx, py)
        sch_text += add_label(label_name, tx, py, 0)
    elif net_name == "GND":
        sch_text += add_wire(px, py, tx, py)
        sch_text += add_gnd(tx, py)
    else:
        sch_text += f'\t(no_connect (at {px:.2f} {py:.2f}) (uuid {u()}))\n'

# PWR_FLAG on GND at J1 Pin 1 wire
p1 = rj45_pins["1"]
p1x, p1y = sym_to_sch(j1_x, j1_y, p1['x'], p1['y'], 0)
pwr_flag_u = u()
sch_text += f"""
\t(symbol (lib_id "power:PWR_FLAG") (at {p1x+5.08:.2f} {p1y+5.08:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {pwr_flag_u})
\t\t(property "Reference" f"#FLG{pwr_flag_u[:4]}" (at {p1x+5.08:.2f} {p1y+7.62:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Value" "PWR_FLAG" (at {p1x+5.08:.2f} {p1y+7.62:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Footprint" "" (at {p1x+5.08:.2f} {p1y+5.08:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Datasheet" "" (at {p1x+5.08:.2f} {p1y+5.08:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(pin "1" (uuid {u()}))
\t\t(instances
\t\t\t(project "satellite"
\t\t\t\t(path "/{sch_uuid}"
\t\t\t\t\t(reference "#FLG{pwr_flag_u[:4]}") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)\n"""
sch_text += add_wire(p1x+5.08, p1y+5.08, p1x+5.08, p1y)

# ENC1: RotaryEncoder_Switch at (127.0, 63.5, 0)
enc_x, enc_y = 127.0, 63.5
enc_uuid = u()
sch_text += f"""
\t(symbol (lib_id "Device:RotaryEncoder_Switch") (at {enc_x:.2f} {enc_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {enc_uuid})
\t\t(property "Reference" "ENC1" (at {enc_x:.2f} {enc_y-10.16:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "EC11E_Switch" (at {enc_x:.2f} {enc_y-7.62:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm" (at {enc_x:.2f} {enc_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Datasheet" "~" (at {enc_x:.2f} {enc_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
"""
for pin_num in ["A", "B", "C", "S1", "S2"]:
    sch_text += f'\t\t(pin "{pin_num}" (uuid {u()}))\n'
sch_text += f"""\t\t(instances
\t\t\t(project "satellite"
\t\t\t\t(path "/{sch_uuid}"
\t\t\t\t\t(reference "ENC1") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)\n"""

# A -> ENC_A
pa = enc_pins['A']
pax, pay = sym_to_sch(enc_x, enc_y, pa['x'], pa['y'], 0)
sch_text += add_wire(pax, pay, pax - 5.08, pay)
sch_text += add_label("ENC_A", pax - 5.08, pay, 180)

# B -> ENC_B
pb = enc_pins['B']
pbx, pby = sym_to_sch(enc_x, enc_y, pb['x'], pb['y'], 0)
sch_text += add_wire(pbx, pby, pbx - 5.08, pby)
sch_text += add_label("ENC_B", pbx - 5.08, pby, 180)

# C -> GND
pc = enc_pins['C']
pcx, pcy = sym_to_sch(enc_x, enc_y, pc['x'], pc['y'], 0)
sch_text += add_wire(pcx, pcy, pcx - 5.08, pcy)
sch_text += add_gnd(pcx - 5.08, pcy)

# S1 -> ENC_SW
ps1 = enc_pins['S1']
ps1x, ps1y = sym_to_sch(enc_x, enc_y, ps1['x'], ps1['y'], 0)
sch_text += add_wire(ps1x, ps1y, ps1x + 5.08, ps1y)
sch_text += add_label("ENC_SW", ps1x + 5.08, ps1y, 0)

# S2 -> GND
ps2 = enc_pins['S2']
ps2x, ps2y = sym_to_sch(enc_x, enc_y, ps2['x'], ps2['y'], 0)
sch_text += add_wire(ps2x, ps2y, ps2x + 5.08, ps2y)
sch_text += add_gnd(ps2x + 5.08, ps2y)

# SW1: SW_Push at (127.0, 96.52, 0)
sw_x, sw_y = 127.0, 96.52
sw_uuid = u()
sch_text += f"""
\t(symbol (lib_id "Switch:SW_Push") (at {sw_x:.2f} {sw_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {sw_uuid})
\t\t(property "Reference" "SW1" (at {sw_x:.2f} {sw_y-7.62:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "SW_Push" (at {sw_x:.2f} {sw_y-5.08:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "Button_Switch_THT:SW_PUSH_6mm" (at {sw_x:.2f} {sw_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Datasheet" "~" (at {sw_x:.2f} {sw_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances
\t\t\t(project "satellite"
\t\t\t\t(path "/{sch_uuid}"
\t\t\t\t\t(reference "SW1") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)\n"""

p1 = sw_pins['1']
p1x, p1y = sym_to_sch(sw_x, sw_y, p1['x'], p1['y'], 0)
sch_text += add_wire(p1x, p1y, p1x - 5.08, p1y)
sch_text += add_label("TOGGLE_SW", p1x - 5.08, p1y, 180)

p2 = sw_pins['2']
p2x, p2y = sym_to_sch(sw_x, sw_y, p2['x'], p2['y'], 0)
sch_text += add_wire(p2x, p2y, p2x + 5.08, p2y)
sch_text += add_gnd(p2x + 5.08, p2y)

# LED1: Green LED at (177.8, 63.5, 270)
led1_x, led1_y, led1_rot = 177.8, 63.5, 90
led1_uuid = u()
sch_text += f"""
\t(symbol (lib_id "Device:LED") (at {led1_x:.2f} {led1_y:.2f} {led1_rot}) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {led1_uuid})
\t\t(property "Reference" "LED1" (at {led1_x+6.35:.2f} {led1_y-1.27:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "LED_Green" (at {led1_x+6.35:.2f} {led1_y+1.27:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "LED_THT:LED_D3.0mm" (at {led1_x:.2f} {led1_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Datasheet" "~" (at {led1_x:.2f} {led1_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances
\t\t\t(project "satellite"
\t\t\t\t(path "/{sch_uuid}"
\t\t\t\t\t(reference "LED1") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)\n"""

l1_a = led_pins['2']
l1_ax, l1_ay = sym_to_sch(led1_x, led1_y, l1_a['x'], l1_a['y'], led1_rot)
sch_text += add_wire(l1_ax, l1_ay, l1_ax, l1_ay - 5.08)
sch_text += add_label("LED_SPK", l1_ax, l1_ay - 5.08, 90)

l1_k = led_pins['1']
l1_kx, l1_ky = sym_to_sch(led1_x, led1_y, l1_k['x'], l1_k['y'], led1_rot)

# R1 at (177.8, 76.2, 0)
r1_x, r1_y, r1_rot = 177.8, 76.2, 0
r1_uuid = u()
sch_text += f"""
\t(symbol (lib_id "Device:R") (at {r1_x:.2f} {r1_y:.2f} {r1_rot}) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {r1_uuid})
\t\t(property "Reference" "R1" (at {r1_x+6.35:.2f} {r1_y-1.27:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "680" (at {r1_x+6.35:.2f} {r1_y+1.27:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" (at {r1_x:.2f} {r1_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Datasheet" "~" (at {r1_x:.2f} {r1_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances
\t\t\t(project "satellite"
\t\t\t\t(path "/{sch_uuid}"
\t\t\t\t\t(reference "R1") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)\n"""

r1_p1 = r_pins['1']
r1_p1x, r1_p1y = sym_to_sch(r1_x, r1_y, r1_p1['x'], r1_p1['y'], r1_rot)
sch_text += add_wire(l1_kx, l1_ky, r1_p1x, r1_p1y)

r1_p2 = r_pins['2']
r1_p2x, r1_p2y = sym_to_sch(r1_x, r1_y, r1_p2['x'], r1_p2['y'], r1_rot)
sch_text += add_wire(r1_p2x, r1_p2y, r1_p2x, r1_p2y + 5.08)
sch_text += add_gnd(r1_p2x, r1_p2y + 5.08)

# LED2: Blue LED at (177.8, 101.6, 270)
led2_x, led2_y, led2_rot = 177.8, 101.6, 90
led2_uuid = u()
sch_text += f"""
\t(symbol (lib_id "Device:LED") (at {led2_x:.2f} {led2_y:.2f} {led2_rot}) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {led2_uuid})
\t\t(property "Reference" "LED2" (at {led2_x+6.35:.2f} {led2_y-1.27:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "LED_Blue" (at {led2_x+6.35:.2f} {led2_y+1.27:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "LED_THT:LED_D3.0mm" (at {led2_x:.2f} {led2_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Datasheet" "~" (at {led2_x:.2f} {led2_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances
\t\t\t(project "satellite"
\t\t\t\t(path "/{sch_uuid}"
\t\t\t\t\t(reference "LED2") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)\n"""

l2_a = led_pins['2']
l2_ax, l2_ay = sym_to_sch(led2_x, led2_y, l2_a['x'], l2_a['y'], led2_rot)
sch_text += add_wire(l2_ax, l2_ay, l2_ax, l2_ay - 5.08)
sch_text += add_label("LED_HP", l2_ax, l2_ay - 5.08, 90)

l2_k = led_pins['1']
l2_kx, l2_ky = sym_to_sch(led2_x, led2_y, l2_k['x'], l2_k['y'], led2_rot)

# R2 at (177.8, 114.3, 0)
r2_x, r2_y, r2_rot = 177.8, 114.3, 0
r2_uuid = u()
sch_text += f"""
\t(symbol (lib_id "Device:R") (at {r2_x:.2f} {r2_y:.2f} {r2_rot}) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {r2_uuid})
\t\t(property "Reference" "R2" (at {r2_x+6.35:.2f} {r2_y-1.27:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "680" (at {r2_x+6.35:.2f} {r2_y+1.27:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" (at {r2_x:.2f} {r2_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(property "Datasheet" "~" (at {r2_x:.2f} {r2_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)) hide)
\t\t)
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances
\t\t\t(project "satellite"
\t\t\t\t(path "/{sch_uuid}"
\t\t\t\t\t(reference "R2") (unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)\n"""

r2_p1 = r_pins['1']
r2_p1x, r2_p1y = sym_to_sch(r2_x, r2_y, r2_p1['x'], r2_p1['y'], r2_rot)
sch_text += add_wire(l2_kx, l2_ky, r2_p1x, r2_p1y)

r2_p2 = r_pins['2']
r2_p2x, r2_p2y = sym_to_sch(r2_x, r2_y, r2_p2['x'], r2_p2['y'], r2_rot)
sch_text += add_wire(r2_p2x, r2_p2y, r2_p2x, r2_p2y + 5.08)
sch_text += add_gnd(r2_p2x, r2_p2y + 5.08)

# End of schematic
sch_text += f"""\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
"""

with open('pcb/satellite/satellite.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(sch_text)

print("Generated satellite.kicad_sch. Running ERC...")
res = subprocess.run(['kicad-cli', 'sch', 'erc', 'pcb/satellite/satellite.kicad_sch'], capture_output=True, text=True)
print("ERC result:", res.returncode)
print(res.stdout)
print(res.stderr)
