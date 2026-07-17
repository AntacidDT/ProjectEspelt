import math


# Periodic table: symbol -> (atomic_number, name, mass, category)
# category: 1=nonmetal, 2=noble gas, 3=alkali, 4=alkaline, 5=metalloid,
#           6=halogen, 7=transition, 8=post-transition, 9=lanthanide, 10=actinide
ELEMENTS = {
    'H':  (1, 'Hydrogen', 1.008, 1),   'He': (2, 'Helium', 4.003, 2),
    'Li': (3, 'Lithium', 6.941, 3),    'Be': (4, 'Beryllium', 9.012, 4),
    'B':  (5, 'Boron', 10.81, 5),      'C':  (6, 'Carbon', 12.011, 1),
    'N':  (7, 'Nitrogen', 14.007, 1),  'O':  (8, 'Oxygen', 15.999, 1),
    'F':  (9, 'Fluorine', 18.998, 6),  'Ne': (10, 'Neon', 20.180, 2),
    'Na': (11, 'Sodium', 22.990, 3),   'Mg': (12, 'Magnesium', 24.305, 4),
    'Al': (13, 'Aluminium', 26.982, 8),'Si': (14, 'Silicon', 28.086, 5),
    'P':  (15, 'Phosphorus', 30.974, 1),'S': (16, 'Sulfur', 32.065, 1),
    'Cl': (17, 'Chlorine', 35.453, 6), 'Ar': (18, 'Argon', 39.948, 2),
    'K':  (19, 'Potassium', 39.098, 3),'Ca': (20, 'Calcium', 40.078, 4),
    'Sc': (21, 'Scandium', 44.956, 7), 'Ti': (22, 'Titanium', 47.867, 7),
    'V':  (23, 'Vanadium', 50.942, 7), 'Cr': (24, 'Chromium', 51.996, 7),
    'Mn': (25, 'Manganese', 54.938, 7),'Fe': (26, 'Iron', 55.845, 7),
    'Co': (27, 'Cobalt', 58.933, 7),   'Ni': (28, 'Nickel', 58.693, 7),
    'Cu': (29, 'Copper', 63.546, 7),   'Zn': (30, 'Zinc', 65.380, 7),
    'Ga': (31, 'Gallium', 69.723, 8),  'Ge': (32, 'Germanium', 72.630, 5),
    'As': (33, 'Arsenic', 74.922, 5),  'Se': (34, 'Selenium', 78.971, 1),
    'Br': (35, 'Bromine', 79.904, 6),  'Kr': (36, 'Krypton', 83.798, 2),
    'Rb': (37, 'Rubidium', 85.468, 3), 'Sr': (38, 'Strontium', 87.620, 4),
    'Y':  (39, 'Yttrium', 88.906, 7),  'Zr': (40, 'Zirconium', 91.224, 7),
    'Nb': (41, 'Niobium', 92.906, 7),  'Mo': (42, 'Molybdenum', 95.950, 7),
    'Tc': (43, 'Technetium', 98, 7),   'Ru': (44, 'Ruthenium', 101.07, 7),
    'Rh': (45, 'Rhodium', 102.91, 7),  'Pd': (46, 'Palladium', 106.42, 7),
    'Ag': (47, 'Silver', 107.87, 7),   'Cd': (48, 'Cadmium', 112.41, 7),
    'In': (49, 'Indium', 114.82, 8),   'Sn': (50, 'Tin', 118.71, 8),
    'Sb': (51, 'Antimony', 121.76, 5), 'Te': (52, 'Tellurium', 127.60, 5),
    'I':  (53, 'Iodine', 126.90, 6),   'Xe': (54, 'Xenon', 131.29, 2),
    'Cs': (55, 'Caesium', 132.91, 3),  'Ba': (56, 'Barium', 137.33, 4),
    'La': (57, 'Lanthanum', 138.91, 9),'Ce': (58, 'Cerium', 140.12, 9),
    'Pr': (59, 'Praseodymium', 140.91, 9),'Nd': (60, 'Neodymium', 144.24, 9),
    'Pm': (61, 'Promethium', 145, 9),  'Sm': (62, 'Samarium', 150.36, 9),
    'Eu': (63, 'Europium', 151.96, 9), 'Gd': (64, 'Gadolinium', 157.25, 9),
    'Tb': (65, 'Terbium', 158.93, 9),  'Dy': (66, 'Dysprosium', 162.50, 9),
    'Ho': (67, 'Holmium', 164.93, 9),  'Er': (68, 'Erbium', 167.26, 9),
    'Tm': (69, 'Thulium', 168.93, 9),  'Yb': (70, 'Ytterbium', 173.05, 9),
    'Lu': (71, 'Lutetium', 174.97, 9), 'Hf': (72, 'Hafnium', 178.49, 7),
    'Ta': (73, 'Tantalum', 180.95, 7), 'W':  (74, 'Tungsten', 183.84, 7),
    'Re': (75, 'Rhenium', 186.21, 7),  'Os': (76, 'Osmium', 190.23, 7),
    'Ir': (77, 'Iridium', 192.22, 7),  'Pt': (78, 'Platinum', 195.08, 7),
    'Au': (79, 'Gold', 196.97, 7),     'Hg': (80, 'Mercury', 200.59, 7),
    'Tl': (81, 'Thallium', 204.38, 8),'Pb': (82, 'Lead', 207.20, 8),
    'Bi': (83, 'Bismuth', 208.98, 8),  'Po': (84, 'Polonium', 209, 8),
    'At': (85, 'Astatine', 210, 6),    'Rn': (86, 'Radon', 222, 2),
    'Fr': (87, 'Francium', 223, 3),    'Ra': (88, 'Radium', 226, 4),
    'Ac': (89, 'Actinium', 227, 10),   'Th': (90, 'Thorium', 232.04, 10),
    'Pa': (91, 'Protactinium', 231.04, 10),'U': (92, 'Uranium', 238.03, 10),
    'Np': (93, 'Neptunium', 237, 10),  'Pu': (94, 'Plutonium', 244, 10),
    'Am': (95, 'Americium', 243, 10),  'Cm': (96, 'Curium', 247, 10),
    'Bk': (97, 'Berkelium', 247, 10),  'Cf': (98, 'Californium', 251, 10),
}

CATEGORY_NAMES = {
    1: 'Nonmetal', 2: 'Noble Gas', 3: 'Alkali Metal', 4: 'Alkaline Earth',
    5: 'Metalloid', 6: 'Halogen', 7: 'Transition Metal',
    8: 'Post-Transition', 9: 'Lanthanide', 10: 'Actinide',
}

KNOWN_MOLECULES = {
    'H2O': 'Water', 'CO2': 'Carbon Dioxide', 'NaCl': 'Sodium Chloride',
    'O2': 'Oxygen Gas', 'N2': 'Nitrogen Gas', 'H2': 'Hydrogen Gas',
    'CH4': 'Methane', 'C2H6': 'Ethane', 'C2H4': 'Ethylene',
    'C2H2': 'Acetylene', 'C6H12O6': 'Glucose', 'C2H5OH': 'Ethanol',
    'H2SO4': 'Sulfuric Acid', 'HCl': 'Hydrochloric Acid',
    'NaOH': 'Sodium Hydroxide', 'CaCO3': 'Calcium Carbonate',
    'Fe2O3': 'Iron(III) Oxide', 'CuSO4': 'Copper(II) Sulfate',
    'NH3': 'Ammonia', 'HNO3': 'Nitric Acid', 'H3PO4': 'Phosphoric Acid',
    'Ca(OH)2': 'Calcium Hydroxide', 'Mg(OH)2': 'Magnesium Hydroxide',
    'Al2O3': 'Aluminium Oxide', 'SiO2': 'Silicon Dioxide',
    'CO': 'Carbon Monoxide', 'SO2': 'Sulfur Dioxide', 'NO2': 'Nitrogen Dioxide',
    'C6H6': 'Benzene', 'CH3COOH': 'Acetic Acid', 'NaHCO3': 'Sodium Bicarbonate',
    'KMnO4': 'Potassium Permanganate', 'CaO': 'Calcium Oxide',
    'MgO': 'Magnesium Oxide', 'ZnO': 'Zinc Oxide', 'CuO': 'Copper(II) Oxide',
    'FeS2': 'Iron Pyrite', 'AgNO3': 'Silver Nitrate',
    'BaCl2': 'Barium Chloride', 'Na2CO3': 'Sodium Carbonate',
    'KOH': 'Potassium Hydroxide', 'LiOH': 'Lithium Hydroxide',
    'H2O2': 'Hydrogen Peroxide', 'Na2O2': 'Sodium Peroxide',
    'Cl2': 'Chlorine Gas', 'Br2': 'Bromine', 'I2': 'Iodine',
    'P4': 'Phosphorus', 'S8': 'Sulfur',
    'CH3OH': 'Methanol', 'C3H8': 'Propane', 'C4H10': 'Butane',
    'C6H14': 'Hexane', 'C8H18': 'Octane',
    'CH3COCH3': 'Acetone', 'C6H5OH': 'Phenol', 'CH3CHO': 'Acetaldehyde',
    'HCOOH': 'Formic Acid', 'C12H22O11': 'Sucrose', 'C2H4O2': 'Acetic Acid',
    'Na2SO4': 'Sodium Sulfate', 'K2CO3': 'Potassium Carbonate',
    'CaCl2': 'Calcium Chloride', 'MgCl2': 'Magnesium Chloride',
    'FeCl3': 'Iron(III) Chloride', 'FeCl2': 'Iron(II) Chloride',
    'CuCl2': 'Copper(II) Chloride', 'ZnCl2': 'Zinc Chloride',
    'AlCl3': 'Aluminium Chloride', 'SnCl2': 'Tin(II) Chloride',
    'PbCl2': 'Lead(II) Chloride', 'BaSO4': 'Barium Sulfate',
    'CaSO4': 'Calcium Sulfate', 'PbSO4': 'Lead(II) Sulfate',
    'AgCl': 'Silver Chloride', 'HgCl2': 'Mercury(II) Chloride',
    'KBr': 'Potassium Bromide', 'NaBr': 'Sodium Bromide',
    'KI': 'Potassium Iodide', 'NaI': 'Sodium Iodide',
    'LiF': 'Lithium Fluoride', 'NaF': 'Sodium Fluoride',
    'KF': 'Potassium Fluoride', 'CaF2': 'Calcium Fluoride',
    'AlF3': 'Aluminium Fluoride', 'MgF2': 'Magnesium Fluoride',
    'NH4Cl': 'Ammonium Chloride', 'NH4NO3': 'Ammonium Nitrate',
    '(NH4)2SO4': 'Ammonium Sulfate', 'NH4OH': 'Ammonium Hydroxide',
    'KNO3': 'Potassium Nitrate', 'NaNO3': 'Sodium Nitrate',
    'Ca(NO3)2': 'Calcium Nitrate', 'Mg(NO3)2': 'Magnesium Nitrate',
    'Fe(NO3)3': 'Iron(III) Nitrate', 'Cu(NO3)2': 'Copper(II) Nitrate',
    'Zn(NO3)2': 'Zinc Nitrate', 'Al(NO3)3': 'Aluminium Nitrate',
    'Na3PO4': 'Sodium Phosphate', 'K3PO4': 'Potassium Phosphate',
    'Ca3(PO4)2': 'Calcium Phosphate', 'FePO4': 'Iron(III) Phosphate',
    'Na2HPO4': 'Disodium Phosphate', 'NaH2PO4': 'Monosodium Phosphate',
    'Na2S': 'Sodium Sulfide', 'K2S': 'Potassium Sulfide',
    'FeS': 'Iron(II) Sulfide', 'CuS': 'Copper(II) Sulfide',
    'ZnS': 'Zinc Sulfide', 'PbS': 'Lead(II) Sulfide',
    'H2S': 'Hydrogen Sulfide', 'CS2': 'Carbon Disulfide',
    'SO3': 'Sulfur Trioxide', 'N2O': 'Nitrous Oxide',
    'NO': 'Nitric Oxide', 'ClO2': 'Chlorine Dioxide',
    'O3': 'Ozone', 'OF2': 'Oxygen Difluoride',
    'CCl4': 'Carbon Tetrachloride', 'CHCl3': 'Chloroform',
    'CH2Cl2': 'Dichloromethane', 'CH3Cl': 'Chloromethane',
    'CF4': 'Carbon Tetrafluoride', 'SF6': 'Sulfur Hexafluoride',
    'PCl5': 'Phosphorus Pentachloride', 'PCl3': 'Phosphorus Trichloride',
    'SCl2': 'Sulfur Dichloride', 'XeF2': 'Xenon Difluoride',
    'C6H5CH3': 'Toluene', 'C6H5NO2': 'Nitrobenzene',
    'C6H4(OH)2': 'Hydroquinone', 'C10H8': 'Naphthalene',
    'C6H12': 'Cyclohexane', 'C5H5N': 'Pyridine',
    'CH3NH2': 'Methylamine', 'C6H5NH2': 'Aniline',
    'CH3COOC2H5': 'Ethyl Acetate', 'C6H5COOH': 'Benzoic Acid',
    'CH3CH2OH': 'Ethanol', 'C3H7OH': 'Isopropanol',
    'HOCH2CH2OH': 'Ethylene Glycol', 'C6H12O6': 'Glucose',
    'C6H8O7': 'Citric Acid', 'C4H6O5': 'Malic Acid',
    'C2H2O4': 'Oxalic Acid', 'C3H6O3': 'Lactic Acid',
    'HOOC-COOH': 'Oxalic Acid', 'C17H35COOH': 'Stearic Acid',
    'C18H34O2': 'Oleic Acid',
}

# Electron shell capacities
SHELL_CAPACITY = [2, 8, 18, 32, 32, 18, 8]

# Oxidation states per element (common ones)
OXIDATION = {
    'H': [1, -1], 'Li': [1], 'Be': [2], 'B': [3], 'C': [4, -4, 2],
    'N': [-3, 3, 5], 'O': [-2], 'F': [-1], 'Na': [1], 'Mg': [2],
    'Al': [3], 'Si': [4, -4], 'P': [3, 5, -3], 'S': [-2, 4, 6],
    'Cl': [-1, 1, 3, 5, 7], 'K': [1], 'Ca': [2], 'Fe': [2, 3],
    'Cu': [1, 2], 'Zn': [2], 'Br': [-1, 1, 3, 5], 'Ag': [1],
    'Au': [1, 3], 'Mn': [2, 4, 7], 'Cr': [3, 6], 'Ni': [2],
    'Co': [2, 3], 'Pb': [2, 4], 'Sn': [2, 4], 'I': [-1, 1, 5, 7],
}

# Known balanced equations: unbalanced -> balanced
COMMON_EQUATIONS = {
    'H2 + O2 -> H2O': '2H2 + O2 -> 2H2O',
    'Fe + O2 -> Fe2O3': '4Fe + 3O2 -> 2Fe2O3',
    'Na + Cl2 -> NaCl': '2Na + Cl2 -> 2NaCl',
    'N2 + H2 -> NH3': 'N2 + 3H2 -> 2NH3',
    'C + O2 -> CO2': 'C + O2 -> CO2',
    'C + O2 -> CO': '2C + O2 -> 2CO',
    'Na + H2O -> NaOH + H2': '2Na + 2H2O -> 2NaOH + H2',
    'K + H2O -> KOH + H2': '2K + 2H2O -> 2KOH + H2',
    'Ca + H2O -> Ca(OH)2 + H2': 'Ca + 2H2O -> Ca(OH)2 + H2',
    'Mg + O2 -> MgO': '2Mg + O2 -> 2MgO',
    'Al + O2 -> Al2O3': '4Al + 3O2 -> 2Al2O3',
    'Zn + HCl -> ZnCl2 + H2': 'Zn + 2HCl -> ZnCl2 + H2',
    'Fe + HCl -> FeCl2 + H2': 'Fe + 2HCl -> FeCl2 + H2',
    'Mg + HCl -> MgCl2 + H2': 'Mg + 2HCl -> MgCl2 + H2',
    'Ca + HCl -> CaCl2 + H2': 'Ca + 2HCl -> CaCl2 + H2',
    'NaOH + HCl -> NaCl + H2O': 'NaOH + HCl -> NaCl + H2O',
    'H2SO4 + NaOH -> Na2SO4 + H2O': 'H2SO4 + 2NaOH -> Na2SO4 + 2H2O',
    'HNO3 + NaOH -> NaNO3 + H2O': 'HNO3 + NaOH -> NaNO3 + H2O',
    'H3PO4 + NaOH -> Na3PO4 + H2O': 'H3PO4 + 3NaOH -> Na3PO4 + 3H2O',
    'CaCO3 -> CaO + CO2': 'CaCO3 -> CaO + CO2',
    '2H2O2 -> 2H2O + O2': '2H2O2 -> 2H2O + O2',
    'H2O2 -> H2O + O2': '2H2O2 -> 2H2O + O2',
    'KClO3 -> KCl + O2': '2KClO3 -> 2KCl + 3O2',
    'KMnO4 -> K2MnO4 + MnO2 + O2': '2KMnO4 -> K2MnO4 + MnO2 + O2',
    'Fe + CuSO4 -> FeSO4 + Cu': 'Fe + CuSO4 -> FeSO4 + Cu',
    'Zn + CuSO4 -> ZnSO4 + Cu': 'Zn + CuSO4 -> ZnSO4 + Cu',
    'Cu + AgNO3 -> Cu(NO3)2 + Ag': 'Cu + 2AgNO3 -> Cu(NO3)2 + 2Ag',
    'Fe + AgNO3 -> Fe(NO3)3 + Ag': 'Fe + 3AgNO3 -> Fe(NO3)3 + 3Ag',
    'NaOH + CuSO4 -> Cu(OH)2 + Na2SO4': '2NaOH + CuSO4 -> Cu(OH)2 + Na2SO4',
    'BaCl2 + Na2SO4 -> BaSO4 + NaCl': 'BaCl2 + Na2SO4 -> BaSO4 + 2NaCl',
    'AgNO3 + NaCl -> AgCl + NaNO3': 'AgNO3 + NaCl -> AgCl + NaNO3',
    'CH4 + O2 -> CO2 + H2O': 'CH4 + 2O2 -> CO2 + 2H2O',
    'C2H5OH + O2 -> CO2 + H2O': 'C2H5OH + 3O2 -> 2CO2 + 3H2O',
    'C3H8 + O2 -> CO2 + H2O': 'C3H8 + 5O2 -> 3CO2 + 4H2O',
    'C2H6 + O2 -> CO2 + H2O': '2C2H6 + 7O2 -> 4CO2 + 6H2O',
    'Fe2O3 + CO -> Fe + CO2': 'Fe2O3 + 3CO -> 2Fe + 3CO2',
    'Fe2O3 + H2 -> Fe + H2O': 'Fe2O3 + 3H2 -> 2Fe + 3H2O',
    'CuO + H2 -> Cu + H2O': 'CuO + H2 -> Cu + H2O',
    'CuO + C -> Cu + CO2': '2CuO + C -> 2Cu + CO2',
    'Fe2O3 + C -> Fe + CO2': '2Fe2O3 + 3C -> 4Fe + 3CO2',
    'ZnO + C -> Zn + CO': 'ZnO + C -> Zn + CO',
    'CuSO4 + Fe -> FeSO4 + Cu': 'CuSO4 + Fe -> FeSO4 + Cu',
    'Na2CO3 + HCl -> NaCl + CO2 + H2O': 'Na2CO3 + 2HCl -> 2NaCl + CO2 + H2O',
    'NaHCO3 + HCl -> NaCl + CO2 + H2O': 'NaHCO3 + HCl -> NaCl + CO2 + H2O',
    'CaCO3 + HCl -> CaCl2 + CO2 + H2O': 'CaCO3 + 2HCl -> CaCl2 + CO2 + H2O',
    'MgCO3 + HCl -> MgCl2 + CO2 + H2O': 'MgCO3 + 2HCl -> MgCl2 + CO2 + H2O',
    'Na2CO3 + Ca(OH)2 -> CaCO3 + NaOH': 'Na2CO3 + Ca(OH)2 -> CaCO3 + 2NaOH',
    'NaHCO3 + NaOH -> Na2CO3 + H2O': 'NaHCO3 + NaOH -> Na2CO3 + H2O',
    'NH3 + HCl -> NH4Cl': 'NH3 + HCl -> NH4Cl',
    'NH3 + HNO3 -> NH4NO3': 'NH3 + HNO3 -> NH4NO3',
    'NH3 + H2SO4 -> (NH4)2SO4': '2NH3 + H2SO4 -> (NH4)2SO4',
    'SO2 + O2 -> SO3': '2SO2 + O2 -> 2SO3',
    'SO3 + H2O -> H2SO4': 'SO3 + H2O -> H2SO4',
    'NO + O2 -> NO2': '2NO + O2 -> 2NO2',
    'NO2 + H2O -> HNO3 + NO': '3NO2 + H2O -> 2HNO3 + NO',
    'NH3 + O2 -> NO + H2O': '4NH3 + 5O2 -> 4NO + 6H2O',
    'Fe2O3 + HCl -> FeCl3 + H2O': 'Fe2O3 + 6HCl -> 2FeCl3 + 3H2O',
    'CuO + HCl -> CuCl2 + H2O': 'CuO + 2HCl -> CuCl2 + H2O',
    'ZnO + HCl -> ZnCl2 + H2O': 'ZnO + 2HCl -> ZnCl2 + H2O',
    'Al2O3 + HCl -> AlCl3 + H2O': 'Al2O3 + 6HCl -> 2AlCl3 + 3H2O',
    'MgO + HCl -> MgCl2 + H2O': 'MgO + 2HCl -> MgCl2 + H2O',
    'Na2O + H2O -> NaOH': 'Na2O + H2O -> 2NaOH',
    'CaO + H2O -> Ca(OH)2': 'CaO + H2O -> Ca(OH)2',
    'K2O + H2O -> KOH': 'K2O + H2O -> 2KOH',
    'CO2 + H2O -> H2CO3': 'CO2 + H2O -> H2CO3',
    'SO2 + H2O -> H2SO3': 'SO2 + H2O -> H2SO3',
    'Na2O2 + H2O -> NaOH + O2': '2Na2O2 + 2H2O -> 4NaOH + O2',
    'CaC2 + H2O -> Ca(OH)2 + C2H2': 'CaC2 + 2H2O -> Ca(OH)2 + C2H2',
    'Al + HCl -> AlCl3 + H2': '2Al + 6HCl -> 2AlCl3 + 3H2',
    'Fe + H2O -> Fe3O4 + H2': '3Fe + 4H2O -> Fe3O4 + 4H2',
    'C + H2O -> CO + H2': 'C + H2O -> CO + H2',
    'Zn + H2SO4 -> ZnSO4 + H2': 'Zn + H2SO4 -> ZnSO4 + H2',
    'Fe + H2SO4 -> FeSO4 + H2': 'Fe + H2SO4 -> FeSO4 + H2',
    'Mg + H2SO4 -> MgSO4 + H2': 'Mg + H2SO4 -> MgSO4 + H2',
    'Cu + H2SO4 -> CuSO4 + SO2 + H2O': 'Cu + 2H2SO4 -> CuSO4 + SO2 + 2H2O',
    'C + H2SO4 -> CO2 + SO2 + H2O': 'C + 2H2SO4 -> CO2 + 2SO2 + 2H2O',
    'AgNO3 + NaOH -> AgOH + NaNO3': 'AgNO3 + NaOH -> AgOH + NaNO3',
    'Cu(NO3)2 + NaOH -> Cu(OH)2 + NaNO3': 'Cu(NO3)2 + 2NaOH -> Cu(OH)2 + 2NaNO3',
    'Fe(NO3)3 + NaOH -> Fe(OH)3 + NaNO3': 'Fe(NO3)3 + 3NaOH -> Fe(OH)3 + 3NaNO3',
    'Al(NO3)3 + NaOH -> Al(OH)3 + NaNO3': 'Al(NO3)3 + 3NaOH -> Al(OH)3 + 3NaNO3',
    'Zn(NO3)2 + NaOH -> Zn(OH)2 + NaNO3': 'Zn(NO3)2 + 2NaOH -> Zn(OH)2 + 2NaNO3',
    'NaOH + Al(OH)3 -> NaAlO2 + H2O': 'NaOH + Al(OH)3 -> NaAlO2 + 2H2O',
    'NaAlO2 + HCl -> Al(OH)3 + NaCl': 'NaAlO2 + HCl + H2O -> Al(OH)3 + NaCl',
    'Cu(OH)2 -> CuO + H2O': 'Cu(OH)2 -> CuO + H2O',
    '2Fe(OH)3 -> Fe2O3 + H2O': '2Fe(OH)3 -> Fe2O3 + 3H2O',
    'Ca(OH)2 + CO2 -> CaCO3 + H2O': 'Ca(OH)2 + CO2 -> CaCO3 + H2O',
    'Ba(OH)2 + H2SO4 -> BaSO4 + H2O': 'Ba(OH)2 + H2SO4 -> BaSO4 + 2H2O',
}

# Thermochemistry database
THERMO_REACTIONS = {
    'combustion': {
        'name': 'Combustion of Methane',
        'equation': 'CH4 + 2O2 -> CO2 + 2H2O',
        'dh': -890,
        'ds': -242,
        'dg': -818,
        'type': 'exothermic',
    },
    'combust methane': {
        'name': 'Combustion of Methane',
        'equation': 'CH4 + 2O2 -> CO2 + 2H2O',
        'dh': -890,
        'ds': -242,
        'dg': -818,
        'type': 'exothermic',
    },
    'neutralization': {
        'name': 'Acid-Base Neutralization',
        'equation': 'NaOH + HCl -> NaCl + H2O',
        'dh': -57.1,
        'ds': 76,
        'dg': -79.7,
        'type': 'exothermic',
    },
    'naoh_hcl': {
        'name': 'Acid-Base Neutralization',
        'equation': 'NaOH + HCl -> NaCl + H2O',
        'dh': -57.1,
        'ds': 76,
        'dg': -79.7,
        'type': 'exothermic',
    },
    'photosynthesis': {
        'name': 'Photosynthesis',
        'equation': '6CO2 + 6H2O -> C6H12O6 + 6O2',
        'dh': 2803,
        'ds': -260,
        'dg': 2880,
        'type': 'endothermic',
    },
    'rusting': {
        'name': 'Rusting of Iron',
        'equation': '4Fe + 3O2 -> 2Fe2O3',
        'dh': -1648,
        'ds': -548,
        'dg': -1485,
        'type': 'exothermic',
    },
    'iron oxidation': {
        'name': 'Rusting of Iron',
        'equation': '4Fe + 3O2 -> 2Fe2O3',
        'dh': -1648,
        'ds': -548,
        'dg': -1485,
        'type': 'exothermic',
    },
    'combust ethanol': {
        'name': 'Combustion of Ethanol',
        'equation': 'C2H5OH + 3O2 -> 2CO2 + 3H2O',
        'dh': -1367,
        'ds': -172,
        'dg': -1315,
        'type': 'exothermic',
    },
    'combust propane': {
        'name': 'Combustion of Propane',
        'equation': 'C3H8 + 5O2 -> 3CO2 + 4H2O',
        'dh': -2220,
        'ds': -334,
        'dg': -2107,
        'type': 'exothermic',
    },
    'haber': {
        'name': 'Haber Process',
        'equation': 'N2 + 3H2 -> 2NH3',
        'dh': -92,
        'ds': -198,
        'dg': -33,
        'type': 'exothermic',
    },
    'haber process': {
        'name': 'Haber Process',
        'equation': 'N2 + 3H2 -> 2NH3',
        'dh': -92,
        'ds': -198,
        'dg': -33,
        'type': 'exothermic',
    },
    'thermal decomposition': {
        'name': 'Thermal Decomposition of CaCO3',
        'equation': 'CaCO3 -> CaO + CO2',
        'dh': 178,
        'ds': 160,
        'dg': 130,
        'type': 'endothermic',
    },
    'thermal decompose limestone': {
        'name': 'Thermal Decomposition of CaCO3',
        'equation': 'CaCO3 -> CaO + CO2',
        'dh': 178,
        'ds': 160,
        'dg': 130,
        'type': 'endothermic',
    },
    'thermite': {
        'name': 'Thermite Reaction',
        'equation': '2Al + Fe2O3 -> Al2O3 + 2Fe',
        'dh': -851,
        'ds': -283,
        'dg': -757,
        'type': 'exothermic',
    },
    'dissolve nacl': {
        'name': 'Dissolving NaCl in Water',
        'equation': 'NaCl(s) -> Na+(aq) + Cl-(aq)',
        'dh': 3.9,
        'ds': 43.4,
        'dg': -9,
        'type': 'endothermic',
    },
    'dissolve ammonium nitrate': {
        'name': 'Dissolving Ammonium Nitrate',
        'equation': 'NH4NO3(s) -> NH4+(aq) + NO3-(aq)',
        'dh': 25.7,
        'ds': 108.7,
        'dg': -6.7,
        'type': 'endothermic',
    },
    'dissolve naoh': {
        'name': 'Dissolving NaOH in Water',
        'equation': 'NaOH(s) -> Na+(aq) + OH-(aq)',
        'dh': -44.5,
        'ds': 18,
        'dg': -49.9,
        'type': 'exothermic',
    },
    'combust hydrogen': {
        'name': 'Combustion of Hydrogen',
        'equation': '2H2 + O2 -> 2H2O',
        'dh': -572,
        'ds': -327,
        'dg': -474,
        'type': 'exothermic',
    },
    'decompose hydrogen peroxide': {
        'name': 'Decomposition of H2O2',
        'equation': '2H2O2 -> 2H2O + O2',
        'dh': -196,
        'ds': -126,
        'dg': -158,
        'type': 'exothermic',
    },
    'rusting of iron': {
        'name': 'Rusting of Iron',
        'equation': '4Fe + 3O2 -> 2Fe2O3',
        'dh': -1648,
        'ds': -548,
        'dg': -1485,
        'type': 'exothermic',
    },
    'contact process': {
        'name': 'Contact Process (SO2 oxidation)',
        'equation': '2SO2 + O2 -> 2SO3',
        'dh': -198,
        'ds': -187,
        'dg': -142,
        'type': 'exothermic',
    },
    'lead acid battery': {
        'name': 'Lead-Acid Battery Discharge',
        'equation': 'Pb + PbO2 + 2H2SO4 -> 2PbSO4 + 2H2O',
        'dh': -350,
        'ds': 62,
        'dg': -368,
        'type': 'exothermic',
    },
    'photosynthesis overall': {
        'name': 'Photosynthesis (overall)',
        'equation': '6CO2 + 6H2O -> C6H12O6 + 6O2',
        'dh': 2803,
        'ds': -260,
        'dg': 2880,
        'type': 'endothermic',
    },
    'cellular respiration': {
        'name': 'Cellular Respiration',
        'equation': 'C6H12O6 + 6O2 -> 6CO2 + 6H2O',
        'dh': -2803,
        'ds': 260,
        'dg': -2880,
        'type': 'exothermic',
    },
}

# Organic compound database
ORGANIC_COMPOUNDS = {
    'methane': {
        'name': 'Methane',
        'formula': 'CH4',
        'group': 'Alkane',
        'uses': 'Fuel, heating, electricity generation',
    },
    'CH4': {
        'name': 'Methane',
        'formula': 'CH4',
        'group': 'Alkane',
        'uses': 'Fuel, heating, electricity generation',
    },
    'ethane': {
        'name': 'Ethane',
        'formula': 'C2H6',
        'group': 'Alkane',
        'uses': 'Fuel, chemical feedstock, plastic production',
    },
    'propane': {
        'name': 'Propane',
        'formula': 'C3H8',
        'group': 'Alkane',
        'uses': 'Fuel, heating, cooking',
    },
    'butane': {
        'name': 'Butane',
        'formula': 'C4H10',
        'group': 'Alkane',
        'uses': 'Fuel, lighter fluid, aerosol propellant',
    },
    'pentane': {
        'name': 'Pentane',
        'formula': 'C5H12',
        'group': 'Alkane',
        'uses': 'Solvent, blowing agent, refrigerant',
    },
    'hexane': {
        'name': 'Hexane',
        'formula': 'C6H14',
        'group': 'Alkane',
        'uses': 'Solvent, extraction, laboratory',
    },
    'octane': {
        'name': 'Octane',
        'formula': 'C8H18',
        'group': 'Alkane',
        'uses': 'Fuel, rating reference for gasoline',
    },
    'ethylene': {
        'name': 'Ethylene (Ethene)',
        'formula': 'C2H4',
        'group': 'Alkene',
        'uses': 'Polymer production, fruit ripening',
    },
    'propylene': {
        'name': 'Propylene (Propene)',
        'formula': 'C3H6',
        'group': 'Alkene',
        'uses': 'Plastic production, fuel',
    },
    'acetylene': {
        'name': 'Acetylene (Ethyne)',
        'formula': 'C2H2',
        'group': 'Alkyne',
        'uses': 'Welding, cutting torches',
    },
    'ethanol': {
        'name': 'Ethanol',
        'formula': 'C2H5OH',
        'group': 'Alcohol',
        'uses': 'Beverage, solvent, fuel, antiseptic',
    },
    'C2H5OH': {
        'name': 'Ethanol',
        'formula': 'C2H5OH',
        'group': 'Alcohol',
        'uses': 'Beverage, solvent, fuel, antiseptic',
    },
    'methanol': {
        'name': 'Methanol',
        'formula': 'CH3OH',
        'group': 'Alcohol',
        'uses': 'Solvent, fuel, antifreeze',
    },
    'CH3OH': {
        'name': 'Methanol',
        'formula': 'CH3OH',
        'group': 'Alcohol',
        'uses': 'Solvent, fuel, antifreeze',
    },
    'isopropanol': {
        'name': 'Isopropanol',
        'formula': 'C3H7OH',
        'group': 'Alcohol',
        'uses': 'Antiseptic, solvent, cleaning agent',
    },
    'acetic acid': {
        'name': 'Acetic Acid',
        'formula': 'CH3COOH',
        'group': 'Carboxylic Acid',
        'uses': 'Vinegar, food additive, solvent',
    },
    'CH3COOH': {
        'name': 'Acetic Acid',
        'formula': 'CH3COOH',
        'group': 'Carboxylic Acid',
        'uses': 'Vinegar, food additive, solvent',
    },
    'formic acid': {
        'name': 'Formic Acid',
        'formula': 'HCOOH',
        'group': 'Carboxylic Acid',
        'uses': 'Leather tanning, rubber production',
    },
    'benzoic acid': {
        'name': 'Benzoic Acid',
        'formula': 'C6H5COOH',
        'group': 'Carboxylic Acid',
        'uses': 'Food preservative, anti-fungal agent',
    },
    'citric acid': {
        'name': 'Citric Acid',
        'formula': 'C6H8O7',
        'group': 'Carboxylic Acid',
        'uses': 'Flavoring, preservative, cleaning agent',
    },
    'glucose': {
        'name': 'Glucose',
        'formula': 'C6H12O6',
        'group': 'Monosaccharide',
        'uses': 'Energy source, food sweetener',
    },
    'C6H12O6': {
        'name': 'Glucose',
        'formula': 'C6H12O6',
        'group': 'Monosaccharide',
        'uses': 'Energy source, food sweetener',
    },
    'fructose': {
        'name': 'Fructose',
        'formula': 'C6H12O6',
        'group': 'Monosaccharide',
        'uses': 'Sweetener, food additive',
    },
    'sucrose': {
        'name': 'Sucrose',
        'formula': 'C12H22O11',
        'group': 'Disaccharide',
        'uses': 'Table sugar, sweetener, preservative',
    },
    'lactose': {
        'name': 'Lactose',
        'formula': 'C12H22O11',
        'group': 'Disaccharide',
        'uses': 'Dairy products, infant formula',
    },
    'starch': {
        'name': 'Starch',
        'formula': '(C6H10O5)n',
        'group': 'Polysaccharide',
        'uses': 'Food thickener, energy storage',
    },
    'cellulose': {
        'name': 'Cellulose',
        'formula': '(C6H10O5)n',
        'group': 'Polysaccharide',
        'uses': 'Paper, textiles, plant structure',
    },
    'acetone': {
        'name': 'Acetone',
        'formula': 'CH3COCH3',
        'group': 'Ketone',
        'uses': 'Solvent, nail polish remover, chemical feedstock',
    },
    'CH3COCH3': {
        'name': 'Acetone',
        'formula': 'CH3COCH3',
        'group': 'Ketone',
        'uses': 'Solvent, nail polish remover, chemical feedstock',
    },
    'acetaldehyde': {
        'name': 'Acetaldehyde',
        'formula': 'CH3CHO',
        'group': 'Aldehyde',
        'uses': 'Chemical feedstock, preservative',
    },
    'formaldehyde': {
        'name': 'Formaldehyde',
        'formula': 'HCHO',
        'group': 'Aldehyde',
        'uses': 'Preservative, disinfectant, plastics',
    },
    'benzene': {
        'name': 'Benzene',
        'formula': 'C6H6',
        'group': 'Aromatic',
        'uses': 'Industrial solvent, plastic production',
    },
    'C6H6': {
        'name': 'Benzene',
        'formula': 'C6H6',
        'group': 'Aromatic',
        'uses': 'Industrial solvent, plastic production',
    },
    'toluene': {
        'name': 'Toluene',
        'formula': 'C6H5CH3',
        'group': 'Aromatic',
        'uses': 'Solvent, paint thinner, octane booster',
    },
    'phenol': {
        'name': 'Phenol',
        'formula': 'C6H5OH',
        'group': 'Aromatic',
        'uses': 'Antiseptic, resin production, disinfectant',
    },
    'aniline': {
        'name': 'Aniline',
        'formula': 'C6H5NH2',
        'group': 'Aromatic Amine',
        'uses': 'Dye production, pharmaceutical synthesis',
    },
    'ethyl acetate': {
        'name': 'Ethyl Acetate',
        'formula': 'CH3COOC2H5',
        'group': 'Ester',
        'uses': 'Solvent, nail polish remover, flavoring',
    },
    'acetic anhydride': {
        'name': 'Acetic Anhydride',
        'formula': '(CH3CO)2O',
        'group': 'Anhydride',
        'uses': 'Aspirin production, cellulose acetate',
    },
    'methylamine': {
        'name': 'Methylamine',
        'formula': 'CH3NH2',
        'group': 'Amine',
        'uses': 'Chemical feedstock, fish processing',
    },
    'ethylenediamine': {
        'name': 'Ethylenediamine',
        'formula': 'C2H8N2',
        'group': 'Diamine',
        'uses': 'Epoxy hardener, chelating agent',
    },
    'dimethyl ether': {
        'name': 'Dimethyl Ether',
        'formula': 'CH3OCH3',
        'group': 'Ether',
        'uses': 'Aerosol propellant, refrigerant, fuel',
    },
    'methyl ethyl ketone': {
        'name': 'Methyl Ethyl Ketone (MEK)',
        'formula': 'C4H8O',
        'group': 'Ketone',
        'uses': 'Industrial solvent, paint remover',
    },
}


def parse_formula(formula):
    if not formula:
        return {}
    tokens = _tokenize(formula)
    return _parse_tokens(tokens, 0, len(tokens))


def _tokenize(f):
    tokens = []
    i = 0
    while i < len(f):
        c = f[i]
        if c == '(' or c == ')':
            tokens.append(c)
            i += 1
        elif c.isupper():
            j = i + 1
            while j < len(f) and f[j].islower():
                j += 1
            elem = f[i:j]
            i = j
            num = ''
            while i < len(f) and f[i].isdigit():
                num += f[i]
                i += 1
            tokens.append((elem, int(num) if num else 1))
        else:
            i += 1
    return tokens


def _parse_tokens(tokens, start, end):
    result = {}
    i = start
    while i < end:
        t = tokens[i]
        if t == '(':
            depth = 1
            j = i + 1
            while j < end:
                if tokens[j] == '(':
                    depth += 1
                elif tokens[j] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            inner = _parse_tokens(tokens, i + 1, j)
            multiplier = 1
            if j + 1 < end and isinstance(tokens[j + 1], tuple):
                multiplier = tokens[j + 1][1]
                j += 1
            for elem, count in inner.items():
                result[elem] = result.get(elem, 0) + count * multiplier
            i = j + 1
        elif isinstance(t, tuple):
            elem, count = t
            result[elem] = result.get(elem, 0) + count
            i += 1
        else:
            i += 1
    return result


def molar_mass(formula):
    comp = parse_formula(formula)
    total = 0.0
    for elem, count in comp.items():
        if elem not in ELEMENTS:
            return None
        total += ELEMENTS[elem][2] * count
    return total


def element_info(symbol):
    symbol = str(symbol).strip()
    if len(symbol) > 0:
        symbol = symbol[0].upper() + symbol[1:].lower()
    if symbol not in ELEMENTS:
        return None
    num, name, mass, cat = ELEMENTS[symbol]
    lines = [
        f'{name} ({symbol})',
        f'  Number: {num}',
        f'  Mass:   {mass}',
        f'  Type:   {CATEGORY_NAMES.get(cat, "?")}',
    ]
    if symbol in OXIDATION:
        ox = ', '.join(str(o) for o in OXIDATION[symbol])
        lines.append(f'  Oxidation: {ox}')
    shell = electron_config_short(num)
    if shell:
        lines.append(f'  Electrons: {shell}')
    return lines


def electron_config_short(num):
    if num <= 0:
        return ''
    shells = []
    remaining = num
    for cap in SHELL_CAPACITY:
        if remaining <= 0:
            break
        n = min(remaining, cap)
        shells.append(n)
        remaining -= n
    if remaining > 0:
        shells.append(remaining)
    return ','.join(str(s) for s in shells)


def electron_config_full(num):
    if num <= 0:
        return ''
    order = [
        (1, '1s'), (2, '2s'), (2, '2p'), (3, '3s'), (3, '3p'),
        (4, '3d'), (4, '4s'), (4, '4p'), (5, '4d'), (5, '5s'),
        (5, '5p'), (6, '4f'), (6, '5d'), (6, '6s'), (6, '6p'),
        (7, '5f'), (7, '6d'), (7, '7s'),
    ]
    maxe = [2, 2, 6, 2, 6, 10, 2, 6, 10, 2, 6, 14, 10, 2, 6, 14, 10, 2]
    remaining = num
    parts = []
    for i, (max_e, label) in enumerate(order):
        if remaining <= 0:
            break
        n = min(remaining, max_e[i])
        if n > 0:
            parts.append(f'{label}{n}')
        remaining -= n
    return ' '.join(parts)


def calc_molarity(moles=None, volume_l=None, mass=None, molar_mass_val=None, volume_ml=None):
    if volume_ml is not None and volume_l is None:
        volume_l = volume_ml / 1000.0
    if mass is not None and molar_mass_val is not None:
        moles = mass / molar_mass_val
    if moles is None or volume_l is None or volume_l == 0:
        return None
    return moles / volume_l


def calc_dilution(c1=None, v1=None, c2=None, v2=None):
    known = sum(1 for x in [c1, v1, c2, v2] if x is not None)
    if known < 3:
        return None
    if c1 is None:
        return c2 * v2 / v1
    if v1 is None:
        return c2 * v2 / c1
    if c2 is None:
        return c1 * v1 / v2
    if v2 is None:
        return c1 * v1 / c2
    return None


def calc_ph(conc_h=None, conc_oh=None, poh=None):
    if conc_h is not None and conc_h > 0:
        return -math.log10(conc_h)
    if conc_oh is not None and conc_oh > 0:
        ph = 14 + math.log10(conc_oh)
        return ph
    if poh is not None:
        return 14 - poh
    return None


def calc_gas_law(p=None, v=None, n=None, t=None, r=0.08206):
    known = sum(1 for x in [p, v, n, t] if x is not None)
    if known < 3:
        return None
    if p is None:
        return n * r * t / v
    if v is None:
        return n * r * t / p
    if n is None:
        return p * v / (r * t)
    if t is None:
        return p * v / (n * r)
    return None


def _parse_side(side_str):
    terms = []
    for term in side_str.split('+'):
        term = term.strip()
        if not term:
            continue
        coeff = 1
        formula = term
        if term[0].isdigit():
            i = 0
            while i < len(term) and term[i].isdigit():
                i += 1
            coeff = int(term[:i])
            formula = term[i:].strip()
        terms.append((coeff, formula))
    return terms


def _get_atom_counts(terms):
    counts = {}
    for coeff, formula in terms:
        comp = parse_formula(formula)
        for elem, n in comp.items():
            counts[elem] = counts.get(elem, 0) + coeff * n
    return counts


def balance_equation(equation_str):
    eq = equation_str.strip()
    eq = eq.replace('==', '->').replace('=', '->').replace('\u2192', '->')

    # Normalize whitespace around ->
    eq = eq.replace('->', ' -> ')

    # Check known equations
    for sep in [' -> ']:
        if sep in eq:
            parts = eq.split(sep)
            if len(parts) == 2:
                left_raw = parts[0].strip()
                right_raw = parts[1].strip()

                # Check COMMON_EQUATIONS with various normalizations
                for key in COMMON_EQUATIONS:
                    if left_raw == key.split(' -> ')[0].strip() and right_raw == key.split(' -> ')[1].strip():
                        return COMMON_EQUATIONS[key]

                # Try normalized version of input
                norm_input = left_raw + ' -> ' + right_raw
                if norm_input in COMMON_EQUATIONS:
                    return COMMON_EQUATIONS[norm_input]

                # Check if it is already balanced
                left_terms = _parse_side(left_raw)
                right_terms = _parse_side(right_raw)

                if not left_terms or not right_terms:
                    return None

                left_atoms = _get_atom_counts(left_terms)
                right_atoms = _get_atom_counts(right_terms)

                if left_atoms == right_atoms:
                    return eq.strip()

                # Build display of what we parsed
                left_display = ' + '.join(
                    (str(c) if c > 1 else '') + f for c, f in left_terms
                )
                right_display = ' + '.join(
                    (str(c) if c > 1 else '') + f for c, f in right_terms
                )
                return left_display + ' -> ' + right_display

    return None


def thermo_info(reaction_name):
    key = reaction_name.strip().lower()
    if key not in THERMO_REACTIONS:
        return None
    rxn = THERMO_REACTIONS[key]
    lines = [
        rxn['name'],
        f'  Equation:  {rxn["equation"]}',
        f'  dH:        {rxn["dh"]} kJ/mol',
        f'  dS:        {rxn["ds"]} J/(mol*K)',
        f'  dG:        {rxn["dg"]} kJ/mol',
        f'  Type:      {rxn["type"]}',
    ]
    return lines


def organic_info(compound):
    key = compound.strip()
    info = ORGANIC_COMPOUNDS.get(key)
    if info is None:
        info = ORGANIC_COMPOUNDS.get(key.lower())
    if info is None:
        return None
    lines = [
        info['name'],
        f'  Formula:   {info["formula"]}',
        f'  Group:     {info["group"]}',
        f'  Uses:      {info["uses"]}',
    ]
    return lines


def all_elements_list():
    lines = []
    period = 1
    prev_num = 0

    for num in range(1, 99):
        sym = None
        for s, data in ELEMENTS.items():
            if data[0] == num:
                sym = s
                break
        if sym is None:
            continue

        # Determine period from electron config
        name = ELEMENTS[sym][1]
        mass = ELEMENTS[sym][2]
        cat = ELEMENTS[sym][3]
        cat_name = CATEGORY_NAMES.get(cat, '?')

        if num in (1,):
            period_label = 'Period 1'
        elif num <= 2:
            period_label = 'Period 1'
        elif num <= 10:
            period_label = 'Period 2'
        elif num <= 18:
            period_label = 'Period 3'
        elif num <= 36:
            period_label = 'Period 4'
        elif num <= 54:
            period_label = 'Period 5'
        elif num <= 86:
            period_label = 'Period 6'
        else:
            period_label = 'Period 7'

        if period_label != period:
            if lines:
                lines.append('')
            lines.append(f'--- {period_label} ---')
            period = period_label

        lines.append(f'  {sym:>3} {num:>3}  {name:<16} {mass:>8.3f}  {cat_name}')

    return lines


def stoich_mass(formula, moles):
    mm = molar_mass(formula)
    if mm is None:
        return None
    return moles * mm


def stoich_moles(mass, formula):
    mm = molar_mass(formula)
    if mm is None or mm == 0:
        return None
    return mass / mm


def percent_composition(formula):
    comp = parse_formula(formula)
    if not comp:
        return None
    total = 0.0
    for elem, count in comp.items():
        if elem not in ELEMENTS:
            return None
        total += ELEMENTS[elem][2] * count
    if total == 0:
        return None
    result = []
    for elem, count in sorted(comp.items()):
        mass = ELEMENTS[elem][2] * count
        pct = mass / total * 100
        result.append((elem, pct))
    return result


def empirical_formula(mass_dict):
    moles = {}
    for elem, mass in mass_dict.items():
        if elem not in ELEMENTS:
            return None
        moles[elem] = mass / ELEMENTS[elem][2]
    if not moles:
        return None
    min_mol = min(moles.values())
    ratios = {}
    for elem, mol in moles.items():
        r = mol / min_mol
        ratios[elem] = round(r)
    parts = []
    for elem in sorted(ratios.keys()):
        count = ratios[elem]
        parts.append(elem + (str(count) if count > 1 else ''))
    return ''.join(parts)


def grams_to_moles(mass, formula):
    mm = molar_mass(formula)
    if mm is None or mm == 0:
        return None
    return mass / mm


def moles_to_grams(moles, formula):
    mm = molar_mass(formula)
    if mm is None:
        return None
    return moles * mm


# ── Additional Gas Laws ──────────────────────────────

def dalton_law(*partial_pressures):
    """Dalton's Law: P_total = P1 + P2 + ..."""
    return sum(partial_pressures)


def graham_rate(m1, m2):
    """Graham's Law: rate1/rate2 = sqrt(M2/M1)
    Returns ratio of effusion rates."""
    if m1 <= 0 or m2 <= 0:
        return None
    return (m2 / m1) ** 0.5


def charles_law(v1, t1, t2=None, v2=None):
    """Charles's Law: V1/T1 = V2/T2 (temperatures in Kelvin)."""
    known = sum(1 for x in [v1, t1, t2, v2] if x is not None)
    if known < 3:
        return None
    if v2 is None:
        return v1 * t2 / t1
    if t2 is None:
        return v2 * t1 / v1
    if v1 is None:
        return v2 * t1 / t2
    if t1 is None:
        return v1 * t2 / v2
    return None


def combined_gas_law(p1=None, v1=None, t1=None, p2=None, v2=None, t2=None):
    """Combined Gas Law: P1*V1/T1 = P2*V2/T2"""
    vals = [p1, v1, t1, p2, v2, t2]
    if sum(1 for x in vals if x is not None) < 5:
        return None
    if p1 is None:
        return p2 * v2 * t1 / (v1 * t2)
    if v1 is None:
        return p2 * v2 * t1 / (p1 * t2)
    if t1 is None:
        return p1 * v1 * t2 / (p2 * v2)
    if p2 is None:
        return p1 * v1 * t2 / (v2 * t1)
    if v2 is None:
        return p1 * v1 * t2 / (p2 * t1)
    if t2 is None:
        return p2 * v2 * t1 / (p1 * v1)
    return None


def ideal_gas_solve(p=None, v=None, n=None, t=None):
    """Ideal Gas Law solver (PV=nRT, R=0.08206).
    Provide 3 of 4, get the 4th."""
    return calc_gas_law(p=p, v=v, n=n, t=t)


# ── Redox Reactions ──────────────────────────────────

REDOX_REACTIONS = {
    'zn_cu': {
        'name': 'Zinc-Copper Cell',
        'oxidation': 'Zn -> Zn2+ + 2e-',
        'reduction': 'Cu2+ + 2e- -> Cu',
        'E0': 1.10,
        'description': 'Zn is oxidized, Cu2+ is reduced',
    },
    'fe_cu': {
        'name': 'Iron-Copper',
        'oxidation': 'Fe -> Fe2+ + 2e-',
        'reduction': 'Cu2+ + 2e- -> Cu',
        'E0': 0.78,
        'description': 'Fe is oxidized, Cu2+ is reduced',
    },
    'mg_hcl': {
        'name': 'Magnesium in HCl',
        'oxidation': 'Mg -> Mg2+ + 2e-',
        'reduction': '2H+ + 2e- -> H2',
        'E0': 1.93,
        'description': 'Mg is oxidized, H+ is reduced',
    },
    'h2_o2': {
        'name': 'Hydrogen Combustion',
        'oxidation': 'H2 -> 2H+ + 2e-',
        'reduction': 'O2 + 4H+ + 4e- -> 2H2O',
        'E0': 1.23,
        'description': 'H2 is oxidized, O2 is reduced',
    },
    'fe_rust': {
        'name': 'Iron Rusting',
        'oxidation': 'Fe -> Fe2+ + 2e-',
        'reduction': 'O2 + 2H2O + 4e- -> 4OH-',
        'E0': 1.67,
        'description': 'Fe is oxidized, O2 is reduced',
    },
}


def redox_info(reaction_name):
    """Return redox reaction details."""
    key = reaction_name.strip().lower()
    if key not in REDOX_REACTIONS:
        names = ', '.join(REDOX_REACTIONS.keys())
        return [f'Unknown reaction', f'Available: {names}']
    rxn = REDOX_REACTIONS[key]
    return [
        rxn['name'],
        f'  Oxidation: {rxn["oxidation"]}',
        f'  Reduction: {rxn["reduction"]}',
        f'  E0: {rxn["E0"]:.2f} V',
        f'  {rxn["description"]}',
    ]


# ── Periodic Trends ──────────────────────────────────

# Electronegativity (Pauling scale) for common elements
ELECTRONEGATIVITY = {
    'H': 2.20, 'Li': 0.98, 'Be': 1.57, 'B': 2.04, 'C': 2.55,
    'N': 3.04, 'O': 3.44, 'F': 3.98, 'Na': 0.93, 'Mg': 1.31,
    'Al': 1.61, 'Si': 1.90, 'P': 2.19, 'S': 2.58, 'Cl': 3.16,
    'K': 0.82, 'Ca': 1.00, 'Fe': 1.83, 'Cu': 1.90, 'Zn': 1.65,
    'Br': 2.96, 'Ag': 1.93, 'I': 2.66, 'Au': 2.54,
}

# First ionization energy (kJ/mol) for common elements
IONIZATION_ENERGY = {
    'H': 1312, 'Li': 520, 'Be': 899, 'B': 801, 'C': 1086,
    'N': 1402, 'O': 1314, 'F': 1681, 'Na': 496, 'Mg': 738,
    'Al': 578, 'Si': 787, 'P': 1012, 'S': 1000, 'Cl': 1251,
    'K': 419, 'Ca': 590, 'Fe': 762, 'Cu': 745, 'Zn': 906,
    'Br': 1140, 'Ag': 731, 'I': 1008, 'Au': 890,
}

# Atomic radius (pm) for common elements
ATOMIC_RADIUS = {
    'H': 53, 'Li': 167, 'Be': 112, 'B': 87, 'C': 67,
    'N': 56, 'O': 48, 'F': 42, 'Na': 190, 'Mg': 145,
    'Al': 118, 'Si': 111, 'P': 98, 'S': 88, 'Cl': 79,
    'K': 243, 'Ca': 194, 'Fe': 126, 'Cu': 128, 'Zn': 134,
    'Br': 94, 'Ag': 144, 'I': 115, 'Au': 136,
}


def periodic_trend(symbol):
    """Show periodic trends for an element."""
    symbol = str(symbol).strip()
    if len(symbol) > 0:
        symbol = symbol[0].upper() + symbol[1:].lower()
    if symbol not in ELEMENTS:
        return [f'Unknown element: {symbol}']
    num, name, mass, cat = ELEMENTS[symbol]
    lines = [f'{name} ({symbol}) - Z={num}']
    if symbol in ELECTRONEGATIVITY:
        en = ELECTRONEGATIVITY[symbol]
        lines.append(f'  Electronegativity: {en:.2f}')
    if symbol in IONIZATION_ENERGY:
        ie = IONIZATION_ENERGY[symbol]
        lines.append(f'  1st Ionization: {ie} kJ/mol')
    if symbol in ATOMIC_RADIUS:
        ar = ATOMIC_RADIUS[symbol]
        lines.append(f'  Atomic Radius: {ar} pm')
    if len(lines) == 1:
        lines.append('  No trend data available')
    return lines


def trend_comparison(element_list):
    """Compare periodic trends across elements."""
    lines = ['=== Trend Comparison ===']
    lines.append(f'{"El":>3} {"EN":>5} {"IE":>6} {"Rad":>5}')
    lines.append('-' * 22)
    for sym in element_list:
        sym = sym.strip()
        if len(sym) > 0:
            sym = sym[0].upper() + sym[1:].lower()
        if sym not in ELEMENTS:
            lines.append(f'{sym:>3}  ?')
            continue
        en = ELECTRONEGATIVITY.get(sym, 0)
        ie = IONIZATION_ENERGY.get(sym, 0)
        ar = ATOMIC_RADIUS.get(sym, 0)
        lines.append(f'{sym:>3} {en:>5.2f} {ie:>6} {ar:>5}')
    return lines


# ── Bonding & Lewis Structures ───────────────────────

# Valence electrons
VALENCE = {
    'H': 1, 'He': 2, 'Li': 1, 'Be': 2, 'B': 3, 'C': 4,
    'N': 5, 'O': 6, 'F': 7, 'Ne': 8, 'Na': 1, 'Mg': 2,
    'Al': 3, 'Si': 4, 'P': 5, 'S': 6, 'Cl': 7, 'Ar': 8,
    'K': 1, 'Ca': 2, 'Fe': 2, 'Cu': 1, 'Zn': 2, 'Br': 7, 'I': 7,
}


def valence_electrons(symbol):
    """Get valence electrons for an element."""
    symbol = str(symbol).strip()
    if len(symbol) > 0:
        symbol = symbol[0].upper() + symbol[1:].lower()
    if symbol in VALENCE:
        return VALENCE[symbol]
    if symbol in ELEMENTS:
        num = ELEMENTS[symbol][0]
        if num <= 2:
            return num
        elif num <= 10:
            return num - 2
        elif num <= 18:
            return num - 10
        elif num <= 36:
            return num - 18
        elif num <= 54:
            return num - 36
        elif num <= 86:
            return num - 54
        else:
            return num - 86
    return None


def lewis_dots(symbol):
    """Generate Lewis dot notation for an element."""
    v = valence_electrons(symbol)
    if v is None:
        return [f'Unknown element: {symbol}']
    dots = '.' * v
    return [
        f'{symbol}: {dots}',
        f'Valence: {v}',
        f'Needs: {max(0, 8 - v)} e- for octet',
    ]


def bond_type(elem1, elem2):
    """Determine bond type between two elements."""
    en1 = ELECTRONEGATIVITY.get(elem1)
    en2 = ELECTRONEGATIVITY.get(elem2)
    if en1 is None or en2 is None:
        return [f'Unknown element(s)']
    diff = abs(en1 - en2)
    if diff < 0.5:
        btype = 'Nonpolar Covalent'
    elif diff < 1.7:
        btype = 'Polar Covalent'
    else:
        btype = 'Ionic'
    return [
        f'{elem1}-{elem2} Bond',
        f'  EN difference: {diff:.2f}',
        f'  Type: {btype}',
        f'  {elem1}: {en1:.2f}, {elem2}: {en2:.2f}',
    ]


# ── Titration Calculator ─────────────────────────────

def titration_calc(c_acid=None, v_acid=None, c_base=None, v_base=None, n_ratio=1):
    """Titration calculator: C1*V1/n1 = C2*V2/n2
    n_ratio = moles acid / moles base in balanced equation.
    Provide 3 of 4 values."""
    vals = [c_acid, v_acid, c_base, v_base]
    if sum(1 for x in vals if x is not None) < 3:
        return None
    if c_acid is None:
        return c_base * v_base * n_ratio / v_acid
    if v_acid is None:
        return c_base * v_base * n_ratio / c_acid
    if c_base is None:
        return c_acid * v_acid / (v_base * n_ratio)
    if v_base is None:
        return c_acid * v_acid / (c_base * n_ratio)
    return None


def titration_ph_at(equivalence_vol, current_vol, c_acid, c_base, n_ratio=1):
    """Estimate pH at a given volume during strong acid-strong base titration."""
    if current_vol <= 0:
        return 0
    if current_vol < equivalence_vol:
        excess_h = (c_acid * equivalence_vol - c_base * current_vol) / (equivalence_vol + current_vol)
        if excess_h > 0:
            return -math.log10(excess_h)
        return 7.0
    elif current_vol > equivalence_vol:
        excess_oh = (c_base * current_vol - c_acid * equivalence_vol) / (equivalence_vol + current_vol)
        if excess_oh > 0:
            poh = -math.log10(excess_oh)
            return 14 - poh
        return 7.0
    return 7.0
