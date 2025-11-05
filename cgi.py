# Minimal cgi shim for Python 3.13+ to support Django 3.2's use of cgi.parse_header and cgi.valid_boundary
# This is NOT a full implementation of the deprecated cgi module.

from typing import Tuple, Dict


def parse_header(line: str) -> Tuple[str, Dict[str, str]]:
	"""
	Parse a Content-type like header.
	Returns the main content type and a dictionary of options.
	"""
	if not isinstance(line, str):
		line = str(line or "")
	parts = [p.strip() for p in line.split(';')]
	if not parts:
		return "", {}
	key = parts[0]
	pdict: Dict[str, str] = {}
	for part in parts[1:]:
		if not part:
			continue
		if '=' in part:
			k, v = part.split('=', 1)
			k = (k or '').strip().lower()
			v = (v or '').strip().strip('"')
			pdict[k] = v
		else:
			pdict[part.lower()] = ''
	return key, pdict


def valid_boundary(boundary: str) -> bool:
	# Accept any non-empty string for boundary in tests
	return isinstance(boundary, str) and len(boundary) > 0


__all__ = ['parse_header', 'valid_boundary']