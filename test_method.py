from spellchecker import SpellChecker

def correct_caption(caption: str) -> str:
    """
    Checks the caption's last word for potential spelling errors and corrects it if necessary.
    This is a quick heuristic that only fixes the final word if it's not recognized.
    
    :param caption: The generated caption.
    :return: The corrected caption.
    """
    spell = SpellChecker(language='en')
    words = caption.split()
    
    if not words:
        return caption
    
    # Check the last word
    last_word = words[-1]
    # If the last word is not in our dictionary and is longer than 2 characters
    if len(last_word) > 2 and last_word.lower() not in spell:
        corrected_last = spell.correction(last_word)
        words[-1] = corrected_last
    return " ".join(words)

# Example usage:
generated_caption = "a picture of a woman sitting on a window sie"
corrected_caption = correct_caption(generated_caption)
print("Corrected Caption:", corrected_caption)
# Expected output: "a picture of a woman sitting on a window sill"
