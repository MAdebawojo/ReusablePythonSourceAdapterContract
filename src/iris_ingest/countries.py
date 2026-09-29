import pycountry

_ALPHA3_TO_ALPHA2 = {c.alpha_3: c.alpha_2 for c in pycountry.countries}
VALID_ALPHA2 = set(_ALPHA3_TO_ALPHA2.values())

def alpha3_to_alpha2(alpha_3_code: str) -> str | None:
    """Convert an ISO 3166-1 alpha-3 code to alpha-2. Returns None if unknown."""
    return _ALPHA3_TO_ALPHA2.get(alpha_3_code.upper())

def normalize_country_code(code: str | None) -> str | None:
    """Normalize a country code to ISO 3166-1 alpha-2, uppercase.

    Accepts alpha-2 or alpha-3 input, in any case, with surrounding
    whitespace. Returns None if the input is missing, empty, or an
    unrecognised alpha-3 code. Does not confirm the alpha-2 result is
    a real country; that is validate_country_code's job.
    """
    if not code:
        return None

    code_upper = "".join(code.split()).upper()

    if len(code_upper) == 2:
        return code_upper
    return alpha3_to_alpha2(code_upper)

def validate_country_code(code: str | None) -> bool:
    """Check whether a code is a real ISO 3166-1 alpha-2 code, exact match only."""
    return code in VALID_ALPHA2
