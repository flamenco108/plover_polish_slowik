# XFZSKTPVLRJE~*IAUCRLBSGTWoy
KEYS = (
    '1-', '2-', '3-', '4-', '5-', '6-', '7-', '8-', '9-', '0-',
    'X-', 'F-', 'Z-', 'S-', 'K-', 'T-', 'P-', 'V-', 'L-', 'R-',
    'J-', 'E-',
    '~', '*', 'I',
    '-A', '-U',
    '-C', '-R', '-L', '-B', '-S', '-G', '-T', '-W', '-o', '-y',
)

IMPLICIT_HYPHEN_KEYS = (
    'J-', 'E-',
    '~', '*', 'I',
    '-A', '-U',
)

SUFFIX_KEYS = ()

NUMBER_KEY = None

NUMBERS = {}

UNDO_STROKE_STENO = '*'

ORTHOGRAPHY_RULES = []

ORTHOGRAPHY_RULES_ALIASES = {}

ORTHOGRAPHY_WORDLIST = None

KEYMAPS = {
    'Treal': {
        '1-': '#2',
        '2-': '#3',
        '3-': '#4',
        '4-': '#5',
        '5-': '#6',
        '6-': '#7',
        '7-': '#8',
        '8-': '#9',
        '9-': '#A',
        '0-': '#B',
        'X-': 'X1-',
        'F-': 'X2-',
        'Z-': 'S1-',
        'S-': 'S2-',
        'K-': 'T-',
        'T-': 'K-',
        'P-': 'P-',
        'V-': 'W-',
        'L-': 'H-',
        'R-': 'R-',
        'J-': 'A-',
        'E-': 'O-',
        '~': '*1',
        '*': '*2',
        'I': 'X3',
        '-A': '-E',
        '-U': '-U',
        '-C': '-F',
        '-R': '-R',
        '-L': '-P',
        '-B': '-B',
        '-S': '-L',
        '-G': '-G',
        '-T': '-T',
        '-W': '-S',
        '-o': '-D',
        '-y': '-Z',
        'no-op': '#1',
    },
    'Keyboard': {
        '1-': '1',
        '2-': '2',
        '3-': '3',
        '4-': '4',
        '5-': '5',
        '6-': '6',
        '7-': '7',
        '8-': '8',
        '9-': '9',
        '0-': '0',
        'X-' : 'q',
        'F-' : 'a',
        'Z-' : 'w',
        'S-' : 's',
        'K-' : 'e',
        'T-' : 'd',
        'P-' : 'r',
        'V-' : 'f',
        'L-' : 't',
        'R-' : 'g',
        'J-' : 'v',
        'E-' : 'b',
        '~' : 'y',
        '*' : 'h',
        'I' : 'n',
        '-A' : 'm',
        '-U' : ',',
        '-C' : 'u',
        '-R' : 'j',
        '-L' : 'i',
        '-B' : 'k',
        '-S' : 'o',
        '-G' : 'l',
        '-T' : 'p',
        '-W' : ';',
        '-o' : '[',
        '-y' : '\'',
        'arpeggiate': 'space'
    },
}

DICTIONARIES_ROOT = 'asset:plover_polish_slowik:dictionaries'
DEFAULT_DICTIONARIES = (
    'slowik_user.json',
    'slowik_suffixes.json',
    'slowik_prefixes.json',
    'slowik_roots.json',
)
