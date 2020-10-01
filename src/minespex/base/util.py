"""
Miscellaneous utility functions.
"""

def as_basic_type(x):
    """Attempts to convert the argument to a basic type (if a string).

    Attempts to convert the argument to a basic type (if a string), otherwise
    returns the argument unchanged.

    Args:
        x (object): Object whose conversion is to be attempted.

    Returns:
        object:
            If `x` is a str, then an attempt is made to convert to an int and
            then a float. If not a string, or if both of these conversions
            fail, then `x` is returned unchanged.
    """
    if isinstance(x, str):
        try:
            return int(x)
        except ValueError:
            try:
                return float(x)
            except ValueError:
                pass
    return x
