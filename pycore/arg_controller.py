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


def resolve_argument_conflict(dict_of_args: dict, method: str = "error") -> dict:
    """Function checks if there are any conflicting argument settings, and applies selected method\n
    Avalilable methods:\n
    `ignore` - Conflicts are ignored\n
    `override` - Conflicted arguments are overridden with default values\n
    `error` - Raise an exception, that's the default method"""


    def conflict_found(conflicting_keys: list):
        if method == "ignore":
            return
        elif method == "error":
            raise Exception(f"Following keys are in conflict {', '.join(conflicting_keys)}")
        elif method == "override":
            default_args = get_arguments()

            for key in conflicting_keys:
                dict_of_args[key] = default_args[key]["default_state"]


    from config import CONFLICTING_ARGUMENTS

    for conflict in CONFLICTING_ARGUMENTS:
        conflicting_states = 0
        keys_in_conflict = conflict.keys()
        for key in keys_in_conflict:
            if dict_of_args[key] == conflict[key]:
                conflicting_states += 1
        if conflicting_states > 1:
            conflict_found(keys_in_conflict)

    return dict_of_args
