def wrong_input():
    print("Wrong input!")
    return []


def split_input(user_input):
    details = []
    raw = str(user_input).split(" ")
    if len(raw) != 2:
        return wrong_input()

    for number in raw:
        try:
            n = int(number)
        except ValueError:
            return wrong_input()
        details.append(n)

    return details


def get_readable_time(time_struct):
    h, m, s = time_struct[3], time_struct[4], time_struct[5]
    if h == 0 and m == 0:
        return f"{s} seconds"
    else:
        return f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}"


def get_zombies(rnd, players):
    zombie_max_ai, zombie_ai_per_player = 24, 6

    multiplier = rnd / 5
    if multiplier < 1:
        multiplier = 1.0
    elif rnd >= 10:
        multiplier = multiplier * (rnd * 0.15)
        
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

    return max_zm


def get_spawn_delay(rnd):
    zombie_spawn_delay = 2.0

    if rnd == 1:
        return zombie_spawn_delay + NETWORK_FRAME
    
    if rnd < 65:
        while rnd > 1 and rnd < 65:
            zombie_spawn_delay *= 0.95
            rnd -= 1

        if zombie_spawn_delay < 0.08:
            zombie_spawn_delay = 0.08
    else:
        zombie_spawn_delay = 0.08

    return zombie_spawn_delay + NETWORK_FRAME


def calculate_rnd_len(zombies, sph):
    hordes = zombies / 24;
    return hordes * sph


def main():
    while True:
        print("Enter round, amount of players (example: 100 1)")
        user_input = input("> ")
        arguments = split_input(user_input)
        if not isinstance(arguments, list) or len(arguments) != 2:
            continue

        zombies = get_zombies(arguments[0], arguments[1])
        spawn_delay = get_spawn_delay(arguments[0])

        ts = gmtime(zombies * spawn_delay)
        nice_result = get_readable_time(ts)
        input(f"{zombies} zombies on round {arguments[0]} will spawn in {nice_result} with spawnrate of {round(spawn_delay, 2)}")


if __name__ == "__main__":
    NETWORK_FRAME = 0.1
    from time import gmtime
    main()