"""Country code mapping for European countries.
Maps common country names to ISO 3166-1 alpha-2 codes for flagcdn.com.
"""

COUNTRY_CODES = {
    'albania': 'al', 'andorra': 'ad', 'austria': 'at', 'belarus': 'by',
    'belgium': 'be', 'bosnia': 'ba', 'bosniaandherzegovina': 'ba',
    'bulgaria': 'bg', 'croatia': 'hr', 'cyprus': 'cy',
    'czechrepublic': 'cz', 'czech': 'cz', 'denmark': 'dk',
    'estonia': 'ee', 'finland': 'fi', 'france': 'fr',
    'germany': 'de', 'greece': 'gr', 'hungary': 'hu',
    'iceland': 'is', 'ireland': 'ie', 'italy': 'it',
    'kosovo': 'xk', 'latvia': 'lv', 'liechtenstein': 'li',
    'lithuania': 'lt', 'luxembourg': 'lu', 'malta': 'mt',
    'moldova': 'md', 'monaco': 'mc', 'montenegro': 'me',
    'netherlands': 'nl', 'northmacedonia': 'mk', 'macedonia': 'mk',
    'norway': 'no', 'poland': 'pl', 'portugal': 'pt',
    'romania': 'ro', 'russia': 'ru', 'sanmarino': 'sm',
    'serbia': 'rs', 'slovakia': 'sk', 'slovenia': 'si',
    'spain': 'es', 'sweden': 'se', 'switzerland': 'ch',
    'turkey': 'tr', 'ukraine': 'ua', 'unitedkingdom': 'gb',
    'uk': 'gb', 'britain': 'gb', 'england': 'gb',
    'greatbritain': 'gb', 'vatican': 'va', 'vaticancity': 'va',
}

COUNTRIES_44 = [
    'albania', 'andorra', 'austria', 'belarus', 'belgium',
    'bosniaandherzegovina', 'bulgaria', 'croatia', 'cyprus',
    'czechrepublic', 'denmark', 'estonia', 'finland', 'france',
    'germany', 'greece', 'hungary', 'iceland', 'ireland', 'italy',
    'kosovo', 'latvia', 'liechtenstein', 'lithuania', 'luxembourg',
    'malta', 'moldova', 'monaco', 'montenegro', 'netherlands',
    'northmacedonia', 'norway', 'poland', 'portugal', 'romania',
    'russia', 'sanmarino', 'serbia', 'slovakia', 'slovenia',
    'spain', 'sweden', 'switzerland', 'turkey', 'ukraine',
    'unitedkingdom', 'vatican',
]


def name_to_code(name):
    n = name.lower().replace(' ', '').replace('-', '')
    if n in COUNTRY_CODES:
        return COUNTRY_CODES[n]
    if len(n) == 2 and n.isalpha():
        return n
    return None


def fetch_flag_svg(code, base_path='/flags'):
    """Load SVG from local filesystem.
    Returns SVG string or None on error.
    """
    path = '{}/{}.svg'.format(base_path, code)
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception:
        return None
