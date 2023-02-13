from dataclasses import dataclass
import numpy as np
import config as cfg

@dataclass
class ZombieRound:
    number: int
    players: int


    def __post_init__(self):
        self.get_network_frame()
        self.get_zombies()
        self.get_spawn_delay()
        self.get_round_time()
        self.get_zombie_health()


    def get_network_frame(self):
        self.network_frame = 0.05
        if self.players == 1:
            self.network_frame = 0.10

        return


    def get_round_spawn_delay(self, raw_delay: np.float32) -> np.float32:
        """Function uses Numpy to emulate Game Engine behavior\n
        Takes float32 `raw_delay` arugment and returns float32 value"""

        self.raw_spawn_delay = np.format_float_positional(raw_delay, min_digits=16)

        if raw_delay < 0.01:
            raw_delay = 0.01

        inside = str(raw_delay).split(".")

        if not len(inside[1]):
            real_decimals = ["0", "0"]
        elif len(inside[1]) == 1:
            real_decimals = [inside[1], "0"]
        else:
            real_decimals = [str(x) for x in inside[1]][:2]

            if len(inside[1]) > 2:
                # Round decimals outside of the scope in a normal way
                dec = reversed([int(x) for x in inside[1]][2:])
                # decimals = []
                remember = 0

                for x in dec:
                    x += remember
                    remember = 0

                    if x >= 5:
                        # decimals.append("0")
                        remember = 1
                    # else:
                    #     decimals.append("0")

                if remember:
                    real_decimals[1] = str(int(real_decimals[1]) + 1)
                    if real_decimals[1] == "10":
                        real_decimals[0] = str(int(real_decimals[0]) + 1)
                        real_decimals[1] = "0"

        # Round decimals in the scope to 0.05 following GSC way
        if real_decimals[1] in ("0", "1", "2"):
            real_decimals[1] = "0"
        elif real_decimals[1] in ("3", "4", "5", "6", "7"):
            real_decimals[1] = "5"
        else:
            real_decimals[1] = "0"
            real_decimals[0] = str(int(real_decimals[0]) + 1)

            if real_decimals[0] == "10":
                real_decimals[0] = "0"
                inside[0] = str(int(inside[0]) + 1)

        inside[1] = "".join(real_decimals)
        # print(f"{inside} / original: {str(self.raw_spawn_delay).split('.')}")

        return np.float32(".".join(inside))


    def get_spawn_delay(self):
        """Function uses Numpy to emulate Game Engine behavior"""
        self.zombie_spawn_delay = np.float32(2.0)
        self.raw_spawn_delay = np.float32(2.0)

        if get_args("remix"):
            self.zombie_spawn_delay = 1.0
            self.raw_spawn_delay = 1.0
        if get_args("waw_spawnrate"):
            self.zombie_spawn_delay = 3.0
            self.raw_spawn_delay = 3.0

        if self.number > 1:
            for _ in range(1, self.number):
                self.zombie_spawn_delay *= np.float32(0.95)

            self.zombie_spawn_delay = self.get_round_spawn_delay(self.zombie_spawn_delay)

            if self.zombie_spawn_delay < 0.1:
                self.zombie_spawn_delay = np.float32(0.1)

        self.zombie_spawn_delay = round(float(self.zombie_spawn_delay), 2)

        return


    def get_zombies(self):
        multiplier = self.number / 5
        if multiplier < 1:
            multiplier = 1.0
        elif self.number >= 10:
            multiplier *= (self.number * 0.15)

        if self.players == 1:
            temp = int(cfg.ZOMBIE_MAX_AI + (0.5 * cfg.ZOMBIE_AI_PER_PLAYER * multiplier))
        else:
            temp = int(cfg.ZOMBIE_MAX_AI + ((self.players - 1) * cfg.ZOMBIE_AI_PER_PLAYER * multiplier))

        self.zombies = temp
        if self.number < 2:
            self.zombies = int(temp * 0.25)
        elif self.number < 3:
            self.zombies = int(temp * 0.3)
        elif self.number < 4:
            self.zombies = int(temp * 0.5)
        elif self.number < 5:
            self.zombies = int(temp * 0.7)
        elif self.number < 6:
            self.zombies = int(temp * 0.9)

        self.hordes = round(self.zombies / 24, 2)

        if get_args("waw_spawnrate") and self.players == 1 and self.zombies > 24:
            self.zombies = 24

        return


    def extract_decimals(self):
        dec = "0"
        # '> 0' could result in 00000001 triggering the expression
        if int(str(self.raw_time).split(".")[1]) >= 1:
            dec = str(self.raw_time).split(".")[1][:3]

        while len(dec) < cfg.DEC:
            dec += "0"
        self.decimals = dec

        return


    def get_round_time(self):
        delay = self.zombie_spawn_delay + self.network_frame
        self.raw_time = (self.zombies * delay) - delay
        self.round_time = round(self.raw_time, 2)

        # self.extract_decimals()

        return


    def get_zombie_health(self):
        """Function uses Numpy to emulate Game Engine behavior"""

        self.is_insta_round = False
        self.health = np.int32(150)

        for r in range(2, self.number + 1):
            if r < 10:
                self.health += 100
            else:
                self.health += np.int32(np.float32(self.health) * np.float32(0.1))

        if (self.health <= np.int32(150)) and (self.number > 1):
            self.is_insta_round = True

            # print(f"DEV: Round: {r} / Health: {self.health}")

        return


@dataclass
class DogRound(ZombieRound):
    special_rounds: int


    def __post_init__(self):
        self.get_network_frame()
        self.get_dogs()
        self.get_teleport_time()
        self.get_dog_spawn_delay()
        self.get_total_delay()
        self.round_up()


    def get_dogs(self):
        self.dogs = self.players * 8

        if self.special_rounds < 3:
            self.dogs = self.players * 6

        return


    def get_teleport_time(self):
        # Seems to be the best indication of representing spawncap accurately, at least in case of solo when comparing to actual gameplay
        self.teleport_time = cfg.DOGS_WAIT_TELEPORT * (self.dogs / (2 * self.players))
        return


    def get_dog_spawn_delay(self):
        self.dog_spawn_delay = 1.50

        if self.special_rounds == 1:
            self.dog_spawn_delay = 3.00
        elif self.special_rounds == 2:
            self.dog_spawn_delay = 2.50
        elif self.special_rounds == 3:
            self.dog_spawn_delay = 2.00

        return


    def get_total_delay(self):
        self.raw_time = 0
        self.delays = []
        for i in range(1, self.dogs):
            delay = self.get_round_spawn_delay(self.dog_spawn_delay - (i / self.dogs))

            self.raw_time += delay
            self.delays.append(delay)

        self.raw_time = round(self.raw_time, 2)


    def add_teleport_time(self):
        # Call if dog teleport time should be added for each dog on class level
        self.raw_time += self.teleport_time
        return


    def round_up(self):
        # round_wait() function clocks every .5 seconds
        time_in_ms = round(self.raw_time * 1000)
        if not time_in_ms % 500:
            self.round_time = self.raw_time
            return

        self.round_time = ((time_in_ms - (time_in_ms % 500)) + 500) / 1000
        return
    

@dataclass
class PrenadesRound(ZombieRound):
    nade_type: str
    radius: float = None
    extra_damage: int = None


    def __post_init__(self):
        self.explosives_handler()


    def get_nadeconfig(self) -> dict:
        nadeconfigs = {
            "frag": {
                "max_radius": np.float32(256.0),
                "min_radius": np.float32(0.0),
                "max_damage": np.int32(300),
                "min_damage": np.int32(75),
                "damage_extra_max": np.int32(200),
                "damage_extra_min": np.int32(100),
            },
            "german": {
                "max_radius": np.float32(256.0),
                "min_radius": np.float32(0.0),
                "max_damage": np.int32(200),
                "min_damage": np.int32(50),
                "damage_extra_max": np.int32(200),
                "damage_extra_min": np.int32(100),
            },
            "semtex": {
                "max_radius": np.float32(256.0),
                "min_radius": np.float32(0.0),
                "max_damage": np.int32(300),
                "min_damage": np.int32(55),
                "damage_extra_max": np.int32(200),
                "damage_extra_min": np.int32(100),
            },
        }

        return nadeconfigs[self.nade_type]
    

    def get_bmx_damage(self) -> np.int32:
        if self.nade_type == "frag":
            return np.int32(np.float32(-0.880) * np.float32(self.radius) + np.int32(300))
        elif self.nade_type == "german":
            return np.int32(np.float32(-0.585) * np.float32(self.radius) + np.int32(200))
        elif self.nade_type == "semtex":
            return np.int32(np.float32(-0.958) * np.float32(self.radius) + np.int32(300))
        else:
            raise Exception(f"Could not set BMX damage value for nade type {self.nade_type}")


    def explosives_handler(self):
        """Function uses Numpy to emulate Game Engine behavior.\n
        Available nade types are `frag`, `german`, `semtex`"""

        if not isinstance(self.radius, float):
            raise Exception(f"Wrong argument type passed to 'radius_override'. Expected '{type(float())}', received '{type(self.radius)}'")

        nadecfg = self.get_nadeconfig()

        # Get average radius or else pickup override value. Important to pass float to the function call
        if self.radius is None:
            self.radius = np.float32((nadecfg["max_radius"] + nadecfg["min_radius"]) / 2)
        else:
            self.radius = np.float32(self.radius)

        # It has to wait until radius is defined
        bmx_damage = self.get_bmx_damage()

        # Get average extra damage or else pickup override value
        if self.extra_damage is None:
            self.extra_damage = np.int32((nadecfg["damage_extra_max"] + nadecfg["damage_extra_min"]) / 2) + np.int32(self.number)
        else:
            self.extra_damage = np.int32(self.extra_damage) + np.int32(self.number)

        self.nade_damage = np.int32(bmx_damage + self.extra_damage)

        current_health = np.int32(self.health)

        nades = np.int32(0)

        # Deal with bigger numbers for high rounds
        # 400_000 and 450_000 are the fastest for computation
        number_of_nades = np.int32(400_000) // self.nade_damage
        damage = number_of_nades * self.nade_damage
        while current_health > np.int32(450_000):
            current_health -= damage
            nades += number_of_nades
            # print(f"DEV: nades: {nades} / number_of_nades: {number_of_nades} / current_health: {current_health}")

        # Get exact number when number is already low
        while self.nade_damage / current_health * np.int32(100) < np.int32(10) and current_health > np.int32(150):
            # print(f"DEV: percent: {self.nade_damage / current_health * 100}% / current_health: {current_health}")
            nades += 1
            current_health -= self.nade_damage

        self.prenades = nades

        # print(f"DEV: Bmx damage: {bmx_damage}")
        # print(f"DEV: Nade damage: {self.nade_damage}")
        # print(f"DEV: Prenades on {self.number}: {self.prenades}")


def save_results_locally(to_save: list, path_override: str = "") -> None:
    from os.path import join
    from time import localtime, time
    try:
        import PySimpleGUI as sg
    except ModuleNotFoundError:
        sg = None

    output = "\n".join(to_save)

    if path_override:
        path = path_override
    elif sg is None:
        print(f"{cfg.CYA}Enter path to where you want to save the file in{cfg.RES}")
        path = str(input("> "))
    else:
        while True:
            save_folder = sg.popup_get_folder("Save as: ", keep_on_top=True)

            if save_folder is None:
                print("Cancelled saving results.")
                return

            path = save_folder
            break

    t = localtime(time())
    a_filename = f"zm_round_calculator_{str(t[0]).zfill(4)}-{str(t[1]).zfill(2)}-{str(t[2]).zfill(2)}_{str(t[3]).zfill(2)}-{str(t[4]).zfill(2)}-{str(t[5]).zfill(2)}.txt"
    with open(join(path, a_filename), "w", encoding="utf-8") as newfile:
        newfile.write(output)

    return


def load_args():
    """Load a dictionary to global `ARGS`"""
    all_arguments = get_arguments()
    global ARGS
    ARGS = {}
    [ARGS.update({key: all_arguments[key]["default_state"]}) for key in all_arguments.keys()]
    return


def get_args(key: str = "") -> bool | dict:
    if not key:
        return ARGS
    return ARGS[key]


def update_args(key: str, state: bool = None) -> None:
    if state is None:
        ARGS[key] = not ARGS[key]
    else:
        ARGS[key] = state
    return


def return_error(nolist: bool = False) -> dict | list[dict]:
    from traceback import format_exc

    if nolist:
        return {"type": "error", "message": str(format_exc())}
    return [{"type": "error", "message": str(format_exc())}]


def get_answer_blueprint() -> dict:
    """Check outputs.MD for reference"""
    return cfg.ANSWER_BLUEPRINT


def get_arguments() -> dict:
    from pycore.api_handler import apiconfing_defined, get_apiconfig

    default_arguments = cfg.DEFAULT_ARGUMENTS

    if apiconfing_defined():
        overrides = get_apiconfig("arg_overrides")
        for high_key in overrides.keys():
            # There is no validation for keys that can be replaced, hopefully there doesn't have to be
            for low_key in overrides[high_key].keys():
                default_arguments.update({high_key[low_key]: overrides[high_key[low_key]]})

    return default_arguments


def curate_arguments(provided_args: dict) -> dict:
    """Define new rules in the dict below.If argument `master` is different than it's default state, argument `slave` is set to it's default state.\n
    If key `eval_true` is set to `True`, function checks if argument `master` is `True`, and if so it sets argument `slave` to `False`"""
    from pycore.api_handler import apiconfing_defined, get_apiconfig

    rules = {}
    if apiconfing_defined():
        rules = get_apiconfig("new_rules")

    rules.update({
        "1": {
            "master": "detailed",
            "slave": "nodecimals",
            "eval_true": True,
        },
        "2": {
            "master": "waw_spawnrate",
            "slave": "remix",
            "eval_true": True,
        }
    })

    defaults = get_arguments()

    registered_pairs = []

    for rule in rules.keys():
        master = rules[rule]["master"]
        slave = rules[rule]["slave"]

        # Ignore rules that repeat or contradict with already applied ones
        if [master, slave] in registered_pairs or [slave, master] in registered_pairs:
            continue

        registered_pairs.append([master, slave])

        if rules[rule]["eval_true"]:
            if provided_args[master]:
                provided_args[slave] = False
        else:
            if provided_args[master] != defaults[master]["default_state"]:
                provided_args[slave] = defaults[slave]["default_state"]

    return provided_args


def get_mods() -> list:
    return cfg.CALCULATOR_MODS


def import_dogrounds() -> tuple:
    print(f"{cfg.CYA}Enter special rounds separated with space.{cfg.RES}")
    raw_special = str(input("> "))

    list_special = [int(x) for x in raw_special.split(" ") if x.isdigit()]
    if len(list_special):
        return tuple(list_special)
    return cfg.DOGS_PERFECT


def get_perfect_times(time_total: float, rnd: int, map_code: str, insta_round: bool) -> dict:
    from pycore.text import map_translator, get_readable_time

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
    from pycore.text import get_readable_time

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


def calculator_handler(json_input: dict = None):
    from pycore.text import map_translator

    # Avoid warning while calculating insta rounds
    np.seterr(over="ignore")

    # Take input if standalone app
    if json_input is None:
        raw_input = input("> ").lower()
        raw_input = raw_input.split(" ")

        if not isinstance(raw_input, list) or len(raw_input) < 2:
            raise ValueError("Wrong data input")
        rnd, players = int(raw_input[0]), int(raw_input[1])

        use_arguments = len(raw_input) > 2
    # Assign variables from json otherwise
    else:
        rnd, players, map_code = int(json_input["rounds"]), int(json_input["players"]), str(json_input["map_code"])
        # try/except clause supports transition between keys, remove later
        try:
            use_arguments = json_input["arguments"] or len(json_input["mods"])
        except KeyError:
            use_arguments = json_input["use_arguments"] or len(json_input["mods"])

    all_arguments = get_arguments()
    load_args()

    # We do not process all the argument logic if arguments are not defined
    result = ZombieRound(rnd, players)
    if not use_arguments:
        return [get_round_times(result)]

    # Define state of arguments
    if json_input is None:
        selected_arguments = raw_input[2:]
        for key in get_args().keys():
            if all_arguments[key]["shortcode"] in selected_arguments:
                update_args(key)
    else:
        for key in get_args().keys():
            try:
                update_args(key, json_input["args"][key])
            # The default state of the argument is already established, the error can be ignored
            except KeyError:
                continue

    # Define state of mods
    if json_input is None:
        selected_mods = raw_input[2:]
    else:
        selected_mods = json_input["mods"]
    mods = [mod for mod in get_mods() if mod in selected_mods]

    # If mods are selected, custom calculator function entered instead
    if len(mods):
        return calculator_custom(rnd, players, mods)

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


def display_results(results: list[dict]):
    readable_results = []

    # If entered from error handler in api, args will not be defined, and they don't need to
    try:
        get_args()
    except (NameError, UnboundLocalError):
        load_args()

    for res in results:

        # Assemble print
        zm_word = "zombies"
        if res["type"] == "error":
            readable_result = f"An error occured, if your inputs are correct, please contact the creator and provide error message.\n{res['message']}"
            readable_results.append(readable_result)
            print(readable_result)

        elif res["type"] == "round_time":
            enemies = res["zombies"]
            if get_args("hordes"):
                zm_word = "hordes"
                enemies = res["hordes"]

            if get_args("clear"):
                readable_result = res["time_output"]
            else:
                readable_result = f"Round {cfg.COL}{res['round']}{cfg.RES} will spawn in {cfg.COL}{res['time_output']}{cfg.RES} and has {cfg.COL}{enemies}{cfg.RES} {zm_word}. (Spawnrate: {cfg.COL}{res['spawnrate']}{cfg.RES} / Network frame: {cfg.COL}{res['network_frame']}{cfg.RES})."

            readable_results.append(readable_result)
            print(readable_result)
            if get_args("break"):
                print()

        elif res["type"] == "perfect_times":
            if get_args("clear"):
                readable_result = res["time_output"]
            else:
                readable_result = f"Perfect time to round {cfg.COL}{res['round']}{cfg.RES} is {cfg.COL}{res['time_output']}{cfg.RES} on {cfg.COL}{res['map_name']}{cfg.RES}."

            readable_results.append(readable_result)
            print(readable_result)
            if get_args("break"):
                print()

        elif res["type"] == "mod":
            readable_result = res["message"]
            readable_results.append(readable_result)
            print(readable_result)

    readable_results = [str(st).replace(cfg.COL, "").replace(cfg.RES, "") for st in readable_results]

    if get_args("save"):
        save_results_locally(readable_results)

    return


def main_app() -> None:
    import os
    from colorama import init, reinit, deinit

    os.system("cls")    # Bodge for colorama not working after compile
    init()              # Be aware, if colorama is not present this is outside of error handler
    print(f"Welcome in ZM Round Calculator {cfg.YEL}V3{cfg.RES} by Zi0")
    print(f"Source: '{cfg.CYA}https://github.com/Zi0MIX/ZM-RoundCalculator{cfg.RES}'")
    print(f"Check out web implementation of the calculator under '{cfg.CYA}https://zi0mix.github.io{cfg.RES}'")
    print("Enter round number and amount of players separated by spacebar, then optional arguments")
    print("Round and Players arguments are mandatory, others are optional. Check ARGUMENTS.MD on GitHub for info.")

    while True:
        try:
            reinit()
            result = calculator_handler(None)
            display_results(result)
            deinit()
        except Exception:
            display_results(return_error())


def main_api(arguments: dict | list) -> dict:
    import pycore.api_handler as api

    try:
        api.init_apiconfig()

        own_print = False
        if api.apiconfing_defined():
            own_print = api.get_apiconfig("own_print")

        arguments["args"] = curate_arguments(arguments["args"])

        if own_print:
            display_results(calculator_handler(arguments))
        return calculator_handler(arguments)

    except Exception:
        if own_print:
            display_results(return_error())
        return return_error()


if __name__ == "__main__":
    try:
        from colorama import Fore
        cfg.COL, cfg.RES = Fore.YELLOW, Fore.RESET
        cfg.YEL, cfg.GRE, cfg.RED, cfg.CYA = Fore.YELLOW, Fore.GREEN, Fore.RED, Fore.CYAN
    except Exception:
        pass

    main_app()
