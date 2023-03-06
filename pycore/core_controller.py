from pycore.classes import ZombieRound, DogRound, DoctorRound, MonkeyRound, LeaperRound, PrenadesRound
from pycore.arg_controller import get_args, eval_break, eval_save
from pycore.api_handler import get_apiconfig


def parse_arguments(calc_input: str, validation: bool = True) -> tuple[dict, list[str]]:
    """Function takes either argv string or direct user input and disassembles it to arguments\n
    Set `validation` to `False` to enable sandbox mode in terms of accepted numbers"""
    import argparse as arg

    v_round, v_players = range(1, 65535), range(1, 9)
    if not validation:
        v_round, v_players = None, None

    # Exit on error removes default error messages, function will back up to try/except in main and display error message there
    parser = arg.ArgumentParser(prog="ZM-RoundCalculator", add_help=False, exit_on_error=False)
    # Main
    parser.add_argument("round", type=int, action="store", choices=v_round)
    parser.add_argument("players", type=int, action="store", choices=v_players)

    # Extra
    parser.add_argument("-map", "--mapcode", required=False, type=str, action="store", dest="map_code", default=None)
    parser.add_argument("-spec", "--specialrounds", required=False, type=str, action="store", dest="special_rounds", default=None)

    # Args
    from config import DEFAULT_ARGUMENTS
    for k, v in DEFAULT_ARGUMENTS.items():

        if not isinstance(v["default_state"], bool):
            parser.add_argument(v["shortcode"], f"--{k}", action="store", dest=k, help=v["exp"], default=v["default_state"], choices=v["allowed_values"])
            continue

        if v["default_state"]:
            store_type = "store_false"
        else:
            store_type = "store_true"

        parser.add_argument(v["shortcode"], f"--{k}", action=store_type, dest=k, help=v["exp"], default=v["default_state"])


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
        # print(f"DEV: data={data}")
        a["answer"].append(generate_answer(calc_type, data))

    if rich:
        a.update(calculated_data)

    return a


def evaluate_class_of_round(rnd: int, special_rounds: list[int], map_code: str, *classes) -> any:
    """Function evaluates provided arguments and returns the object that's to be used while evaluating provided round"""
    from config import MAP_DOGS, MAP_DOCTOR, MAP_MONKEYS, MAP_LEAPERS


    def return_object(object):
        """Wrapping function to allow dev print"""
        print(f"DEV: rnd={rnd} class_of_round={type(object).__name__} special_rounds={special_rounds} map_code={map_code}")
        return object


    def match_type(object: any, match: any) -> bool:
        """Match exact type of object, to counter inherited matches"""

        if isinstance(match, (tuple, list)):
            for m in match:
                if type(match) is m:
                    return True
            return False
        
        if type(object) is match:
            return True
        return False


    default = None
    for i, c in enumerate(classes):
        print(f"DEV: rnd={rnd} | i={i} | c={type(c).__name__} | default={type(default).__name__}")

        # If perfect times is not used, we only really care about ZombieRound
        if not get_args("perfect_times") and match_type(c, ZombieRound):
            return return_object(c)
        elif not get_args("perfect_times"):
            continue

        # DogRound
        if rnd in special_rounds and map_code in MAP_DOGS and match_type(c, DogRound):
            return return_object(c)
        # DoctorRound
        elif rnd in special_rounds and map_code in MAP_DOCTOR and match_type(c, DoctorRound):
            return return_object(c)
        # MonkeyRound
        elif rnd in special_rounds and map_code in MAP_MONKEYS and match_type(c, MonkeyRound):
            return return_object(c)
        # LeaperRound
        elif rnd in special_rounds and map_code in MAP_LEAPERS and match_type(c, LeaperRound):
            return return_object(c)
        # ZombieRound
        elif match_type(c, ZombieRound):
            default = c

    if default is None:
        raise Exception("Could not evaluate class_of_round")

    return return_object(default)


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


def get_class_vars(instance: any, key: str = None) -> dict | None:
    """Function makes a call to vars but will return `None` on exception, allowing for passing wrong instance, such as `None`"""
    try:
        class_content = vars(instance)
        if key is None:
            return class_content
        return class_content[key]
    except Exception:
        return None


def display_output(data: dict, c: dict, **extras) -> None:
    if data["type"] == "error":
        print(f"{c['f_red']}An error occured:{c['reset']}\n{data['answer'][0]}\n")
        return

    save_path = None
    if "save_path" in extras.keys():
        save_path = extras["save_path"]

    data_to_output = data["answer"]

    if not get_args("range"):
        data_to_output = data_to_output[-1]
    elif get_args("perfect_times"):
        data_to_output = data_to_output[1:]

    if isinstance(data_to_output, list):
        for a in data_to_output:
            print(a)
            eval_break()
            eval_save(a, save_path)
    else:
        print(data_to_output)
        eval_break()
        eval_save(data_to_output, save_path)

    return


def return_error(*passthrough) -> list[dict, any]:
    from traceback import format_exc

    answer = {
        "type": "error",
        "answer": [str(format_exc(chain=False))],
    }

    return [answer] + list(passthrough)
