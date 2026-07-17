
import math


# ── Unit symbols for TFT (using extended font chars) ──
OHM = '\u03A9'       # Ω
MICRO = '\u03BC'      # μ
INF = '\u221E'        # ∞
PI = '\u03C0'         # π
SQRT = '\u221A'       # √
DEG = '\u00B0'        # °

# ── SI Prefixes ──
SI_PREFIXES = [
    (1e12, 'T'), (1e9, 'G'), (1e6, 'M'), (1e3, 'k'),
    (1, ''), (1e-3, 'm'), (1e-6, MICRO), (1e-9, 'n'), (1e-12, 'p'),
]

def fmt_val(v, unit=''):
    if v is None:
        return 'ERR'
    av = abs(v)
    for scale, prefix in SI_PREFIXES:
        if av >= scale * 0.999:
            scaled = v / scale
            if abs(scaled) >= 100:
                s = str(int(round(scaled)))
            elif abs(scaled) >= 10:
                s = '%.1f' % scaled
            else:
                s = '%.2f' % scaled
            return s + prefix + unit
    return '%.2e' % v + unit

def _parse_val(s):
    s = s.strip().replace(' ', '')
    if not s:
        return None
    s = s.replace(MICRO, 'e-6').replace('u', 'e-6').replace('U', 'e-6')
    s = s.replace('k', 'e3').replace('K', 'e3')
    s = s.replace('M', 'e6').replace('G', 'e9').replace('T', 'e12')
    s = s.replace('n', 'e-9').replace('N', 'e-9')
    s = s.replace('p', 'e-12').replace('P', 'e-12')
    s = s.replace('m', 'e-3')
    s = s.replace(OHM, '').replace('R', '').replace('ohm', '')
    s = s.replace('F', '').replace('H', '').replace('V', '').replace('A', '')
    s = s.replace('W', '').replace('Hz', '').replace('hz', '')
    s = s.replace('db', '').replace('dB', '').replace('dBm', '')
    return float(s)


# ══════════════════════════════════════════════════════════════
#  FORMULA CATEGORIES
# ══════════════════════════════════════════════════════════════

CATEGORIES = {
    'circuit': {
        'name': 'Circuit Basics',
        'formulas': {
            'V=IR': {
                'desc': "Ohm's Law",
                'vars': ['V', 'I', 'R'],
                'solve': {
                    'V': lambda I, R: I * R,
                    'I': lambda V, R: V / R if R != 0 else None,
                    'R': lambda V, I: V / I if I != 0 else None,
                },
            },
            'P=IV': {
                'desc': 'Electric power',
                'vars': ['P', 'I', 'V'],
                'solve': {
                    'P': lambda I, V: I * V,
                    'I': lambda P, V: P / V if V != 0 else None,
                    'V': lambda P, I: P / I if I != 0 else None,
                },
            },
            'P=I2R': {
                'desc': 'Power (I-squared-R)',
                'vars': ['P', 'I', 'R'],
                'solve': {
                    'P': lambda I, R: I * I * R,
                    'I': lambda P, R: math.sqrt(P / R) if R != 0 and P >= 0 else None,
                    'R': lambda P, I: P / (I * I) if I != 0 else None,
                },
            },
            'P=V2/R': {
                'desc': 'Power (V-squared-over-R)',
                'vars': ['P', 'V', 'R'],
                'solve': {
                    'P': lambda V, R: V * V / R if R != 0 else None,
                    'V': lambda P, R: math.sqrt(P * R) if P >= 0 else None,
                    'R': lambda P, V: V * V / P if P != 0 else None,
                },
            },
            'Rseries': {
                'desc': 'Series resistors (R1+R2+R3)',
                'vars': ['R1', 'R2', 'R3', 'Rtotal'],
                'solve': {
                    'Rtotal': lambda R1, R2, R3: R1 + R2 + R3,
                    'R1': lambda R2, R3, Rtotal: Rtotal - R2 - R3,
                },
            },
            'Rparallel': {
                'desc': 'Parallel resistors (2)',
                'vars': ['R1', 'R2', 'Rtotal'],
                'solve': {
                    'Rtotal': lambda R1, R2: (R1 * R2) / (R1 + R2) if (R1 + R2) != 0 else None,
                    'R1': lambda R2, Rtotal: (Rtotal * R2) / (R2 - Rtotal) if (R2 - Rtotal) != 0 else None,
                    'R2': lambda R1, Rtotal: (Rtotal * R1) / (R1 - Rtotal) if (R1 - Rtotal) != 0 else None,
                },
            },
            'Vdiv': {
                'desc': 'Voltage divider',
                'vars': ['Vin', 'R1', 'R2', 'Vout'],
                'solve': {
                    'Vout': lambda Vin, R1, R2: Vin * R2 / (R1 + R2) if (R1 + R2) != 0 else None,
                    'Vin': lambda Vout, R1, R2: Vout * (R1 + R2) / R2 if R2 != 0 else None,
                    'R1': lambda Vin, Vout, R2: R2 * (Vin / Vout - 1) if Vout != 0 else None,
                    'R2': lambda Vin, Vout, R1: R1 / (Vin / Vout - 1) if Vout != 0 and Vin != Vout else None,
                },
            },
            'Idiv': {
                'desc': 'Current divider (2)',
                'vars': ['Itotal', 'R1', 'R2', 'I1'],
                'solve': {
                    'I1': lambda Itotal, R1, R2: Itotal * R2 / (R1 + R2) if (R1 + R2) != 0 else None,
                    'Itotal': lambda I1, R1, R2: I1 * (R1 + R2) / R2 if R2 != 0 else None,
                },
            },
            'tauRC': {
                'desc': 'RC time constant',
                'vars': ['tau', 'R', 'C'],
                'solve': {
                    'tau': lambda R, C: R * C,
                    'R': lambda tau, C: tau / C if C != 0 else None,
                    'C': lambda tau, R: tau / R if R != 0 else None,
                },
            },
            'f_RC': {
                'desc': 'RC cutoff frequency',
                'vars': ['f', 'R', 'C'],
                'solve': {
                    'f': lambda R, C: 1 / (2 * math.pi * R * C) if R != 0 and C != 0 else None,
                    'R': lambda f, C: 1 / (2 * math.pi * f * C) if f != 0 and C != 0 else None,
                    'C': lambda f, R: 1 / (2 * math.pi * f * R) if f != 0 and R != 0 else None,
                },
            },
            'tauRL': {
                'desc': 'RL time constant',
                'vars': ['tau', 'R', 'L'],
                'solve': {
                    'tau': lambda R, L: L / R if R != 0 else None,
                    'R': lambda tau, L: L / tau if tau != 0 else None,
                    'L': lambda tau, R: tau * R,
                },
            },
        },
    },
    'ac': {
        'name': 'AC Circuits',
        'formulas': {
            'Z=impedance': {
                'desc': 'Impedance Z=SQRT(R2+X2)',
                'vars': ['Z', 'R', 'X'],
                'solve': {
                    'Z': lambda R, X: math.sqrt(R * R + X * X),
                    'R': lambda Z, X: math.sqrt(Z * Z - X * X) if Z * Z >= X * X else None,
                    'X': lambda Z, R: math.sqrt(Z * Z - R * R) if Z * Z >= R * R else None,
                },
            },
            'XL=2pifL': {
                'desc': 'Inductive reactance',
                'vars': ['XL', 'f', 'L'],
                'solve': {
                    'XL': lambda f, L: 2 * math.pi * f * L,
                    'f': lambda XL, L: XL / (2 * math.pi * L) if L != 0 else None,
                    'L': lambda XL, f: XL / (2 * math.pi * f) if f != 0 else None,
                },
            },
            'XC=1/(2pifC)': {
                'desc': 'Capacitive reactance',
                'vars': ['XC', 'f', 'C'],
                'solve': {
                    'XC': lambda f, C: 1 / (2 * math.pi * f * C) if f != 0 and C != 0 else None,
                    'f': lambda XC, C: 1 / (2 * math.pi * XC * C) if XC != 0 and C != 0 else None,
                    'C': lambda XC, f: 1 / (2 * math.pi * XC * f) if XC != 0 and f != 0 else None,
                },
            },
            'phase=atan(X/R)': {
                'desc': 'Phase angle',
                'vars': ['phase', 'X', 'R'],
                'solve': {
                    'phase': lambda X, R: math.degrees(math.atan2(X, R)),
                    'X': lambda phase, R: R * math.tan(math.radians(phase)),
                    'R': lambda phase, X: X / math.tan(math.radians(phase)) if math.tan(math.radians(phase)) != 0 else None,
                },
            },
            'PF=cos(phase)': {
                'desc': 'Power factor',
                'vars': ['PF', 'phase'],
                'solve': {
                    'PF': lambda phase: math.cos(math.radians(phase)),
                    'phase': lambda PF: math.degrees(math.acos(PF)) if -1 <= PF <= 1 else None,
                },
            },
            'Vrms=Vpk/SQRT2': {
                'desc': 'RMS voltage',
                'vars': ['Vrms', 'Vpk'],
                'solve': {
                    'Vrms': lambda Vpk: Vpk / math.sqrt(2),
                    'Vpk': lambda Vrms: Vrms * math.sqrt(2),
                },
            },
            'Irms=Ipk/SQRT2': {
                'desc': 'RMS current',
                'vars': ['Irms', 'Ipk'],
                'solve': {
                    'Irms': lambda Ipk: Ipk / math.sqrt(2),
                    'Ipk': lambda Irms: Irms * math.sqrt(2),
                },
            },
        },
    },
    'resonance': {
        'name': 'LC Resonance',
        'formulas': {
            'f0=1/(2piSQRT(LC))': {
                'desc': 'Resonant frequency',
                'vars': ['f0', 'L', 'C'],
                'solve': {
                    'f0': lambda L, C: 1 / (2 * math.pi * math.sqrt(L * C)) if L > 0 and C > 0 else None,
                    'L': lambda f0, C: 1 / ((2 * math.pi * f0) ** 2 * C) if f0 != 0 and C != 0 else None,
                    'C': lambda f0, L: 1 / ((2 * math.pi * f0) ** 2 * L) if f0 != 0 and L != 0 else None,
                },
            },
            'Q=X/R': {
                'desc': 'Quality factor',
                'vars': ['Q', 'X', 'R'],
                'solve': {
                    'Q': lambda X, R: X / R if R != 0 else None,
                    'X': lambda Q, R: Q * R,
                    'R': lambda Q, X: X / Q if Q != 0 else None,
                },
            },
            'BW=f0/Q': {
                'desc': 'Bandwidth',
                'vars': ['BW', 'f0', 'Q'],
                'solve': {
                    'BW': lambda f0, Q: f0 / Q if Q != 0 else None,
                    'f0': lambda BW, Q: BW * Q,
                    'Q': lambda f0, BW: f0 / BW if BW != 0 else None,
                },
            },
            'Ec=0.5CV2': {
                'desc': 'Capacitor energy',
                'vars': ['E', 'C', 'V'],
                'solve': {
                    'E': lambda C, V: 0.5 * C * V * V,
                    'C': lambda E, V: 2 * E / (V * V) if V != 0 else None,
                    'V': lambda E, C: math.sqrt(2 * E / C) if C != 0 and E >= 0 else None,
                },
            },
            'EL=0.5LI2': {
                'desc': 'Inductor energy',
                'vars': ['E', 'L', 'I'],
                'solve': {
                    'E': lambda L, I: 0.5 * L * I * I,
                    'L': lambda E, I: 2 * E / (I * I) if I != 0 else None,
                    'I': lambda E, L: math.sqrt(2 * E / L) if L != 0 and E >= 0 else None,
                },
            },
        },
    },
    'digital': {
        'name': 'Digital Logic',
        'formulas': {
            'NOT': {
                'desc': 'NOT gate (inverter)',
                'vars': ['A', 'Y'],
                'solve': {
                    'Y': lambda A: 0 if A != 0 else 1,
                },
            },
            'AND': {
                'desc': 'AND gate',
                'vars': ['A', 'B', 'Y'],
                'solve': {
                    'Y': lambda A, B: 1 if A != 0 and B != 0 else 0,
                },
            },
            'OR': {
                'desc': 'OR gate',
                'vars': ['A', 'B', 'Y'],
                'solve': {
                    'Y': lambda A, B: 1 if A != 0 or B != 0 else 0,
                },
            },
            'NAND': {
                'desc': 'NAND gate',
                'vars': ['A', 'B', 'Y'],
                'solve': {
                    'Y': lambda A, B: 0 if A != 0 and B != 0 else 1,
                },
            },
            'NOR': {
                'desc': 'NOR gate',
                'vars': ['A', 'B', 'Y'],
                'solve': {
                    'Y': lambda A, B: 1 if A == 0 and B == 0 else 0,
                },
            },
            'XOR': {
                'desc': 'XOR gate',
                'vars': ['A', 'B', 'Y'],
                'solve': {
                    'Y': lambda A, B: 1 if (A != 0) != (B != 0) else 0,
                },
            },
            'XNOR': {
                'desc': 'XNOR gate',
                'vars': ['A', 'B', 'Y'],
                'solve': {
                    'Y': lambda A, B: 0 if (A != 0) != (B != 0) else 1,
                },
            },
            'DeMorgan': {
                'desc': "De Morgan: NOT(A AND B)=NOT(A) OR NOT(B)",
                'vars': ['A', 'B', 'nAB', 'nA_o_nB'],
                'solve': {
                    'nAB': lambda A, B: 0 if A != 0 and B != 0 else 1,
                    'nA_o_nB': lambda A, B: 1 if A == 0 or B == 0 else 0,
                },
            },
            'full_add': {
                'desc': 'Full adder sum',
                'vars': ['A', 'B', 'Cin', 'Sum', 'Cout'],
                'solve': {
                    'Sum': lambda A, B, Cin: int(A) ^ int(B) ^ int(Cin),
                    'Cout': lambda A, B, Cin: 1 if (int(A) + int(B) + int(Cin)) >= 2 else 0,
                },
            },
            'mux2': {
                'desc': '2:1 multiplexer',
                'vars': ['I0', 'I1', 'Sel', 'Y'],
                'solve': {
                    'Y': lambda I0, I1, Sel: I1 if Sel != 0 else I0,
                },
            },
        },
    },
    'transistor': {
        'name': 'Transistors',
        'formulas': {
            'BJT_Ic': {
                'desc': 'BJT collector current (Ic=hFE*Ib)',
                'vars': ['Ic', 'hFE', 'Ib'],
                'solve': {
                    'Ic': lambda hFE, Ib: hFE * Ib,
                    'hFE': lambda Ic, Ib: Ic / Ib if Ib != 0 else None,
                    'Ib': lambda Ic, hFE: Ic / hFE if hFE != 0 else None,
                },
            },
            'BJT_Vce': {
                'desc': 'BJT Vce = Vcc - Ic*Rc',
                'vars': ['Vcc', 'Ic', 'Rc', 'Vce'],
                'solve': {
                    'Vce': lambda Vcc, Ic, Rc: Vcc - Ic * Rc,
                    'Vcc': lambda Vce, Ic, Rc: Vce + Ic * Rc,
                    'Ic': lambda Vcc, Vce, Rc: (Vcc - Vce) / Rc if Rc != 0 else None,
                    'Rc': lambda Vcc, Ic, Vce: (Vcc - Vce) / Ic if Ic != 0 else None,
                },
            },
            'BJT_bias': {
                'desc': 'BJT voltage divider bias (Vb)',
                'vars': ['Vcc', 'R1', 'R2', 'Vb'],
                'solve': {
                    'Vb': lambda Vcc, R1, R2: Vcc * R2 / (R1 + R2) if (R1 + R2) != 0 else None,
                    'Vcc': lambda Vb, R1, R2: Vb * (R1 + R2) / R2 if R2 != 0 else None,
                },
            },
            'MOSFET_Vgs': {
                'desc': 'MOSFET Vgs threshold',
                'vars': ['Vg', 'Vs', 'Vgs'],
                'solve': {
                    'Vgs': lambda Vg, Vs: Vg - Vs,
                    'Vg': lambda Vgs, Vs: Vgs + Vs,
                    'Vs': lambda Vg, Vgs: Vg - Vgs,
                },
            },
            'MOSFET_Rdson': {
                'desc': 'MOSFET power (P=I2*Rdson)',
                'vars': ['P', 'Id', 'Rdson'],
                'solve': {
                    'P': lambda Id, Rdson: Id * Id * Rdson,
                    'Id': lambda P, Rdson: math.sqrt(P / Rdson) if Rdson != 0 and P >= 0 else None,
                    'Rdson': lambda P, Id: P / (Id * Id) if Id != 0 else None,
                },
            },
        },
    },
    'opamp': {
        'name': 'Op-Amp Circuits',
        'formulas': {
            'inv_gain': {
                'desc': 'Inverting amplifier (Gain=-Rf/Rin)',
                'vars': ['Gain', 'Rf', 'Rin'],
                'solve': {
                    'Gain': lambda Rf, Rin: -Rf / Rin if Rin != 0 else None,
                    'Rf': lambda Gain, Rin: -Gain * Rin,
                    'Rin': lambda Gain, Rf: -Rf / Gain if Gain != 0 else None,
                },
            },
            'noninv_gain': {
                'desc': 'Non-inverting (Gain=1+Rf/Rin)',
                'vars': ['Gain', 'Rf', 'Rin'],
                'solve': {
                    'Gain': lambda Rf, Rin: 1 + Rf / Rin if Rin != 0 else None,
                    'Rf': lambda Gain, Rin: (Gain - 1) * Rin,
                    'Rin': lambda Gain, Rf: Rf / (Gain - 1) if Gain != 1 else None,
                },
            },
            'summing': {
                'desc': 'Summing amp (Vout=-Rf*(V1/R1+V2/R2))',
                'vars': ['Rf', 'V1', 'R1', 'V2', 'R2', 'Vout'],
                'solve': {
                    'Vout': lambda Rf, V1, R1, V2, R2: -Rf * (V1 / R1 + V2 / R2) if R1 != 0 and R2 != 0 else None,
                },
            },
            'noninv_sum': {
                'desc': 'Non-inv summing (Vout=V1+V2 with R)',
                'vars': ['V1', 'V2', 'Vout'],
                'solve': {
                    'Vout': lambda V1, V2: V1 + V2,
                },
            },
            'follower': {
                'desc': 'Voltage follower (Vout=Vin)',
                'vars': ['Vin', 'Vout'],
                'solve': {
                    'Vout': lambda Vin: Vin,
                    'Vin': lambda Vout: Vout,
                },
            },
            'integrator': {
                'desc': 'Integrator (Vout=-1/(RC)*integral(Vin dt))',
                'vars': ['R', 'C', 'Vin', 'dt', 'Vout'],
                'solve': {
                    'Vout': lambda R, C, Vin, dt: -Vin * dt / (R * C) if R != 0 and C != 0 else None,
                },
            },
            'differentiator': {
                'desc': 'Differentiator (Vout=-RC*dV/dt)',
                'vars': ['R', 'C', 'dV', 'dt', 'Vout'],
                'solve': {
                    'Vout': lambda R, C, dV, dt: -R * C * dV / dt if dt != 0 else None,
                },
            },
        },
    },
    'power': {
        'name': 'Power Supply',
        'formulas': {
            'buck': {
                'desc': 'Buck converter (Vout=D*Vin)',
                'vars': ['Vin', 'D', 'Vout'],
                'solve': {
                    'Vout': lambda Vin, D: Vin * D,
                    'Vin': lambda Vout, D: Vout / D if D != 0 else None,
                    'D': lambda Vout, Vin: Vout / Vin if Vin != 0 else None,
                },
            },
            'boost': {
                'desc': 'Boost converter (Vout=Vin/(1-D))',
                'vars': ['Vin', 'D', 'Vout'],
                'solve': {
                    'Vout': lambda Vin, D: Vin / (1 - D) if D != 1 else None,
                    'Vin': lambda Vout, D: Vout * (1 - D),
                    'D': lambda Vout, Vin: 1 - Vin / Vout if Vout != 0 else None,
                },
            },
            'buck_boost': {
                'desc': 'Buck-boost (Vout=Vin*D/(1-D))',
                'vars': ['Vin', 'D', 'Vout'],
                'solve': {
                    'Vout': lambda Vin, D: Vin * D / (1 - D) if D != 1 else None,
                    'Vin': lambda Vout, D: Vout * (1 - D) / D if D != 0 else None,
                    'D': lambda Vout, Vin: Vout / (Vin + Vout) if (Vin + Vout) != 0 else None,
                },
            },
            'ripple_V': {
                'desc': 'Capacitor voltage ripple (dV=I*dt/C)',
                'vars': ['I', 'dt', 'C', 'dV'],
                'solve': {
                    'dV': lambda I, dt, C: I * dt / C if C != 0 else None,
                    'I': lambda dV, dt, C: dV * C / dt if dt != 0 else None,
                    'C': lambda I, dt, dV: I * dt / dV if dV != 0 else None,
                },
            },
            'LDO_headroom': {
                'desc': 'LDO headroom (Vin=Vout+Vdropout)',
                'vars': ['Vin', 'Vout', 'Vdrop'],
                'solve': {
                    'Vin': lambda Vout, Vdrop: Vout + Vdrop,
                    'Vout': lambda Vin, Vdrop: Vin - Vdrop,
                    'Vdrop': lambda Vin, Vout: Vin - Vout,
                },
            },
            'heatsink': {
                'desc': 'Heatsink (Rja=(Tj-Ta)/P)',
                'vars': ['Tj', 'Ta', 'P', 'Rja'],
                'solve': {
                    'Rja': lambda Tj, Ta, P: (Tj - Ta) / P if P != 0 else None,
                    'Tj': lambda Ta, P, Rja: Ta + P * Rja,
                    'Ta': lambda Tj, P, Rja: Tj - P * Rja,
                    'P': lambda Tj, Ta, Rja: (Tj - Ta) / Rja if Rja != 0 else None,
                },
            },
        },
    },
}


# ══════════════════════════════════════════════════════════════
#  REFERENCE DATA
# ══════════════════════════════════════════════════════════════

# Resistor color codes: (name, multiplier, tolerance)
RCOLORS = [
    ('black', 0, 1, None),
    ('brown', 1, 10, '1%'),
    ('red', 2, 100, '2%'),
    ('orange', 3, 1e3, None),
    ('yellow', 4, 1e4, None),
    ('green', 5, 1e5, '0.5%'),
    ('blue', 6, 1e6, '0.25%'),
    ('violet', 7, 1e7, '0.1%'),
    ('grey', 8, 1e8, '0.05%'),
    ('white', 9, 1e9, None),
    ('gold', -1, 0.1, '5%'),
    ('silver', -2, 0.01, '10%'),
]

COLOR_NAMES = [c[0] for c in RCOLORS]
COLOR_VALS = {c[0]: c[1] for c in RCOLORS}
COLOR_MULT = {c[0]: c[2] for c in RCOLORS}
COLOR_TOL = {c[0]: c[3] for c in RCOLORS}

# Standard E12/E24 resistor values (ohms)
STD_VALUES = [
    1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2,
]

# LED forward voltages by color
LED_VF = {
    'red': 1.8, 'orange': 2.0, 'yellow': 2.1, 'green': 2.2,
    'blue': 3.3, 'white': 3.3, 'violet': 3.3, 'purple': 3.3,
    'ir': 1.3, 'uv': 3.6,
}
LED_IF_MAX = {
    'red': 20, 'orange': 20, 'yellow': 20, 'green': 20,
    'blue': 30, 'white': 30, 'violet': 20, 'purple': 20,
    'ir': 100, 'uv': 50,
}

# Wire gauge table (AWG -> mm, amps)
WIRE_GAUGE = {
    30: (0.25, 0.5), 28: (0.32, 0.7), 26: (0.40, 1.0), 24: (0.50, 1.5),
    22: (0.64, 2.1), 20: (0.81, 3.0), 18: (1.02, 4.7), 16: (1.29, 7.0),
    14: (1.63, 9.5), 12: (2.05, 13.5), 10: (2.59, 19), 8: (3.26, 28),
    6: (4.11, 40), 4: (5.19, 55), 2: (6.54, 75), 1: (7.35, 90),
    0: (8.25, 100),
}

# Common IC pinouts
IC_PINOUTS = {
    '555': {
        'name': '555 Timer',
        'pins': [
            '1: GND', '2: TRIG', '3: OUT', '4: RESET',
            '5: CTRL', '6: THRES', '7: DISCH', '8: VCC',
        ],
    },
    '7805': {
        'name': '7805 5V Regulator',
        'pins': ['1: IN', '2: GND', '3: OUT'],
    },
    '7812': {
        'name': '7812 12V Regulator',
        'pins': ['1: IN', '2: GND', '3: OUT'],
    },
    'LM317': {
        'name': 'LM317 Adjustable Regulator',
        'pins': ['1: ADJ', '2: OUT', '3: IN'],
    },
    'LM358': {
        'name': 'LM358 Dual Op-Amp',
        'pins': [
            '1: OUT1', '2: IN1-', '3: IN1+', '4: GND',
            '5: IN2+', '6: IN2-', '7: OUT2', '8: VCC',
        ],
    },
    'NE5532': {
        'name': 'NE5532 Dual Op-Amp',
        'pins': [
            '1: OUT1', '2: IN1-', '3: IN1+', '4: VEE',
            '5: IN2+', '6: IN2-', '7: OUT2', '8: VCC',
        ],
    },
    'LM741': {
        'name': 'LM741 Op-Amp',
        'pins': [
            '1: OFFSET', '2: IN-', '3: IN+', '4: VEE',
            '5: OFFSET', '6: OUT', '7: VCC', '8: NC',
        ],
    },
    'ATmega328': {
        'name': 'ATmega328P (Arduino)',
        'pins': [
            '1: PC6/RESET', '2: PD0/RXD', '3: PD1/TXD', '4: PD2',
            '5: PD3/PWM', '6: PD4', '7: VCC', '8: GND',
            '9: PB6/XTAL', '10: PB7/XTAL', '11: PD5/PWM', '12: PD6/PWM',
            '13: PD7', '14: PB0', '15: PB1/PWM', '16: PB2/PWM/SS',
            '17: PB3/PWM/MOSI', '18: PB4/MISO', '19: PB5/SCK', '20: AVCC',
            '21: AREF', '22: GND', '23: PC0', '24: PC1',
            '25: PC2', '26: PC3', '27: PC4/SDA', '28: PC5/SCL',
        ],
    },
}

# UART baud rates
BAUD_RATES = [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]

# SMD capacitor code table
SMD_CAP_CODES = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
}


# ══════════════════════════════════════════════════════════════
#  TOOLS
# ══════════════════════════════════════════════════════════════

def resistor_color(value_ohms):
    if value_ohms <= 0:
        return None, None, None, None
    v = value_ohms
    mult = 0
    while v >= 100:
        v /= 10
        mult += 1
    while v < 10:
        v *= 10
        mult -= 1
    d1 = int(v / 10)
    d2 = int(v) % 10
    color_list = ['black', 'brown', 'red', 'orange', 'yellow',
                  'green', 'blue', 'violet', 'grey', 'white']
    if 0 <= d1 <= 9 and 0 <= d2 <= 9:
        return color_list[d1], color_list[d2], mult, '5%'
    return None, None, None, None


def resistor_value(c1, c2, cmult):
    c1 = c1.lower().strip()
    c2 = c2.lower().strip()
    cmult = cmult.lower().strip()
    if c1 not in COLOR_VALS or c2 not in COLOR_VALS:
        return None
    v1 = COLOR_VALS[c1]
    v2 = COLOR_VALS[c2]
    if v1 < 0 or v2 < 0:
        return None
    mult = COLOR_MULT.get(cmult, None)
    if mult is None:
        return None
    return (v1 * 10 + v2) * mult


def led_resistor(vsupply, vf, if_target_ma):
    if if_target_ma <= 0:
        return None
    r = (vsupply - vf) / (if_target_ma / 1000)
    return r if r > 0 else None


def decode_cap_code(code):
    code = code.strip().upper()
    if not code:
        return None
    if len(code) == 1:
        return int(code) if code.isdigit() else None
    if len(code) == 2 and code.isdigit():
        return int(code) * 1e-12
    if len(code) >= 3 and code[0].isdigit() and code[1].isdigit():
        d1 = int(code[0])
        d2 = int(code[1])
        exp = int(code[2]) if code[2].isdigit() else 0
        if len(code) > 3 and code[3] == '+':
            exp = int(code[2]) * 10 + (int(code[3 + 1]) if len(code) > 4 and code[4].isdigit() else 0)
        return (d1 * 10 + d2) * (10 ** exp) * 1e-12
    return None


def uart_frame_time(baud, bits=10):
    if baud <= 0:
        return None
    return bits / baud


def decode_smd_cap(code):
    code = code.strip().upper()
    if not code or len(code) < 2:
        return None
    if code[-1] == 'P':
        try:
            return int(code[:-1]) * 1e-12
        except:
            return None
    if code[-1] == 'N':
        try:
            return int(code[:-1]) * 1e-9
        except:
            return None
    if code[-1] == 'U':
        try:
            return int(code[:-1]) * 1e-6
        except:
            return None
    try:
        return int(code) * 1e-12
    except:
        return None


# ══════════════════════════════════════════════════════════════
#  FORMULA SOLVER
# ══════════════════════════════════════════════════════════════

def get_category_display():
    cats = []
    for key in CATEGORIES:
        cats.append((key, CATEGORIES[key]['name']))
    cats.append(('constants', 'SI Prefixes'))
    cats.append(('tools', 'Tools'))
    cats.append(('reference', 'Reference'))
    return cats


def get_formula_display(cat_key):
    if cat_key not in CATEGORIES:
        return []
    formulas = CATEGORIES[cat_key]['formulas']
    result = []
    for key in formulas:
        result.append((key, formulas[key]['desc']))
    return result


def get_formula_info(cat_key, formula_key):
    if cat_key not in CATEGORIES:
        return None
    formulas = CATEGORIES[cat_key]['formulas']
    if formula_key not in formulas:
        return None
    return formulas[formula_key]


def solve_formula(cat_key, formula_key, known):
    if cat_key not in CATEGORIES:
        return None, 'bad category'
    formulas = CATEGORIES[cat_key]['formulas']
    if formula_key not in formulas:
        return None, 'bad formula'
    formula = formulas[formula_key]
    solve = formula.get('solve', {})
    vars_list = formula.get('vars', [])
    unknown = None
    for v in vars_list:
        if v not in known:
            if unknown is None:
                unknown = v
            else:
                return None, 'need 2+ unknowns'
    if unknown is None:
        return None, 'all known'
    if unknown not in solve:
        return None, 'cant solve'
    try:
        result = solve[unknown](**{k: known[k] for k in known})
        return result, unknown
    except Exception as e:
        return None, str(e)


def format_result(v):
    if v is None:
        return 'ERR'
    if isinstance(v, float):
        av = abs(v)
        if av == 0:
            return '0'
        if av >= 1e9:
            return '%.2e' % v
        if av >= 1e6:
            return '%.2f M' % (v / 1e6)
        if av >= 1e3:
            return '%.2f k' % (v / 1e3)
        if av >= 1:
            return '%.4f' % v
        if av >= 1e-3:
            return '%.4f m' % (v * 1e3)
        if av >= 1e-6:
            return '%.4f %s' % (v * 1e6, MICRO)
        if av >= 1e-9:
            return '%.4f n' % (v * 1e9)
        return '%.2e' % v
    return str(v)


# SI Prefixes display
SI_PREFIX_DATA = [
    ('T', 'tera', 1e12),
    ('G', 'giga', 1e9),
    ('M', 'mega', 1e6),
    ('k', 'kilo', 1e3),
    ('', '', 1),
    ('m', 'milli', 1e-3),
    (MICRO, 'micro', 1e-6),
    ('n', 'nano', 1e-9),
    ('p', 'pico', 1e-12),
    ('f', 'femto', 1e-15),
]


def get_tools_display():
    return [
        ('rcalc', 'Resistor color code calc'),
        ('vdiv', 'Voltage divider calc'),
        ('led', 'LED resistor calc'),
        ('rcfilt', 'RC filter calc'),
        ('lcfilt', 'LC resonant calc'),
        ('baud', 'UART baud rate calc'),
        ('cap', 'Capacitor code decode'),
    ]


def get_reference_display():
    return [
        ('ic', 'IC pinouts'),
        ('wire', 'Wire gauge table'),
        ('led', 'LED forward voltages'),
        ('truth', 'Logic gate truth tables'),
        ('smd_cap', 'SMD capacitor codes'),
    ]


# ══════════════════════════════════════════════════════════════
#  TOOL SOLVERS
# ══════════════════════════════════════════════════════════════

def tool_rcalc(known, val):
    known = known.lower().strip()
    val = val.lower().strip()
    if known == 'color':
        colors = val.split()
        if len(colors) == 3:
            r = resistor_value(colors[0], colors[1], colors[2])
            if r is not None:
                return 'R = ' + fmt_val(r, OHM)
        return 'Need 3 colors'
    if known == 'value':
        r = _parse_val(val)
        if r is None:
            return 'Bad value'
        c1, c2, cmult, ctol = resistor_color(r)
        if c1 is None:
            return 'Cant convert'
        color_list = ['black', 'brown', 'red', 'orange', 'yellow',
                      'green', 'blue', 'violet', 'grey', 'white']
        mult_name = color_list[cmult] if 0 <= cmult <= 9 else str(cmult)
        return c1 + ' ' + c2 + ' ' + mult_name + ' ' + ctol
    return 'Use: rcalc color c1 c2 cmult\n   or: rcalc value 4700'


def tool_vdiv(vin, r1, r2):
    if r1 + r2 == 0:
        return 'ERR: R1+R2=0'
    vout = vin * r2 / (r1 + r2)
    i = vout / r2 if r2 != 0 else 0
    p = vin * i
    return ('Vout=' + fmt_val(vout, 'V') +
            '  I=' + fmt_val(i, 'A') +
            '  P=' + fmt_val(p, 'W'))


def tool_led(vsupply, vf, if_ma):
    r = led_resistor(vsupply, vf, if_ma)
    if r is None:
        return 'ERR: negative R'
    p = (vsupply - vf) * (if_ma / 1000)
    nearest = min(STD_VALUES, key=lambda x: abs(x - r))
    return ('R=' + fmt_val(r, OHM) +
            '  nearest=' + fmt_val(nearest, OHM) +
            '  P=' + fmt_val(p, 'W'))


def tool_rcfilt(r, c):
    if r == 0 or c == 0:
        return 'ERR'
    tau = r * c
    fc = 1 / (2 * math.pi * tau)
    return ('tau=' + fmt_val(tau, 's') +
            '  fc=' + fmt_val(fc, 'Hz'))


def tool_lcfilt(l, c):
    if l == 0 or c == 0:
        return 'ERR'
    f0 = 1 / (2 * math.pi * math.sqrt(l * c))
    xl = 2 * math.pi * f0 * l
    return ('f0=' + fmt_val(f0, 'Hz') +
            '  XL=' + fmt_val(xl, OHM))


def tool_baud(baud):
    ft = uart_frame_time(baud)
    if ft is None:
        return 'ERR'
    return ('frame=' + '%.1f' % (ft * 1e6) + 'us' +
            '  byte/s=' + str(baud // 10))


def tool_cap(code):
    v = decode_smd_cap(code)
    if v is None:
        return 'Bad code'
    return fmt_val(v, 'F')


# ══════════════════════════════════════════════════════════════
#  REFERENCE LOOKUP
# ══════════════════════════════════════════════════════════════

def ref_ic(name):
    name = name.upper().strip().replace(' ', '')
    for key in IC_PINOUTS:
        if key.upper() == name:
            ic = IC_PINOUTS[key]
            lines = [ic['name']]
            lines.extend(ic['pins'])
            return lines
    lines = ['Available ICs:']
    for key in sorted(IC_PINOUTS.keys()):
        lines.append('  ' + key + ' - ' + IC_PINOUTS[key]['name'])
    return lines


def ref_wire(awg):
    if awg in WIRE_GAUGE:
        mm, amps = WIRE_GAUGE[awg]
        return ['AWG %d' % awg, '  diameter: %.2f mm' % mm, '  max: %.1f A' % amps]
    lines = ['AWG  diam   Max']
    for g in sorted(WIRE_GAUGE.keys()):
        mm, amps = WIRE_GAUGE[g]
        lines.append('  %2d  %4.2fmm  %4.1fA' % (g, mm, amps))
    return lines


def ref_led():
    lines = ['Color     Vf    Imax']
    for color in ['red', 'orange', 'yellow', 'green', 'blue', 'white', 'ir', 'uv']:
        vf = LED_VF[color]
        imax = LED_IF_MAX[color]
        lines.append('  %-8s %.1fV  %dmA' % (color, vf, imax))
    return lines


def ref_truth(gate):
    gate = gate.upper().strip()
    tables = {
        'NOT': ['A Y', '0 1', '1 0'],
        'AND': ['A B Y', '0 0 0', '0 1 0', '1 0 0', '1 1 1'],
        'OR': ['A B Y', '0 0 0', '0 1 1', '1 0 1', '1 1 1'],
        'NAND': ['A B Y', '0 0 1', '0 1 1', '1 0 1', '1 1 0'],
        'NOR': ['A B Y', '0 0 1', '0 1 0', '1 0 0', '1 1 0'],
        'XOR': ['A B Y', '0 0 0', '0 1 1', '1 0 1', '1 1 0'],
        'XNOR': ['A B Y', '0 0 1', '0 1 0', '1 0 0', '1 1 1'],
    }
    if gate in tables:
        return tables[gate]
    lines = ['Gates:']
    for g in ['NOT', 'AND', 'OR', 'NAND', 'NOR', 'XOR', 'XNOR']:
        lines.append('  ' + g)
    return lines


def ref_smd_cap():
    return [
        'SMD Capacitor Codes',
        '',
        '  3-digit: XY Z => (XY * 10^Z) pF',
        '  Example: 104 => 100,000pF = 100nF',
        '  Example: 222 => 2,200pF = 2.2nF',
        '  Example: 471 => 470pF',
        '  Example: 100 => 10pF',
        '',
        '  With letter suffix:',
        '  10P => 10pF',
        '  4N7 => 4.7nF',
        '  1U0 => 1.0uF',
        '',
        '  Common values:',
        '  104 = 100nF = 0.1uF',
        '  222 = 2.2nF',
        '  473 = 47nF',
        '  106 = 10uF',
    ]
