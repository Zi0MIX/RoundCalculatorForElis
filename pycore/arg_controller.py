from . import ARGS


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
