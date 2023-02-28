import argparse
from pycore.core_controller import parse_arguments


def collect_input() -> tuple[dict, any]:
    calc_input = str(input("> "))
    try:
        known_input, unknown_input = parse_arguments(calc_input)
    except argparse.ArgumentError as exc:
        raise Exception(f"An error occured while parsing arguments\n{exc}")
    return (process_input(known_input), unknown_input)


def process_input(raw_input: dict) -> dict:
    """Function transforms raw class dictionary dump into api structure"""
    from config import DEFAULT_ARGUMENTS, MODIFIER_DEFINITIONS

    output = {
        "mode": "string",
        "rich_answer": False,
        "data": {
            "round": raw_input["round"],
            "players": raw_input["players"],
            "map_code": raw_input["map_code"],
            "special_rounds": raw_input["special_rounds"],
        },
        "output_types": None,    # Set in calculator handler
        "arguments": {},
        "modifier": None,
        "save_path": None,
    }

    # Set arguments
    for argument in DEFAULT_ARGUMENTS.keys():
        output["arguments"].update({argument: raw_input[argument]})

    # Set modifier
    for mod_key, mod_value in MODIFIER_DEFINITIONS.items():
        if raw_input[mod_value]:
            output["modifier"] = mod_key
            break

    return output
