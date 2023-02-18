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


def init_apiconfig():
    """Load a dictionary to global `APICONFIG`, if file is not defined, load defaults"""
    import os.path
    from config import DEFAULT_APICONFIG
    from json import load

    global APICONFIG

    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apiconfig.json")
        with open(path, "r", encoding="utf-8") as rawcfg:
            api_cfg = load(rawcfg)
        APICONFIG = api_cfg

    except Exception as exc:
        APICONFIG = DEFAULT_APICONFIG


def verify_optional_input(data: dict, key: str) -> any:
    if key in data.keys() and data[key] is not None and data[key]:
        return data[key]
    return None
