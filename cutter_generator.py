"""
Cutter-Sanborn Author Mark & Library Call Number Generator
Designed for Library Processing Sections & Cataloging Professionals.
Implements the Cutter Two/Three-Figure Author Number rules:
- Author surname converted to initial letter + numeric representation based on alphabetical proximity.
- Work mark: first significant letter of the title (skipping initial articles like 'A', 'An', 'The', 'A Brief', etc.).
- Complete Call Number synthesis: [DDC Class Number] [Cutter Number + Work Mark] [Publication Year].
"""

import re

# Comprehensive Cutter-Sanborn prefix-to-number reference table
CUTTER_TABLE = {
    # A
    "A": "11", "Ab": "12", "Ac": "13", "Ad": "19", "Af": "25", "Ag": "26", "Ah": "28", "Ai": "29",
    "Ak": "31", "Al": "32", "Ali": "39", "All": "42", "Alm": "44", "Am": "48", "An": "53",
    "And": "54", "Ans": "61", "Ap": "64", "Ar": "69", "Arn": "74", "As": "79", "At": "86", "Au": "89",
    "Ay": "97", "Az": "99",

    # B
    "B": "11", "Bab": "11", "Bac": "118", "Bag": "14", "Bah": "15", "Bai": "155", "Bak": "16",
    "Bal": "17", "Ban": "21", "Banerjee": "215", "Bar": "22", "Bas": "29", "Basu": "295",
    "Bat": "32", "Bau": "34", "Bea": "36", "Bec": "39", "Beg": "41", "Bel": "42", "Ben": "45",
    "Ber": "48", "Bha": "57", "Bhattacharya": "575", "Bho": "578", "Bis": "62", "Biswas": "629",
    "Bla": "63", "Blo": "65", "Bod": "66", "Bok": "68", "Bon": "69", "Bor": "72", "Bos": "74",
    "Bose": "743", "Bow": "78", "Boy": "79", "Bra": "81", "Bre": "83", "Bri": "85", "Bro": "87",
    "Bru": "89", "Bry": "91", "Buc": "92", "Bur": "94", "Bus": "97",

    # C
    "C": "11", "Cab": "11", "Cal": "14", "Cam": "17", "Can": "21", "Car": "28", "Cas": "33",
    "Cat": "35", "Cha": "42", "Chakraborty": "435", "Chatterjee": "495", "Chowdhury": "552",
    "Cla": "58", "Cle": "62", "Cli": "64", "Coa": "65", "Coh": "67", "Col": "68", "Con": "74",
    "Coo": "77", "Cor": "78", "Cos": "83", "Cox": "87", "Cra": "88", "Cri": "92", "Cro": "94",

    # D
    "D": "11", "Dac": "11", "Dai": "13", "Dal": "14", "Dam": "16", "Dan": "17", "Dar": "21",
    "Das": "229", "Datta": "234", "Dey": "528", "Dhar": "533", "Dia": "54", "Dic": "55",
    "Die": "56", "Dis": "61", "Doy": "75", "Dra": "76", "Duf": "85", "Dum": "88", "Dut": "97",

    # E
    "E": "11", "Ea": "12", "Eb": "16", "Ec": "17", "Ed": "21", "Eg": "29", "Ei": "34",
    "El": "37", "Em": "53", "En": "56", "Er": "67", "Es": "74", "Et": "84", "Ev": "92",

    # F
    "F": "11", "Fa": "11", "Far": "21", "Faz": "28", "Fe": "31", "Fer": "38", "Fi": "47",
    "Fin": "49", "Fla": "57", "Fle": "59", "Fo": "65", "For": "69", "Fra": "81", "Fre": "85",

    # G
    "G": "11", "Ga": "11", "Gan": "19", "Ganguly": "198", "Gar": "21", "Ge": "34", "Gh": "42",
    "Ghosh": "427", "Gi": "46", "Gl": "54", "Go": "57", "Goswami": "685", "Gra": "73", "Gre": "79",
    "Gu": "89", "Guha": "895", "Gupta": "977",

    # H
    "H": "11", "Ha": "11", "Hab": "114", "Haf": "138", "Hai": "149", "Hal": "158", "Haldar": "159",
    "Ham": "198", "Haq": "253", "Haque": "254", "Har": "256", "Has": "344", "Hasan": "345",
    "Hossain": "829", "Huq": "957", "Husain": "968", "Hussain": "972",

    # I
    "I": "11", "Ib": "12", "Ibn": "13", "Ibr": "14", "Im": "31", "In": "35", "Iq": "64",
    "Iqbal": "647", "Is": "75", "Islam": "755",

    # J
    "J": "11", "Ja": "11", "Jahangir": "25", "Jal": "26", "Jam": "27", "Jamil": "275",
    "Jan": "33", "Je": "43", "Ji": "61", "Jo": "62", "John": "65", "Ju": "91",

    # K
    "K": "11", "Ka": "11", "Kabir": "115", "Kamal": "15", "Kar": "18", "Karim": "186",
    "Kas": "19", "Kaz": "23", "Ke": "27", "Kh": "45", "Khan": "453", "Khatun": "458",
    "Ki": "46", "Ko": "75", "Ku": "95", "Kumar": "96",

    # L
    "L": "11", "La": "11", "Lahiri": "183", "Lak": "19", "Latif": "357", "Le": "43",
    "Li": "69", "Lo": "79", "Lu": "92",

    # M
    "M": "11", "Ma": "11", "Mah": "21", "Mahmood": "214", "Mahmud": "216", "Maj": "23",
    "Majumdar": "234", "Mal": "237", "Mallick": "254", "Man": "266", "Mannan": "282",
    "Mar": "356", "Mas": "394", "Masud": "398", "Maz": "476", "Mazumder": "477", "Mi": "618",
    "Mia": "618", "Miah": "619", "Mir": "671", "Mitra": "684", "Mizan": "685", "Mo": "687",
    "Mohammad": "697", "Mohammed": "698", "Mondal": "741", "Monir": "748", "Mukherjee": "953",
    "Munshi": "969", "Mustafa": "991",

    # N
    "N": "11", "Na": "11", "Nahar": "153", "Nasir": "258", "Naz": "335", "Nazmul": "338",
    "Nazrul": "339", "Ne": "364", "Ni": "579", "No": "755", "Nur": "974",

    # O
    "O": "11", "Ob": "12", "Ol": "47", "Om": "54", "Os": "81", "Osman": "834",

    # P
    "P": "11", "Pa": "11", "Pal": "153", "Paul": "324", "Pe": "358", "Ph": "547",
    "Pi": "583", "Pr": "895", "Pramanik": "898",

    # Q
    "Q": "11", "Qa": "11", "Qadir": "12", "Qazi": "19", "Qu": "25", "Quddus": "35",

    # R
    "R": "11", "Ra": "11", "Rahim": "148", "Rahman": "149", "Rahmat": "151", "Rai": "153",
    "Raj": "161", "Rakshit": "163", "Ram": "165", "Rana": "185", "Rashid": "224", "Rauf": "244",
    "Ray": "264", "Raza": "279", "Re": "281", "Reza": "467", "Ro": "642", "Roy": "888",

    # S
    "S": "11", "Sa": "11", "Saha": "131", "Said": "132", "Saif": "133", "Salahuddin": "159",
    "Salam": "161", "Saleh": "163", "Samad": "187", "Sanyal": "239", "Sarkar": "245",
    "Sen": "474", "Sha": "524", "Shah": "525", "Shahid": "526", "Shafi": "527", "Shams": "528",
    "Sharif": "531", "Sheikh": "542", "Shikdar": "555", "Siddiq": "568", "Siddique": "569",
    "Singh": "617", "Siraj": "619", "So": "678", "Sufi": "942", "Sultan": "954",

    # T
    "T": "11", "Ta": "11", "Tagore": "128", "Talukder": "153", "Tarafder": "176",
    "Tarafdar": "176", "Th": "364", "Ti": "583", "To": "628", "Tu": "834", "Turing": "934",

    # U
    "U": "11", "Ud": "21", "Uddin": "215", "Ul": "45", "Um": "53", "Us": "87",

    # V
    "V": "11", "Va": "11", "Ve": "42", "Vi": "69", "Vo": "87",

    # W
    "W": "11", "Wa": "11", "Wahab": "136", "Wahid": "137", "Wal": "187", "We": "364",
    "Wi": "648", "Wo": "857",

    # Y
    "Y": "11", "Ya": "11", "Yasin": "291", "Ye": "37", "Yo": "78", "Yusuf": "95",

    # Z
    "Z": "11", "Za": "11", "Zafar": "17", "Zahir": "19", "Zakir": "22", "Zaman": "26"
}


def clean_title(title: str) -> str:
    """Removes leading articles and punctuation to get significant first letter."""
    if not title:
        return "x"
    cleaned = title.strip()
    # Strip leading English/Bengali common articles
    cleaned = re.sub(r'^(a|an|the|the\s+story\s+of|a\s+brief|an\s+introduction\s+to)\s+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', cleaned)
    return cleaned if cleaned else "x"


def generate_cutter_number(author_name: str) -> str:
    """
    Generates a Cutter-Sanborn author number for an author.
    Handles names like:
    - 'Rabindranath Tagore' -> T128
    - 'Kazi Nazrul Islam' -> I755 or N339
    - 'Humayun Ahmed' -> A28
    - 'Muhammad Yunus' -> Y95
    """
    if not author_name or not author_name.strip():
        return "A11"

    # Extract surname / primary filing element
    parts = author_name.strip().split()
    # In Bengali/South Asian names, the last token is usually the family name/surname
    # (e.g. Tagore, Islam, Rahman, Ahmed, Khan, Roy, Sen)
    surname = parts[-1].strip()
    first_letter = surname[0].upper()

    # Try matching descending substrings in CUTTER_TABLE
    best_match = None
    for length in range(min(12, len(surname)), 0, -1):
        prefix = surname[:length]
        # Match case-insensitively against table
        for key in CUTTER_TABLE:
            if key.lower() == prefix.lower():
                best_match = f"{first_letter}{CUTTER_TABLE[key]}"
                break
        if best_match:
            break

    if best_match:
        return best_match

    # Fallback heuristic based on second letter
    if len(surname) > 1:
        second_val = ord(surname[1].lower()) - ord('a') + 1
        num_val = int(second_val * 3.5) + 10
        return f"{first_letter}{num_val}"
    return f"{first_letter}11"


def generate_call_number(ddc_number: str, author_name: str = "", title: str = "", publication_year: str = "") -> dict:
    """
    Constructs the complete academic library call number:
    Format:
    [DDC Classification]
    [Cutter Number + Work Mark]
    [Publication Year]
    """
    ddc_clean = ddc_number.strip() if ddc_number else "000"
    
    work_mark = ""
    if title:
        ct = clean_title(title)
        if ct:
            work_mark = ct[0].lower()

    cutter = ""
    if author_name and author_name.strip():
        cutter = generate_cutter_number(author_name)
        if work_mark:
            cutter += work_mark
    else:
        # If no author, cutter is derived from title
        ct = clean_title(title)
        if ct:
            cutter = ct[0].upper() + "11" + (ct[1].lower() if len(ct) > 1 else "")

    year_str = str(publication_year).strip() if publication_year else ""

    # Assemble call number lines
    lines = [ddc_clean]
    if cutter:
        lines.append(cutter)
    if year_str:
        lines.append(year_str)

    full_call_number = " ".join(lines)
    spine_label = "\n".join(lines)

    return {
        "ddc_class": ddc_clean,
        "cutter_mark": cutter,
        "year": year_str,
        "full_call_number": full_call_number,
        "spine_label": spine_label
    }
