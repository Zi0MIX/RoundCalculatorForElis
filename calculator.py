def split_input(user_input: str) -> list | bool:
    if " " not in user_input:
        return False

    raw = str(user_input).split(" ")
    try:
        details = [int(x) for x in raw]
    except ValueError:
        return False

    return details


def get_readable_time(time_struct: list) -> str:
    d, h, m, s = time_struct[2], time_struct[3], time_struct[4], time_struct[5]
    if d > 1:   # It always has at least 1
        return f"{str(h + ((d - 1) * 24)).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}"
    elif h == 0 and m == 0:
        return f"{s} seconds"
    elif h == 0:
        return f"{str(m).zfill(2)}:{str(s).zfill(2)}"
    else:
        return f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}"


def get_zombies(rnd: int, players: int) -> int:
    zombie_max_ai, zombie_ai_per_player = 24, 6

    multiplier = rnd / 5
    if multiplier < 1:
        multiplier = 1.0
    elif rnd >= 10:
        multiplier *= (rnd * 0.15)
 
    if players == 1:
        temp = int(zombie_max_ai + (0.5 * zombie_ai_per_player * multiplier))
    else:
        temp = int(zombie_max_ai + ((players - 1) * zombie_ai_per_player * multiplier))

    max_zm = temp
    if rnd < 2:
        max_zm = int(temp * 0.25)
    elif rnd < 3:
        max_zm = int(temp * 0.3)
    elif rnd < 4:
        max_zm = int(temp * 0.5)
    elif rnd < 5:
        max_zm = int(temp * 0.7)
    elif rnd < 6:
        max_zm = int(temp * 0.9)

    if CALC_DEBUG:
        print(f"multiplier: {multiplier} / temp: {temp} / max_zm: {max_zm}")

    return max_zm


def get_dogs(rnd: int, players: int, doground_count: int) -> int:

    dogs_default = 6
    if doground_count > 2:
        dogs_default = 8
    
    return int(dogs_default * players)


def get_dogs_spawnrate(doground_count: int) -> float:
    
    spawnrate = 1.5
    if doground_count == 1:
        spawnrate = 3.0
    elif doground_count == 2:
        spawnrate = 2.5
    elif doground_count == 3:
        spawnrate = 2.0

    return spawnrate


def round_spawn_delay(spawn: float, rnd: int) -> float:
    """https://docs.google.com/spreadsheets/d/12uRE4LLZPrNT3Or6CPajfgOYHg_deIKNLB_46ZWL3Ho/edit?usp=sharing"""

    spawn = round(spawn, 2)

    # All kinds of loving exceptions like that
    if rnd in (2, 3, 5, 9):
        spawn += 0.10
    elif rnd < 20 or rnd in (22, 23, 25, 27, 29, 31):
        spawn += 0.05

    saved_spawn = 0.0
    while (spawn > 0.10):
        spawn -= 0.10
        saved_spawn += 0.10

    if spawn < 0.015:
        spawn = 0.00
    elif spawn < 0.065:
        spawn = 0.05
    else:
        spawn = 0.10
    spawn += saved_spawn

    if CALC_DEBUG:
        print(f"spawn: {spawn} / saved_spawn: {saved_spawn}")

    return spawn


def get_spawn_delay(rnd: int, players: int) -> float:
    zombie_spawn_delay = 2.0

    if rnd == 1:
        return zombie_spawn_delay

    for _ in range(rnd):
        zombie_spawn_delay *= 0.95

    if CALC_DEBUG:
        print(f"zombie_spawn_delay: {zombie_spawn_delay}")

    zombie_spawn_delay = round_spawn_delay(zombie_spawn_delay, rnd)

    if zombie_spawn_delay < 0.2 and players == 1:
        zombie_spawn_delay = 0.2
    elif zombie_spawn_delay < 0.15:
        zombie_spawn_delay = 0.15

    return zombie_spawn_delay


def get_network_frame(players: int) -> float:
    if players == 1:
        return 0.10
    return 0.05


def main():
    from colorama import Fore, init, reinit, deinit
    import os

    os.system("cls")    # Bodge for colorama not working after compile
    print("Welcome in perfect round times calculator by Zi0.")
    print("Source: https://github.com/Zi0MIX/ZM-RoundCalculator")
    print("Enter values separated by spacebar: (round) (players) (range)")
    print("Round and Players arguments are mandatory, others are optional. Check ARGUMENTS.MD on GitHub for info.")

    init()
    FR, FC = Fore.RESET, Fore.CYAN
    _rnd_wait_initial, _between_round_wait = 10.25, 12.50
    _perfect_dog_rounds = [int(x) for x in range(256) if x % 4 == 1 and x > 4]
    _dog_wait_start, _dog_wait_end = 7, 8

    while True:
        user_input = input("> ")

        arguments = split_input(user_input)
        if not isinstance(arguments, list) or len(arguments) < 2:
            continue

        players = arguments[1]

        round_range = [arguments[0]]
        if len(arguments) >= 3 and arguments[2]:
            round_range = range(1, arguments[0])

        network_frame = get_network_frame(players)

        get_perfect_round_times = False
        ingame_time = _rnd_wait_initial
        if len(arguments) >= 4 and arguments[3]:
            get_perfect_round_times = True

        calculate_with_dogs = False
        dog_round_count = 0
        if len(arguments) >= 5 and arguments[4]:
            calculate_with_dogs = True

        reinit()
        for rnd in round_range:
            zombies = get_zombies(rnd, players)
            spawn_delay = get_spawn_delay(rnd, players)

            spawn_delay += network_frame

            raw = zombies * spawn_delay
            ts = gmtime(raw)
            nice_result = get_readable_time(ts)

            if len(str(spawn_delay)) == 3:
                spawn_delay = str(f"{spawn_delay}0")
            else:
                spawn_delay = str(round(spawn_delay, 2))

            if get_perfect_round_times:
                if rnd in (30, 50, 70, 100, 163, 200, 255):
                # if rnd in range(31):
                    print(f"Theoritical fastest time to round {rnd} for {players} players: {get_readable_time(gmtime(ingame_time))}")

                if rnd in _perfect_dog_rounds and calculate_with_dogs:
                    dog_round_count += 1
                    dogs = get_dogs(rnd, players, dog_round_count)
                    spawnrate = get_dogs_spawnrate(dog_round_count)
                    raw = dogs * spawnrate
                    ingame_time += _dog_wait_start + _dog_wait_end

                ingame_time += raw + _between_round_wait
            else:
                # print(f"Round {FC}{rnd}{FR} will spawn in {FC}{nice_result}{FR} and consist of {FC}{zombies}{FR} zombies. Network frame: {FC}{network_frame}{FR}\n")
                print(nice_result)

        deinit()


if __name__ == "__main__":
    CALC_DEBUG = False
    from time import gmtime
    main()