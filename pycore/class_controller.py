from pycore.classes import ZombieRound, DogRound, PrenadesRound


def import_dogrounds() -> tuple:
    from config import CYA, RES, DOGS_PERFECT
    print(f"{CYA}Enter special rounds separated with space.{RES}")
    raw_special = str(input("> "))

    list_special = [int(x) for x in raw_special.split(" ") if x.isdigit()]
    if len(list_special):
        return tuple(list_special)
    return DOGS_PERFECT



def assemble_output_from_class(calc_mode: str, zombie_round: ZombieRound = None, dog_round: DogRound = None, prenade_round: PrenadesRound = None):
    """Function assembles a dictionary using data from provided classes"""
    from pycore.output_controller import get_answer_blueprint

    a = get_answer_blueprint()
    a["type"] = calc_mode

