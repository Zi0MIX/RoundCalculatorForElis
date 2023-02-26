from pycore.classes import ZombieRound, DogRound, DoctorRound, MonkeyRound, LeaperRound, PrenadesRound
from pycore.arg_controller import get_args
from pycore.api_handler import get_apiconfig


def parse_arguments(calc_input: str, validation: bool = True) -> tuple[dict, list[str]]:
    """Function takes either argv string or direct user input and disassembles it to arguments\n
    Set `validation` to `False` to enable sandbox mode in terms of accepted numbers"""
    import argparse as arg

    v_round, v_players = range(1, 65535), range(1, 9)
    if not validation:
        v_round, v_players = None, None

    parser = arg.ArgumentParser(prog="ZM-RoundCalculator", add_help=False)
    # Main
    parser.add_argument("round", type=int, action="store", choices=v_round)
    parser.add_argument("players", type=int, action="store", choices=v_players)

    # Extra
    parser.add_argument("-map", "--mapcode", required=False, type=str, action="store", dest="map_code")
    parser.add_argument("-spec", "--specialrounds", required=False, type=str, action="store", dest="special_rounds")

    # Args
    from config import DEFAULT_ARGUMENTS
    for k, v in DEFAULT_ARGUMENTS.items():
        store_type = "store_true"
        if not isinstance(v["default_state"], bool):
            store_type = "store"
        parser.add_argument(v["shortcode"], f"--{k}", action=store_type, dest=k, help=v["exp"])

    # Mods (can only use one at the time)
    mods = parser.add_mutually_exclusive_group()
    from config import MODIFIER_DEFINITIONS

    modifier_definitions = MODIFIER_DEFINITIONS
    apiconfig_mods = get_apiconfig("custom_modifiers")
    if isinstance(apiconfig_mods, dict):
        modifier_definitions.update(apiconfig_mods)

    for k, v in modifier_definitions.items():
        mods.add_argument(k, f"--{v}", action="store_true", dest=v)

    # Parse
    if isinstance(calc_input, str):
        calc_input = calc_input.split(" ")
    args, remainer = parser.parse_known_args(calc_input)

    return (vars(args), remainer)


def import_dogrounds() -> tuple:
    from config import CYA, RES, DOGS_PERFECT
    print(f"{CYA}Enter special rounds separated with space.{RES}")
    raw_special = str(input("> "))

    list_special = [int(x) for x in raw_special.split(" ") if x.isdigit()]
    if len(list_special):
        return tuple(list_special)
    return DOGS_PERFECT


def assemble_output(rich: bool, calculated_data: dict, calculator_data: dict) -> dict:
    """Function assembles a dictionary using provided data"""
    from config import WILDCARDS_TRANSLATION

    def generate_answer(calc_type: str, data_this_line: dict) -> str:
        pattern: str = calculator_data["output_types"][calc_type]

        # Map values with wildcards
        wildcard_map = {}
        for k, v in WILDCARDS_TRANSLATION.items():
            wildcard_map.update({k: data_this_line[v]})

        # Format output accordingly
        answer = pattern.format(**wildcard_map)

        return answer


    calc_type = calculator_data["calculator_type"]
    a = {
        "type": calc_type,
        "answer": list(),
    }

    for data in calculated_data.values():
        a["answer"].append(generate_answer(calc_type, data))

    if rich:
        a.update(calculated_data)

    return a


def evaluate_class_of_round(rnd: int, special_rounds: list[int], map_code: str, *classes) -> any:
    """Function evaluates provided arguments and returns the object that's to be used while evaluating provided round"""
    from config import MAP_DOGS, MAP_DOCTOR, MAP_MONKEYS, MAP_LEAPERS

    for c in classes:
        # If perfect times is not used, we only really care about ZombieRound
        if not get_args("perfect_times") and isinstance(c, ZombieRound):
            return c
        elif not get_args("perfect_times"):
            continue

        # DogRound
        if rnd in special_rounds and map_code in MAP_DOGS and isinstance(c, DogRound):
            return c
        # DoctorRound
        elif rnd in special_rounds and map_code in MAP_DOCTOR and isinstance(c, DoctorRound):
            return c
        # MonkeyRound
        elif rnd in special_rounds and map_code in MAP_MONKEYS and isinstance(c, MonkeyRound):
            return c
        # LeaperRound
        elif rnd in special_rounds and map_code in MAP_LEAPERS and isinstance(c, LeaperRound):
            return c
        # ZombieRound
        elif isinstance(c, ZombieRound):
            return c

    raise Exception("Could not evaluate class_of_round")


def evaluate_special_round(current_average: float, current_spec_rounds: int, rnd: int, class_of_round: any) -> tuple[float, int, bool]:
    """Function evaluates provided arguments and returns a tuple containing:\n
    `average`: float = Either passes through provided average, or if it's a special round, returns recalculated average\n
    `current_spec_round`: int = Either passes through number of special rounds that occured so far, or returns that number incremented by 1\n
    `is_special_round`: bool = True or False depending if it's a special round or not"""

    if isinstance(class_of_round, ZombieRound) or isinstance(class_of_round, PrenadesRound):
        return (current_average, current_spec_rounds, False)

    # Prevent division by 0
    if not current_spec_rounds:
        avg = rnd
    else:
        avg = rnd // current_spec_rounds

    return (avg, current_spec_rounds + 1, True)


def evaluate_round_time(class_of_round: any) -> int | float:
    """Function evaluates provided arguments and returns amount of seconds the round has taken"""

    # Add teleport time to dog round
    if isinstance(class_of_round, DogRound) and get_args("teleport_time"):
        class_of_round.add_teleport_time()

    return class_of_round.round_time


def evaluate_game_time(game_time: int | float, round_time: int | float) -> int | float:
    """Function evaluates provided arguments and returns total game time after the round"""
    from config import RND_WAIT_END

    new_game_time = game_time + round_time + RND_WAIT_END
    return new_game_time