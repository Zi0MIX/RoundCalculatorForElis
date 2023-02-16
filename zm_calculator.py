from pycore.classes import ZombieRound, DogRound, PrenadesRound
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
    from pycore.class_controller import import_dogrounds
    from pycore.mods_controller import get_mods
    from pycore.output_controller import map_translator

    def verify_optional_input(data: dict, key: str) -> any:
        if key in data.keys() and data[key] is not None and data[key]:
            return data[key]
        return None

    def parse_calculator_data(data: dict) -> tuple[int, int, str, str]:
        rnd, players = int(data["round"]), int(data["players"])
        map_code = verify_optional_input(data, "map_code")

        return (rnd, players, map_code)

    # Avoid warning while calculating insta rounds
    np.seterr(over="ignore")

    # Load default argument settings and assign to global variable
    all_arguments = get_arguments()
    load_args()

    # Extract data from calc_message
    is_api: bool = calc_message["mode"] == "api"
    calc_data: dict = calc_message["data"]
    calc_arguments: dict = calc_message["arguments"]

    # Extract data from calc_data
    rnd, players, map_code, modifier = parse_calculator_data(calc_data)

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

    ### ENDMARK ###

    all_results = []

    # Process perfect splits
    if get_args("perfect_times"):

        if json_input is None:
            print("Enter map code (eg. zm_theater)")
            map_code = input("> ").lower()

        if map_code not in cfg.MAP_LIST:
            if json_input is None:
                print(f"Map {cfg.COL}{map_translator(map_code)}{cfg.RES} is not supported.")
            raise ValueError(f"{map_translator(map_code)} is not supported")

        time_total = cfg.RND_WAIT_INITIAL

        try:
            # Not map with dogs
            if map_code not in cfg.MAP_DOGS:
                set_dog_rounds = tuple()
            # Not specified special_rounds or is remix
            elif not get_args("special_rounds") or get_args("remix"):
                set_dog_rounds = cfg.DOGS_PERFECT
            # Not api mode or empty api entry provided -> take input
            elif not json_input or not len(json_input["spec_rounds"]):
                set_dog_rounds = import_dogrounds()
            # Take entry from api call
            else:
                set_dog_rounds = tuple(json_input["spec_rounds"])
        except KeyError:
            if not json_input:
                print("Warning: Key error dog rounds")
            set_dog_rounds = cfg.DOGS_PERFECT

        dog_rounds_average = 0.0
        if len(set_dog_rounds):
            from statistics import mean
            dog_rounds_average = round(mean(set_dog_rounds), 1)

        dog_rounds = 1
        for r in range(1, rnd):
            zm_round = ZombieRound(r, players)
            dog_round = DogRound(r, players, dog_rounds)

            # Handle arguments here
            if get_args("teleport_time"):
                dog_round.add_teleport_time()

            is_dog_round = r in set_dog_rounds

            if is_dog_round:
                dog_rounds += 1
                round_duration = cfg.DOGS_WAIT_START + cfg.DOGS_WAIT_TELEPORT + dog_round.round_time + cfg.DOGS_WAIT_END + cfg.RND_WAIT_END
                time_total += round_duration
            else:
                round_duration = zm_round.round_time + cfg.RND_WAIT_END
                time_total += round_duration

            if get_args("range"):
                remembered_dog_average = 0.0

                res = get_perfect_times(time_total, r + 1, map_code, zm_round.is_insta_round)
                res["players"] = players
                res["class_content"] = vars(zm_round)
                res["special_average"] = remembered_dog_average
                if is_dog_round:
                    res["class_content"] = vars(dog_round)

                    # Get new average on each dog round
                    temp_dog_rounds = [d for d in set_dog_rounds if d <= r]
                    res["special_average"] = round(sum(temp_dog_rounds) / len(temp_dog_rounds), 1)
                    remembered_dog_average = res["special_average"]

                all_results.append(res)

        if not get_args("range"):
            res = get_perfect_times(time_total, rnd, map_code, zm_round.is_insta_round)
            res["players"] = players
            res["class_content"] = vars(zm_round)
            res["special_average"] = dog_rounds_average
            if is_dog_round:
                res["class_content"] = vars(dog_round)
            all_results.append(res)

        return all_results

    if get_args("range"):
        all_results = [get_round_times(ZombieRound(r, players)) for r in range (1, rnd)]
        return all_results

    return [get_round_times(ZombieRound(rnd, players))]


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
