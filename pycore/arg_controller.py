def load_args():
    """Load a dictionary to global `ARGS`"""
    all_arguments = get_arguments()
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


def get_arguments() -> dict:
    from config import DEFAULT_ARGUMENTS
    from pycore.api_handler import apiconfing_defined, get_apiconfig

    default_arguments = DEFAULT_ARGUMENTS

    if apiconfing_defined():
        overrides = get_apiconfig("arg_overrides")
        for high_key in overrides.keys():
            # There is no validation for keys that can be replaced, hopefully there doesn't have to be
            for low_key in overrides[high_key].keys():
                default_arguments.update({high_key[low_key]: overrides[high_key[low_key]]})

    return default_arguments


def curate_arguments(provided_args: dict) -> dict:
    """Define new rules in the dict below.If argument `master` is different than it's default state, argument `slave` is set to it's default state.\n
    If key `eval_true` is set to `True`, function checks if argument `master` is `True`, and if so it sets argument `slave` to `False`"""
    from pycore.api_handler import apiconfing_defined, get_apiconfig

    rules = {}
    if apiconfing_defined():
        rules = get_apiconfig("new_rules")

    rules.update({
        "1": {
            "master": "detailed",
            "slave": "nodecimals",
            "eval_true": True,
        },
        "2": {
            "master": "waw_spawnrate",
            "slave": "remix",
            "eval_true": True,
        }
    })

    defaults = get_arguments()

    registered_pairs = []

    for rule in rules.keys():
        master = rules[rule]["master"]
        slave = rules[rule]["slave"]

        # Ignore rules that repeat or contradict with already applied ones
        if [master, slave] in registered_pairs or [slave, master] in registered_pairs:
            continue

        registered_pairs.append([master, slave])

        if rules[rule]["eval_true"]:
            if provided_args[master]:
                provided_args[slave] = False
        else:
            if provided_args[master] != defaults[master]["default_state"]:
                provided_args[slave] = defaults[slave]["default_state"]

    return provided_args
