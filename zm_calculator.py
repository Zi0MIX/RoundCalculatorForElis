import numpy as np
import config as cfg
import sys
from pycore.api_handler import apiconfing_defined, get_apiconfig
from pycore.arg_controller import get_args, update_args, eval_hordes
from pycore.classes import ZombieRound, DogRound, DoctorRound, MonkeyRound, LeaperRound, PrenadesRound
from pycore.core_controller import evaluate_class_of_round, evaluate_game_time, evaluate_round_time, assemble_output, evaluate_special_round, get_class_vars, display_output
from pycore.functions import verify_optional_input, mod_preprocessor, display_metadata, time_processor, get_player_string, get_insta_round, get_162_health
from pycore.output_controller import map_translator, return_error


def calculator_handler(calc_message: dict) -> tuple[dict, str]:

    def parse_calculator_data(data: dict) -> tuple[int, int, str, str]:
        def evaluate_special_rounds(spec_rounds: any) -> list[int]:
            # Special rounds array hasn't been provided or we calculating remix
            if spec_rounds is None or get_args("remix"):
                # We default to dog rounds. In the future lock others behind if statements based on map_code
                spec_rounds = cfg.DOGS_PERFECT
            # Else make sure everything is an integer
            else:
                spec_rounds = [int(d) for d in spec_rounds]

            return spec_rounds


        rnd, players = int(data["round"]), int(data["players"])
        map_code = verify_optional_input(data, "map_code")
        special_rounds = evaluate_special_rounds(verify_optional_input(data, "special_rounds"))

        return (rnd, players, map_code, special_rounds)


    def parse_output_types(output_types: dict | None) -> dict:
        """Function assembles a dictionary of patterns\n
        1. cfg.DEFAULT_PATTERNS\n
        2. cfg.CLEAR_PATTERNS are used to override if argument `clear` is set\n
        3. Apiconfig key `custom_patterns` is used to override / add\n
        4. Calculator message from key `output_types` is used to override / add"""

        patterns = cfg.DEFAULT_PATTERNS
        if get_args("clear"):
            patterns.update(cfg.CLEAR_PATTERNS)

        if apiconfing_defined():
            patterns.update(get_apiconfig("custom_patterns"))

        if output_types is not None:
            patterns.update(output_types)

        return patterns


    def parse_calculator_types(modifier: str) -> str:
        """Function defines the calculator type based on conditions in following order:\n
        1. Built-in mods - If built-in mod is used, that'll be prioritised\n
        2. Apiconfig mods - Then if api-defined mod is used, that'll be evaluated\n
        3. Arguments - Lastly, if argument is used that changes calc type, that'll be applied"""

        if modifier in cfg.MODIFIER_DEFINITIONS.keys():
            return cfg.MODIFIER_DEFINITIONS[modifier]
        if apiconfing_defined():
            apiconfig_mods = get_apiconfig("custom_modifiers")
            if isinstance(apiconfig_mods, dict) and modifier in apiconfig_mods.keys():
                return apiconfig_mods[modifier]
        if get_args("perfect_times"):
            return "perfect_times"
        if get_args("prenades"):
            return "prenades"

        return "round_times"


    # Avoid warning while calculating insta rounds
    np.seterr(over="ignore")

    # Extract data from calc_message
    calc_data: dict = calc_message["data"]
    calc_arguments: dict = calc_message["arguments"]
    is_rich_answer = calc_message["rich_answer"]

    # Extract data from calc_data
    rnd, players, map_code, spec_rounds = parse_calculator_data(calc_data)

    # Set args from calc_arguments
    for key in get_args().keys():
        try:
            update_args(key, calc_arguments[key])
        # The default state of the argument is already established, the error can be ignored
        except KeyError:
            continue

    # Extract modifier from calc_message
    # Remember to add modifier handling somewhere, there is already a relation defined in config.py between modifier and output pattern
    calc_modifier = verify_optional_input(calc_message, "modifier")

    # Extract output types from calc message
    output_types = parse_output_types(calc_message["output_types"])

    # Evaluate presence of required arguments
    for arg, settings in cfg.DEFAULT_ARGUMENTS.items():
        # Verify map code presence
        if calc_arguments[arg] and settings["require_map"]:
            if map_code is None:
                raise Exception(f"Argument {settings['readable_name']} requires a map to be selected")
            elif map_code not in cfg.MAP_LIST:
                raise Exception(f"Map {map_translator(map_code)} is not supported")
        # Verify special rounds presence
        if calc_arguments[arg] and settings["require_special_round"]:
            if spec_rounds is None:
                raise Exception(f"Argument {settings['readable_name']} requires special rounds be specified")

    calculator_type = parse_calculator_types(calc_modifier)

    has_special_rounds = map_code is not None and (map_code in cfg.MAP_DOGS or map_code in cfg.MAP_DOCTOR or map_code in cfg.MAP_MONKEYS or map_code in cfg.MAP_LEAPERS)

    all_results = {}
    game_time = cfg.RND_WAIT_INITIAL

    # Initialize variables for for loop
    special_average, num_of_special_rounds = 0.0, 0
    health_162 = get_162_health()

    preprocess = mod_preprocessor(calc_modifier)

    for r in range(1, rnd + 1):
        # print(f"DEV: tick {r}")
        zombie_round = ZombieRound(r, players, map_code)
        # Cast for separate classes, decided not to make one universal gigant for special rounds in general, allowes for more freedom outside of class
        if has_special_rounds:
            dog_round = DogRound(r, players, map_code, spec_rounds)
            doc_round = DoctorRound(r, players, map_code, spec_rounds)
            monkey_round = MonkeyRound(r, players, map_code, spec_rounds)
            leaper_round = LeaperRound(r, players, map_code, spec_rounds)
        else:
            dog_round = None
            doc_round = None
            monkey_round = None
            leaper_round = None

        if r <= 100:
            prenades_round = PrenadesRound(r, players, map_code, health_162, radius=float(get_args("grenade_radius")), extra_damage=int(get_args("grenade_damage")))
        elif get_args("prenades"):
            break
        else:
            prenades_round = None

        class_of_round = evaluate_class_of_round(r, spec_rounds, map_code, zombie_round, dog_round, doc_round, monkey_round, leaper_round, prenades_round)

        is_special_round = False
        if has_special_rounds:
            special_average, num_of_special_rounds, is_special_round = evaluate_special_round(special_average, num_of_special_rounds, r, class_of_round)

        round_time = evaluate_round_time(class_of_round)

        # Seems good place, perhaps move around later
        if preprocess is not None:
            if preprocess(class_of_round) == "skip_noninsta_round":
                continue

        # Assemble simple answer
        round_result = {
            "round": r,
            "players": players,
            "players_string": get_player_string(players),
            "enemy_health": class_of_round.health,
            "spawnrate": class_of_round.spawn_delay,
            "raw_spawnrate": class_of_round.raw_spawn_delay,
            "network_frame": class_of_round.network_frame,
            "round_time": time_processor(round_time),
            "game_time": time_processor(game_time),

            "is_insta_round": class_of_round.is_insta_round,
            "insta_round_text": get_insta_round(class_of_round.is_insta_round),

            "map_code": map_code,
            "map_name": map_translator(map_code),

            "is_special_round": is_special_round,
            "spec_round_average": special_average,
            "num_of_spec_rounds": num_of_special_rounds,

            "prenades": get_class_vars(prenades_round, "prenades"),
            "nade_type": get_class_vars(prenades_round, "grenade_type"),
            "nade_name": get_class_vars(prenades_round, "grenade_name"),

            "class_of_round": type(class_of_round).__name__,
            "zombie_round": get_class_vars(zombie_round),
            "dog_round": get_class_vars(dog_round),
            "doctor_round": get_class_vars(doc_round),
            "monkey_round": get_class_vars(monkey_round),
            "leaper_round": get_class_vars(leaper_round),
            "prenades_round": get_class_vars(prenades_round),
        }

        # Add dynamic keys
        round_result["enemies"], round_result["enemy_type"] = eval_hordes(class_of_round)

        # Update all results
        all_results.update({str(r): round_result})

        # Calculate it after updating results, the reason for it is that'll be the actual representation of gametime till specified round, eg time to round 1 will always equal to `cfg.RND_WAIT_INITIAL`. It makes the calcultion redundant for last iteration, but it's fine
        game_time = evaluate_game_time(game_time, round_time)

    assemble_data = {
        "calculator_type": calculator_type,
        "spec_rounds": spec_rounds,
        "calc_modifier": calc_modifier,
        "output_types": output_types,
    }

    return (assemble_output(is_rich_answer, all_results, assemble_data), calc_modifier)


def get_colorama() -> dict:
    
    def stub() -> str:
        return ""
    
    keys = ["reset", "f_black", "f_white", "f_red", "f_blue", "f_yellow", "f_green", "f_cyan", "b_black", "b_white", "b_red", "b_blue", "b_yellow", "b_green", "b_cyan"]

    try:
        from colorama import init, reinit, deinit, just_fix_windows_console, Fore, Back, Style

        just_fix_windows_console()
        init(autoreset=True)
        c = {
            "reinit": reinit,
            "deinit": deinit,
            "reset": Style.RESET_ALL,
            "f_black": Fore.BLACK,
            "f_white": Fore.WHITE,
            "f_red": Fore.RED,
            "f_blue": Fore.BLUE,
            "f_yellow": Fore.YELLOW,
            "f_green": Fore.GREEN,
            "f_cyan": Fore.CYAN,
            "b_black": Back.BLACK,
            "b_white": Back.WHITE,
            "b_red": Back.RED,
            "b_blue": Back.BLUE,
            "b_yellow": Back.YELLOW,
            "b_green": Back.GREEN,
            "b_cyan": Back.CYAN,
        }

    except ModuleNotFoundError:
        print("Could not load dependency: colorama\n")

        c = {
            "reinit": stub,
            "deinit": stub,
        }

        for key in keys:
            c.update({key: ""})

    return c


def main() -> None:
    from pycore.app_controller import collect_input
    from pycore.arg_controller import init_args

    init_args()
    c = get_colorama()
    print(f"Welcome in ZM Round Calculator {c['f_yellow']}V4{c['reset']} by Zi0")
    print(f"Source: '{c['f_cyan']}https://github.com/Zi0MIX/ZM-RoundCalculator{c['reset']}'")
    print(f"Check out web implementation of the calculator under '{c['f_cyan']}https://zi0mix.github.io{c['reset']}'")
    print("Enter round number and amount of players separated by spacebar, then optional arguments")
    print("Round and Players arguments are mandatory, others are optional. Check ARGUMENTS.MD on GitHub for info.")

    while True:
        try:
            c["reinit"]()
            calc_input, scrap = collect_input()
            result, modifier = calculator_handler(calc_input)
            display_output(result, c, **display_metadata(modifier, calc_input))
            c["deinit"]()
        except Exception:
            display_output(*return_error(c))


def api(msg_to_api: dict | str) -> dict:
    from pycore.api_handler import init_apiconfig, load_api_message_from_file, verify_api_message
    from pycore.arg_controller import init_args

    try:
        init_apiconfig()
        init_args()

        if isinstance(msg_to_api, str):
            msg_to_api = load_api_message_from_file(msg_to_api)
        msg_to_api = verify_api_message(msg_to_api)

        return calculator_handler(msg_to_api)

    except Exception:
        pass


if __name__ == "__main__":
    main()
