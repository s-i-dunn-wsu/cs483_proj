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
    if text:
        sub_aux = lambda match: alt_text_to_curly_bracket(match.group(1))
        pattern = r'<\s*img\s.*?alt="(.*?)".*?>'
        return re.sub(pattern, sub_aux, text)

def alt_text_to_curly_bracket(text):
    """
    Converts the text that appears in the alt attribute of image tags from gatherer
    to a curly-bracket mana notation.
    ex: 'Green'->{G}, 'Blue or Red'->{U/R}
        'Variable Colorless' -> {XC}
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
            if color.lower() == 'blue': return 'U'
            else: return color[0].upper()

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
        if 'Variable' in text:
            text = 'X'
        else:
            # hopefully all that's left is just simple color symbols.
            text = convert_color_to_letter(text)

    # at this point we've hopefully
    return f"{{{text}}}"

def replace_curly_brackets_in_text(text):
    """
    Replaces curly bracket notation in text with the correct
    image link.
    """
    if text:
        sub_aux = lambda match: curly_bracket_to_img_link(match.group(1))
        pattern = r'(\{.*?\})'
        return re.sub(pattern, sub_aux, text)

def curly_bracket_to_img_link(cb):
    """
    Takes the curly-bracket notation for some mana type
    and creates the appropriate image html tag.
    """
    file_safe_name = cb[1:-1].replace('/', '_').replace(' ', '_')
    ext = 'png' if 'Phyrexian' in file_safe_name or file_safe_name in ('C', 'E') else 'gif'
    return f"<img src=\"/images/mana/{file_safe_name}.{ext}\">"

def fix_variable_mana(card):
    """
    This function was created to fix a problem in the dataset.
    We're currently pretty up against the wall and I realized
    that 'Variable' mana texts were not correctly converted to {X}
    so this function is fed cards and corrects their mana values
    if it detects this problem.
    """
    def correct_field(symbol):
        if 'Variable' in symbol:
            # strip out brackets:
            symbol = symbol[1:-1]

            # remove 'Variable'
            symbol = symbol.replace('Variable', '').strip()

            # get the correct color-letter
            symbol = alt_text_to_curly_bracket(symbol)

            # 'insert' X and return the corrected symbol.
            return f'{{X{symbol[1:-1]}}}'
        else:
            return symbol
    corrected = [x for x in card.mana_cost]
    card.mana_cost = corrected