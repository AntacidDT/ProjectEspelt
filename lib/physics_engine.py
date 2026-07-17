
import math


CATEGORIES = {
    'mechanics': {
        'name': 'Mechanics',
        'formulas': {
            'v=u+at': {
                'desc': 'Final velocity',
                'vars': ['v', 'u', 'a', 't'],
                'solve': {
                    'v': lambda u, a, t: u + a * t,
                    'u': lambda v, a, t: v - a * t,
                    'a': lambda v, u, t: (v - u) / t if t != 0 else None,
                    't': lambda v, u, a: (v - u) / a if a != 0 else None,
                },
            },
            's=ut+0.5at^2': {
                'desc': 'Displacement',
                'vars': ['s', 'u', 'a', 't'],
                'solve': {
                    's': lambda u, a, t: u * t + 0.5 * a * t * t,
                    'u': lambda s, a, t: (s - 0.5 * a * t * t) / t if t != 0 else None,
                    'a': lambda s, u, t: 2 * (s - u * t) / (t * t) if t != 0 else None,
                    't': lambda s, u, a: _quad_t(s, u, a),
                },
            },
            'v^2=u^2+2as': {
                'desc': 'Velocity-displacement',
                'vars': ['v', 'u', 'a', 's'],
                'solve': {
                    'v': lambda u, a, s: math.sqrt(u * u + 2 * a * s) if (u * u + 2 * a * s) >= 0 else None,
                    'u': lambda v, a, s: math.sqrt(v * v - 2 * a * s) if (v * v - 2 * a * s) >= 0 else None,
                    'a': lambda v, u, s: (v * v - u * u) / (2 * s) if s != 0 else None,
                    's': lambda v, u, a: (v * v - u * u) / (2 * a) if a != 0 else None,
                },
            },
            'F=ma': {
                'desc': "Newton's 2nd law",
                'vars': ['F', 'm', 'a'],
                'solve': {
                    'F': lambda m, a: m * a,
                    'm': lambda F, a: F / a if a != 0 else None,
                    'a': lambda F, m: F / m if m != 0 else None,
                },
            },
            'p=mv': {
                'desc': 'Momentum',
                'vars': ['p', 'm', 'v'],
                'solve': {
                    'p': lambda m, v: m * v,
                    'm': lambda p, v: p / v if v != 0 else None,
                    'v': lambda p, m: p / m if m != 0 else None,
                },
            },
            'W=Fs': {
                'desc': 'Work done',
                'vars': ['W', 'F', 's'],
                'solve': {
                    'W': lambda F, s: F * s,
                    'F': lambda W, s: W / s if s != 0 else None,
                    's': lambda W, F: W / F if F != 0 else None,
                },
            },
            'KE=0.5mv^2': {
                'desc': 'Kinetic energy',
                'vars': ['KE', 'm', 'v'],
                'solve': {
                    'KE': lambda m, v: 0.5 * m * v * v,
                    'm': lambda KE, v: 2 * KE / (v * v) if v != 0 else None,
                    'v': lambda KE, m: math.sqrt(2 * KE / m) if m != 0 else None,
                },
            },
            'PE=mgh': {
                'desc': 'Gravitational PE',
                'vars': ['PE', 'm', 'g', 'h'],
                'solve': {
                    'PE': lambda m, g, h: m * g * h,
                    'm': lambda PE, g, h: PE / (g * h) if g * h != 0 else None,
                    'g': lambda PE, m, h: PE / (m * h) if m * h != 0 else None,
                    'h': lambda PE, m, g: PE / (m * g) if m * g != 0 else None,
                },
            },
            'P=W/t': {
                'desc': 'Power',
                'vars': ['P', 'W', 't'],
                'solve': {
                    'P': lambda W, t: W / t if t != 0 else None,
                    'W': lambda P, t: P * t,
                    't': lambda P, W: W / P if P != 0 else None,
                },
            },
            'Fg=Gmm/r^2': {
                'desc': 'Gravitational force',
                'vars': ['Fg', 'G', 'm1', 'm2', 'r'],
                'solve': {
                    'Fg': lambda G, m1, m2, r: G * m1 * m2 / (r * r) if r != 0 else None,
                    'r': lambda Fg, G, m1, m2: math.sqrt(G * m1 * m2 / Fg) if Fg != 0 else None,
                },
            },
            'tau=Ialpha': {
                'desc': 'Torque (rotational 2nd law)',
                'vars': ['tau', 'I', 'alpha'],
                'solve': {
                    'tau': lambda I, alpha: I * alpha,
                    'I': lambda tau, alpha: tau / alpha if alpha != 0 else None,
                    'alpha': lambda tau, I: tau / I if I != 0 else None,
                },
            },
            'L=Iomega': {
                'desc': 'Angular momentum',
                'vars': ['L', 'I', 'omega'],
                'solve': {
                    'L': lambda I, omega: I * omega,
                    'I': lambda L, omega: L / omega if omega != 0 else None,
                    'omega': lambda L, I: L / I if I != 0 else None,
                },
            },
            'KErot=0.5Iomega^2': {
                'desc': 'Rotational kinetic energy',
                'vars': ['KErot', 'I', 'omega'],
                'solve': {
                    'KErot': lambda I, omega: 0.5 * I * omega * omega,
                    'I': lambda KErot, omega: 2 * KErot / (omega * omega) if omega != 0 else None,
                    'omega': lambda KErot, I: math.sqrt(2 * KErot / I) if I != 0 else None,
                },
            },
            'omega=omega0+alphat': {
                'desc': 'Angular velocity',
                'vars': ['omega', 'omega0', 'alpha', 't'],
                'solve': {
                    'omega': lambda omega0, alpha, t: omega0 + alpha * t,
                    'omega0': lambda omega, alpha, t: omega - alpha * t,
                    'alpha': lambda omega, omega0, t: (omega - omega0) / t if t != 0 else None,
                    't': lambda omega, omega0, alpha: (omega - omega0) / alpha if alpha != 0 else None,
                },
            },
            'theta=omega0t+0.5alphat^2': {
                'desc': 'Angular displacement',
                'vars': ['theta', 'omega0', 'alpha', 't'],
                'solve': {
                    'theta': lambda omega0, alpha, t: omega0 * t + 0.5 * alpha * t * t,
                    'omega0': lambda theta, alpha, t: (theta - 0.5 * alpha * t * t) / t if t != 0 else None,
                    'alpha': lambda theta, omega0, t: 2 * (theta - omega0 * t) / (t * t) if t != 0 else None,
                    't': lambda theta, omega0, alpha: _quad_t(theta, omega0, alpha),
                },
            },
            'Fc=mv^2/r': {
                'desc': 'Centripetal force',
                'vars': ['Fc', 'm', 'v', 'r'],
                'solve': {
                    'Fc': lambda m, v, r: m * v * v / r if r != 0 else None,
                    'm': lambda Fc, v, r: Fc * r / (v * v) if v != 0 else None,
                    'v': lambda Fc, m, r: math.sqrt(Fc * r / m) if m != 0 else None,
                    'r': lambda Fc, m, v: m * v * v / Fc if Fc != 0 else None,
                },
            },
            'Ipoint=mr^2': {
                'desc': 'Moment of inertia (point)',
                'vars': ['I', 'm', 'r'],
                'solve': {
                    'I': lambda m, r: m * r * r,
                    'm': lambda I, r: I / (r * r) if r != 0 else None,
                    'r': lambda I, m: math.sqrt(I / m) if m != 0 else None,
                },
            },
            'Idisc=0.5mr^2': {
                'desc': 'Moment of inertia (disc)',
                'vars': ['I', 'm', 'r'],
                'solve': {
                    'I': lambda m, r: 0.5 * m * r * r,
                    'm': lambda I, r: 2 * I / (r * r) if r != 0 else None,
                    'r': lambda I, m: math.sqrt(2 * I / m) if m != 0 else None,
                },
            },
            'v=romega': {
                'desc': 'Tangential-angular velocity',
                'vars': ['v', 'r', 'omega'],
                'solve': {
                    'v': lambda r, omega: r * omega,
                    'r': lambda v, omega: v / omega if omega != 0 else None,
                    'omega': lambda v, r: v / r if r != 0 else None,
                },
            },
        },
    },
    'waves': {
        'name': 'Waves & Optics',
        'formulas': {
            'v=f*lambda': {
                'desc': 'Wave speed',
                'vars': ['v', 'f', 'lambda'],
                'solve': {
                    'v': lambda f, l: f * l,
                    'f': lambda v, l: v / l if l != 0 else None,
                    'lambda': lambda v, f: v / f if f != 0 else None,
                },
            },
            'T=1/f': {
                'desc': 'Period',
                'vars': ['T', 'f'],
                'solve': {
                    'T': lambda f: 1 / f if f != 0 else None,
                    'f': lambda T: 1 / T if T != 0 else None,
                },
            },
            '1/f=1/u+1/v': {
                'desc': 'Thin lens equation',
                'vars': ['f', 'u', 'v'],
                'solve': {
                    'f': lambda u, v: 1 / (1 / u + 1 / v) if (1 / u + 1 / v) != 0 else None,
                    'u': lambda f, v: 1 / (1 / f - 1 / v) if (1 / f - 1 / v) != 0 else None,
                    'v': lambda f, u: 1 / (1 / f - 1 / u) if (1 / f - 1 / u) != 0 else None,
                },
            },
            'M=-v/u': {
                'desc': 'Magnification',
                'vars': ['M', 'v', 'u'],
                'solve': {
                    'M': lambda v, u: -v / u if u != 0 else None,
                    'v': lambda M, u: -M * u,
                    'u': lambda M, v: -v / M if M != 0 else None,
                },
            },
            'n=c/v': {
                'desc': 'Refractive index',
                'vars': ['n', 'c', 'v'],
                'solve': {
                    'n': lambda c, v: c / v if v != 0 else None,
                    'c': lambda n, v: n * v,
                    'v': lambda n, c: c / n if n != 0 else None,
                },
            },
            'n1s1=n2s2': {
                'desc': "Snell's law",
                'vars': ['n1', 's1', 'n2', 's2'],
                'solve': {
                    'n1': lambda s1, n2, s2: n2 * s2 / s1 if s1 != 0 else None,
                    's1': lambda n1, n2, s2: n1 * s1 / (n2 * s2) if n2 * s2 != 0 else None,
                    'n2': lambda n1, s1, s2: n1 * s1 / s2 if s2 != 0 else None,
                    's2': lambda n1, s1, n2: n1 * s1 / n2 if n2 != 0 else None,
                },
            },
            'fdoppler=fv/(v+-vs)': {
                'desc': 'Doppler effect',
                'vars': ['fd', 'f', 'v', 'vs'],
                'solve': {
                    'fd': lambda f, v, vs: f * v / (v - vs) if (v - vs) != 0 else None,
                    'f': lambda fd, v, vs: fd * (v - vs) / v if v != 0 else None,
                    'v': lambda fd, f, vs: f * vs / (f - fd) if (f - fd) != 0 else None,
                    'vs': lambda fd, f, v: v * (f - fd) / f if f != 0 else None,
                },
            },
            'fn=nv/2L': {
                'desc': 'Standing waves (fixed)',
                'vars': ['fn', 'n', 'v', 'L'],
                'solve': {
                    'fn': lambda n, v, L: n * v / (2 * L) if L != 0 else None,
                    'n': lambda fn, v, L: 2 * fn * L / v if v != 0 else None,
                    'v': lambda fn, n, L: 2 * fn * L / n if n != 0 else None,
                    'L': lambda fn, n, v: n * v / (2 * fn) if fn != 0 else None,
                },
            },
            'dsin=nlambda': {
                'desc': 'Diffraction grating',
                'vars': ['d', 'sin', 'n', 'lambda'],
                'solve': {
                    'd': lambda sin, n, l: n * l / sin if sin != 0 else None,
                    'sin': lambda d, n, l: n * l / d if d != 0 else None,
                    'n': lambda d, sin, l: d * sin / l if l != 0 else None,
                    'lambda': lambda d, sin, n: d * sin / n if n != 0 else None,
                },
            },
            'I=I0cos^2': {
                'desc': "Malus's law",
                'vars': ['I', 'I0', 'theta'],
                'solve': {
                    'I': lambda I0, theta: I0 * math.cos(theta) ** 2,
                    'I0': lambda I, theta: I / (math.cos(theta) ** 2) if math.cos(theta) != 0 else None,
                    'theta': lambda I, I0: math.acos(math.sqrt(I / I0)) if I0 != 0 else None,
                },
            },
        },
    },
    'electricity': {
        'name': 'Electricity',
        'formulas': {
            'V=IR': {
                'desc': "Ohm's law",
                'vars': ['V', 'I', 'R'],
                'solve': {
                    'V': lambda I, R: I * R,
                    'I': lambda V, R: V / R if R != 0 else None,
                    'R': lambda V, I: V / I if I != 0 else None,
                },
            },
            'P=VI': {
                'desc': 'Electrical power',
                'vars': ['P', 'V', 'I'],
                'solve': {
                    'P': lambda V, I: V * I,
                    'V': lambda P, I: P / I if I != 0 else None,
                    'I': lambda P, V: P / V if V != 0 else None,
                },
            },
            'P=I^2R': {
                'desc': 'Power (resistance)',
                'vars': ['P', 'I', 'R'],
                'solve': {
                    'P': lambda I, R: I * I * R,
                    'I': lambda P, R: math.sqrt(P / R) if R != 0 else None,
                    'R': lambda P, I: P / (I * I) if I != 0 else None,
                },
            },
            'P=V^2/R': {
                'desc': 'Power (voltage)',
                'vars': ['P', 'V', 'R'],
                'solve': {
                    'P': lambda V, R: V * V / R if R != 0 else None,
                    'V': lambda P, R: math.sqrt(P * R) if P * R >= 0 else None,
                    'R': lambda P, V: V * V / P if P != 0 else None,
                },
            },
            'E=QV': {
                'desc': 'Energy (charge)',
                'vars': ['E', 'Q', 'V'],
                'solve': {
                    'E': lambda Q, V: Q * V,
                    'Q': lambda E, V: E / V if V != 0 else None,
                    'V': lambda E, Q: E / Q if Q != 0 else None,
                },
            },
            'Q=It': {
                'desc': 'Charge',
                'vars': ['Q', 'I', 't'],
                'solve': {
                    'Q': lambda I, t: I * t,
                    'I': lambda Q, t: Q / t if t != 0 else None,
                    't': lambda Q, I: Q / I if I != 0 else None,
                },
            },
            'V=Ed': {
                'desc': 'Electric field',
                'vars': ['V', 'E', 'd'],
                'solve': {
                    'V': lambda E, d: E * d,
                    'E': lambda V, d: V / d if d != 0 else None,
                    'd': lambda V, E: V / E if E != 0 else None,
                },
            },
            'C=Q/V': {
                'desc': 'Capacitance',
                'vars': ['C', 'Q', 'V'],
                'solve': {
                    'C': lambda Q, V: Q / V if V != 0 else None,
                    'Q': lambda C, V: C * V,
                    'V': lambda C, Q: Q / C if C != 0 else None,
                },
            },
            'Ec=0.5CV^2': {
                'desc': 'Capacitor energy',
                'vars': ['Ec', 'C', 'V'],
                'solve': {
                    'Ec': lambda C, V: 0.5 * C * V * V,
                    'C': lambda Ec, V: 2 * Ec / (V * V) if V != 0 else None,
                    'V': lambda Ec, C: math.sqrt(2 * Ec / C) if C != 0 else None,
                },
            },
            'F=kQ1Q2/r^2': {
                'desc': "Coulomb's law",
                'vars': ['F', 'k', 'Q1', 'Q2', 'r'],
                'solve': {
                    'F': lambda k, Q1, Q2, r: k * Q1 * Q2 / (r * r) if r != 0 else None,
                    'r': lambda F, k, Q1, Q2: math.sqrt(k * Q1 * Q2 / F) if F != 0 else None,
                },
            },
            'Epoint=kQ/r^2': {
                'desc': 'E-field (point charge)',
                'vars': ['E', 'k', 'Q', 'r'],
                'solve': {
                    'E': lambda k, Q, r: k * Q / (r * r) if r != 0 else None,
                    'Q': lambda E, k, r: E * r * r / k if k != 0 else None,
                    'r': lambda E, k, Q: math.sqrt(k * Q / E) if E != 0 else None,
                },
            },
            'Vpoint=kQ/r': {
                'desc': 'Potential (point charge)',
                'vars': ['V', 'k', 'Q', 'r'],
                'solve': {
                    'V': lambda k, Q, r: k * Q / r if r != 0 else None,
                    'Q': lambda V, k, r: V * r / k if k != 0 else None,
                    'r': lambda V, k, Q: k * Q / V if V != 0 else None,
                },
            },
            'Fmag=qvB': {
                'desc': 'Magnetic force',
                'vars': ['F', 'q', 'v', 'B'],
                'solve': {
                    'F': lambda q, v, B: q * v * B,
                    'q': lambda F, v, B: F / (v * B) if v * B != 0 else None,
                    'v': lambda F, q, B: F / (q * B) if q * B != 0 else None,
                    'B': lambda F, q, v: F / (q * v) if q * v != 0 else None,
                },
            },
            'Fwire=BIL': {
                'desc': 'Force on wire',
                'vars': ['F', 'B', 'I', 'L'],
                'solve': {
                    'F': lambda B, I, L: B * I * L,
                    'B': lambda F, I, L: F / (I * L) if I * L != 0 else None,
                    'I': lambda F, B, L: F / (B * L) if B * L != 0 else None,
                    'L': lambda F, B, I: F / (B * I) if B * I != 0 else None,
                },
            },
            'Vemf=BLv': {
                'desc': 'Motional EMF',
                'vars': ['V', 'B', 'L', 'v'],
                'solve': {
                    'V': lambda B, L, v: B * L * v,
                    'B': lambda V, L, v: V / (L * v) if L * v != 0 else None,
                    'L': lambda V, B, v: V / (B * v) if B * v != 0 else None,
                    'v': lambda V, B, L: V / (B * L) if B * L != 0 else None,
                },
            },
            'Phi=BAcostheta': {
                'desc': 'Magnetic flux',
                'vars': ['Phi', 'B', 'A', 'theta'],
                'solve': {
                    'Phi': lambda B, A, theta: B * A * math.cos(theta),
                    'B': lambda Phi, A, theta: Phi / (A * math.cos(theta)) if A * math.cos(theta) != 0 else None,
                    'A': lambda Phi, B, theta: Phi / (B * math.cos(theta)) if B * math.cos(theta) != 0 else None,
                    'theta': lambda Phi, B, A: math.acos(Phi / (B * A)) if B * A != 0 else None,
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
                    'XC': lambda f, C: 1 / (2 * math.pi * f * C) if f * C != 0 else None,
                    'f': lambda XC, C: 1 / (2 * math.pi * XC * C) if XC * C != 0 else None,
                    'C': lambda XC, f: 1 / (2 * math.pi * f * XC) if f * XC != 0 else None,
                },
            },
            'Z=sqrt(R^2+(XL-XC)^2)': {
                'desc': 'Impedance',
                'vars': ['Z', 'R', 'XL', 'XC'],
                'solve': {
                    'Z': lambda R, XL, XC: math.sqrt(R * R + (XL - XC) ** 2),
                    'R': lambda Z, XL, XC: math.sqrt(Z * Z - (XL - XC) ** 2) if Z * Z >= (XL - XC) ** 2 else None,
                },
            },
        },
    },
    'thermal': {
        'name': 'Thermal Physics',
        'formulas': {
            'Q=mcT': {
                'desc': 'Heat energy',
                'vars': ['Q', 'm', 'c', 'T'],
                'solve': {
                    'Q': lambda m, c, T: m * c * T,
                    'm': lambda Q, c, T: Q / (c * T) if c * T != 0 else None,
                    'c': lambda Q, m, T: Q / (m * T) if m * T != 0 else None,
                    'T': lambda Q, m, c: Q / (m * c) if m * c != 0 else None,
                },
            },
            'PV=nRT': {
                'desc': 'Ideal gas law',
                'vars': ['P', 'V', 'n', 'R', 'T'],
                'solve': {
                    'P': lambda V, n, R, T: n * R * T / V if V != 0 else None,
                    'V': lambda P, n, R, T: n * R * T / P if P != 0 else None,
                    'n': lambda P, V, R, T: P * V / (R * T) if R * T != 0 else None,
                    'T': lambda P, V, n, R: P * V / (n * R) if n * R != 0 else None,
                },
            },
            'eff=Wout/Qh': {
                'desc': 'Efficiency',
                'vars': ['eff', 'Wout', 'Qh'],
                'solve': {
                    'eff': lambda Wout, Qh: Wout / Qh if Qh != 0 else None,
                    'Wout': lambda eff, Qh: eff * Qh,
                    'Qh': lambda eff, Wout: Wout / eff if eff != 0 else None,
                },
            },
            'e=1-Tc/Th': {
                'desc': 'Carnot efficiency',
                'vars': ['e', 'Tc', 'Th'],
                'solve': {
                    'e': lambda Tc, Th: 1 - Tc / Th if Th != 0 else None,
                    'Tc': lambda e, Th: Th * (1 - e),
                    'Th': lambda e, Tc: Tc / (1 - e) if (1 - e) != 0 else None,
                },
            },
            'P=rhoVg': {
                'desc': 'Buoyant force (Archimedes)',
                'vars': ['P', 'rho', 'V', 'g'],
                'solve': {
                    'P': lambda rho, V, g: rho * V * g,
                    'rho': lambda P, V, g: P / (V * g) if V * g != 0 else None,
                    'V': lambda P, rho, g: P / (rho * g) if rho * g != 0 else None,
                    'g': lambda P, rho, V: P / (rho * V) if rho * V != 0 else None,
                },
            },
            'A1v1=A2v2': {
                'desc': 'Continuity equation',
                'vars': ['A1', 'v1', 'A2', 'v2'],
                'solve': {
                    'A1': lambda v1, A2, v2: A2 * v2 / v1 if v1 != 0 else None,
                    'v1': lambda A1, A2, v2: A2 * v2 / A1 if A1 != 0 else None,
                    'A2': lambda A1, v1, v2: A1 * v1 / v2 if v2 != 0 else None,
                    'v2': lambda A1, v1, A2: A1 * v1 / A2 if A2 != 0 else None,
                },
            },
            'P=rhoGh': {
                'desc': 'Hydrostatic pressure',
                'vars': ['P', 'rho', 'g', 'h'],
                'solve': {
                    'P': lambda rho, g, h: rho * g * h,
                    'rho': lambda P, g, h: P / (g * h) if g * h != 0 else None,
                    'g': lambda P, rho, h: P / (rho * h) if rho * h != 0 else None,
                    'h': lambda P, rho, g: P / (rho * g) if rho * g != 0 else None,
                },
            },
        },
    },
    'nuclear': {
        'name': 'Nuclear Physics',
        'formulas': {
            'E=mc^2': {
                'desc': 'Mass-energy equivalence',
                'vars': ['E', 'm', 'c'],
                'solve': {
                    'E': lambda m, c: m * c * c,
                    'm': lambda E, c: E / (c * c) if c != 0 else None,
                    'c': lambda E, m: math.sqrt(E / m) if m != 0 else None,
                },
            },
            'N=N0e^(-lt)': {
                'desc': 'Radioactive decay',
                'vars': ['N', 'N0', 'l', 't'],
                'solve': {
                    'N': lambda N0, l, t: N0 * math.exp(-l * t),
                    'N0': lambda N, l, t: N / math.exp(-l * t) if math.exp(-l * t) != 0 else None,
                    'l': lambda N, N0, t: -math.log(N / N0) / t if t != 0 and N / N0 > 0 else None,
                    't': lambda N, N0, l: -math.log(N / N0) / l if l != 0 and N / N0 > 0 else None,
                },
            },
            't12=ln2/l': {
                'desc': 'Half-life',
                'vars': ['t12', 'l'],
                'solve': {
                    't12': lambda l: math.log(2) / l if l != 0 else None,
                    'l': lambda t12: math.log(2) / t12 if t12 != 0 else None,
                },
            },
            'Ephoton=hf': {
                'desc': 'Photon energy',
                'vars': ['E', 'h', 'f'],
                'solve': {
                    'E': lambda h, f: h * f,
                    'h': lambda E, f: E / f if f != 0 else None,
                    'f': lambda E, h: E / h if h != 0 else None,
                },
            },
            'lambda=h/p': {
                'desc': 'de Broglie wavelength',
                'vars': ['lambda', 'h', 'p'],
                'solve': {
                    'lambda': lambda h, p: h / p if p != 0 else None,
                    'h': lambda lambda_, p: lambda_ * p,
                    'p': lambda h, lambda_: h / lambda_ if lambda_ != 0 else None,
                },
            },
            'DE=Dt_ge_hbar2': {
                'desc': 'Uncertainty principle',
                'vars': ['dE', 'dt'],
                'solve': {
                    'dE': lambda dt: 5.27286e-35 / dt if dt != 0 else None,
                    'dt': lambda dE: 5.27286e-35 / dE if dE != 0 else None,
                },
            },
        },
    },
    'relativity': {
        'name': 'Relativity',
        'formulas': {
            'gamma=1/sqrt(1-v2c2)': {
                'desc': 'Lorentz factor',
                'vars': ['gamma', 'v', 'c'],
                'solve': {
                    'gamma': lambda v, c: 1 / math.sqrt(1 - (v / c) ** 2) if abs(v / c) < 1 else None,
                    'v': lambda gamma, c: c * math.sqrt(1 - 1 / (gamma ** 2)) if gamma > 1 else None,
                },
            },
            'tdilated=gamma*t0': {
                'desc': 'Time dilation',
                'vars': ['td', 'gamma', 't0'],
                'solve': {
                    'td': lambda gamma, t0: gamma * t0,
                    'gamma': lambda td, t0: td / t0 if t0 != 0 else None,
                    't0': lambda td, gamma: td / gamma if gamma != 0 else None,
                },
            },
            'Lcontract=L0/gamma': {
                'desc': 'Length contraction',
                'vars': ['L', 'L0', 'gamma'],
                'solve': {
                    'L': lambda L0, gamma: L0 / gamma if gamma != 0 else None,
                    'L0': lambda L, gamma: L * gamma,
                    'gamma': lambda L, L0: L0 / L if L != 0 else None,
                },
            },
            'E2=(pc)2+(mc2)2': {
                'desc': 'Energy-momentum',
                'vars': ['E', 'p', 'c', 'm'],
                'solve': {
                    'E': lambda p, c, m: math.sqrt((p * c) ** 2 + (m * c * c) ** 2),
                    'p': lambda E, c, m: math.sqrt(E * E - (m * c * c) ** 2) / c if E > m * c * c else None,
                    'm': lambda E, p, c: math.sqrt(E * E - (p * c) ** 2) / (c * c) if E > p * c else None,
                },
            },
            'prel=gamma*m*v': {
                'desc': 'Relativistic momentum',
                'vars': ['p', 'gamma', 'm', 'v'],
                'solve': {
                    'p': lambda gamma, m, v: gamma * m * v,
                    'gamma': lambda p, m, v: p / (m * v) if m * v != 0 else None,
                    'm': lambda p, gamma, v: p / (gamma * v) if gamma * v != 0 else None,
                    'v': lambda p, gamma, m: p / (gamma * m) if gamma * m != 0 else None,
                },
            },
            'Krel=(gamma-1)mc2': {
                'desc': 'Relativistic KE',
                'vars': ['K', 'gamma', 'm', 'c'],
                'solve': {
                    'K': lambda gamma, m, c: (gamma - 1) * m * c * c,
                    'gamma': lambda K, m, c: K / (m * c * c) + 1 if m * c * c != 0 else None,
                    'm': lambda K, gamma, c: K / ((gamma - 1) * c * c) if (gamma - 1) * c * c != 0 else None,
                },
            },
        },
    },
    'modern': {
        'name': 'Modern Physics',
        'formulas': {
            'S=klW': {
                'desc': 'Boltzmann entropy',
                'vars': ['S', 'k', 'W'],
                'solve': {
                    'S': lambda k, W: k * math.log(W) if W > 0 else None,
                    'k': lambda S, W: S / math.log(W) if W > 0 and math.log(W) != 0 else None,
                    'W': lambda S, k: math.exp(S / k) if k != 0 else None,
                },
            },
            'DS=Q/T': {
                'desc': 'Entropy change',
                'vars': ['DS', 'Q', 'T'],
                'solve': {
                    'DS': lambda Q, T: Q / T if T != 0 else None,
                    'Q': lambda DS, T: DS * T,
                    'T': lambda DS, Q: Q / DS if DS != 0 else None,
                },
            },
            'COP=Tc/(Th-Tc)': {
                'desc': 'Heat pump COP',
                'vars': ['COP', 'Tc', 'Th'],
                'solve': {
                    'COP': lambda Tc, Th: Tc / (Th - Tc) if (Th - Tc) != 0 else None,
                    'Tc': lambda COP, Th: COP * Th / (COP + 1) if (COP + 1) != 0 else None,
                    'Th': lambda COP, Tc: Tc * (COP + 1) / COP if COP != 0 else None,
                },
            },
            'lambda_max=b/T': {
                'desc': "Wien's displacement",
                'vars': ['lambda_max', 'b', 'T'],
                'solve': {
                    'lambda_max': lambda b, T: b / T if T != 0 else None,
                    'b': lambda lambda_max, T: lambda_max * T,
                    'T': lambda lambda_max, b: b / lambda_max if lambda_max != 0 else None,
                },
            },
            'I=sigmaT4': {
                'desc': 'Stefan-Boltzmann law',
                'vars': ['I', 'sigma', 'T'],
                'solve': {
                    'I': lambda sigma, T: sigma * T ** 4,
                    'sigma': lambda I, T: I / (T ** 4) if T != 0 else None,
                    'T': lambda I, sigma: (I / sigma) ** 0.25 if sigma != 0 and I / sigma >= 0 else None,
                },
            },
        },
    },
    'constants': {
        'name': 'Constants',
        'formulas': {},
    },
}

PHYS_CONSTANTS = {
    'c': 299792458.0,
    'g': 9.80665,
    'G': 6.674e-11,
    'h': 6.626e-34,
    'e': 1.602e-19,
    'R': 8.314,
    'k': 1.381e-23,
    'me': 9.109e-31,
    'mp': 1.673e-27,
    'NA': 6.022e23,
    'epsilon0': 8.854e-12,
    'mu0': 1.257e-6,
    'sigma': 5.670e-8,
}

CONST_NAMES = {
    'c': 'Speed of light (m/s)',
    'g': 'Gravity (m/s^2)',
    'G': 'Grav. constant (N m^2/kg^2)',
    'h': 'Planck constant (J s)',
    'e': 'Electron charge (C)',
    'R': 'Gas constant (J/mol K)',
    'k': 'Boltzmann constant (J/K)',
    'me': 'Electron mass (kg)',
    'mp': 'Proton mass (kg)',
    'NA': 'Avogadro number',
    'epsilon0': 'Epsilon_0 (F/m)',
    'mu0': 'Mu_0 (H/m)',
    'sigma': 'Stefan-Boltzmann (W/m^2 K^4)',
}


def _quad_t(s, u, a):
    if a == 0:
        return s / u if u != 0 else None
    disc = u * u - 2 * a * (-s)
    if disc < 0:
        return None
    t1 = (-u + math.sqrt(disc)) / a
    t2 = (-u - math.sqrt(disc)) / a
    candidates = []
    if t1 >= 0:
        candidates.append(t1)
    if t2 >= 0:
        candidates.append(t2)
    if not candidates:
        return None
    return min(candidates)


def get_categories():
    return list(CATEGORIES.keys())


def get_category_display():
    lines = []
    for key, cat in CATEGORIES.items():
        count = len(cat['formulas'])
        if key == 'constants':
            lines.append((key, 'CONSTANTS ({} values)'.format(len(PHYS_CONSTANTS))))
        else:
            lines.append((key, '{} ({} formulas)'.format(cat['name'], count)))
    return lines


def get_formula_display(cat_key):
    cat = CATEGORIES.get(cat_key)
    if not cat:
        return []
    lines = []
    for formula, info in cat['formulas'].items():
        lines.append((formula, info['desc']))
    return lines


def get_formula_info(cat_key, formula_key):
    cat = CATEGORIES.get(cat_key)
    if not cat:
        return None
    return cat['formulas'].get(formula_key)


def solve_formula(cat_key, formula_key, known):
    info = get_formula_info(cat_key, formula_key)
    if not info:
        return None, 'Unknown formula'
    solve_funcs = info.get('solve', {})
    all_vars = info.get('vars', [])
    unknown = None
    for v in all_vars:
        if v not in known:
            if unknown is None:
                unknown = v
            else:
                return None, 'Need exactly 1 unknown'
    if unknown is None:
        return None, 'No unknown variable'
    if unknown not in solve_funcs:
        return None, 'Cannot solve for ' + unknown
    try:
        kwargs = {v: known[v] for v in all_vars if v != unknown and v in known}
        result = solve_funcs[unknown](**kwargs)
        if result is None:
            return None, 'Math error (div by zero?)'
        if isinstance(result, complex):
            return None, 'Complex result'
        return result, unknown
    except Exception as e:
        return None, str(e)


def format_result(value, unit=''):
    if isinstance(value, float):
        if value != value:
            return 'NaN'
        if value == float('inf'):
            return 'inf'
        if value == float('-inf'):
            return '-inf'
        if abs(value) >= 1e6 or (abs(value) < 0.001 and value != 0):
            s = '{:.4e}'.format(value)
        elif value == int(value) and abs(value) < 1e15:
            s = str(int(value))
        else:
            s = '{:.6g}'.format(value)
    else:
        s = str(value)
    if unit:
        return s + ' ' + unit
    return s
