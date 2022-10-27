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


    def round_spawn_delay(self):
        """https://docs.google.com/spreadsheets/d/12uRE4LLZPrNT3Or6CPajfgOYHg_deIKNLB_46ZWL3Ho/edit?usp=sharing"""

        self.zombie_spawn_delay = round(self.zombie_spawn_delay, 2)

        # All kinds of loving exceptions like that
        if self.number in (2, 3, 5, 9):
            self.zombie_spawn_delay += 0.10
        elif self.number < 20 or self.number in (22, 23, 25, 27, 29, 31):
            self.zombie_spawn_delay += 0.05

        saved_spawn = 0.0
        while (self.zombie_spawn_delay > 0.10):
            self.zombie_spawn_delay -= 0.10
            saved_spawn += 0.10

        if self.zombie_spawn_delay < 0.015:
            self.zombie_spawn_delay = 0.00
        elif self.zombie_spawn_delay < 0.065:
            self.zombie_spawn_delay = 0.05
        else:
            self.zombie_spawn_delay = 0.10
        self.zombie_spawn_delay += saved_spawn

        return


    def get_spawn_delay(self):
        self.zombie_spawn_delay = 2.0

        if self.number > 1:
            for _ in range(self.number):
                self.zombie_spawn_delay *= 0.95

            self.round_spawn_delay()

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


    def get_round_time(self):
        self.raw_time = self.zombies * (self.zombie_spawn_delay + self.network_frame)
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


def get_readable_time(raw_time) -> str:
    d, h, m, s = raw_time[2], raw_time[3], raw_time[4], raw_time[5]
    if d > 1:   # It always has at least 1
        new_time = f"{str(h + ((d - 1) * 24)).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}"
    elif h == 0 and m == 0:
        new_time = f"{s} seconds"
    elif h == 0:
        new_time = f"{str(m).zfill(2)}:{str(s).zfill(2)}"
    else:
        new_time = f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}"

    return new_time


def calculator_handler(fc, fr):
    raw_input = input("> ").lower()
    raw_input = raw_input.split(" ")

    if not isinstance(raw_input, list) or len(raw_input) < 2:
        return

    try:
        rnd, players = int(raw_input[0]), int(raw_input[1])
    except (ValueError, IndexError):
        return

    arg_range, arg_perfect_round, arg_clear_output = False, False, False
    map_name = ""

    result = Round(rnd, players)
    if len(raw_input) == 2:
        print(f"Round {fc}{rnd}{fr} will spawn in {fc}{get_readable_time(result.round_time)}{fr} and consist of {fc}{result.zombies}{fr} zombies. Network frame: {fc}{result.network_frame}{fr}\n")
    else:
        for arg in raw_input[2:]:
            if arg == "-r":
                arg_range = True
            if arg == "-p":
                arg_perfect_round = True
            if arg == "c":
                arg_clear_output = True

        if arg_perfect_round:
            print("Enter map code (eg. zm_theater)")
            map_name = input("> ").lower()

            time_total = cfg.RND_WAIT_INITIAL
            match map_name:
                case "zm_prototype" | "zm_asylum" | "zm_coast" | "zm_temple" | "zm_transit" | "zm_nuked" | "zm_prison" | "zm_buried" | "zm_tomb":
                    for r in range(1, rnd):
                        time_total += Round(r, players).raw_time
                        time_total += cfg.RND_WAIT_BETWEEN

                        if arg_range and arg_clear_output:
                            print(get_readable_time(gmtime(time_total)))
                        elif arg_range:
                            print(f"Perfect time to round {fc}{r + 1}{fr} is {fc}{get_readable_time(gmtime(time_total))}{fr} on {fc}{map_name}{fr}\n")

                    if not arg_range and arg_clear_output:
                        print(get_readable_time(gmtime(time_total)))
                    elif not arg_range:
                        print(f"Perfect time to round {fc}{rnd + 1}{fr} is {fc}{get_readable_time(gmtime(time_total))}{fr} on {fc}{map_name}{fr}\n")


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
                    print(f"Map {fc}{map_name}{fr} is not supported.")

            return

        if arg_range:
            for r in range(1, rnd):
                result = Round(r, players)
                if arg_clear_output:
                    print(get_readable_time(result.round_time))
                else:
                    print(f"Round {fc}{r}{fr} will spawn in {fc}{get_readable_time(result.round_time)}{fr} and consist of {fc}{result.zombies}{fr} zombies. Network frame: {fc}{result.network_frame}{fr}\n")

            return

        if arg_clear_output:
            print(get_readable_time(result.round_time))
        else:
            print(f"Round {fc}{rnd}{fr} will spawn in {fc}{get_readable_time(result.round_time)}{fr} and consist of {fc}{result.zombies}{fr} zombies. Network frame: {fc}{result.network_frame}{fr}\n")

    return


def main():
    import os
    from colorama import Fore, init, reinit, deinit

    os.system("cls")    # Bodge for colorama not working after compile
    init()
    print("Welcome in ZM Round Calculator V2 by Zi0")
    print("Source: https://github.com/Zi0MIX/ZM-RoundCalculator")
    print("Enter round number and amount of players separated by spacebar, then optional arguments")
    print("Round and Players arguments are mandatory, others are optional. Check ARGUMENTS.MD on GitHub for info.")

    FC, FR = Fore.CYAN, Fore.RESET
    
    while True:
        reinit()
        calculator_handler(FC, FR)
        deinit()


if __name__ == "__main__":
    main()