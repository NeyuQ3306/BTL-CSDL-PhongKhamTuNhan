"""Split the project's semicolon-delimited MySQL scripts."""
import re


_TOKENS = re.compile(
    r"'(?:''|\\[\s\S]|[^'\\])*'|\"(?:\"\"|\\[\s\S]|[^\"\\])*\"|`(?:``|[^`])*`|"
    r"--(?=\s|$)[^\r\n]*|#[^\r\n]*|/\*[\s\S]*?\*/|;|[^;'\"`/#-]+|[\s\S]"
)


def statements(source):
    """Yield statements, preserving quoted tokens and MySQL executable comments."""
    parts = []
    for match in _TOKENS.finditer(source):
        token = match.group()
        if token.startswith(('--', '#')) or (
            token.startswith('/*') and not token.startswith(('/*!', '/*+'))
        ):
            parts.append('\n')
        elif token == ';':
            if statement := ''.join(parts).strip():
                yield statement
            parts.clear()
        else:
            parts.append(token)
    if statement := ''.join(parts).strip():
        yield statement
