"""
FIPS code standardization utility.
Ensures all FIPS codes are zero-padded 5-digit strings.
"""

def standardize_fips(fips_value) -> str:
    """Convert any FIPS representation to zero-padded 5-digit string."""
    if fips_value is None:
        return None
    s = str(fips_value).strip()
    # Remove any decimal (e.g. "6037.0" -> "6037")
    if '.' in s:
        s = s.split('.')[0]
    # Zero-pad to 5 digits
    return s.zfill(5)


def get_state_fips(county_fips: str) -> str:
    """Extract 2-digit state FIPS from 5-digit county FIPS."""
    return county_fips[:2] if county_fips and len(county_fips) >= 2 else None
