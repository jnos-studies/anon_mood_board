import importlib.util
import sys

# import the authentication module
spec = importlib.util.spec_from_file_location("authentication", "authentication.py")
authentication = importlib.util.module_from_spec(spec)
sys.modules["authentication"] = authentication
spec.loader.exec_module(authentication)
from authentication import convert_to_regexp


def test_conversion_to_regexp():
    # properly reject's input if it contains a space, digit, or backspace character after performing escapes
    # on sre_parsed characters.
    r_pattern_true = convert_to_regexp("test")
    r_pattern_false = convert_to_regexp("a b c")
    truthy = r_pattern_true.isalpha()
    falsey = r_pattern_false.isalpha()

    assert truthy == True and falsey == False, "Properly rejects input that is not a single word"
