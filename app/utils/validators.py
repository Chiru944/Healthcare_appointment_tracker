"""Reusable input validation helpers."""
import re

def valid_phone(value: str) -> bool:
    return bool(re.fullmatch(r'[+()\-\d ]{7,20}', value.strip()))
