import numpy as np
import pycore.arg_controller as arg
from pycore.classes import ZombieRound


def verify_optional_input(data: dict, key: str) -> any:
    if key in data.keys() and data[key] is not None and data[key]:
        return data[key]
    return None


def mod_preprocessor(mod: str) -> any:
    """Function used to execute mods before the main loop. It is recommended to kill the program early after it's used"""
    print(f"DEV: mod {mod}")
    if mod == "-exc":
        raise Exception(f"This is a test exception raised by mod {mod}")
    if mod == "-irn":
        return filter_only_instarounds
    return


def display_metadata(mod: str, calc_message: dict) -> dict:
    """Function assembles helper dictionary for display function"""
    metadata = {
        "modifier": mod,
        "save_path": verify_optional_input(calc_message, "save_path")
    }

    return metadata


def time_processor(time: int | float) -> str:
    def get_higher_unit(lower_unit: int, calculated_unit: int, amount_of_lower_in_higher: int = 60) -> tuple[int, int]:
        """Extract higher unit from lower unit, return amount of higher unit and a remainer"""
        while lower_unit > amount_of_lower_in_higher - 1:
            calculated_unit += 1
            lower_unit -= amount_of_lower_in_higher
        return (calculated_unit, lower_unit)


    time_ms = int(time * 1000)

    # 'detailed' is set to true, we return miliseconds only
    if arg.get_args("detailed"):
        return f"{time_ms} ms"
    
    time_s, time_ms = get_higher_unit(time_ms, 0 , 1000)
    time_m, time_s = get_higher_unit(time_s, 0)    
    time_h, time_m = get_higher_unit(time_m, 0)

    # 'lower_time' is false and 'nodecimal' is true, we always add a second
    if not arg.get_args("lower_time") and arg.get_args("nodecimal"):
        time_s += 1
        time_m, time_s = get_higher_unit(time_s, time_m)
        time_h, time_m = get_higher_unit(time_m, time_h)

    # Convert decimals, or remove them if 'nodecimal' is true
    decimal = f".{str(time_ms).zfill(3)}"
    if arg.get_args("nodecimal"):
        decimal = ""

    seconds_str = "seconds"
    if time_s == 1:
        seconds_str = "second"

    ptime = lambda x: str(x).zfill(2)

    # 'even_time' is true, format is always MM:SS
    if arg.get_args("even_time"):
        return f"{ptime(time_m)}:{ptime(time_s)}"

    if not time_h and not time_m:
        return f"{ptime(time_s)}{decimal} {seconds_str}"
    if not time_h:
        return f"{ptime(time_m)}:{ptime(time_s)}{decimal}"
    return f"{ptime(time_h)}:{ptime(time_m)}:{ptime(time_s)}{decimal}"


def get_player_string(num_of_players: int) -> str:
    if num_of_players == 1:
        return "player"
    return "players"


def get_insta_round(is_insta_round: bool) -> str:
    if arg.get_args("insta_rounds") and is_insta_round:
        if arg.get_args("perfect_times"):
            return "It was Insta-Kill round"
        else:
            return "It's Insta-Kill round"
    return ""


def filter_only_instarounds(obj: ZombieRound) -> bool:
    if not isinstance(obj, ZombieRound) or not obj.is_insta_round:
        return "skip_noninsta_round"
    return ""


def get_162_health() -> np.int32:

    health = np.int32(150)
    for r in range(2, 163):
        if r < 10:
            health += np.int32(100)
        else:
            health += np.int32(np.float32(health) * np.float32(0.1))
    return health
