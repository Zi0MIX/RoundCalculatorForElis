import config as cfg
from dataclasses import dataclass


@dataclass
class Round:
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


    def round_spawn_delay(self):
        self.raw_spawn_delay = self.zombie_spawn_delay
        inside = str(self.zombie_spawn_delay).split(".")

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

        self.zombie_spawn_delay = float(".".join(inside))
        return


    def get_spawn_delay(self):
        self.zombie_spawn_delay = 2.0
        self.raw_spawn_delay = 2.0

        if self.number > 1:
            for _ in range(1, self.number):
                self.zombie_spawn_delay *= 0.95

            self.round_spawn_delay()

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
        self.raw_time = self.zombies * (self.zombie_spawn_delay + self.network_frame)

        # self.extract_decimals()

        return


@dataclass
class DogRound(Round):
    special_rounds: int


    def __post_init__(self):
        self.get_network_frame()
        self.get_dogs()
        self.get_dog_spawn_delay()
        self.get_total_delay()


    def get_dogs(self):
        self.dogs = self.players * 8

        if self.special_rounds < 3:
            self.dogs = self.players * 6

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
        self.raw_time = 0.0
        dog = 0
        while dog < self.dogs:
            dog += 1
            # Need to verify for gsc rounding in that value
            # maps/_zombiemode_ai_dogs ~ 238
            self.raw_time += self.dog_spawn_delay - (dog / self.dogs)


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


def get_readable_time(raw_time: int) -> str:
    h, m, s, ms = 0, 0, 0, int(raw_time * 1000)

    while ms > 999:
        s += 1
        ms -= 1000
    while s > 59:
        m += 1
        s -= 60
    while m > 59:
        h += 1
        m -= 60

    dec = f".{str(ms).zfill(3)}"
    if args["nodecimal"] and not args["lower_time"]:
        dec = ""
        s += 1
        if s > 59:
            m += 1
            s -= 60
            if m > 59:
                h += 1
                m -= 60
    elif args["nodecimal"]:
        dec = ""

    if not h and not m:
        new_time = f"{s}{dec} seconds"
    elif not h:
        new_time = f"{str(m).zfill(2)}:{str(s).zfill(2)}{dec}"
    else:
        new_time = f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}{dec}"

    return new_time


def print_perfect_times(time_total: float, rnd: int, map_code: str) -> None:

    split_adj = 0
    if args["speedrun_time"]:
        split_adj = cfg.RND_BETWEEN_NUMBER_FLAG

    readable_time = get_readable_time(time_total - split_adj)

    if args["clear_output"] and not args["detailed"]:
        print(readable_time)
    elif args["clear_output"] and args["detailed"]:
        print(readable_time * 1000)
    elif args["detailed"]:
        print(f"Perfect time to round {cfg.COL}{rnd}{cfg.RES} is {cfg.COL}{(time_total - split_adj) * 1000}{cfg.RES}ms on {cfg.COL}{map_translator(map_code)}{cfg.RES}")
    elif not args["detailed"] and not args["clear_output"]:
        print(f"Perfect time to round {cfg.COL}{rnd}{cfg.RES} is {cfg.COL}{readable_time}{cfg.RES} on {cfg.COL}{map_translator(map_code)}{cfg.RES}")

    if args["break"]:
        print()

    return


def print_round_times(rnd: Round) -> None:

    split_adj = 0
    if args["speedrun_time"]:
        split_adj = cfg.RND_BETWEEN_NUMBER_FLAG

    readable_time = get_readable_time(rnd.raw_time - split_adj)

    if args["clear_output"] and not args["detailed"]:
        print(readable_time)
    elif args["clear_output"] and args["detailed"]:
        print(readable_time * 1000)
    elif args["detailed"]:
        print(f"Round {cfg.COL}{rnd.number}{cfg.RES} will spawn in {cfg.COL}{rnd.raw_time * 1000}{cfg.RES}ms and has {cfg.COL}{rnd.zombies}{cfg.RES} zombies. Spawnrate: {cfg.COL}{rnd.zombie_spawn_delay}{cfg.RES} Network frame: {cfg.COL}{rnd.network_frame}{cfg.RES}")
    elif not args["detailed"] and not args["clear_output"]:
        print(f"Round {cfg.COL}{rnd.number}{cfg.RES} will spawn in {cfg.COL}{readable_time}{cfg.RES} and has {cfg.COL}{rnd.zombies}{cfg.RES} zombies. Spawnrate: {cfg.COL}{rnd.zombie_spawn_delay}{cfg.RES} Network frame: {cfg.COL}{rnd.network_frame}{cfg.RES}")

    if args["break"]:
        print()

    return


def calculator_custom(base_input: list, mods: list) -> None:
    for r in range(1, int(base_input[0]) + 1):
        rnd = Round(r, int(base_input[1]))
        if "-rs" in mods:
            print(rnd.raw_spawn_delay)
        if "-ps" in mods:
            print(rnd.zombie_spawn_delay)
        if "-zc" in mods:
            print(rnd.zombies)

    return


def calculator_handler():
    raw_input = input("> ").lower()
    raw_input = raw_input.split(" ")

    if not isinstance(raw_input, list) or len(raw_input) < 2:
        return

    try:
        rnd, players = int(raw_input[0]), int(raw_input[1])
    except (ValueError, IndexError):
        return

    mods = []
    map_code = ""

    result = Round(rnd, players)
    if len(raw_input) == 2:
        print_round_times(result)
        return

    global args
    args = {
        "range": False,
        "perfect_round": False,
        "clear_output": False,
        "break": True,
        "detailed": False,
        "nodecimal": False,
        "speedrun_time": True,
        "lower_time": False,
    }

    for arg in raw_input[2:]:
        if arg == "-r" or arg == "-range":
            args["range"] = True
        if arg == "-p" or arg == "-perfectround":
            args["perfect_round"] = True
        if arg == "-c" or arg == "-clearoutput":
            args["clear_output"] = True
        if arg == "-b" or arg == "-break":
            args["break"] = False
        if arg == "-d" or arg == "-detailed":
            args["detailed"] = True
        if arg == "-n" or arg == "-nodecimal":
            args["nodecimal"] = True
        if arg == "-s" or arg == "-speedruntime":
            args["speedrun_time"] = False
        if arg == "-l" or arg == "-lowertime":
            args["lower_time"] = True

        if arg == "-rs" or arg == "-rawspawnrate":
            mods.append("-rs")
        if arg == "-zc" or arg == "-zombiecount":
            mods.append("-zc")
        if arg == "-ps" or arg == "-processedspawnrate":
            mods.append("-ps")

    if len(mods):
        calculator_custom(raw_input[:2], mods)
        return

    if args["perfect_round"]:
        print("Enter map code (eg. zm_theater)")
        map_code = input("> ").lower()

        adjust_to_split = 0
        if args["speedrun_time"]:
            adjust_to_split = cfg.RND_BETWEEN_NUMBER_FLAG

        time_total = cfg.RND_WAIT_INITIAL
        time_offset = cfg.RND_WAIT_BETWEEN

        match map_code:
            case "zm_prototype" | "zm_asylum" | "zm_coast" | "zm_temple" | "zm_transit" | "zm_nuked" | "zm_prison" | "zm_buried" | "zm_tomb":

                for r in range(1, rnd):
                    result = Round(r, players)
                    time_total += result.raw_time + time_offset

                    if args["range"]:
                        print_perfect_times(time_total, result.number + 1, map_code)

                if not args["range"]:
                    print_perfect_times(time_total, result.number, map_code)


            case "zm_sumpf" | "zm_factory" | "zm_theater":
                dog_rounds = 0
                for r in range(1, rnd):

                    if r in cfg.DOGS_PERFECT:
                        result = DogRound(r, players, dog_rounds)
                        dog_rounds += 1
                        time_total += cfg.DOGS_WAIT_START
                        time_total += result.raw_time
                        time_total += cfg.DOGS_WAIT_END
                    else:
                        result = Round(r, players)
                        time_total += result.raw_time

                    time_total += time_offset

                    if args["range"]:
                        print_perfect_times(time_total, result.number + 1, map_code)

                if not args["range"]:
                    print_perfect_times(time_total, result.number, map_code)


            case _:
                print(f"Map {cfg.COL}{map_translator(map_code)}{cfg.RES} is not supported.")

        return

    if args["range"]:
        [print_round_times(Round(r, players)) for r in range (1, rnd)]
        return

    print_round_times(Round(rnd, players))

    return


def main():
    import os
    from colorama import init, reinit, deinit

    os.system("cls")    # Bodge for colorama not working after compile
    init()
    print("Welcome in ZM Round Calculator V2 by Zi0")
    print("Source: https://github.com/Zi0MIX/ZM-RoundCalculator")
    print("Enter round number and amount of players separated by spacebar, then optional arguments")
    print("Round and Players arguments are mandatory, others are optional. Check ARGUMENTS.MD on GitHub for info.")

    while True:
        reinit()
        calculator_handler()
        deinit()


if __name__ == "__main__":
    main()