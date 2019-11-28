# Samuel Dunn
# CS 483, Fall 2019

# This module provides functions for normalizing mana symbols and converting them to and
# from whatever format is necesary.

# Possible notations:
# - link notation (on gatherer), where mana symbols are just links to images.
# - curly bracket notation: what we'll use internally and try to get users to use
# - however the user inputs mana. :shrug: we'll look for specific reference to an MTG color and convert it as necessary

import re

def replace_mana_links_in_text(text):
    """
    This function takes an input string - likely from gatherer itself - and converts mana symbol-tags to curly-bracket notation
    """
    sub_aux = lambda match: alt_text_to_curly_bracket(match.group(1))
    pattern = r'<\s*img\s.*?alt="(.*?)".*?>'
    return re.sub(pattern, sub_aux, text)

def alt_text_to_curly_bracket(text):
    """
    Converts the text that appears in the alt attribute of image tags from gatherer
    to a curly-bracket mana notation.
    ex: 'Green'->{G}, 'Blue or Red'->{U/R}
        'Variable Colorless' -> {X}
        'Colorless' -> {C}
        'N colorless' -> {N}, where N is some number
    """
    def convert_color_to_letter(color):
        if color.lower() not in ('red', 'white', 'blue', 'green', 'black', 'colorless', 'tap', 'energy'):
            # some cards have weird split mana costs where you can pay N colorless
            # or one of a specific color.
            # Since we're ending up here, and what we're given isn't a color, lets assume its N
            return color
        else:
            return color[0].upper()

    try:
        val = int(text, 10)
    except Exception:
        pass
    else:
        # This is just a number. Easy enough.
        return f"{{{text}}}"

    if ' or ' in text:
        # this is a compound color, not as easy to deal with.
        text = text.replace('or', '')
        text = '/'.join([convert_color_to_letter(x) for x in text.split()])

    else:
        # hopefully all that's left is just simple color symbols.
        text = convert_color_to_letter(text)

    # at this point we've hopefully
    return f"{{{text}}}"
