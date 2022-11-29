from dataclasses import dataclass


OWN_PRINT = True
COL, RES = "", ""
DEC = 3

# Time from "initial_blackscreen_passed" to "start_of_round" triggers
RND_WAIT_INITIAL = 8.25
# Time from "end_of_round" to "start_of_round"
RND_WAIT_END = 12.50
# Time from "end_of_round" to "between_round_over"
RND_WAIT_BETWEEN = RND_WAIT_END - 2.5
# Time difference between "start_of_round" trigger and new round number appearing
RND_BETWEEN_NUMBER_FLAG = 4.0

ZOMBIE_MAX_AI = 24
ZOMBIE_AI_PER_PLAYER = 6

# Perfect dog rounds, r5 then all 4 rounders
DOGS_PERFECT = [int(x) for x in range(256) if x % 4 == 1 and x > 4]
DOGS_WAIT_START = 7.05      # 0.05 from ingame timing, code says 7 dot
DOGS_WAIT_END = 8
# Time between dog spawning to dog appearing on the map
DOGS_WAIT_TELEPORT = 1.5

MAP_LIST = ("zm_prototype", "zm_asylum", "zm_sumpf", "zm_factory", "zm_theater", "zm_pentagon", "zm_cosmodrome", "zm_coast", "zm_temple", "zm_moon", "zm_transit", "zm_nuked", "zm_highrise", "zm_prison", "zm_buried", "zm_tomb")
MAP_DOGS = ("zm_sumpf", "zm_factory", "zm_theater")


@dataclass
class ZombieRound:
    number: int
    players: int


    def __post_init__(self):
        self.get_network_frame()
        self.get_zombies()
        self.get_spawn_delay()
        self.get_round_time()


    def get_network_frame(self):
        self.network_frame = 0.05
        if self.players == 1:
            self.network_frame = 0.10

        return


    def get_round_spawn_delay(self, raw_delay: float) -> float:
        self.raw_spawn_delay = raw_delay

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

        return float(".".join(inside))


    def get_spawn_delay(self):
        self.zombie_spawn_delay = 2.0
        self.raw_spawn_delay = 2.0

        if args["remix"]:
            self.zombie_spawn_delay = 1.0
            self.raw_spawn_delay = 1.0

        if self.number > 1:
            for _ in range(1, self.number):
                self.zombie_spawn_delay *= 0.95

            self.zombie_spawn_delay = self.get_round_spawn_delay(self.zombie_spawn_delay)

            if self.zombie_spawn_delay < 0.1:
                self.zombie_spawn_delay = 0.1

        self.zombie_spawn_delay = round(self.zombie_spawn_delay, 2)

        return


    def get_zombies(self):
        multiplier = self.number / 5
        if multiplier < 1:
            multiplier = 1.0
        elif self.number >= 10:
            multiplier *= (self.number * 0.15)

        if self.players == 1:
            temp = int(ZOMBIE_MAX_AI + (0.5 * ZOMBIE_AI_PER_PLAYER * multiplier))
        else:
            temp = int(ZOMBIE_MAX_AI + ((self.players - 1) * ZOMBIE_AI_PER_PLAYER * multiplier))

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

        return


    def extract_decimals(self):
        dec = "0"
        # '> 0' could result in 00000001 triggering the expression
        if int(str(self.raw_time).split(".")[1]) >= 1:
            dec = str(self.raw_time).split(".")[1][:3]

        while len(dec) < DEC:
            dec += "0"
        self.decimals = dec

        return


    def get_round_time(self):
        delay = self.zombie_spawn_delay + self.network_frame
        self.raw_time = (self.zombies * delay) - delay
        self.round_time = round(self.raw_time, 2)

        # self.extract_decimals()

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
        self.teleport_time = DOGS_WAIT_TELEPORT * (self.dogs / (2 * self.players))
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


def return_error(err_code: Exception | str, nolist: bool = False) -> list[dict]:
    if nolist:
        return {"type": "error", "message": str(err_code)}
    return [{"type": "error", "message": str(err_code)}]


def eval_argv(cli_in: list) -> list | dict:
    try:
        cli_in = cli_in[1:]

        if cli_in[0] == "json":
            from json import loads
            cli_out = loads(" ".join(cli_in[1:]))
        elif cli_in[0] == "str":
            cli_out = cli_in[1:]
        else:
            raise TypeError("Inproper 'type' argument provided. Values have to be either 'str' or 'json'")

        return cli_out
    except (IndexError, TypeError) as err:
        return return_error(err)


def get_answer_blueprint() -> dict:
    """Check outputs.MD for reference"""
    return {
        "type": "blueprint",
        "mod": "",
        "message": "",
        "round": 0,
        "players": 0,
        "zombies": 0,
        "hordes": 0.0,
        "time_output": "00:00",
        "special_average": 0.0,
        "spawnrate": 0.0,
        "raw_spawnrate": 0.0,
        "network_frame": 0.0,
        "map_name": "",
        "class_content": {},
    }


def get_arguments() -> dict:
    return {
        "break": {
            "use_in_web": True,
            "readable_name": "Break",
            "shortcode": "-b",
            "default_state": True,
            "exp": "Display an empty line between results."
        },
        "clear": {
            "use_in_web": True,
            "readable_name": "Clear output",
            "shortcode": "-c",
            "default_state": False,
            "exp": "Show only numeric output as oppose to complete sentences. Use for datasets."
        },
        "detailed": {
            "use_in_web": True,
            "readable_name": "Detailed",
            "shortcode": "-d",
            "default_state": False,
            "exp": "Show time in miliseconds instead of formatted string."
        },
        "even_time": {
            "use_in_web": True,
            "readable_name": "Even time",
            "shortcode": "-e",
            "default_state": False,
            "exp": "Time output always has 5 symbols."
        },
        "hordes": {
            "use_in_web": True,
            "readable_name": "Hordes",
            "shortcode": "-h",
            "default_state": False,
            "exp": "Show the amount of hordes instead of the amount of zombies in the output."
        },
        "lower_time": {
            "use_in_web": True,
            "readable_name": "Lower Time",
            "shortcode": "-l",
            "default_state": False,
            "exp": "Change seconds rounding to go down instead of up."
        },
        "nodecimal": {
            "use_in_web": True,
            "readable_name": "Nodecimal",
            "shortcode": "-n",
            "default_state": True,
            "exp": "Show time without decimals."
        },
        "perfect_times": {
            "use_in_web": True,
            "readable_name": "Perfect times",
            "shortcode": "-p",
            "default_state": False,
            "exp": "Instead of perfect round times, display perfect split times for choosen map."
        },
        "range": {
            "use_in_web": True,
            "readable_name": "Range",
            "shortcode": "-r",
            "default_state": False,
            "exp": "Show results for all rounds leading to selected number."
        },
        "remix": {
            "use_in_web": True,
            "readable_name": "Remix",
            "shortcode": "-remix",
            "default_state": False,
            "exp": "Use spawn and zombie logic applied in 5and5s mod Remix."
        },
        "special_rounds": {
            "use_in_web": False,
            "readable_name": "Special rounds",
            "shortcode": "-spec",
            "default_state": False,
            "exp": "Add own set of special rounds to perfect times predictor to maps that support it."
        },
        "speedrun_time": {
            "use_in_web": True,
            "readable_name": "Speedrun time",
            "shortcode": "-s",
            "default_state": False,
            "exp": "Show times accordingly to speedrun rules, round end is on number transition instead of when zombies start spawning."
        },
        "teleport_time": {
            "use_in_web": True,
            "readable_name": "Teleport time",
            "shortcode": "-t",
            "default_state": True,
            "exp": "Adds dog appearance time to perfect dog rounds accordingly to the pattern: 't * dogs / (2 * players))'"
        },
    }


def curate_arguments(provided_args: dict) -> dict:
    """Define new rules in the dict below.If argument `master` is different than it's default state, argument `slave` is set to it's default state.\nIf key `eval_true` is set to `True`, function checks if argument `master` is `True`, and if so it sets argument `slave` to `False`"""
    rules = {
        "1": {
            "master": "detailed",
            "slave": "nodecimals",
            "eval_true": True,
        },
    }

    defaults = get_arguments()

    for rule in rules.keys():
        master = rules[rule]["master"]
        slave = rules[rule]["slave"]

        if rules[rule]["eval_true"]:
            if provided_args[master]:
                provided_args[slave] = False
        else:
            if provided_args[master] != defaults[master]["default_state"]:
                provided_args[slave] = defaults[slave]["default_state"]

    return provided_args


def convert_arguments(list_of_args: list) -> dict:
    converted = {}
    try:
        converted.update({"rounds": int(list_of_args[0])})
        converted.update({"players": int(list_of_args[1])})
        converted.update({"map_code": str(list_of_args[2])})
        # We set arguments to true, easier handling and CLI entry point can be processed fully, doesn't hurt
        converted.update({"arguments": True})
        # Currently not supported from CLI call
        converted.update({"spec_rounds": tuple()})

        default_arguments, arguments = get_arguments(), {}
        # Fill up dict with default values
        [arguments.update({a: default_arguments[a]["default_state"]}) for a in default_arguments.keys()]
        # Override arguments with opposite bool if argument is detected in input
        if len(list_of_args) > 3:
            [arguments.update({x: not default_arguments[x]["default_state"]}) for x in default_arguments.keys() if default_arguments[x]["shortcode"] in list_of_args[3:]]
        converted.update({"args": arguments})

        converted.update({"mods": []})
        if len(list_of_args) > 3:
            default_mods = get_mods()
            converted.update({"mods": [m for m in list_of_args[3:] if m in default_mods]})

        return converted
    except Exception as err:
        return return_error(str(err), nolist=True)


def get_mods() -> list:
    return ["-db", "-ddb", "-ps", "-rs", "-zc"]


def map_translator(map_code: str) -> str:
    if map_code == "zm_prototype":
        return "Nacht Der Untoten"
    if map_code == "zm_asylum":
        return "Verruckt"
    if map_code == "zm_sumpf":
        return "Shi No Numa"
    if map_code == "zm_factory":
        return "Der Riese"
    if map_code == "zm_theater":
        return "Kino Der Toten"
    if map_code == "zm_pentagon":
        return "FIVE"
    if map_code == "zm_cosmodrome":
        return "Ascension"
    if map_code == "zm_coast":
        return "Call of the Dead"
    if map_code == "zm_temple":
        return "Shangri-La"
    if map_code == "zm_moon":
        return "Moon"
    if map_code == "zm_transit":
        return "Tranzit"
    if map_code == "zm_nuked":
        return "Nuketown"
    if map_code == "zm_highrise":
        return "Die Rise"
    if map_code == "zm_prison":
        return "Mob of the Dead"
    if map_code == "zm_buried":
        return "Buried"
    if map_code == "zm_tomb":
        return "Origins"

    return map_code


def import_dogrounds() -> tuple:
    print(f"{CYA}Enter special rounds separated with space.{RES}")
    raw_special = str(input("> "))

    list_special = [int(x) for x in raw_special.split(" ") if x.isdigit()]
    if len(list_special):
        return tuple(list_special)
    return DOGS_PERFECT


def get_readable_time(round_time: float) -> str:
    h, m, s, ms = 0, 0, 0, int(round_time * 1000)

    while ms > 999:
        s += 1
        ms -= 1000
    while s > 59:
        m += 1
        s -= 60
    # Do not reduce minutes to hours if even_time is on
    if not args["even_time"]:
        while m > 59:
            h += 1
            m -= 60

    dec = f".{str(ms).zfill(3)}"
    # Clear decimals and append a second, this way it's always rounding up
    if args["nodecimal"] and not args["lower_time"]:
        dec = ""
        s += 1
        if s > 59:
            m += 1
            s -= 60
            if m > 59:
                h += 1
                m -= 60
    # Otherwise just clear decimals, it then rounds down
    elif args["nodecimal"]:
        dec = ""

    if not h and not m:
        new_time = f"{s}{dec} seconds"
    elif not h:
        new_time = f"{str(m).zfill(2)}:{str(s).zfill(2)}{dec}"
    else:
        new_time = f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}{dec}"

    if args["even_time"]:
        new_time = f"{str(m).zfill(2)}:{str(s).zfill(2)}"

    return new_time


def get_perfect_times(time_total: float, rnd: int, map_code: str) -> dict:

    a = get_answer_blueprint()
    a["type"] = "perfect_times"
    a["round"] = rnd
    a["raw_time"] = time_total
    a["map_name"] = map_translator(map_code)

    split_adj = 0.0
    if args["speedrun_time"]:
        split_adj = RND_BETWEEN_NUMBER_FLAG

    if args["detailed"]:
        a["time_output"] = str(round(time_total * 1000)) + " ms"
    else:
        a["time_output"] = get_readable_time(time_total - split_adj)

    return a


def get_round_times(rnd) -> dict:
    """Rnd: ZombieRound | DogRound"""

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
    a["class_content"] = vars(rnd)

    split_adj = 0
    if args["speedrun_time"]:
        split_adj = RND_BETWEEN_NUMBER_FLAG

    if args["detailed"]:
        a["time_output"] = str(round(rnd.round_time * 1000)) + " ms"
    else:
        a["time_output"] = get_readable_time(rnd.round_time - split_adj)

    return a


def calculator_custom(rnd: int, players: int, mods: list) -> list[dict]:
    calc_result = []
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
        a["class_content"] = vars(zm_round)

        if "-rs" in mods:
            a["mod"] = "-rs"
            a["message"] = str(a["raw_spawnrate"])
        elif "-ps" in mods:
            a["mod"] = "-ps"
            a["message"] = str(a["spawnrate"])
        elif "-zc" in mods:
            a["mod"] = "-zc"
            a["message"] = str(a["zombies"])
        elif "-db" in mods:
            a["mod"] = "-db"
            a["message"] = str(a["class_content"])
        elif "-ddb" in mods:
            a["mod"] = "-ddb"
            a["class_content"] = vars(dog_round)
            a["message"] = str(a["class_content"])

        calc_result.append(a)

    return calc_result


def calculator_handler(json_input: dict | None = None):

    # Take input if standalone app
    if json_input is None:
        raw_input = input("> ").lower()
        raw_input = raw_input.split(" ")

        try:
            if not isinstance(raw_input, list) or len(raw_input) < 2:
                raise ValueError("Wrong data input")
            rnd, players = int(raw_input[0]), int(raw_input[1])

            use_arguments = len(raw_input) > 2
        except (ValueError, IndexError) as err:
            return [{"type": err}]
    # Assign variables from json otherwise
    else:
        rnd, players, map_code = int(json_input["rounds"]), int(json_input["players"]), str(json_input["map_code"])
        # try/except clause supports transition between keys, remove later
        try:
            use_arguments = json_input["arguments"] or len(json_input["mods"])
        except KeyError:
            use_arguments = json_input["use_arguments"] or len(json_input["mods"])

    all_arguments = get_arguments()
    global args
    args = {}

    # Assemble arguments list
    [args.update({key: all_arguments[key]["default_state"]}) for key in all_arguments.keys()]

    # We do not process all the argument logic if arguments are not defined
    result = ZombieRound(rnd, players)
    if not use_arguments:
        return [get_round_times(result)]

    # Define state of arguments
    if json_input is None:
        selected_arguments = raw_input[2:]
        for key in args.keys():
            if all_arguments[key]["shortcode"] in selected_arguments:
                args.update({key: not all_arguments[key]["default_state"]})
    else:
        for key in args.keys():
            try:
                args.update({key: json_input["args"][key]})
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
    if args["perfect_times"]:

        if json_input is None:
            print("Enter map code (eg. zm_theater)")
            map_code = input("> ").lower()

        if map_code not in MAP_LIST:
            if json_input is None:
                print(f"Map {COL}{map_translator(map_code)}{RES} is not supported.")
            return return_error(f"{map_translator(map_code)} is not supported")

        time_total = RND_WAIT_INITIAL

        try:
            # Not map with dogs
            if map_code not in MAP_DOGS:
                set_dog_rounds = tuple()
            # Not specified special_rounds or is remix
            elif not args["special_rounds"] or args["remix"]:
                set_dog_rounds = DOGS_PERFECT
            # Not api mode or empty api entry provided -> take input
            elif not json_input or not len(json_input["spec_rounds"]):
                set_dog_rounds = import_dogrounds()
            # Take entry from api call
            else:
                set_dog_rounds = tuple(json_input["spec_rounds"])
        except KeyError:
            if not json_input:
                print("Warning: Key error dog rounds")
            set_dog_rounds = DOGS_PERFECT

        dog_rounds_average = 0.0
        if len(set_dog_rounds):
            from statistics import mean
            dog_rounds_average = round(mean(set_dog_rounds), 1)

        dog_rounds = 1
        for r in range(1, rnd):
            zm_round = ZombieRound(r, players)
            dog_round = DogRound(r, players, dog_rounds)

            # Handle arguments here
            if args["teleport_time"]:
                dog_round.add_teleport_time()

            is_dog_round = r in set_dog_rounds

            if is_dog_round:
                dog_rounds += 1
                round_duration = DOGS_WAIT_START + DOGS_WAIT_TELEPORT + dog_round.round_time + DOGS_WAIT_END + RND_WAIT_END
                time_total += round_duration
            else:
                round_duration = zm_round.round_time + RND_WAIT_END
                time_total += round_duration

            if args["range"]:
                remembered_dog_average = 0.0

                res = get_perfect_times(time_total, r + 1, map_code)
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

        if not args["range"]:
            res = get_perfect_times(time_total, rnd, map_code)
            res["players"] = players
            res["class_content"] = vars(zm_round)
            res["special_average"] = dog_rounds_average
            if is_dog_round:
                res["class_content"] = vars(dog_round)
            all_results.append(res)

        return all_results

    if args["range"]:
        all_results = [get_round_times(ZombieRound(r, players)) for r in range (1, rnd)]
        return all_results

    return [get_round_times(ZombieRound(rnd, players))]


def display_results(results: list[dict]) -> list[dict]:
    for res in results:

        # Assemble print
        zm_word = "zombies"
        match res["type"]:
            case "round_time":
                enemies = res["zombies"]
                if args["hordes"]:
                    zm_word = "hordes"
                    enemies = res["hordes"]

                if args["clear"]:
                    print(res["time_output"])
                else:
                    print(f"Round {COL}{res['round']}{RES} will spawn in {COL}{res['time_output']}{RES} and has {COL}{enemies}{RES} {zm_word}. (Spawnrate: {COL}{res['spawnrate']}{RES} / Network frame: {COL}{res['network_frame']}{RES}).")

                if args["break"]:
                    print()

            case "perfect_times":
                if args["clear"]:
                    print(res["time_output"])
                else:
                    print(f"Perfect time to round {COL}{res['round']}{RES} is {COL}{res['time_output']}{RES} on {COL}{res['map_name']}{RES}.")

                if args["break"]:
                    print()

            case "mod":
                print(res["message"])

            case "error":
                print("An error occured, if your inputs are correct, please contact the creator.")
                print(res["message"])

    return results


def main_app() -> None:
    import os
    from colorama import init, reinit, deinit

    os.system("cls")    # Bodge for colorama not working after compile
    init()
    print(f"Welcome in ZM Round Calculator {YEL}V3 BETA{RES} by Zi0")
    print(f"Source: '{CYA}https://github.com/Zi0MIX/ZM-RoundCalculator{RES}'")
    print(f"Check out web implementation of the calculator under '{CYA}https://zi0mix.github.io{RES}'")
    print("Enter round number and amount of players separated by spacebar, then optional arguments")
    print("Round and Players arguments are mandatory, others are optional. Check ARGUMENTS.MD on GitHub for info.")

    while True:
        reinit()
        result = calculator_handler(None)
        display_results(result)
        deinit()


def main_api(arguments: dict | list) -> dict:
    if isinstance(arguments, list):
        arguments = convert_arguments(arguments)
        # Passing error
        if "type" in arguments.keys():
            print(arguments["message"])
            return arguments

    arguments["args"] = curate_arguments(arguments["args"])

    if OWN_PRINT:
        return display_results(calculator_handler(arguments))
    return calculator_handler(arguments)

# print(__name__)
if __name__ == "__main__":
    from sys import argv

    if len(argv) > 1:
        argv = eval_argv(argv)
        main_api(argv)
    else:
        from colorama import Fore
        # For output syntax highlighting use COL variable
        COL, RES = Fore.YELLOW, Fore.RESET
        YEL, GRE, RED, CYA = Fore.YELLOW, Fore.GREEN, Fore.RED, Fore.CYAN

        # Standalone app
        main_app()
