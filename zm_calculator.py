from pycore.classes import ZombieRound, DogRound, DoctorRound, MonkeyRound, LeaperRound, PrenadesRound
import numpy as np
import config as cfg

def get_perfect_times(time_total: float, rnd: int, map_code: str, insta_round: bool) -> dict:
    from pycore.arg_controller import get_args
    from pycore.output_controller import map_translator, get_readable_time, get_answer_blueprint

    a = get_answer_blueprint()
    a["type"] = "perfect_times"
    a["round"] = rnd
    a["raw_time"] = time_total
    a["map_name"] = map_translator(map_code)
    a["is_insta_round"] = insta_round

    split_adj = 0.0
    if get_args("speedrun_time"):
        split_adj = cfg.RND_BETWEEN_NUMBER_FLAG

    if get_args("detailed"):
        a["time_output"] = str(round(time_total * 1000)) + " ms"
    else:
        a["time_output"] = get_readable_time(time_total - split_adj, get_args())

    return a


def get_round_times(rnd: ZombieRound | DogRound) -> dict:
    from pycore.arg_controller import get_args
    from pycore.output_controller import get_readable_time, get_answer_blueprint

    a = get_answer_blueprint()
    a["type"] = "round_time"
    a["round"] = rnd.number
    a["players"] = rnd.players
    a["zombies"] = rnd.zombies
    a["hordes"] = rnd.hordes
    a["raw_time"] = rnd.raw_time
    a["spawnrate"] = rnd.zombie_spawn_delay
    a["raw_spawnrate"] = rnd.raw_spawn_delay
    a["network_frame"] = rnd.network_frame
    a["is_insta_round"] = rnd.is_insta_round
    a["class_content"] = vars(rnd)

    split_adj = 0
    if get_args("speedrun_time"):
        split_adj = cfg.RND_BETWEEN_NUMBER_FLAG

    if get_args("detailed"):
        a["time_output"] = str(round(rnd.round_time * 1000)) + " ms"
    else:
        a["time_output"] = get_readable_time(rnd.round_time - split_adj, get_args())

    return a


def calculator_custom(rnd: int, players: int, mods: list[str]) -> list[dict]:
    from pycore.arg_controller import get_arguments
    from pycore.output_controller import get_answer_blueprint

    calc_result = []
    single_iteration = False
    for r in range(1, rnd + 1):
        zm_round = ZombieRound(r, players)
        dog_round = DogRound(r, players, r)

        a = get_answer_blueprint()
        a["type"] = "mod"
        a["round"] = r
        a["players"] = players
        a["raw_spawnrate"] = zm_round.raw_spawn_delay
        a["spawnrate"] = zm_round.zombie_spawn_delay
        a["zombies"] = zm_round.zombies
        a["health"] = zm_round.health
        a["class_content"] = vars(zm_round)
        a["message"] = ""

        if "-exc" in mods:
            raise Exception("This is a test exception")
        elif "-ga" in mods:
            rgs = get_arguments()
            a["mod"] = "-ga"
            a["message"] = "\n".join([f"{rgs[r]['shortcode']}: {rgs[r]['exp']}" for r in rgs.keys()])
            single_iteration = True
        elif "-ir" in mods:
            a["mod"] = "-ir"
            if zm_round.is_insta_round:
                a["message"] = f"Round {zm_round.number} is an insta-kill round. Zombie health: {zm_round.health}"
            else:
                continue
        elif "-rs" in mods:
            a["mod"] = "-rs"
            a["message"] = str(a["raw_spawnrate"])
        elif "-ps" in mods:
            a["mod"] = "-ps"
            a["message"] = str(a["spawnrate"])
        elif "-zc" in mods:
            a["mod"] = "-zc"
            a["message"] = str(a["zombies"])
        elif "-zh" in mods:
            a["mod"] = "-zh"
            a["message"] = str(a["health"])
        elif "-db" in mods:
            a["mod"] = "-db"
            a["message"] = str(a["class_content"])
        elif "-ddb" in mods:
            a["mod"] = "-ddb"
            a["class_content"] = vars(dog_round)
            a["message"] = str(a["class_content"])

        calc_result.append(a)

        if single_iteration:
            break

    return calc_result


def calculator_handler(calc_message: dict):
    from pycore.arg_controller import get_args, get_arguments, load_args, update_args
    from pycore.core_controller import import_dogrounds, evaluate_class_of_round, evaluate_game_time, evaluate_round_time, assemble_output, assemble_rich_output, evaluate_special_round
    from pycore.output_controller import map_translator

    def verify_optional_input(data: dict, key: str) -> any:
        if key in data.keys() and data[key] is not None and data[key]:
            return data[key]
        return None

    def parse_calculator_data(data: dict) -> tuple[int, int, str, str]:
        rnd, players = int(data["round"]), int(data["players"])
        map_code = verify_optional_input(data, "map_code")

        return (rnd, players, map_code)
    
    def parse_grenade_data(data: dict) -> dict:
        grenade_data = data["grenade_data"]
        grenades = {}
        grenades.update({"type": grenade_data["type"]})
        grenades.update({"radius": verify_optional_input(grenade_data, "radius")})
        grenades.update({"extra_damage": verify_optional_input(grenade_data, "extra_damage")})

        return grenades
    
    def evaluate_calculator_type(modifier: str) -> str:
        """Function defines the calculator type based on conditions in following order:\n
        1. Built-in mods - If built-in mod is used, that'll be prioritised\n
        2. Apiconfig mods - Then if api-defined mod is used, that'll be evaluated\n
        3. Arguments - Lastly, if argument is used that changes calc type, that'll be applied"""
        from pycore.api_handler import apiconfing_defined, get_apiconfig
        from config import MODIFIER_DEFINITIONS

        if modifier in MODIFIER_DEFINITIONS.keys():
            return MODIFIER_DEFINITIONS[modifier]
        if apiconfing_defined():
            apiconfig_mods = get_apiconfig("custom_modifiers")
            if isinstance(apiconfig_mods, dict) and modifier in apiconfig_mods.keys():
                return apiconfig_mods[modifier]
        if get_args("perfect_times"):
            return "perfect_times"
        
        return "round_times"


    # Avoid warning while calculating insta rounds
    np.seterr(over="ignore")

    # Load default argument settings and assign to global variable
    all_arguments = get_arguments()
    load_args()

    # Extract data from calc_message
    calc_data: dict = calc_message["data"]
    calc_arguments: dict = calc_message["arguments"]
    is_rich_answer = calc_message["rich_answer"]

    # Extract data from calc_data
    rnd, players, map_code = parse_calculator_data(calc_data)

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

    # Extract special rounds from calc message
    spec_rounds = verify_optional_input(calc_message, "special_rounds")
    # Special rounds array hasn't been provided or we calculating remix
    if spec_rounds is None or get_args("remix"):
        # We default to dog rounds. In the future lock others behind if statements based on map_code
        spec_rounds = cfg.DOGS_PERFECT
    # Else make sure everything is an integer
    else:
        spec_rounds = [int(d) for d in spec_rounds]

    # Extract nades setup from calc message
    grenade_setup = parse_grenade_data(calc_message)

    # Extract output types from calc message
    output_types = calc_message["output_types"]

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

    calculator_type = evaluate_calculator_type(calc_modifier)

    has_special_rounds = map_code is not None and (map_code in cfg.MAP_DOGS or map_code in cfg.MAP_DOCTOR or map_code in cfg.MAP_MONKEYS or map_code in cfg.MAP_LEAPERS)

    all_results = {}
    game_time = cfg.RND_WAIT_INITIAL

    # Initialize variables for for loop
    special_average, num_of_special_rounds = 0.0, 0

    for r in range(1, rnd + 1):
        zombie_round = ZombieRound(r, players)
        if has_special_rounds:
            dog_round = DogRound(r, players, spec_rounds)
            doc_round = DoctorRound()
            monkey_round = MonkeyRound()
            leaper_round = LeaperRound()
        else:
            dog_round = None
            doc_round = None
            monkey_round = None
            leaper_round = None
        prenades_round = PrenadesRound(r, players, grenade_setup["type"], grenade_setup["radius"], grenade_setup["extra_damage"])

        class_of_round = evaluate_class_of_round(r, spec_rounds, map_code, zombie_round, dog_round, doc_round, monkey_round, leaper_round, prenades_round)

        is_special_round = False
        if has_special_rounds:
            special_average, num_of_special_rounds, is_special_round = evaluate_special_round(special_average, num_of_special_rounds, r, class_of_round)

        round_time = evaluate_round_time(class_of_round)

        all_results.update({
            str(r): {
                "round": r,
                "players": players,
                "is_special_round": is_special_round,
                "spec_round_average": special_average,
                "num_of_spec_rounds": num_of_special_rounds,
                "round_time": round_time,
                "game_time": game_time,
                "class_of_round": class_of_round,
                "zombie_round": zombie_round,
                "dog_round": dog_round,
                "doctor_round": doc_round,
                "monkey_round": monkey_round,
                "leaper_round": leaper_round,
                "prenades_round": prenades_round,
            }
        })

        # Calculate it after updating results, the reason for it is that'll be the actual representation of gametime till specified round, eg time to round 1 will always equal to `cfg.RND_WAIT_INITIAL`. It makes the calcultion redundant for last iteration, but it's fine
        game_time = evaluate_game_time(game_time, round_time)

    assemble_data = {
        "calculator_type": calculator_type,
        "spec_rounds": spec_rounds,
        "calc_modifier": calc_modifier,
        "output_types": output_types,
    }
    if is_rich_answer:
        assemble_output(True, all_results, assemble_data)
    else:
        assemble_output(False, all_results, assemble_data)


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
    from pycore.output_controller import display_results, return_error

    c = get_colorama()
    print(f"Welcome in ZM Round Calculator {c['f_yellow']}V3{c['reset']} by Zi0")
    print(f"Source: '{c['f_cyan']}https://github.com/Zi0MIX/ZM-RoundCalculator{c['reset']}'")
    print(f"Check out web implementation of the calculator under '{c['f_cyan']}https://zi0mix.github.io{c['reset']}'")
    print("Enter round number and amount of players separated by spacebar, then optional arguments")
    print("Round and Players arguments are mandatory, others are optional. Check ARGUMENTS.MD on GitHub for info.")

    while True:
        try:
            c["reinit"]()
            result = calculator_handler(None)
            display_results(result)
            c["deinit"]()
        except Exception:
            display_results(return_error())


def api(msg_to_api: dict | str) -> dict:
    from pycore.output_controller import display_results, return_error
    import pycore.api_handler as api

    try:
        api.init_apiconfig()

        if isinstance(msg_to_api, str):
            msg_to_api = api.load_api_message_from_file(msg_to_api)
        msg_to_api = api.verify_api_message(msg_to_api)

        calculator_handler(msg_to_api)
        # display_results(calculator_handler(arguments))
        # return calculator_handler(arguments)

    except Exception:
        pass

if __name__ == "__main__":
    main()
