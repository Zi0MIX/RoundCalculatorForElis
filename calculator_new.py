import config as cfg
from dataclasses import dataclass
from time import gmtime


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


    def get_spawn_delay(self):
        self.zombie_spawn_delay = 2.0

        if self.number > 1:
            for _ in range(self.number):
                self.zombie_spawn_delay *= 0.95

            if self.zombie_spawn_delay < 0.2 and self.players == 1:
                self.zombie_spawn_delay = 0.2
            elif self.zombie_spawn_delay < 0.15:
                self.zombie_spawn_delay = 0.15

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

        self.extract_decimals()
        self.round_time = gmtime(self.raw_time)

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

        self.round_time = gmtime(self.raw_time)


def map_translator(map_code: str) -> str:
    # Add translations here
    return map_code


def get_readable_time(raw_time, decimals: str, nodecimal: bool) -> str:
    d, h, m, s = raw_time[2], raw_time[3], raw_time[4], raw_time[5]
    dec = f".{decimals}"
    if nodecimal:
        dec = ""
        s += 1
        if s > 59:
            m += 1
            s -= 60
            if m > 59:
                h += 1
                m -= 60

    if d > 1:   # It always has at least 1
        new_time = f"{str(h + ((d - 1) * 24)).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}{dec}"
    elif h == 0 and m == 0:
        new_time = f"{s}{dec} seconds"
    elif h == 0:
        new_time = f"{str(m).zfill(2)}:{str(s).zfill(2)}{dec}"
    else:
        new_time = f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}{dec}"

    return new_time


def print_times(time_to_print: str, round_number: int, map_code: str, arg_break: bool, clear_output: bool = False) -> None:

    if clear_output:
        print(time_to_print)
    else:
        print(f"Perfect time to round {cfg.COL}{round_number}{cfg.RES} is {cfg.COL}{time_to_print}{cfg.RES} on {cfg.COL}{map_code}{cfg.RES}")
        if arg_break:
            print()
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

    arg_speedrun_time, arg_break = True, True
    arg_range, arg_perfect_round, arg_clear_output, arg_detailed, arg_nodecimal = False, False, False, False, False
    map_code = ""

    result = Round(rnd, players)
    if len(raw_input) == 2:
        print(f"Round {cfg.COL}{rnd}{cfg.RES} will spawn in {cfg.COL}{get_readable_time(result.round_time, result.decimals, False)}{cfg.RES} and consist of {cfg.COL}{result.zombies}{cfg.RES} zombies. Network frame: {cfg.COL}{result.network_frame}{cfg.RES}\n")
    else:
        for arg in raw_input[2:]:
            if arg == "-r":
                arg_range = True
            if arg == "-p":
                arg_perfect_round = True
            if arg == "-c":
                arg_clear_output = True
            if arg == "-b":
                arg_break = False
            if arg == "-d":
                arg_detailed = True
            if arg == "-n":
                arg_nodecimal = True
            if arg == "-s":
                arg_speedrun_time = False

        if arg_perfect_round:
            print("Enter map code (eg. zm_theater)")
            map_code = input("> ").lower()
            map_name = map_translator(map_code)

            adjust_to_split = 0
            if arg_speedrun_time:
                adjust_to_split = cfg.RND_BETWEEN_NUMBER_FLAG

            time_total = cfg.RND_WAIT_INITIAL
            match map_code:
                case "zm_prototype" | "zm_asylum" | "zm_coast" | "zm_temple" | "zm_transit" | "zm_nuked" | "zm_prison" | "zm_buried" | "zm_tomb":
                    for r in range(1, rnd):
                        result = Round(r, players)
                        time_total += result.raw_time
                        time_total += cfg.RND_WAIT_BETWEEN

                        if arg_detailed:
                           readable_time = f"{int((time_total - adjust_to_split) * 1000)} ms"
                        else:
                            readable_time = get_readable_time(gmtime(time_total - adjust_to_split), result.decimals, arg_nodecimal)

                        if arg_range and arg_clear_output:
                            print_times(readable_time, r + 1, map_code, arg_break, clear_output=True)
                        elif arg_range:
                            print_times(readable_time, r + 1, map_code, arg_break)

                    if arg_detailed:
                        readable_time = f"{int((time_total - adjust_to_split) * 1000)} ms"
                    else:
                        readable_time = get_readable_time(gmtime(time_total - adjust_to_split), result.decimals, arg_nodecimal)

                    if not arg_range and arg_clear_output:
                        print_times(readable_time, rnd, map_code, arg_break, clear_output=True)
                    elif not arg_range:
                        print_times(readable_time, rnd, map_code, arg_break)


                case "zm_sumpf" | "zm_factory" | "zm_theater":
                    dog_rounds = 0
                    for r in range(rnd):
                        r += 1

                        if r in cfg.DOGS_PERFECT:
                            dog_rounds += 1
                            time_total += cfg.DOGS_WAIT_START
                            time_total += DogRound(r, players, dog_rounds).raw_time
                            time_total += cfg.DOGS_WAIT_END
                        else:
                            time_total += Round(r, players).raw_time

                        time_total += cfg.RND_WAIT_BETWEEN

                case _:
                    print(f"Map {cfg.COL}{map_code}{cfg.RES} is not supported.")

            return

        if arg_range:
            for r in range(1, rnd):
                result = Round(r, players)
                if arg_detailed:
                    readable_time = f"{int(result.raw_time * 1000)} ms"
                else:
                    readable_time = get_readable_time(result.round_time, result.decimals, arg_nodecimal)

                if arg_clear_output:
                    print(readable_time)
                else:
                    print(f"Round {cfg.COL}{r}{cfg.RES} will spawn in {cfg.COL}{readable_time}{cfg.RES} and consist of {cfg.COL}{result.zombies}{cfg.RES} zombies. Network frame: {cfg.COL}{result.network_frame}{cfg.RES}")
                    if arg_break:
                        print()

            return

        if arg_detailed:
            readable_time = f"{int(result.raw_time * 1000)} ms"
        else:
            readable_time = get_readable_time(result.round_time, result.decimals, arg_nodecimal)

        if arg_clear_output:
            print(readable_time)
        else:
            print(f"Round {cfg.COL}{rnd}{cfg.RES} will spawn in {cfg.COL}{readable_time}{cfg.RES} and consist of {cfg.COL}{result.zombies}{cfg.RES} zombies. Network frame: {cfg.COL}{result.network_frame}{cfg.RES}")
            if arg_break:
                print()

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