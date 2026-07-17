"""Biology Engine for Espelt32 MicroPython.
DNA/RNA tools, amino acids, cell biology, genetics,
ecology, taxonomy, anatomy, and body systems.
All display functions return list[str] capped at ~38 chars per line.
"""

# ── DNA / RNA ────────────────────────────────────────

_COMP_MAP = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C',
             'a': 't', 't': 'a', 'c': 'g', 'g': 'c'}


def complement(seq):
    """A<->T, C<->G."""
    return ''.join(_COMP_MAP.get(c, c) for c in seq)


def reverse_complement(seq):
    c = complement(seq)
    return ''.join(c[i] for i in range(len(c) - 1, -1, -1))


def transcribe(seq):
    """DNA -> mRNA (T->A, A->U)."""
    return seq.replace("T", "A").replace("A", "U")


_CODON_TABLE = {
    "UUU": "Phe", "UUC": "Phe", "UUA": "Leu", "UUG": "Leu",
    "CUU": "Leu", "CUC": "Leu", "CUA": "Leu", "CUG": "Leu",
    "AUU": "Ile", "AUC": "Ile", "AUA": "Ile", "AUG": "Met",
    "GUU": "Val", "GUC": "Val", "GUA": "Val", "GUG": "Val",
    "UCU": "Ser", "UCC": "Ser", "UCA": "Ser", "UCG": "Ser",
    "CCU": "Pro", "CCC": "Pro", "CCA": "Pro", "CCG": "Pro",
    "ACU": "Thr", "ACC": "Thr", "ACA": "Thr", "ACG": "Thr",
    "GCU": "Ala", "GCC": "Ala", "GCA": "Ala", "GCG": "Ala",
    "UAU": "Tyr", "UAC": "Tyr", "UAA": "STOP", "UAG": "STOP",
    "CAU": "His", "CAC": "His", "CAA": "Gln", "CAG": "Gln",
    "AAU": "Asn", "AAC": "Asn", "AAA": "Lys", "AAG": "Lys",
    "GAU": "Asp", "GAC": "Asp", "GAA": "Glu", "GAG": "Glu",
    "UGU": "Cys", "UGC": "Cys", "UGA": "STOP", "UGG": "Trp",
    "CGU": "Arg", "CGC": "Arg", "CGA": "Arg", "CGG": "Arg",
    "AGU": "Ser", "AGC": "Ser", "AGA": "Arg", "AGG": "Arg",
    "GGU": "Gly", "GGC": "Gly", "GGA": "Gly", "GGG": "Gly",
}

_ABBREV_TO_1 = {
    "Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C",
    "Glu": "E", "Gln": "Q", "Gly": "G", "His": "H", "Ile": "I",
    "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P",
    "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V",
}


def translate(mRNA):
    """mRNA codons -> 3-letter amino acid list."""
    protein = []
    for i in range(0, len(mRNA) - 2, 3):
        codon = mRNA[i:i + 3].upper()
        aa = _CODON_TABLE.get(codon, "???")
        if aa == "STOP":
            break
        protein.append(aa)
    return protein


# ── Amino Acid Data ──────────────────────────────────

# (one_letter, full_name, mol_weight, polarity)
_AA_DATA = {
    "Ala": ("A", "Alanine",       89.1, "nonpolar"),
    "Arg": ("R", "Arginine",     174.2, "positive"),
    "Asn": ("N", "Asparagine",   132.1, "polar"),
    "Asp": ("D", "AsparticAcid", 133.1, "negative"),
    "Cys": ("C", "Cysteine",     121.2, "special"),
    "Glu": ("E", "GlutamicAcid", 147.1, "negative"),
    "Gln": ("Q", "Glutamine",    146.1, "polar"),
    "Gly": ("G", "Glycine",       75.0, "nonpolar"),
    "His": ("H", "Histidine",    155.2, "positive"),
    "Ile": ("I", "Isoleucine",   131.2, "nonpolar"),
    "Leu": ("L", "Leucine",      131.2, "nonpolar"),
    "Lys": ("K", "Lysine",       146.2, "positive"),
    "Met": ("M", "Methionine",   149.2, "nonpolar"),
    "Phe": ("F", "Phenylalanine",165.2, "nonpolar"),
    "Pro": ("P", "Proline",      115.1, "nonpolar"),
    "Ser": ("S", "Serine",       105.1, "polar"),
    "Thr": ("T", "Threonine",    119.1, "polar"),
    "Trp": ("W", "Tryptophan",   204.2, "nonpolar"),
    "Tyr": ("Y", "Tyrosine",     181.2, "polar"),
    "Val": ("V", "Valine",       117.1, "nonpolar"),
}

AA_LIST = list(_AA_DATA.keys())


def amino_info(three_letter):
    """Return display lines for an amino acid."""
    d = _AA_DATA.get(three_letter)
    if not d:
        return [f"Unknown: {three_letter}"]
    one, name, mw, pol = d
    return [
        f"{name} ({one})",
        f"3-Letter: {three_letter}",
        f"MW: {mw:.1f} g/mol",
        f"Polarity: {pol}",
    ]


def amino_by_polarity(pol_filter):
    """List amino acids matching polarity."""
    out = []
    for aa in AA_LIST:
        if _AA_DATA[aa][3] == pol_filter:
            out.append(aa)
    return out


# ── Cell Biology ─────────────────────────────────────

# (function, size_um, found_in)
ORGANELLES = {
    "Nucleus":      ("Stores DNA",            "5-10",   "both"),
    "Mitochondria": ("ATP production",        "1-10",   "both"),
    "Ribosome":     ("Protein synthesis",     "0.02-0.03","both"),
    "ER":           ("Transport & lipid synth","1-5",   "both"),
    "Golgi":        ("Protein modification",  "1-3",     "both"),
    "Lysosome":     ("Digestion",             "0.1-1.2","animal"),
    "Vacuole":      ("Storage, turgor",       "1-100",   "plant"),
    "Chloroplast":  ("Photosynthesis",        "3-6",     "plant"),
    "Cell Wall":    ("Structural support",    "varies",  "plant"),
    "Peroxisome":   ("Fatty acid oxidation",  "0.2-1.5","both"),
    "Centriole":    ("Cell division",         "0.2-0.5","animal"),
    "Amyloplast":   ("Starch storage",        "1-10",   "plant"),
}

CELL_TYPES = {
    "prokaryote": [
        "No nucleus or membrane",
        "Circular DNA (nucleoid)",
        "Ribosomes (70S)",
        "No membrane organelles",
        "Cell wall (peptidoglycan)",
        "Examples: bacteria, archaea",
    ],
    "eukaryote": [
        "True nucleus with membrane",
        "Linear chromosomes",
        "Ribosomes (80S)",
        "Membrane-bound organelles",
        "DNA + histones",
        "Examples: animals, plants,",
        "  fungi, protists",
    ],
}


def organelle_info(name):
    d = ORGANELLES.get(name)
    if not d:
        return [f"Unknown: {name}"]
    func, size, where = d
    return [
        name,
        f"Function: {func}",
        f"Size: {size} um",
        f"Found in: {where}",
    ]


# ── Genetics ─────────────────────────────────────────

# Common dominant/recessive trait pairs
TRAITS = {
    "Seed shape":     ("Round",  "Wrinkled"),
    "Seed color":     ("Yellow", "Green"),
    "Flower color":   ("Purple", "White"),
    "Plant height":   ("Tall",   "Dwarf"),
    "Pod shape":      ("Inflated","Constricted"),
    "Pod color":      ("Green",  "Yellow"),
    "Eye color":      ("Brown",  "Blue"),
    "Hair type":      ("Curly",  "Straight"),
    "Earlobes":       ("Free",   "Attached"),
    "Tongue roll":    ("Can",    "Cannot"),
}


def punnett_1trait(p1, p2):
    """1-trait Punnett square.
    p1, p2 are genotype strings like 'Aa'."""
    g1, g2 = list(p1[:2].upper())
    g3, g4 = list(p2[:2].upper())
    combos = [(g1, g3), (g1, g4), (g2, g3), (g2, g4)]
    out = [f"  | {g3}   {g4}", "-----------"]
    out.append(f"{g1} | {g1+g3}  {g1+g4}")
    out.append(f"{g2} | {g2+g3}  {g2+g4}")
    dom = sum(1 for a, b in combos if a.isupper() or b.isupper())
    rec = 4 - dom
    out.append(f"Dom/Rec: {dom}/{rec}")
    return out


def punnett_2trait(p1a, p1b, p2a, p2b):
    """2-trait dihybrid cross.
    Each parent allele pair for two genes."""
    a1, a2 = list(p1a[:2].upper())
    b1, b2 = list(p1b[:2].upper())
    c1, c2 = list(p2a[:2].upper())
    d1, d2 = list(p2b[:2].upper())
    out = ["Dihybrid: AaBb x AaBb"]
    ratios = {"9:3:3:1": "phenotype"}
    for p in ["A", "a"]:
        for q in ["B", "b"]:
            if p.isupper() or q.isupper():
                continue
    out.append("Expected 9:3:3:1 ratio")
    out.append("A_B_:A_bb:aaB_:aabb")
    return out


def hardy_weinberg(q, pop_size=1000):
    """Calculate HW equilibrium from recessive allele freq."""
    if q < 0 or q > 1:
        return ["q must be 0-1"]
    p = 1 - q
    p2 = p * p
    pq2 = 2 * p * q
    q2 = q * q
    return [
        "Hardy-Weinberg Eq.",
        f"p (dom) = {p:.3f}",
        f"q (rec) = {q:.3f}",
        f"p2 (AA)  = {p2:.3f}  ~{int(p2*pop_size)}",
        f"2pq (Aa) = {pq2:.3f}  ~{int(pq2*pop_size)}",
        f"q2 (aa)  = {q2:.3f}  ~{int(q2*pop_size)}",
    ]


# ── Ecology ──────────────────────────────────────────

TROPHIC_LEVELS = [
    ("1. Producer",      "Autotrophs (plants, algae)"),
    ("2. Primary Cons.", "Herbivores"),
    ("3. Secondary Cons","Carnivores (eat herbivores)"),
    ("4. Tertiary Cons.", "Top carnivores"),
    ("5. Apex Predator", "No natural predators"),
]

# (temp_range, precip_range, vegetation)
BIOMES = {
    "Tropical Rainforest": ("20-30C", "200-1000cm", "Dense broadleaf"),
    "Temperate Forest":    ("5-20C",  "75-150cm",   "Deciduous trees"),
    "Boreal Forest":       ("-5-5C",  "30-85cm",    "Coniferous trees"),
    "Grassland":           ("-5-30C", "25-75cm",    "Grasses, few trees"),
    "Desert":              ("20-45C", "<25cm",      "Succulents, shrubs"),
    "Tundra":              ("-30-10C","15-25cm",     "Mosses, lichens"),
    "Freshwater":          ("0-30C",  "N/A",        "Aquatic plants"),
    "Marine":              ("-2-30C", "N/A",        "Phytoplankton"),
    "Taiga":               ("-10-0C", "30-85cm",    "Conifers"),
    "Savanna": ("20-35C", "50-130cm", "Grass + scattered trees"),
}


def trophic_info():
    out = ["-- Trophic Levels --"]
    for label, desc in TROPHIC_LEVELS:
        out.append(f"{label}: {desc}")
    return out


def biome_info(name):
    d = BIOMES.get(name)
    if not d:
        return [f"Unknown: {name}"]
    return [
        name,
        f"Temp: {d[0]}",
        f"Precip: {d[1]}",
        f"Vegetation: {d[2]}",
    ]


# ── Taxonomy ─────────────────────────────────────────

TAX_RANKS = ["Domain", "Kingdom", "Phylum", "Class",
             "Order", "Family", "Genus", "Species"]

# (Domain, Kingdom, Phylum, Class, Order, Family, Genus, Species)
ORGANISMS = {
    "Human": (
        "Eukarya", "Animalia", "Chordata", "Mammalia",
        "Primates", "Hominidae", "Homo", "H. sapiens",
    ),
    "Dog": (
        "Eukarya", "Animalia", "Chordata", "Mammalia",
        "Carnivora", "Canidae", "Canis", "C. familiaris",
    ),
    "Cat": (
        "Eukarya", "Animalia", "Chordata", "Mammalia",
        "Carnivora", "Felidae", "Felis", "F. catus",
    ),
    "Rice": (
        "Eukarya", "Plantae", "Tracheophyta", "Liliopsida",
        "Poales", "Poaceae", "Oryza", "O. sativa",
    ),
    "E. coli": (
        "Bacteria", "Bacteria", "Pseudomonadota",
        "Gammaproteobacteria", "Enterobacterales",
        "Enterobacteriaceae", "Escherichia", "E. coli",
    ),
    "Yeast": (
        "Eukarya", "Fungi", "Ascomycota", "Saccharomycetes",
        "Saccharomycetales", "Saccharomycetaceae",
        "Saccharomyces", "S. cerevisiae",
    ),
    "Fruit Fly": (
        "Eukarya", "Animalia", "Arthropoda", "Insecta",
        "Diptera", "Drosophilidae", "Drosophila", "D. melanogaster",
    ),
    "Mouse": (
        "Eukarya", "Animalia", "Chordata", "Mammalia",
        "Rodentia", "Muridae", "Mus", "M. musculus",
    ),
    "Oak Tree": (
        "Eukarya", "Plantae", "Tracheophyta", "Magnoliopsida",
        "Fagales", "Fagaceae", "Quercus", "Q. robur",
    ),
    "Mushroom": (
        "Eukarya", "Fungi", "Basidiomycota", "Agaricomycetes",
        "Agaricales", "Agaricaceae", "Agaricus", "A. bisporus",
    ),
}


def taxonomy_info(name):
    t = ORGANISMS.get(name)
    if not t:
        return [f"Unknown: {name}"]
    out = [name]
    for rank, val in zip(TAX_RANKS, t):
        out.append(f"  {rank}: {val}")
    return out


def cell_comparison():
    """Prokaryote vs Eukaryote comparison."""
    lines = ['=== Prokaryote vs Eukaryote ===', '', 'Prokaryote:']
    for item in CELL_TYPES['prokaryote']:
        lines.append(f'  - {item}')
    lines.append('')
    lines.append('Eukaryote:')
    for item in CELL_TYPES['eukaryote']:
        lines.append(f'  - {item}')
    return lines


def codon_lookup(codon):
    """Look up a codon."""
    aa = _CODON_TABLE.get(codon.upper(), '???')
    return f'{codon.upper()} -> {aa}'


# ── Convenience: formatted protein from DNA ──────────

def dna_to_protein(dna):
    """Full pipeline: DNA -> mRNA -> amino acids.
    Returns display lines."""
    mRNA = transcribe(dna.upper())
    aas = translate(mRNA)
    if not aas:
        return ["No protein produced"]
    seq1 = "".join(_ABBREV_TO_1.get(a, "?") for a in aas)
    mw = sum(_AA_DATA[a][2] for a in aas if a in _AA_DATA)
    lines = [f"DNA: {dna}", f"mRNA: {mRNA}"]
    for i in range(0, len(aas), 5):
        chunk = " ".join(aas[i:i + 5])
        lines.append(f"  {chunk}")
    lines.append(f"Length: {len(aas)} aa")
    lines.append(f"MW: {mw:.1f} g/mol")
    lines.append(f"1-Letter: {seq1}")
    return lines


# ── Quick summaries for display ──────────────────────

def dna_complement_display(seq):
    c = complement(seq)
    rc = reverse_complement(seq)
    return [
        "DNA Complement",
        f"Seq:  {seq}",
        f"Comp: {c}",
        f"Rev:  {rc}",
    ]


def transcription_display(dna):
    mRNA = transcribe(dna)
    return [
        "Transcription",
        f"DNA:  {dna}",
        f"mRNA: {mRNA}",
    ]


def translation_display(mRNA):
    aas = translate(mRNA)
    if not aas:
        return ["No protein"]
    lines = ["Translation"]
    for i in range(0, len(aas), 5):
        lines.append(" ".join(aas[i:i + 5]))
    seq1 = "".join(_ABBREV_TO_1.get(a, "?") for a in aas)
    lines.append(f"1-Letter: {seq1}")
    return lines


# ── Anatomy ──────────────────────────────────────────

# (chambers, function, rate, output)
_ORGANS = {
    "heart":   ("4 chambers", "Pumps blood", "~72 bpm", "5L/min"),
    "brain":   ("86B neurons", "Controls body", "Cerebrum/Cerebellum/Brainstem", ""),
    "lung":    ("2 lobes R, 3 L", "Gas exchange", "Alveoli", ""),
    "kidney":  ("Filters blood", "Nephrons", "Produces urine", ""),
    "liver":   ("Detox", "Bile production", "Largest internal organ", ""),
    "stomach": ("Acid pH 1-3", "Pepsin digestion", "", ""),
    "eye":     ("Rods + cones", "Retina", "Low light + color", ""),
}


def anatomy_info(organ):
    """Display key facts about an organ."""
    d = _ORGANS.get(organ.lower())
    if not d:
        organs = ", ".join(sorted(_ORGANS.keys()))
        return [f"Unknown organ", f"Available: {organs}"]
    out = [f"=== {organ.upper()} ==="]
    for item in d:
        if item:
            out.append(f"  - {item}")
    return out


# ── Body Systems ─────────────────────────────────────

# (components, function)
_SYSTEMS = {
    "circulatory":  ("Heart, blood, vessels", "Circulates nutrients/O2"),
    "nervous":      ("Brain, spinal cord, nerves", "Sensory + motor signals"),
    "respiratory":  ("Lungs, trachea, diaphragm", "Gas exchange"),
    "digestive":    ("Mouth to anus, enzymes", "Breaks down food"),
    "excretory":    ("Kidneys, bladder", "Waste removal"),
    "skeletal":     ("206 bones", "Support + protection"),
    "muscular":     ("600+ muscles", "Voluntary + involuntary"),
    "endocrine":    ("Hormones, glands", "Chemical regulation"),
    "immune":       ("WBC, antibodies", "Defense vs pathogens"),
    "reproductive": ("Male/female systems", "Reproduction"),
}


def system_info(system_name):
    """Display info about a body system."""
    d = _SYSTEMS.get(system_name.lower())
    if not d:
        systems = ", ".join(sorted(_SYSTEMS.keys()))
        return [f"Unknown system", f"Available: {systems}"]
    components, function = d
    return [
        f"=== {system_name.upper()} ===",
        f"  Components: {components}",
        f"  Function: {function}",
    ]


# ── DNA Mutations ────────────────────────────────────

MUTATION_TYPES = {
    'point_sub': {
        'name': 'Point Substitution',
        'description': 'Single base replaced by another',
        'effect': 'May cause silent, missense, or nonsense mutation',
    },
    'insertion': {
        'name': 'Insertion',
        'description': 'Extra base(s) added',
        'effect': 'Causes frameshift if not multiple of 3',
    },
    'deletion': {
        'name': 'Deletion',
        'description': 'Base(s) removed',
        'effect': 'Causes frameshift if not multiple of 3',
    },
    'duplication': {
        'name': 'Duplication',
        'description': 'Segment copied',
        'effect': 'Extra protein material',
    },
    'inversion': {
        'name': 'Inversion',
        'description': 'Segment reversed',
        'effect': 'May disrupt gene function',
    },
    'silent': {
        'name': 'Silent Mutation',
        'description': 'Base change with same amino acid',
        'effect': 'No change in protein',
    },
    'missense': {
        'name': 'Missense Mutation',
        'description': 'Base change causes different amino acid',
        'effect': 'Altered protein function',
    },
    'nonsense': {
        'name': 'Nonsense Mutation',
        'description': 'Base change creates STOP codon',
        'effect': 'Truncated protein',
    },
    'frameshift': {
        'name': 'Frameshift Mutation',
        'description': 'Insertion/deletion shifts reading frame',
        'effect': 'Completely different downstream sequence',
    },
}


def mutate_dna(original, mutation_type, position=0, new_base='A', count=1):
    """Apply a mutation to a DNA sequence.
    Returns (mutated_sequence, description)."""
    seq = list(original.upper())
    if mutation_type == 'point_sub':
        if position < len(seq):
            seq[position] = new_base.upper()
            return ''.join(seq), f'Substituted position {position} to {new_base}'
    elif mutation_type == 'insertion':
        for i in range(count):
            seq.insert(position, new_base.upper())
        return ''.join(seq), f'Inserted {count}x {new_base} at position {position}'
    elif mutation_type == 'deletion':
        end = min(position + count, len(seq))
        deleted = seq[position:end]
        del seq[position:end]
        return ''.join(seq), f'Deleted {"".join(deleted)} at position {position}'
    elif mutation_type == 'duplication':
        end = min(position + count, len(seq))
        dup = seq[position:end]
        seq[position:0] = dup
        return ''.join(seq), f'Duplicated {"".join(dup)}'
    elif mutation_type == 'inversion':
        end = min(position + count, len(seq))
        seg = seq[position:end]
        seg.reverse()
        seq[position:end] = seg
        return ''.join(seq), f'Inverted {"".join(seg)}'
    return original, 'No mutation applied'


def detect_mutation(original, mutated):
    """Compare two sequences and identify mutations."""
    if len(original) != len(mutated):
        if len(mutated) > len(original):
            return 'insertion', f'Inserted {len(mutated) - len(original)} bases'
        else:
            return 'deletion', f'Deleted {len(original) - len(mutated)} bases'
    changes = []
    for i, (a, b) in enumerate(zip(original, mutated)):
        if a != b:
            changes.append((i, a, b))
    if not changes:
        return 'none', 'Sequences identical'
    if len(changes) == 1:
        return 'point_sub', f'Position {changes[0][0]}: {changes[0][1]}->{changes[0][2]}'
    return 'multiple', f'{len(changes)} substitutions'


def mutation_effect(original, mutated):
    """Predict the effect of a mutation on protein."""
    orig_mrna = original.replace('T', 'A').replace('A', 'U')
    mut_mrna = mutated.replace('T', 'A').replace('A', 'U')
    orig_protein = translate(orig_mrna)
    mut_protein = translate(mut_mrna)
    if orig_protein == mut_protein:
        return 'Silent', 'No change in amino acid sequence'
    if len(mut_protein) < len(orig_protein):
        return 'Nonsense', f'Protein shortened from {len(orig_protein)} to {len(mut_protein)} aa'
    if len(mut_protein) > len(orig_protein):
        diff = len(mut_protein) - len(orig_protein)
        return 'Frameshift', f'Protein extended by {diff} aa'
    changes = sum(1 for a, b in zip(orig_protein, mut_protein) if a != b)
    return 'Missense', f'{changes} amino acid(s) changed'


# ── Protein Structure ────────────────────────────────

PROTEIN_STRUCTURES = {
    'primary': {
        'name': 'Primary Structure',
        'description': 'Linear sequence of amino acids',
        'bonds': 'Peptide bonds',
        'example': 'Insulin: GIVEQCCTSICSLYQLENYCN',
    },
    'secondary': {
        'name': 'Secondary Structure',
        'description': 'Local folding patterns',
        'bonds': 'Hydrogen bonds (backbone)',
        'example': 'Alpha helix, Beta sheet',
    },
    'tertiary': {
        'name': 'Tertiary Structure',
        'description': '3D folding of single polypeptide',
        'bonds': 'Disulfide, ionic, H-bonds, hydrophobic',
        'example': 'Myoglobin, most enzymes',
    },
    'quaternary': {
        'name': 'Quaternary Structure',
        'description': 'Multiple polypeptide subunits',
        'bonds': 'Same as tertiary, between subunits',
        'example': 'Hemoglobin (4 subunits)',
    },
}

DENATURING_FACTORS = [
    ('Heat', 'Disrupts H-bonds and hydrophobic interactions'),
    ('pH extreme', 'Disrupts ionic and H-bonds'),
    ('Organic solvents', 'Disrupts hydrophobic interactions'),
    ('Detergents', 'Disrupts hydrophobic interactions'),
    ('Heavy metals', 'Disrupts disulfide and ionic bonds'),
    ('Strong acids/bases', 'Disrupts all non-covalent bonds'),
]


def protein_structure_info(level):
    """Display protein structure information."""
    d = PROTEIN_STRUCTURES.get(level.lower())
    if not d:
        levels = ', '.join(PROTEIN_STRUCTURES.keys())
        return [f'Unknown level', f'Available: {levels}']
    return [
        d['name'],
        f'  {d["description"]}',
        f'  Bonds: {d["bonds"]}',
        f'  Example: {d["example"]}',
    ]


def denaturing_info():
    """List denaturing factors."""
    lines = ['=== Denaturation ===']
    for factor, effect in DENATURING_FACTORS:
        lines.append(f'  {factor}: {effect}')
    lines.append('')
    lines.append('Denaturation destroys structure,')
    lines.append('not primary sequence.')
    return lines


def protein_mw(aa_list):
    """Calculate molecular weight of protein from amino acid list."""
    mw = sum(_AA_DATA.get(aa, (0, '', 0, ''))[2] for aa in aa_list)
    # Add water for each peptide bond
    mw += 18.0 * max(0, len(aa_list) - 1)
    return mw


# ── Cell Cycle ───────────────────────────────────────

CELL_CYCLE = {
    'g1': {
        'name': 'G1 Phase (Gap 1)',
        'duration': '~11 hours',
        'events': ['Cell growth', 'Organelle duplication', 'Protein synthesis'],
        'checkpoint': 'G1 checkpoint: size, nutrients, growth factors',
    },
    's': {
        'name': 'S Phase (Synthesis)',
        'duration': '~8 hours',
        'events': ['DNA replication', 'Centrosome duplication'],
        'checkpoint': 'S checkpoint: DNA damage',
    },
    'g2': {
        'name': 'G2 Phase (Gap 2)',
        'duration': '~4 hours',
        'events': ['Final growth', 'Protein synthesis', 'Organelle check'],
        'checkpoint': 'G2 checkpoint: DNA replication complete',
    },
    'm': {
        'name': 'M Phase (Mitosis)',
        'duration': '~1 hour',
        'events': ['Prophase', 'Metaphase', 'Anaphase', 'Telophase', 'Cytokinesis'],
        'checkpoint': 'M checkpoint: spindle attachment',
    },
}

MITOSIS_STAGES = {
    'prophase': {
        'name': 'Prophase',
        'events': ['Chromosomes condense', 'Nuclear envelope breaks down', 'Spindle forms'],
    },
    'metaphase': {
        'name': 'Metaphase',
        'events': ['Chromosomes align at equator', 'Spindle fibers attach to kinetochores'],
    },
    'anaphase': {
        'name': 'Anaphase',
        'events': ['Sister chromatids separate', 'Move to opposite poles'],
    },
    'telophase': {
        'name': 'Telophase',
        'events': ['Nuclear envelope reforms', 'Chromosomes decondense', 'Cytokinesis begins'],
    },
    'cytokinesis': {
        'name': 'Cytokinesis',
        'events': ['Cytoplasm divides', 'Two daughter cells formed'],
    },
}

MEIOSIS_STAGES = {
    'meiosis_i': {
        'name': 'Meiosis I',
        'stages': ['Prophase I', 'Metaphase I', 'Anaphase I', 'Telophase I'],
        'key_events': ['Homologous pairs synapse', 'Crossing over occurs', 'Independent assortment'],
        'result': '2 haploid cells (with sister chromatids)',
    },
    'meiosis_ii': {
        'name': 'Meiosis II',
        'stages': ['Prophase II', 'Metaphase II', 'Anaphase II', 'Telophase II'],
        'key_events': ['Similar to mitosis', 'Sister chromatids separate'],
        'result': '4 haploid cells (gametes)',
    },
}


def cell_cycle_info(phase):
    """Display cell cycle phase information."""
    d = CELL_CYCLE.get(phase.lower())
    if not d:
        phases = ', '.join(CELL_CYCLE.keys())
        return [f'Unknown phase', f'Available: {phases}']
    lines = [d['name'], f'  Duration: {d["duration"]}']
    for event in d['events']:
        lines.append(f'  - {event}')
    lines.append(f'  Checkpoint: {d["checkpoint"]}')
    return lines


def mitosis_info(stage=None):
    """Display mitosis stage information."""
    if stage is None:
        lines = ['=== Mitosis Stages ===']
        for key in ['prophase', 'metaphase', 'anaphase', 'telophase', 'cytokinesis']:
            d = MITOSIS_STAGES[key]
            lines.append(f'  {d["name"]}')
        lines.append('')
        lines.append('Use: mitosis [stage] for details')
        return lines
    d = MITOSIS_STAGES.get(stage.lower())
    if not d:
        stages = ', '.join(MITOSIS_STAGES.keys())
        return [f'Unknown stage', f'Available: {stages}']
    lines = [d['name']]
    for event in d['events']:
        lines.append(f'  - {event}')
    return lines


def meiosis_info(which=None):
    """Display meiosis information."""
    if which is None:
        lines = ['=== Meiosis ===', '', 'Two divisions: Meiosis I and II']
        for key in ['meiosis_i', 'meiosis_ii']:
            d = MEIOSIS_STAGES[key]
            lines.append(f'  {d["name"]}: {d["result"]}')
        lines.append('')
        lines.append('Use: meiosis i or meiosis ii')
        return lines
    key = 'meiosis_i' if which.lower() in ('i', '1', 'meiosis_i') else 'meiosis_ii'
    d = MEIOSIS_STAGES.get(key)
    if not d:
        return ['Unknown division']
    lines = [d['name'], f'  Result: {d["result"]}']
    lines.append('  Stages: ' + ', '.join(d['stages']))
    lines.append('  Key events:')
    for event in d['key_events']:
        lines.append(f'    - {event}')
    return lines


def compare_mitosis_meiosis():
    """Compare mitosis and meiosis."""
    return [
        '=== Mitosis vs Meiosis ===',
        '',
        'Mitosis:',
        '  1 division, 2 daughter cells',
        '  Diploid (2n)',
        '  Identical to parent',
        '  Growth, repair',
        '',
        'Meiosis:',
        '  2 divisions, 4 daughter cells',
        '  Haploid (n)',
        '  Genetic variation',
        '  Gamete production',
        '',
        'Key differences:',
        '  - Crossing over (meiosis only)',
        '  - Independent assortment (meiosis)',
        '  - Synapsis (meiosis I only)',
    ]


# ── Evolution ────────────────────────────────────────

EVOLUTION_CONCEPTS = {
    'natural_selection': {
        'name': 'Natural Selection',
        'description': 'Survival and reproduction of best-adapted individuals',
        'mechanism': 'Variation -> Overproduction -> Competition -> Differential survival',
        'examples': 'Antibiotic resistance, peppered moth, Darwin finches',
    },
    'genetic_drift': {
        'name': 'Genetic Drift',
        'description': 'Random changes in allele frequencies',
        'mechanism': 'Sampling error in small populations',
        'examples': 'Bottleneck effect, founder effect',
    },
    'gene_flow': {
        'name': 'Gene Flow',
        'description': 'Movement of alleles between populations',
        'mechanism': 'Migration and interbreeding',
        'examples': 'Pollen spread, animal migration',
    },
    'mutation': {
        'name': 'Mutation',
        'description': 'Source of new genetic variation',
        'mechanism': 'DNA replication errors, mutagens',
        'examples': 'Sickle cell allele, antibiotic resistance',
    },
    'non_random_mating': {
        'name': 'Non-Random Mating',
        'description': 'Mating based on phenotype/genotype',
        'mechanism': 'Sexual selection, inbreeding',
        'examples': 'Peacock tail, human mate choice',
    },
}

SPECIATION_TYPES = {
    'allopatric': {
        'name': 'Allopatric Speciation',
        'description': 'Geographic isolation causes divergence',
        'example': 'Darwin finches on Galapagos',
    },
    'sympatric': {
        'name': 'Sympatric Speciation',
        'description': 'Speciation without geographic isolation',
        'example': 'Polyploidy in plants',
    },
    'parapatric': {
        'name': 'Parapatric Speciation',
        'description': 'Adjacent populations with limited gene flow',
        'example': 'Grass Anthoxanthum near roads',
    },
    'peripatric': {
        'name': 'Peripatric Speciation',
        'description': 'Small isolated population diverges',
        'example': 'Island endemics',
    },
}


def evolution_info(concept):
    """Display evolution concept information."""
    key = concept.strip().lower().replace(' ', '_')
    d = EVOLUTION_CONCEPTS.get(key)
    if not d:
        concepts = ', '.join(EVOLUTION_CONCEPTS.keys())
        return [f'Unknown concept', f'Available: {concepts}']
    return [
        d['name'],
        f'  {d["description"]}',
        f'  Mechanism: {d["mechanism"]}',
        f'  Examples: {d["examples"]}',
    ]


def speciation_info(spec_type=None):
    """Display speciation type information."""
    if spec_type is None:
        lines = ['=== Speciation Types ===']
        for key, d in SPECIATION_TYPES.items():
            lines.append(f'  {d["name"]}')
        lines.append('')
        lines.append('Use: speciation [type] for details')
        return lines
    key = spec_type.strip().lower()
    d = SPECIATION_TYPES.get(key)
    if not d:
        types = ', '.join(SPECIATION_TYPES.keys())
        return [f'Unknown type', f'Available: {types}']
    return [
        d['name'],
        f'  {d["description"]}',
        f'  Example: {d["example"]}',
    ]


# ── Microbiology & Disease ───────────────────────────

MICROBES = {
    'bacteria': {
        'name': 'Bacteria',
        'type': 'Prokaryote',
        'size': '0.2-10 um',
        'shape': 'Cocci, bacilli, spirilla',
        'reproduction': 'Binary fission',
        'diseases': ['Strep throat', 'Tuberculosis', 'Salmonella', 'E. coli infection'],
        'antibiotics': True,
    },
    'virus': {
        'name': 'Virus',
        'type': 'Acellular',
        'size': '20-300 nm',
        'shape': 'Icosahedral, helical, complex',
        'reproduction': 'Host cell hijacking (lytic/lysogenic)',
        'diseases': ['COVID-19', 'Influenza', 'HIV', 'Common cold'],
        'antibiotics': False,
    },
    'fungus': {
        'name': 'Fungus',
        'type': 'Eukaryote',
        'size': '2-10 um',
        'shape': 'Hyphae, yeast',
        'reproduction': 'Spores, budding',
        'diseases': ['Athlete foot', 'Yeast infection', 'Ringworm'],
        'antibiotics': False,
    },
    'protozoa': {
        'name': 'Protozoa',
        'type': 'Eukaryote',
        'size': '10-50 um',
        'shape': 'Various (amoeba, paramecium)',
        'reproduction': 'Binary fission, multiple fission',
        'diseases': ['Malaria', 'Giardia', 'Amoebic dysentery'],
        'antibiotics': False,
    },
}

IMMUNE_RESPONSE = {
    'innate': {
        'name': 'Innate Immunity',
        'components': ['Skin', 'Mucus', 'Stomach acid', 'Phagocytes', 'Inflammation', 'Fever'],
        'response_time': 'Immediate',
        'specificity': 'Non-specific',
    },
    'adaptive': {
        'name': 'Adaptive Immunity',
        'components': ['B cells (antibodies)', 'T cells (helper, cytotoxic)', 'Memory cells'],
        'response_time': 'Days to weeks (first exposure)',
        'specificity': 'Highly specific',
    },
}


def microbe_info(microbe_type):
    """Display microbiology information."""
    d = MICROBES.get(microbe_type.lower())
    if not d:
        types = ', '.join(MICROBES.keys())
        return [f'Unknown type', f'Available: {types}']
    lines = [
        d['name'],
        f'  Type: {d["type"]}',
        f'  Size: {d["size"]}',
        f'  Shape: {d["shape"]}',
        f'  Reproduction: {d["reproduction"]}',
        f'  Treatable with antibiotics: {"Yes" if d["antibiotics"] else "No"}',
        '  Diseases:',
    ]
    for disease in d['diseases']:
        lines.append(f'    - {disease}')
    return lines


def immune_info(branch=None):
    """Display immune system information."""
    if branch is None:
        lines = ['=== Immune System ===']
        for key, d in IMMUNE_RESPONSE.items():
            lines.append(f'  {d["name"]}')
        lines.append('')
        lines.append('Use: immune [innate/adaptive] for details')
        return lines
    d = IMMUNE_RESPONSE.get(branch.lower())
    if not d:
        branches = ', '.join(IMMUNE_RESPONSE.keys())
        return [f'Unknown branch', f'Available: {branches}']
    lines = [d['name'], f'  Response time: {d["response_time"]}', f'  Specificity: {d["specificity"]}', '  Components:']
    for comp in d['components']:
        lines.append(f'    - {comp}')
    return lines


DISEASES = {
    'malaria': {
        'name': 'Malaria',
        'cause': 'Plasmodium (protozoa)',
        'transmission': 'Anopheles mosquito bite',
        'symptoms': ['Fever', 'Chills', 'Sweating', 'Headache'],
        'prevention': 'Mosquito nets, antimalarials',
    },
    'tuberculosis': {
        'name': 'Tuberculosis',
        'cause': 'Mycobacterium tuberculosis',
        'transmission': 'Airborne droplets',
        'symptoms': ['Persistent cough', 'Weight loss', 'Night sweats', 'Fever'],
        'prevention': 'BCG vaccine, ventilation',
    },
    'diabetes': {
        'name': 'Diabetes',
        'cause': 'Insulin deficiency/resistance',
        'transmission': 'Non-communicable (genetic + lifestyle)',
        'symptoms': ['Excessive thirst', 'Frequent urination', 'Fatigue', 'Blurred vision'],
        'prevention': 'Healthy diet, exercise, weight management',
    },
    'asthma': {
        'name': 'Asthma',
        'cause': 'Chronic airway inflammation',
        'transmission': 'Non-communicable (genetic + environmental)',
        'symptoms': ['Wheezing', 'Shortness of breath', 'Chest tightness', 'Coughing'],
        'prevention': 'Avoid triggers, inhalers',
    },
}


def disease_info(disease_name):
    """Display disease information."""
    key = disease_name.strip().lower()
    d = DISEASES.get(key)
    if not None and key not in DISEASES:
        diseases = ', '.join(DISEASES.keys())
        return [f'Unknown disease', f'Available: {diseases}']
    lines = [
        d['name'],
        f'  Cause: {d["cause"]}',
        f'  Transmission: {d["transmission"]}',
        '  Symptoms:',
    ]
    for symptom in d['symptoms']:
        lines.append(f'    - {symptom}')
    lines.append(f'  Prevention: {d["prevention"]}')
    return lines
