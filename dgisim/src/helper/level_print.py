from typing import Dict

_INDENTATION = "| "
INDENT = len(_INDENTATION)

def level_print(strs: Dict[str, str], indent: int = 0) -> str:
    indentation = _INDENTATION * (indent // INDENT)
    str_builder = []
    for key, val in strs.items():
        if val and val[-1] == '\n':
            str_builder.append(indentation + '<' + key + ">:\n")
            str_builder.append(val)
        else:
            str_builder.append(indentation + '<' + key + ">: ")
            str_builder.append(val + '\n')
    return ''.join(str_builder)

def level_print_single(s: str, indent: int = 0) -> str:
    """
    format prints one line of string
    """
    indentation = _INDENTATION * (indent // INDENT)
    return indentation + s + '\n'
