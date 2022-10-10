def spawn_override(rnd):
    overrides = {
        "1": 2,
        "2": 1.9,
        "3": 1.8,
        "4": 1.7,
        "5": 1.65,
        "6": 1.55,
        "7": 1.45,
        "8": 1.4,
        "9": 1.35,
        "10": 1.25,
        "11": 1.2,
        "12": 1.15,
        "13": 1.1,
        "14": 1.05,
        "15": 1,
        "16": 0.95,
        "17": 0.9,
        "18": 0.85,
        "19": 0.8,
        "20": 0.75,
        "21": 0.7,
        "22": 0.7,
        "23": 0.65,
        "24": 0.6,
        "25": 0.6,
        "26": 0.55,
        "27": 0.55,
        "28": 0.5,
        "29": 0.5,
        "30": 0.45,
        "31": 0.45,
        "32": 0.4,
        "33": 0.4,
        "34": 0.35,
        "35": 0.35,
        "36": 0.35,
        "37": 0.3,
        "38": 0.3,
        "39": 0.3,
        "40": 0.25,
        "41": 0.25,
        "42": 0.25,
        "43": 0.25,
        "44": 0.2,
        "45": 0.2,
        "46": 0.2,
        "47": 0.2,
        "48": 0.2,
        "49": 0.15,
        "50": 0.15,
        "51": 0.15,
        "52": 0.15,
        "53": 0.15,
        "54": 0.15,
        "55": 0.15,
        "56": 0.1,
        "57": 0.1,
        "58": 0.1,
        "59": 0.1,
        "60": 0.1,
        "61": 0.1,
        "62": 0.1,
        "63": 0.1,
    }

    return overrides[str(rnd)]

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


def round_spawn_delay(spawn: float) -> float:
    # spawn += 0.05

    # saved_spawn = 0.0
    # while (spawn > 0.10):
    #     spawn -= 0.10
    #     saved_spawn += 0.10

    # if spawn > 0.05:
    #     spawn = 0.10
    # else:
    #     spawn = 0.05
    # spawn += saved_spawn

    # if CALC_DEBUG:
    #     print(f"spawn: {spawn} / saved_spawn: {saved_spawn}")

    # return round(spawn, 4)
    return spawn


def get_spawn_delay(rnd):
    zombie_spawn_delay = 2.0

    if rnd == 1:
        return zombie_spawn_delay
    
    for _ in range(0, rnd):
        zombie_spawn_delay *= 0.95

    if CALC_DEBUG:
        print(f"zombie_spawn_delay: {zombie_spawn_delay}")

    zombie_spawn_delay = round_spawn_delay(zombie_spawn_delay)

    # This check should now be obsolete
    if zombie_spawn_delay < 0.08:
        zombie_spawn_delay = 0.08

    return zombie_spawn_delay


def get_network_frame(players: int) -> float:
    if players == 1:
        return 0.10
    return 0.05


def print_sequence():
    network_frame = get_network_frame(1)
    for x in range(1, 65):
        zombies = get_zombies(x, 1)
        spawn_delay = get_spawn_delay(x) + network_frame
        ts = gmtime(zombies * spawn_delay)
        nice_result = get_readable_time(ts)
        # print(f"{zombies} zombies on round {x} will spawn in {nice_result} with spawnrate of {round(spawn_delay, 2)} (network frame: {network_frame})")
        print(spawn_delay)
    return


def main():
    while True:
        print("Enter round, amount of players (example: 100 1)")
        user_input = input("> ")
        if user_input == "printall":
            print_sequence()
            continue

        arguments = split_input(user_input)
        if not isinstance(arguments, list) or len(arguments) != 2:
            continue

        network_frame = get_network_frame(arguments[1])

        zombies = get_zombies(arguments[0], arguments[1])
        if OVERRIDE_SPAWN:
            spawn_delay = spawn_override(arguments[0])
        else:
            spawn_delay = get_spawn_delay(arguments[0])

        spawn_delay += network_frame

        ts = gmtime(zombies * spawn_delay)
        nice_result = get_readable_time(ts)
        input(f"{zombies} zombies on round {arguments[0]} will spawn in {nice_result} with spawnrate of {round(spawn_delay, 2)} (network frame: {network_frame})")


if __name__ == "__main__":
    CALC_DEBUG = False
    OVERRIDE_SPAWN = False
    from time import gmtime
    main()