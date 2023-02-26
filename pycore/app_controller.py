from pycore.core_controller import parse_arguments


def collect_input(c: dict) -> dict:
    calc_input = str(input("> "))
    known_input, unknown_input = parse_arguments(calc_input)
    return known_input
