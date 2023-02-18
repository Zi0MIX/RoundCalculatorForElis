import numpy as np
import config as cfg
from pycore import verify_optional_input
from pycore.api_handler import apiconfing_defined, get_apiconfig
from pycore.arg_controller import get_args, get_arguments, load_args, update_args
from pycore.classes import ZombieRound, DogRound, DoctorRound, MonkeyRound, LeaperRound, PrenadesRound
from pycore.core_controller import import_dogrounds, evaluate_class_of_round, evaluate_game_time, evaluate_round_time, assemble_output, evaluate_special_round
from pycore.output_controller import map_translator, get_readable_time, display_results, return_error


def get_perfect_times(time_total: float, rnd: int, map_code: str, insta_round: bool) -> dict:

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


