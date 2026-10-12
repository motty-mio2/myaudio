import uuid
import re
import math
import subprocess

def u():
    return str(uuid.uuid4())

GRID = 1.27
def snap(val):
    return round(round(val / GRID) * GRID, 2)

def sym_to_sch(sym_x, sym_y, pin_x, pin_y, rot=0):
    rad = math.radians(rot)
    rx = pin_x * math.cos(rad) - pin_y * math.sin(rad)
    ry = pin_x * math.sin(rad) + pin_y * math.cos(rad)
    return snap(sym_x + rx), snap(sym_y - ry)

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

# Standard symbols extraction
rj45_def = get_sym_def('/usr/share/kicad/symbols/Connector.kicad_sym', '8P8C', 'Connector:8P8C')
pt2258_def = get_sym_def('/usr/share/kicad/symbols/Audio.kicad_sym', 'PT2258', 'Audio:PT2258')
relay_def = get_sym_def('/usr/share/kicad/symbols/Relay.kicad_sym', 'G6K-2', 'Relay:G6K-2')
fet_def = get_sym_def('/usr/share/kicad/symbols/Transistor_FET.kicad_sym', '2N7000', 'Transistor_FET:2N7000')
diode_def = get_sym_def('/usr/share/kicad/symbols/Device.kicad_sym', 'D', 'Device:D')
audio_jack_def = get_sym_def('/usr/share/kicad/symbols/Connector_Audio.kicad_sym', 'AudioJack3', 'Connector_Audio:AudioJack3')
r_def = get_sym_def('/usr/share/kicad/symbols/Device.kicad_sym', 'R', 'Device:R')
c_def = get_sym_def('/usr/share/kicad/symbols/Device.kicad_sym', 'C', 'Device:C')
cp_def = get_sym_def('/usr/share/kicad/symbols/Device.kicad_sym', 'C_Polarized', 'Device:C_Polarized')
l_def = get_sym_def('/usr/share/kicad/symbols/Device.kicad_sym', 'L', 'Device:L')
nettie_def = get_sym_def('/usr/share/kicad/symbols/Device.kicad_sym', 'NetTie_2', 'Device:NetTie_2')
gnd_def = get_sym_def('/usr/share/kicad/symbols/power.kicad_sym', 'GND', 'power:GND')
gnda_def = get_sym_def('/usr/share/kicad/symbols/power.kicad_sym', 'GNDA', 'power:GNDA')
gndd_def = get_sym_def('/usr/share/kicad/symbols/power.kicad_sym', 'GNDD', 'power:GNDD')
p5v_def = get_sym_def('/usr/share/kicad/symbols/power.kicad_sym', '+5V', 'power:+5V')
p3v3_def = get_sym_def('/usr/share/kicad/symbols/power.kicad_sym', '+3V3', 'power:+3V3')
pwr_flag_def = get_sym_def('/usr/share/kicad/symbols/power.kicad_sym', 'PWR_FLAG', 'power:PWR_FLAG')

# myaudio:XIAO_ESP32C6 from local lib
with open('pcb/main_board/myaudio.kicad_sym', 'r', encoding='utf-8') as f:
    xiao_lib_text = f.read()
xiao_sym_def = get_sym_def('pcb/main_board/myaudio.kicad_sym', 'XIAO_ESP32C6', 'myaudio:XIAO_ESP32C6')

xiao_pins = parse_pins(xiao_sym_def)
pt2258_pins = parse_pins(pt2258_def)
relay_pins = parse_pins(relay_def)
fet_pins = parse_pins(fet_def)
diode_pins = parse_pins(diode_def)
jack_pins = parse_pins(audio_jack_def)
rj45_pins = parse_pins(rj45_def)
r_pins = parse_pins(r_def)
c_pins = parse_pins(c_def)
cp_pins = parse_pins(cp_def)
l_pins = parse_pins(l_def)
nettie_pins = parse_pins(nettie_def)

sch_uuid = u()

sch_text = f"""(kicad_sch
\t(version 20260306)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid {sch_uuid})
\t(paper "A3")
\t(title_block
\t\t(title "Desk Audio Router & Controller - Main Board")
\t\t(company "Desk Audio Controller")
\t\t(rev "1.0")
\t)
\t(lib_symbols
{rj45_def}
{pt2258_def}
{relay_def}
{fet_def}
{diode_def}
{audio_jack_def}
{r_def}
{c_def}
{cp_def}
{l_def}
{nettie_def}
{xiao_sym_def}
{gnd_def}
{gnda_def}
{gndd_def}
{p5v_def}
{p3v3_def}
{pwr_flag_def}
\t)
"""

def add_wire(x1, y1, x2, y2):
    return f"""\t(wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f}))
\t\t(stroke (width 0) (type solid))
\t\t(uuid {u()})
\t)\n"""

def add_junction(x, y):
    return f"""\t(junction (at {x:.2f} {y:.2f}) (diameter 0) (color 0 0 0 0) (uuid {u()}))\n"""

def add_label(name, x, y, rot=0):
    return f"""\t(label "{name}" (at {x:.2f} {y:.2f} {rot}) (fields_autoplaced)
\t\t(effects (font (size 1.27 1.27)) (justify {'right' if rot==180 else ('left' if rot==0 else 'bottom')}))
\t\t(uuid {u()})
\t)\n"""

def add_gnd(x, y, net_label="DGND"):
    g_u = u()
    if net_label == "AGND":
        lib_id = "power:GNDA"
        val_y = y + 3.81
    else:
        lib_id = "power:GNDD"
        val_y = y + 3.18
    return f"""\t(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {g_u})
\t\t(property "Reference" "#PWR?" (at {x:.2f} {y+5.08:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Value" "{net_label}" (at {x:.2f} {val_y:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "#PWR{g_u[:4]}") (unit 1))))
\t)\n"""

def add_pwr(lib_id, val, x, y):
    p_u = u()
    return f"""\t(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {p_u})
\t\t(property "Reference" "#PWR?" (at {x:.2f} {y-3.81:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Value" "{val}" (at {x:.2f} {y-2.54:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "#PWR{p_u[:4]}") (unit 1))))
\t)\n"""

def add_pwr_flag(x, y):
    pf_u = u()
    return f"""\t(symbol (lib_id "power:PWR_FLAG") (at {x:.2f} {y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {pf_u})
\t\t(property "Reference" "#FLG?" (at {x:.2f} {y-3.81:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Value" "PWR_FLAG" (at {x:.2f} {y-2.54:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "#FLG{pf_u[:4]}") (unit 1))))
\t)\n"""

# =========================================================================
# 1. U1: XIAO ESP32-C6 (at 76.20, 76.20)
# =========================================================================
u1_x, u1_y = 76.20, 76.20
u1_uuid = u()
sch_text += f"""\t(symbol (lib_id "myaudio:XIAO_ESP32C6") (at {u1_x:.2f} {u1_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {u1_uuid})
\t\t(property "Reference" "U1" (at {u1_x:.2f} {u1_y-12.7:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "XIAO_ESP32C6" (at {u1_x:.2f} {u1_y-10.16:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "main_board_footprints:XIAO_ESP32C6_Socket" (at {u1_x:.2f} {u1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/" (at {u1_x:.2f} {u1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
"""
for p in range(1, 15):
    sch_text += f'\t\t(pin "{p}" (uuid {u()}))\n'
sch_text += f"""\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "U1") (unit 1))))
\t)\n"""

# U1 Left Pins (1 to 7)
u1_left_nets = [
    ('1', 'RELAY_CTRL'),
    ('2', 'ENC_A'),
    ('3', 'ENC_B'),
    ('4', 'ENC_SW'),
    ('5', 'I2C_SDA'),
    ('6', 'I2C_SCL'),
]
for p_num, net in u1_left_nets:
    p = xiao_pins[p_num]
    px, py = sym_to_sch(u1_x, u1_y, p['x'], p['y'], 0)
    sch_text += add_wire(px, py, px - 5.08, py)
    sch_text += add_label(net, px - 5.08, py, 180)

# Pin 7: NC
p7 = xiao_pins['7']
p7x, p7y = sym_to_sch(u1_x, u1_y, p7['x'], p7['y'], 0)
sch_text += f'\t(no_connect (at {p7x:.2f} {p7y:.2f}) (uuid {u()}))\n'

# Pin 8: NC
p8 = xiao_pins['8']
p8x, p8y = sym_to_sch(u1_x, u1_y, p8['x'], p8['y'], 0)
sch_text += f'\t(no_connect (at {p8x:.2f} {p8y:.2f}) (uuid {u()}))\n'

# U1 Right Pins (9 to 14)
u1_right_nets = [
    ('9', 'TOGGLE_SW'),
    ('10', 'LED_SPK'),
    ('11', 'LED_HP'),
]
for p_num, net in u1_right_nets:
    p = xiao_pins[p_num]
    px, py = sym_to_sch(u1_x, u1_y, p['x'], p['y'], 0)
    sch_text += add_wire(px, py, px + 5.08, py)
    sch_text += add_label(net, px + 5.08, py, 0)

# Pin 12 (+3.3V)
p12 = xiao_pins['12']
p12x, p12y = sym_to_sch(u1_x, u1_y, p12['x'], p12['y'], 0)
sch_text += add_wire(p12x, p12y, p12x + 5.08, p12y)
sch_text += add_pwr("power:+3V3", "+3V3", p12x + 5.08, p12y)

# Pin 13 (GND) -> DGND
p13 = xiao_pins['13']
p13x, p13y = sym_to_sch(u1_x, u1_y, p13['x'], p13['y'], 0)
sch_text += add_wire(p13x, p13y, p13x + 5.08, p13y)
sch_text += add_gnd(p13x + 5.08, p13y, "DGND")
sch_text += add_pwr_flag(p13x + 5.08, p13y) # DGND power flag

# Pin 14 (+5V)
p14 = xiao_pins['14']
p14x, p14y = sym_to_sch(u1_x, u1_y, p14['x'], p14['y'], 0)
sch_text += add_wire(p14x, p14y, p14x + 5.08, p14y)
sch_text += add_pwr("power:+5V", "+5V", p14x + 5.08, p14y)

# =========================================================================
# 2. Power Section: LC Filter & Decoupling (at 127.0, 50.8)
# =========================================================================
# L1: 10uH from +5V to +5V_FILT (at 127.0, 50.8, rot=90)
l1_x, l1_y, l1_rot = 127.0, 50.8, 90
l1_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:L") (at {l1_x:.2f} {l1_y:.2f} {l1_rot}) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {l1_uuid})
\t\t(property "Reference" "L1" (at {l1_x:.2f} {l1_y-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "10uH" (at {l1_x:.2f} {l1_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Inductor_THT:L_Axial_L7.0mm_D3.3mm_P10.16mm_Horizontal_Fastron_MICC" (at {l1_x:.2f} {l1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {l1_x:.2f} {l1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "L1") (unit 1))))
\t)\n"""
l1_p1 = sym_to_sch(l1_x, l1_y, l_pins['1']['x'], l_pins['1']['y'], l1_rot)
l1_p2 = sym_to_sch(l1_x, l1_y, l_pins['2']['x'], l_pins['2']['y'], l1_rot)
sch_text += add_wire(l1_p1[0], l1_p1[1], l1_p1[0] - 5.08, l1_p1[1])
sch_text += add_pwr("power:+5V", "+5V", l1_p1[0] - 5.08, l1_p1[1])
sch_text += add_wire(l1_p2[0], l1_p2[1], l1_p2[0] + 5.08, l1_p2[1])
sch_text += add_label("+5V_FILT", l1_p2[0] + 5.08, l1_p2[1], 0)
sch_text += add_pwr_flag(l1_p2[0] + 5.08, l1_p2[1])

# C6: 100uF Electrolytic from +5V_FILT to DGND (at 147.32, 63.50, rot=0)
c6_x, c6_y = 147.32, 63.50
c6_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:C_Polarized") (at {c6_x:.2f} {c6_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {c6_uuid})
\t\t(property "Reference" "C6" (at {c6_x+3.81:.2f} {c6_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "100uF" (at {c6_x+3.81:.2f} {c6_y+1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm" (at {c6_x:.2f} {c6_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {c6_x:.2f} {c6_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "C6") (unit 1))))
\t)\n"""
c6_p1 = sym_to_sch(c6_x, c6_y, cp_pins['1']['x'], cp_pins['1']['y'], 0) # Pin 1: (x, y - 3.81)
c6_p2 = sym_to_sch(c6_x, c6_y, cp_pins['2']['x'], cp_pins['2']['y'], 0) # Pin 2: (x, y + 3.81)
sch_text += add_wire(c6_p1[0], c6_p1[1], c6_p1[0], c6_p1[1] - 2.54)
sch_text += add_label("+5V_FILT", c6_p1[0], c6_p1[1] - 2.54, 90)
sch_text += add_wire(c6_p2[0], c6_p2[1], c6_p2[0], c6_p2[1] + 2.54)
sch_text += add_gnd(c6_p2[0], c6_p2[1] + 2.54, "DGND")

# C7: 0.1uF Ceramic from +5V_FILT to DGND (at 160.02, 63.50, rot=0)
c7_x, c7_y = 160.02, 63.50
c7_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:C") (at {c7_x:.2f} {c7_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {c7_uuid})
\t\t(property "Reference" "C7" (at {c7_x+3.81:.2f} {c7_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "0.1uF" (at {c7_x+3.81:.2f} {c7_y+1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" (at {c7_x:.2f} {c7_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {c7_x:.2f} {c7_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "C7") (unit 1))))
\t)\n"""
c7_p1 = sym_to_sch(c7_x, c7_y, c_pins['1']['x'], c_pins['1']['y'], 0)
c7_p2 = sym_to_sch(c7_x, c7_y, c_pins['2']['x'], c_pins['2']['y'], 0)
sch_text += add_wire(c7_p1[0], c7_p1[1], c7_p1[0], c7_p1[1] - 2.54)
sch_text += add_label("+5V_FILT", c7_p1[0], c7_p1[1] - 2.54, 90)
sch_text += add_wire(c7_p2[0], c7_p2[1], c7_p2[0], c7_p2[1] + 2.54)
sch_text += add_gnd(c7_p2[0], c7_p2[1] + 2.54, "DGND")

# C5: 0.1uF Ceramic Decoupling for +3V3 (at 172.72, 63.50, rot=0)
c5_x, c5_y = 172.72, 63.50
c5_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:C") (at {c5_x:.2f} {c5_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {c5_uuid})
\t\t(property "Reference" "C5" (at {c5_x+3.81:.2f} {c5_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "0.1uF" (at {c5_x+3.81:.2f} {c5_y+1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm" (at {c5_x:.2f} {c5_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {c5_x:.2f} {c5_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "C5") (unit 1))))
\t)\n"""
c5_p1 = sym_to_sch(c5_x, c5_y, c_pins['1']['x'], c_pins['1']['y'], 0)
c5_p2 = sym_to_sch(c5_x, c5_y, c_pins['2']['x'], c_pins['2']['y'], 0)
sch_text += add_wire(c5_p1[0], c5_p1[1], c5_p1[0], c5_p1[1] - 2.54)
sch_text += add_pwr("power:+3V3", "+3V3", c5_p1[0], c5_p1[1] - 2.54)
sch_text += add_wire(c5_p2[0], c5_p2[1], c5_p2[0], c5_p2[1] + 2.54)
sch_text += add_gnd(c5_p2[0], c5_p2[1] + 2.54, "DGND")

# =========================================================================
# 3. I2C Pull-up Resistors (at 127.0, 101.6)
# =========================================================================
# R1: 4.7k for SDA (at 127.0, 101.6, rot=0)
r1_x, r1_y = 127.0, 101.6
r1_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:R") (at {r1_x:.2f} {r1_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {r1_uuid})
\t\t(property "Reference" "R1" (at {r1_x+3.81:.2f} {r1_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "4.7k" (at {r1_x+3.81:.2f} {r1_y+1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" (at {r1_x:.2f} {r1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {r1_x:.2f} {r1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "R1") (unit 1))))
\t)\n"""
r1_p1 = sym_to_sch(r1_x, r1_y, r_pins['1']['x'], r_pins['1']['y'], 0)
r1_p2 = sym_to_sch(r1_x, r1_y, r_pins['2']['x'], r_pins['2']['y'], 0)
sch_text += add_wire(r1_p1[0], r1_p1[1], r1_p1[0], r1_p1[1] - 2.54)
sch_text += add_pwr("power:+3V3", "+3V3", r1_p1[0], r1_p1[1] - 2.54)
sch_text += add_wire(r1_p2[0], r1_p2[1], r1_p2[0], r1_p2[1] + 2.54)
sch_text += add_label("I2C_SDA", r1_p2[0], r1_p2[1] + 2.54, 270)

# R2: 4.7k for SCL (at 139.7, 101.6, rot=0)
r2_x, r2_y = 139.7, 101.6
r2_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:R") (at {r2_x:.2f} {r2_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {r2_uuid})
\t\t(property "Reference" "R2" (at {r2_x+3.81:.2f} {r2_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "4.7k" (at {r2_x+3.81:.2f} {r2_y+1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" (at {r2_x:.2f} {r2_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {r2_x:.2f} {r2_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "R2") (unit 1))))
\t)\n"""
r2_p1 = sym_to_sch(r2_x, r2_y, r_pins['1']['x'], r_pins['1']['y'], 0)
r2_p2 = sym_to_sch(r2_x, r2_y, r_pins['2']['x'], r_pins['2']['y'], 0)
sch_text += add_wire(r2_p1[0], r2_p1[1], r2_p1[0], r2_p1[1] - 2.54)
sch_text += add_pwr("power:+3V3", "+3V3", r2_p1[0], r2_p1[1] - 2.54)
sch_text += add_wire(r2_p2[0], r2_p2[1], r2_p2[0], r2_p2[1] + 2.54)
sch_text += add_label("I2C_SCL", r2_p2[0], r2_p2[1] + 2.54, 270)

# =========================================================================
# 4. U2: PT2258 6ch Electronic Volume Controller (at 203.20, 101.60)
# =========================================================================
u2_x, u2_y = 203.20, 101.60
u2_uuid = u()
sch_text += f"""\t(symbol (lib_id "Audio:PT2258") (at {u2_x:.2f} {u2_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {u2_uuid})
\t\t(property "Reference" "U2" (at {u2_x:.2f} {u2_y-20.32:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "PT2258" (at {u2_x:.2f} {u2_y-17.78:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Package_DIP:DIP-20_W7.62mm" (at {u2_x:.2f} {u2_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "http://www.princeton.com.tw/Portals/0/Product/PT2258.pdf" (at {u2_x:.2f} {u2_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
"""
for p in range(1, 21):
    sch_text += f'\t\t(pin "{p}" (uuid {u()}))\n'
sch_text += f"""\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "U2") (unit 1))))
\t)\n"""

# PT2258 Pin Connections:
# Pin 16: VCC (+5V_FILT)
p16 = pt2258_pins['16']
p16x, p16y = sym_to_sch(u2_x, u2_y, p16['x'], p16['y'], 0)
sch_text += add_wire(p16x, p16y, p16x, p16y - 5.08)
sch_text += add_label("+5V_FILT", p16x, p16y - 5.08, 90)

# Pin 14 (GND) & Pin 5 (DGND): Both tied together to AGND at bottom
p14_u2 = pt2258_pins['14']
p14x_u2, p14y_u2 = sym_to_sch(u2_x, u2_y, p14_u2['x'], p14_u2['y'], 0)
p5 = pt2258_pins['5']
p5x, p5y = sym_to_sch(u2_x, u2_y, p5['x'], p5['y'], 0)
sch_text += add_wire(p14x_u2, p14y_u2, p14x_u2, p14y_u2 + 3.81)
sch_text += add_wire(p5x, p5y, p5x, p5y + 3.81)
sch_text += add_wire(p14x_u2, p14y_u2 + 3.81, p5x, p5y + 3.81)
mid_bottom_x = (p14x_u2 + p5x) / 2.0
sch_text += add_junction(mid_bottom_x, p14y_u2 + 3.81)
sch_text += add_wire(mid_bottom_x, p14y_u2 + 3.81, mid_bottom_x, p14y_u2 + 6.35)
sch_text += add_gnd(mid_bottom_x, p14y_u2 + 6.35, "AGND")

# Unused audio inputs (Pin 3, 8, 9, 10) & Address pins (Pin 17, 4: CODE1, CODE2):
# All tied to AGND on a single clean vertical bus on the left!
bus_agnd_x = p14x_u2 - 10.16 # x = 185.42
agnd_left_pins = ['3', '8', '9', '10', '17', '4']
agnd_pts = []
for unpin in agnd_left_pins:
    p = pt2258_pins[unpin]
    px, py = sym_to_sch(u2_x, u2_y, p['x'], p['y'], 0)
    sch_text += add_wire(px, py, bus_agnd_x, py)
    sch_text += add_junction(bus_agnd_x, py)
    agnd_pts.append(py)
sch_text += add_wire(bus_agnd_x, min(agnd_pts), bus_agnd_x, max(agnd_pts))
mid_left_y = agnd_pts[3] # Pin 10 at y=101.60
sch_text += add_wire(bus_agnd_x, mid_left_y, bus_agnd_x - 3.81, mid_left_y)
sch_text += add_gnd(bus_agnd_x - 3.81, mid_left_y, "AGND")

# Pin 6 (SCL): I2C_SCL
p6_u2 = pt2258_pins['6']
p6x_u2, p6y_u2 = sym_to_sch(u2_x, u2_y, p6_u2['x'], p6_u2['y'], 0)
sch_text += add_wire(p6x_u2, p6y_u2, p6x_u2 - 8.89, p6y_u2)
sch_text += add_label("I2C_SCL", p6x_u2 - 8.89, p6y_u2, 180)

# Pin 7 (SDA): I2C_SDA
p7_u2 = pt2258_pins['7']
p7x_u2, p7y_u2 = sym_to_sch(u2_x, u2_y, p7_u2['x'], p7_u2['y'], 0)
sch_text += add_wire(p7x_u2, p7y_u2, p7x_u2 - 8.89, p7y_u2)
sch_text += add_label("I2C_SDA", p7x_u2 - 8.89, p7y_u2, 180)

# Unused audio outputs: Pin 11 (OUT6), Pin 12 (OUT5), Pin 13 (OUT4), Pin 18 (OUT3)
for unpin in ['11', '12', '13', '18']:
    p = pt2258_pins[unpin]
    px, py = sym_to_sch(u2_x, u2_y, p['x'], p['y'], 0)
    sch_text += f'\t(no_connect (at {px:.2f} {py:.2f}) (uuid {u()}))\n'

# Pin 15 (REF): 10uF cap C8 to AGND (rot=0)
p15 = pt2258_pins['15']
p15x, p15y = sym_to_sch(u2_x, u2_y, p15['x'], p15['y'], 0)
c8_x, c8_y = p15x + 12.7, p15y
c8_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:C_Polarized") (at {c8_x:.2f} {c8_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {c8_uuid})
\t\t(property "Reference" "C8" (at {c8_x+3.81:.2f} {c8_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "10uF" (at {c8_x+3.81:.2f} {c8_y+1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm" (at {c8_x:.2f} {c8_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {c8_x:.2f} {c8_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "C8") (unit 1))))
\t)\n"""
c8_p1 = sym_to_sch(c8_x, c8_y, cp_pins['1']['x'], cp_pins['1']['y'], 0) # Pin 1: (c8_x, c8_y - 3.81)
c8_p2 = sym_to_sch(c8_x, c8_y, cp_pins['2']['x'], cp_pins['2']['y'], 0) # Pin 2: (c8_x, c8_y + 3.81)
sch_text += add_wire(p15x, p15y, c8_p1[0], p15y)
sch_text += add_wire(c8_p1[0], p15y, c8_p1[0], c8_p1[1])
sch_text += add_wire(c8_p2[0], c8_p2[1], c8_p2[0], c8_p2[1] + 2.54)
sch_text += add_gnd(c8_p2[0], c8_p2[1] + 2.54, "AGND")

# Active Inputs:
# Pin 1 (IN1, Left): wire to C1
p1_u2 = pt2258_pins['1']
p1x_u2, p1y_u2 = sym_to_sch(u2_x, u2_y, p1_u2['x'], p1_u2['y'], 0)
sch_text += add_wire(p1x_u2, p1y_u2, p1x_u2 - 5.08, p1y_u2)
sch_text += add_label("VOL_IN_L", p1x_u2 - 5.08, p1y_u2, 180)

# Pin 2 (IN2, Right): wire to C2
p2_u2 = pt2258_pins['2']
p2x_u2, p2y_u2 = sym_to_sch(u2_x, u2_y, p2_u2['x'], p2_u2['y'], 0)
sch_text += add_wire(p2x_u2, p2y_u2, p2x_u2 - 5.08, p2y_u2)
sch_text += add_label("VOL_IN_R", p2x_u2 - 5.08, p2y_u2, 180)

# Active Outputs:
# Pin 20 (OUT1, Left): wire to C3
p20 = pt2258_pins['20']
p20x, p20y = sym_to_sch(u2_x, u2_y, p20['x'], p20['y'], 0)
sch_text += add_wire(p20x, p20y, p20x + 5.08, p20y)
sch_text += add_label("VOL_OUT_L", p20x + 5.08, p20y, 0)

# Pin 19 (OUT2, Right): wire to C4
p19 = pt2258_pins['19']
p19x, p19y = sym_to_sch(u2_x, u2_y, p19['x'], p19['y'], 0)
sch_text += add_wire(p19x, p19y, p19x + 5.08, p19y)
sch_text += add_label("VOL_OUT_R", p19x + 5.08, p19y, 0)

# =========================================================================
# 5. Audio Input AC Coupling: C1, C2 & J1 (Line In) (at 279.4, 50.8)
# =========================================================================
# C1: 4.7uF for Left Channel (at 254.0, 43.18, rot=270)
# In rot=270, Pin 1 (+) is at (x + 3.81, y) [Right], Pin 2 (-) is at (x - 3.81, y) [Left]
# Audio flow: J1 (Line In) -> C1 Pin 1 (+) -> C1 Pin 2 (-) -> VOL_IN_L
# So Pin 1 (+) connects to LINE_IN_L (pull right), Pin 2 (-) connects to VOL_IN_L (pull left)
c1_x, c1_y = 254.0, 43.18
c1_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:C_Polarized") (at {c1_x:.2f} {c1_y:.2f} 270) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {c1_uuid})
\t\t(property "Reference" "C1" (at {c1_x:.2f} {c1_y-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "4.7uF" (at {c1_x:.2f} {c1_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm" (at {c1_x:.2f} {c1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {c1_x:.2f} {c1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "C1") (unit 1))))
\t)\n"""
c1_p1 = sym_to_sch(c1_x, c1_y, cp_pins['1']['x'], cp_pins['1']['y'], 270) # Right
c1_p2 = sym_to_sch(c1_x, c1_y, cp_pins['2']['x'], cp_pins['2']['y'], 270) # Left
sch_text += add_wire(c1_p1[0], c1_p1[1], c1_p1[0] + 5.08, c1_p1[1])
sch_text += add_label("LINE_IN_L", c1_p1[0] + 5.08, c1_p1[1], 0)
sch_text += add_wire(c1_p2[0], c1_p2[1], c1_p2[0] - 5.08, c1_p2[1])
sch_text += add_label("VOL_IN_L", c1_p2[0] - 5.08, c1_p2[1], 180)

# C2: 4.7uF for Right Channel (at 254.0, 55.88, rot=270)
c2_x, c2_y = 254.0, 55.88
c2_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:C_Polarized") (at {c2_x:.2f} {c2_y:.2f} 270) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {c2_uuid})
\t\t(property "Reference" "C2" (at {c2_x:.2f} {c2_y-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "4.7uF" (at {c2_x:.2f} {c2_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm" (at {c2_x:.2f} {c2_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {c2_x:.2f} {c2_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "C2") (unit 1))))
\t)\n"""
c2_p1 = sym_to_sch(c2_x, c2_y, cp_pins['1']['x'], cp_pins['1']['y'], 270) # Right
c2_p2 = sym_to_sch(c2_x, c2_y, cp_pins['2']['x'], cp_pins['2']['y'], 270) # Left
sch_text += add_wire(c2_p1[0], c2_p1[1], c2_p1[0] + 5.08, c2_p1[1])
sch_text += add_label("LINE_IN_R", c2_p1[0] + 5.08, c2_p1[1], 0)
sch_text += add_wire(c2_p2[0], c2_p2[1], c2_p2[0] - 5.08, c2_p2[1])
sch_text += add_label("VOL_IN_R", c2_p2[0] - 5.08, c2_p2[1], 180)

# J1: 3.5mm Line In Jack (at 289.56, 48.26, rot=0)
j1_x, j1_y = 289.56, 48.26
j1_uuid = u()
sch_text += f"""\t(symbol (lib_id "Connector_Audio:AudioJack3") (at {j1_x:.2f} {j1_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {j1_uuid})
\t\t(property "Reference" "J1" (at {j1_x:.2f} {j1_y-8.89:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "Line_In" (at {j1_x:.2f} {j1_y-6.35:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Connector_Audio:Jack_3.5mm_CUI_SJ1-3523N_Horizontal" (at {j1_x:.2f} {j1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {j1_x:.2f} {j1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "R" (uuid {u()}))
\t\t(pin "S" (uuid {u()}))
\t\t(pin "T" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "J1") (unit 1))))
\t)\n"""
j1_t = sym_to_sch(j1_x, j1_y, jack_pins['T']['x'], jack_pins['T']['y'], 0) # Tip: Left
j1_r = sym_to_sch(j1_x, j1_y, jack_pins['R']['x'], jack_pins['R']['y'], 0) # Ring: Right
j1_s = sym_to_sch(j1_x, j1_y, jack_pins['S']['x'], jack_pins['S']['y'], 0) # Sleeve: AGND
sch_text += add_wire(j1_t[0], j1_t[1], j1_t[0] + 5.08, j1_t[1])
sch_text += add_label("LINE_IN_L", j1_t[0] + 5.08, j1_t[1], 0)
sch_text += add_wire(j1_r[0], j1_r[1], j1_r[0] + 5.08, j1_r[1])
sch_text += add_label("LINE_IN_R", j1_r[0] + 5.08, j1_r[1], 0)
sch_text += add_wire(j1_s[0], j1_s[1], j1_s[0] + 2.54, j1_s[1])
sch_text += add_wire(j1_s[0] + 2.54, j1_s[1], j1_s[0] + 2.54, j1_s[1] + 5.08)
sch_text += add_gnd(j1_s[0] + 2.54, j1_s[1] + 5.08, "AGND")

# =========================================================================
# 6. Audio Output AC Coupling: C3, C4 (at 254.0, 91.44)
# =========================================================================
# Output flow: PT2258 OUT -> C3/C4 Pin 1 (+) -> C3/C4 Pin 2 (-) -> Relay COM
# In rot=90, Pin 1 (+) is at (x - 3.81, y) [Left], Pin 2 (-) is at (x + 3.81, y) [Right]
# Let's use rot=90 so Pin 1 (+) is on Left (from PT2258) and Pin 2 (-) is on Right (to Relay COM)!
c3_x, c3_y = 254.0, 83.82
c3_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:C_Polarized") (at {c3_x:.2f} {c3_y:.2f} 90) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {c3_uuid})
\t\t(property "Reference" "C3" (at {c3_x:.2f} {c3_y-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "4.7uF" (at {c3_x:.2f} {c3_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm" (at {c3_x:.2f} {c3_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {c3_x:.2f} {c3_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "C3") (unit 1))))
\t)\n"""
c3_p1 = sym_to_sch(c3_x, c3_y, cp_pins['1']['x'], cp_pins['1']['y'], 90) # Left (Pin 1 +)
c3_p2 = sym_to_sch(c3_x, c3_y, cp_pins['2']['x'], cp_pins['2']['y'], 90) # Right (Pin 2 -)
sch_text += add_wire(c3_p1[0], c3_p1[1], c3_p1[0] - 5.08, c3_p1[1])
sch_text += add_label("VOL_OUT_L", c3_p1[0] - 5.08, c3_p1[1], 180)
sch_text += add_wire(c3_p2[0], c3_p2[1], c3_p2[0] + 5.08, c3_p2[1])
sch_text += add_label("COM_L", c3_p2[0] + 5.08, c3_p2[1], 0)

# C4: 4.7uF for Right Output (at 254.0, 96.52, rot=90)
c4_x, c4_y = 254.0, 96.52
c4_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:C_Polarized") (at {c4_x:.2f} {c4_y:.2f} 90) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {c4_uuid})
\t\t(property "Reference" "C4" (at {c4_x:.2f} {c4_y-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "4.7uF" (at {c4_x:.2f} {c4_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm" (at {c4_x:.2f} {c4_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {c4_x:.2f} {c4_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "C4") (unit 1))))
\t)\n"""
c4_p1 = sym_to_sch(c4_x, c4_y, cp_pins['1']['x'], cp_pins['1']['y'], 90) # Left (Pin 1 +)
c4_p2 = sym_to_sch(c4_x, c4_y, cp_pins['2']['x'], cp_pins['2']['y'], 90) # Right (Pin 2 -)
sch_text += add_wire(c4_p1[0], c4_p1[1], c4_p1[0] - 5.08, c4_p1[1])
sch_text += add_label("VOL_OUT_R", c4_p1[0] - 5.08, c4_p1[1], 180)
sch_text += add_wire(c4_p2[0], c4_p2[1], c4_p2[0] + 5.08, c4_p2[1])
sch_text += add_label("COM_R", c4_p2[0] + 5.08, c4_p2[1], 0)

# =========================================================================
# 7. RY1: Mechanical DPDT Relay (Omron G6K-2) (at 279.4, 137.16)
# =========================================================================
ry1_x, ry1_y = 279.4, 137.16
ry1_uuid = u()
sch_text += f"""\t(symbol (lib_id "Relay:G6K-2") (at {ry1_x:.2f} {ry1_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {ry1_uuid})
\t\t(property "Reference" "RY1" (at {ry1_x+16.51:.2f} {ry1_y+3.81:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "G6K-2P-Y_DC5" (at {ry1_x+16.51:.2f} {ry1_y+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Relay_THT:Relay_DPDT_Omron_G6K-2P-Y" (at {ry1_x:.2f} {ry1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "http://omronfs.omron.com/en_US/ecb/products/pdf/en-g6k.pdf" (at {ry1_x:.2f} {ry1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
"""
for p in ['1', '2', '3', '4', '5', '6', '7', '8']:
    sch_text += f'\t\t(pin "{p}" (uuid {u()}))\n'
sch_text += f"""\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "RY1") (unit 1))))
\t)\n"""

# Relay Connections:
# Pin 1: Coil + (+5V)
ry_p1 = sym_to_sch(ry1_x, ry1_y, relay_pins['1']['x'], relay_pins['1']['y'], 0)
sch_text += add_wire(ry_p1[0], ry_p1[1], ry_p1[0] - 5.08, ry_p1[1])
sch_text += add_pwr("power:+5V", "+5V", ry_p1[0] - 5.08, ry_p1[1])

# Pin 8: Coil - (RELAY_COIL_NEG)
ry_p8 = sym_to_sch(ry1_x, ry1_y, relay_pins['8']['x'], relay_pins['8']['y'], 0)
sch_text += add_wire(ry_p8[0], ry_p8[1], ry_p8[0] - 5.08, ry_p8[1])
sch_text += add_label("RELAY_COIL_NEG", ry_p8[0] - 5.08, ry_p8[1], 180)

# Pin 3: COM 1 (Left) -> from C3 (COM_L)
ry_p3 = sym_to_sch(ry1_x, ry1_y, relay_pins['3']['x'], relay_pins['3']['y'], 0)
sch_text += add_wire(ry_p3[0], ry_p3[1], ry_p3[0], ry_p3[1] + 5.08)
sch_text += add_label("COM_L", ry_p3[0], ry_p3[1] + 5.08, 270)

# Pin 2: NC 1 (Left) -> SPK_OUT_L
ry_p2 = sym_to_sch(ry1_x, ry1_y, relay_pins['2']['x'], relay_pins['2']['y'], 0)
sch_text += add_wire(ry_p2[0], ry_p2[1], ry_p2[0], ry_p2[1] - 5.08)
sch_text += add_label("SPK_OUT_L", ry_p2[0], ry_p2[1] - 5.08, 90)

# Pin 4: NO 1 (Left) -> HP_OUT_L
ry_p4 = sym_to_sch(ry1_x, ry1_y, relay_pins['4']['x'], relay_pins['4']['y'], 0)
sch_text += add_wire(ry_p4[0], ry_p4[1], ry_p4[0], ry_p4[1] - 5.08)
sch_text += add_label("HP_OUT_L", ry_p4[0], ry_p4[1] - 5.08, 90)

# Pin 6: COM 2 (Right) -> from C4 (COM_R)
ry_p6 = sym_to_sch(ry1_x, ry1_y, relay_pins['6']['x'], relay_pins['6']['y'], 0)
sch_text += add_wire(ry_p6[0], ry_p6[1], ry_p6[0], ry_p6[1] + 5.08)
sch_text += add_label("COM_R", ry_p6[0], ry_p6[1] + 5.08, 270)

# Pin 7: NC 2 (Right) -> SPK_OUT_R
ry_p7 = sym_to_sch(ry1_x, ry1_y, relay_pins['7']['x'], relay_pins['7']['y'], 0)
sch_text += add_wire(ry_p7[0], ry_p7[1], ry_p7[0], ry_p7[1] - 5.08)
sch_text += add_label("SPK_OUT_R", ry_p7[0], ry_p7[1] - 5.08, 90)

# Pin 5: NO 2 (Right) -> HP_OUT_R
ry_p5 = sym_to_sch(ry1_x, ry1_y, relay_pins['5']['x'], relay_pins['5']['y'], 0)
sch_text += add_wire(ry_p5[0], ry_p5[1], ry_p5[0], ry_p5[1] - 5.08)
sch_text += add_label("HP_OUT_R", ry_p5[0], ry_p5[1] - 5.08, 90)

# =========================================================================
# 8. Relay Driver: Q1 (2N7000), D1 (1N4148), R_G (1k), R3 (10k) (at 228.6, 177.8)
# =========================================================================
# D1: 1N4148 flyback diode (at 213.36, 177.80, rot=90)
d1_x, d1_y, d1_rot = 213.36, 177.80, 90
d1_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:D") (at {d1_x:.2f} {d1_y:.2f} {d1_rot}) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {d1_uuid})
\t\t(property "Reference" "D1" (at {d1_x:.2f} {d1_y-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "1N4148" (at {d1_x:.2f} {d1_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal" (at {d1_x:.2f} {d1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "https://assets.nexperia.com/documents/data-sheet/1N4148_1N4448.pdf" (at {d1_x:.2f} {d1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "D1") (unit 1))))
\t)\n"""
d1_k = sym_to_sch(d1_x, d1_y, diode_pins['1']['x'], diode_pins['1']['y'], d1_rot) # Cathode: Pin 1
d1_a = sym_to_sch(d1_x, d1_y, diode_pins['2']['x'], diode_pins['2']['y'], d1_rot) # Anode: Pin 2
sch_text += add_wire(d1_k[0], d1_k[1], d1_k[0], d1_k[1] - 2.54)
sch_text += add_pwr("power:+5V", "+5V", d1_k[0], d1_k[1] - 2.54)
sch_text += add_wire(d1_a[0], d1_a[1], d1_a[0], d1_a[1] + 2.54)
sch_text += add_label("RELAY_COIL_NEG", d1_a[0], d1_a[1] + 2.54, 270)

# R_G: 1k gate resistor (at 231.14, 167.64, rot=90)
# Pin 1: (rg_x - 3.81, rg_y), Pin 2: (rg_x + 3.81, rg_y)
rg_x, rg_y, rg_rot = 231.14, 167.64, 90
rg_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:R") (at {rg_x:.2f} {rg_y:.2f} {rg_rot}) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {rg_uuid})
\t\t(property "Reference" "R_G" (at {rg_x:.2f} {rg_y-5.08:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "1k" (at {rg_x:.2f} {rg_y-2.54:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" (at {rg_x:.2f} {rg_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {rg_x:.2f} {rg_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "R_G") (unit 1))))
\t)\n"""
rg_p1 = sym_to_sch(rg_x, rg_y, r_pins['1']['x'], r_pins['1']['y'], rg_rot)
rg_p2 = sym_to_sch(rg_x, rg_y, r_pins['2']['x'], r_pins['2']['y'], rg_rot)
sch_text += add_wire(rg_p1[0], rg_p1[1], rg_p1[0] - 5.08, rg_p1[1])
sch_text += add_label("RELAY_CTRL", rg_p1[0] - 5.08, rg_p1[1], 180)

# Q1: 2N7000 (at 254.0, 167.64, rot=0)
q1_x, q1_y = 254.0, 167.64
q1_uuid = u()
sch_text += f"""\t(symbol (lib_id "Transistor_FET:2N7000") (at {q1_x:.2f} {q1_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {q1_uuid})
\t\t(property "Reference" "Q1" (at {q1_x+5.08:.2f} {q1_y-1.91:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Value" "2N7000" (at {q1_x+5.08:.2f} {q1_y:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))
\t\t(property "Footprint" "Package_TO_SOT_THT:TO-92_Inline" (at {q1_x:.2f} {q1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "https://www.vishay.com/docs/70226/70226.pdf" (at {q1_x:.2f} {q1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(pin "3" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "Q1") (unit 1))))
\t)\n"""
q1_s = sym_to_sch(q1_x, q1_y, fet_pins['1']['x'], fet_pins['1']['y'], 0) # Source: Pin 1
q1_g = sym_to_sch(q1_x, q1_y, fet_pins['2']['x'], fet_pins['2']['y'], 0) # Gate: Pin 2
q1_d = sym_to_sch(q1_x, q1_y, fet_pins['3']['x'], fet_pins['3']['y'], 0) # Drain: Pin 3

sch_text += add_wire(q1_s[0], q1_s[1], q1_s[0], q1_s[1] + 2.54)
sch_text += add_gnd(q1_s[0], q1_s[1] + 2.54, "DGND")
sch_text += add_wire(q1_d[0], q1_d[1], q1_d[0], q1_d[1] - 2.54)
sch_text += add_label("RELAY_COIL_NEG", q1_d[0], q1_d[1] - 2.54, 90)

# Wire from R_G pin 2 to Q1 Gate
sch_text += add_wire(rg_p2[0], rg_p2[1], q1_g[0], q1_g[1])

# R3: 10k pulldown from Gate to DGND (at 241.30, 180.34, rot=0)
r3_x, r3_y = 241.30, 180.34
r3_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:R") (at {r3_x:.2f} {r3_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {r3_uuid})
\t\t(property "Reference" "R3" (at {r3_x+3.81:.2f} {r3_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "10k" (at {r3_x+3.81:.2f} {r3_y+1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" (at {r3_x:.2f} {r3_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {r3_x:.2f} {r3_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "R3") (unit 1))))
\t)\n"""
r3_p1 = sym_to_sch(r3_x, r3_y, r_pins['1']['x'], r_pins['1']['y'], 0) # (r3_x, r3_y - 3.81)
r3_p2 = sym_to_sch(r3_x, r3_y, r_pins['2']['x'], r_pins['2']['y'], 0) # (r3_x, r3_y + 3.81)

# Connect R3 pin 1 up to wire between R_G and Q1 gate:
gate_wire_y = q1_g[1]
sch_text += add_wire(r3_p1[0], r3_p1[1], r3_p1[0], gate_wire_y)
sch_text += add_junction(r3_p1[0], gate_wire_y)
sch_text += add_wire(r3_p2[0], r3_p2[1], r3_p2[0], r3_p2[1] + 2.54)
sch_text += add_gnd(r3_p2[0], r3_p2[1] + 2.54, "DGND")

# =========================================================================
# 9. Output Audio Jacks: J2 (Speaker Out), J3 (Headphone Out) (at 330.2, 101.6)
# =========================================================================
# J2: Speaker Out (at 330.2, 88.90, rot=0)
j2_x, j2_y = 330.2, 88.90
j2_uuid = u()
sch_text += f"""\t(symbol (lib_id "Connector_Audio:AudioJack3") (at {j2_x:.2f} {j2_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {j2_uuid})
\t\t(property "Reference" "J2" (at {j2_x:.2f} {j2_y-8.89:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "Speaker_Out" (at {j2_x:.2f} {j2_y-6.35:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Connector_Audio:Jack_3.5mm_CUI_SJ1-3523N_Horizontal" (at {j2_x:.2f} {j2_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {j2_x:.2f} {j2_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "R" (uuid {u()}))
\t\t(pin "S" (uuid {u()}))
\t\t(pin "T" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "J2") (unit 1))))
\t)\n"""
j2_t = sym_to_sch(j2_x, j2_y, jack_pins['T']['x'], jack_pins['T']['y'], 0)
j2_r = sym_to_sch(j2_x, j2_y, jack_pins['R']['x'], jack_pins['R']['y'], 0)
j2_s = sym_to_sch(j2_x, j2_y, jack_pins['S']['x'], jack_pins['S']['y'], 0)
sch_text += add_wire(j2_t[0], j2_t[1], j2_t[0] + 5.08, j2_t[1])
sch_text += add_label("SPK_OUT_L", j2_t[0] + 5.08, j2_t[1], 0)
sch_text += add_wire(j2_r[0], j2_r[1], j2_r[0] + 5.08, j2_r[1])
sch_text += add_label("SPK_OUT_R", j2_r[0] + 5.08, j2_r[1], 0)
sch_text += add_wire(j2_s[0], j2_s[1], j2_s[0] + 2.54, j2_s[1])
sch_text += add_wire(j2_s[0] + 2.54, j2_s[1], j2_s[0] + 2.54, j2_s[1] + 5.08)
sch_text += add_gnd(j2_s[0] + 2.54, j2_s[1] + 5.08, "AGND")

# J3: Headphone Out (at 330.2, 139.70, rot=0)
j3_x, j3_y = 330.2, 139.70
j3_uuid = u()
sch_text += f"""\t(symbol (lib_id "Connector_Audio:AudioJack3") (at {j3_x:.2f} {j3_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {j3_uuid})
\t\t(property "Reference" "J3" (at {j3_x:.2f} {j3_y-8.89:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "Headphone_Out" (at {j3_x:.2f} {j3_y-6.35:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Connector_Audio:Jack_3.5mm_CUI_SJ1-3523N_Horizontal" (at {j3_x:.2f} {j3_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {j3_x:.2f} {j3_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "R" (uuid {u()}))
\t\t(pin "S" (uuid {u()}))
\t\t(pin "T" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "J3") (unit 1))))
\t)\n"""
j3_t = sym_to_sch(j3_x, j3_y, jack_pins['T']['x'], jack_pins['T']['y'], 0)
j3_r = sym_to_sch(j3_x, j3_y, jack_pins['R']['x'], jack_pins['R']['y'], 0)
j3_s = sym_to_sch(j3_x, j3_y, jack_pins['S']['x'], jack_pins['S']['y'], 0)
sch_text += add_wire(j3_t[0], j3_t[1], j3_t[0] + 5.08, j3_t[1])
sch_text += add_label("HP_OUT_L", j3_t[0] + 5.08, j3_t[1], 0)
sch_text += add_wire(j3_r[0], j3_r[1], j3_r[0] + 5.08, j3_r[1])
sch_text += add_label("HP_OUT_R", j3_r[0] + 5.08, j3_r[1], 0)
sch_text += add_wire(j3_s[0], j3_s[1], j3_s[0] + 2.54, j3_s[1])
sch_text += add_wire(j3_s[0] + 2.54, j3_s[1], j3_s[0] + 2.54, j3_s[1] + 5.08)
sch_text += add_gnd(j3_s[0] + 2.54, j3_s[1] + 5.08, "AGND")

# =========================================================================
# 10. NT1: NetTie_2 Single-Point Ground Star Connection (at 152.4, 177.8)
# =========================================================================
nt1_x, nt1_y = 152.4, 177.8
nt1_uuid = u()
sch_text += f"""\t(symbol (lib_id "Device:NetTie_2") (at {nt1_x:.2f} {nt1_y:.2f} 90) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {nt1_uuid})
\t\t(property "Reference" "NT1" (at {nt1_x:.2f} {nt1_y-3.81:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "NetTie_2" (at {nt1_x:.2f} {nt1_y-1.27:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "NetTie:NetTie-2_THT_Pad1.0mm" (at {nt1_x:.2f} {nt1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {nt1_x:.2f} {nt1_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(pin "1" (uuid {u()}))
\t\t(pin "2" (uuid {u()}))
\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "NT1") (unit 1))))
\t)\n"""
nt1_p1 = sym_to_sch(nt1_x, nt1_y, nettie_pins['1']['x'], nettie_pins['1']['y'], 90)
nt1_p2 = sym_to_sch(nt1_x, nt1_y, nettie_pins['2']['x'], nettie_pins['2']['y'], 90)
sch_text += add_wire(nt1_p1[0], nt1_p1[1], nt1_p1[0] - 5.08, nt1_p1[1])
sch_text += add_gnd(nt1_p1[0] - 5.08, nt1_p1[1], "AGND")
sch_text += add_pwr_flag(nt1_p1[0] - 5.08, nt1_p1[1]) # AGND power flag
sch_text += add_wire(nt1_p2[0], nt1_p2[1], nt1_p2[0] + 5.08, nt1_p2[1])
sch_text += add_gnd(nt1_p2[0] + 5.08, nt1_p2[1], "DGND")

# =========================================================================
# 11. J4: RJ45 8P8C Satellite Link Connector (at 76.20, 177.80)
# =========================================================================
j4_x, j4_y = 76.20, 177.80
j4_uuid = u()
sch_text += f"""\t(symbol (lib_id "Connector:8P8C") (at {j4_x:.2f} {j4_y:.2f} 0) (unit 1)
\t\t(in_bom yes) (on_board yes) (dnp no)
\t\t(uuid {j4_uuid})
\t\t(property "Reference" "J4" (at {j4_x:.2f} {j4_y-13.97:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Value" "RJ45_Satellite" (at {j4_x:.2f} {j4_y-11.43:.2f} 0) (effects (font (size 1.27 1.27))))
\t\t(property "Footprint" "Connector_RJ:RJ45_Amphenol_RJHSE5380" (at {j4_x:.2f} {j4_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
\t\t(property "Datasheet" "~" (at {j4_x:.2f} {j4_y:.2f} 0) (effects (font (size 1.27 1.27)) hide))
"""
for p in range(1, 9):
    sch_text += f'\t\t(pin "{p}" (uuid {u()}))\n'
sch_text += f"""\t\t(instances (project "main_board" (path "/{sch_uuid}" (reference "J4") (unit 1))))
\t)\n"""

j4_pin_nets = {
    '1': ('DGND', None),
    '2': ('+3V3', '+3V3'),
    '3': ('ENC_A', 'ENC_A'),
    '4': ('ENC_B', 'ENC_B'),
    '5': ('ENC_SW', 'ENC_SW'),
    '6': ('TOGGLE_SW', 'TOGGLE_SW'),
    '7': ('LED_SPK', 'LED_SPK'),
    '8': ('LED_HP', 'LED_HP'),
}
for pin_num, (net_name, label_name) in j4_pin_nets.items():
    p = rj45_pins[pin_num]
    px, py = sym_to_sch(j4_x, j4_y, p['x'], p['y'], 0)
    tx = px + 5.08
    sch_text += add_wire(px, py, tx, py)
    if label_name == '+3V3':
        sch_text += add_pwr("power:+3V3", "+3V3", tx, py)
    elif label_name:
        sch_text += add_label(label_name, tx, py, 0)
    else:
        sch_text += add_gnd(tx, py, "DGND")

# End of schematic
sch_text += f"""\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
"""

with open('pcb/main_board/main_board.kicad_sch', 'w', encoding='utf-8') as f:
    f.write(sch_text)

print("Generated main_board.kicad_sch. Running ERC...")
res = subprocess.run(['kicad-cli', 'sch', 'erc', 'pcb/main_board/main_board.kicad_sch'], capture_output=True, text=True)
print("ERC result code:", res.returncode)
print(res.stdout)
print(res.stderr)
