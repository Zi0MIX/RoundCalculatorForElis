from pycore.classes import ZombieRound


def init_args():
    """Initialize global variable `ARGS`. It can then be accessed or modified using `get_args()` and `update_args()` respectivelly"""
    from config import DEFAULT_ARGUMENTS
    from pycore.api_handler import apiconfing_defined, get_apiconfig

    all_arguments = DEFAULT_ARGUMENTS

    if apiconfing_defined():
        overrides = get_apiconfig("arg_overrides")
        for high_key in overrides.keys():
            # There is no validation for keys that can be replaced, hopefully there doesn't have to be
            for low_key in overrides[high_key].keys():
                all_arguments.update({high_key[low_key]: overrides[high_key[low_key]]})

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


def resolve_argument_conflict(dict_of_args: dict, method: str = "error") -> dict:
    """Function checks if there are any conflicting argument settings, and applies selected method\n
    Avalilable methods:\n
    `ignore` - Conflicts are ignored\n
    `override` - Conflicted arguments are overridden with default values\n
    `error` - Raise an exception, that's the default method"""
    from config import CONFLICTING_ARGUMENTS, DEFAULT_ARGUMENTS

    def conflict_found(conflicting_keys: list):
        if method == "ignore":
            return
        elif method == "error":
            raise Exception(f"Following keys are in conflict {', '.join(conflicting_keys)}")
        elif method == "override":
            for key in conflicting_keys:
                # At this point in the workflow, `ARGS` is storing default values
                dict_of_args[key] = get_args(key)


    for conflict in CONFLICTING_ARGUMENTS:
        conflicting_states = 0
        keys_in_conflict = conflict.keys()
        for key in keys_in_conflict:
            if dict_of_args[key] == conflict[key]:
                conflicting_states += 1
        if conflicting_states > 1:
            conflict_found(keys_in_conflict)

    return dict_of_args


def eval_break():
    """Insert empty line if argument `break` is set to `True`"""
    if get_args("break"):
        print()
    return


def eval_save(content: str, path: str = None) -> tuple[bool, str]:

    if not get_args("save"):
        return

    import os.path
    import datetime as dt

    if path is None:
        print("Path to where the file should be saved in:")
        path = input("> ")

    filename = f"calculator{str(int(dt.datetime.now().timestamp()))}.txt"
    try:
        with open(os.path.join(path, filename), "a", encoding="utf-8") as txt_io:
            txt_io.write(content)
        print(f"Results saved in '{filename}'")
    except Exception as exc:
        print(f"Failed to save results in '{filename}'\n{exc}")

    return


def eval_hordes(class_of_round: any) -> tuple[float, str]:
    if isinstance(class_of_round, ZombieRound) and get_args("hordes"):
        return (round(class_of_round.enemies / 24, 2), "hordes")
    return (class_of_round.enemies, class_of_round.enemy_type)
