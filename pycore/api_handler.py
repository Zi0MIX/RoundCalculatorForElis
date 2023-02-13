def init_apiconfig():
    """Load a dictionary to global `APICONFIG`"""
    import os.path
    from json import load

    global APICONFIG
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apiconfig.json")
        with open(path, "r", encoding="utf-8") as rawcfg:
            api_cfg = load(rawcfg)
        APICONFIG = api_cfg
    except Exception as exc:
        APICONFIG = None


def apiconfing_defined() -> bool:
    """Return a bool depending whether `APICONFIG` is in global scope and is an instance of dictionary"""

    try:
        if isinstance(APICONFIG, dict):
            return True
    except Exception:
        pass

    return False


def get_apiconfig(key: str = "") -> dict | None:
    """Return either `key` from `APICONFIG` or the `APICONFIG` as a whole"""

    try:
        APICONFIG
    except (NameError, UnboundLocalError):
        init_apiconfig()

    if isinstance(APICONFIG, dict) and key:
        return APICONFIG["api"][key]
    elif isinstance(APICONFIG, dict):
        return APICONFIG["api"]
    return APICONFIG


def eval_argv(cli_in: list[str]) -> list:
    """Return arvgs without filename"""
    return cli_in[1:]


def convert_arguments(list_of_args: list[str], arguments: dict, mods: list) -> dict:
    converted = {}
    converted.update({"rounds": int(list_of_args[0])})
    converted.update({"players": int(list_of_args[1])})
    try:
        converted.update({"map_code": str(list_of_args[2])})
    except IndexError:
        converted.update({"map_code": "unspecified"})
    # We set arguments to true, easier handling and CLI entry point can be processed fully, doesn't hurt
    converted.update({"arguments": True})
    # Currently not supported from CLI call
    converted.update({"spec_rounds": tuple()})

    default_arguments, arguments = arguments, {}
    # Fill up dict with default values
    [arguments.update({a: default_arguments[a]["default_state"]}) for a in default_arguments.keys()]
    # Override arguments with opposite bool if argument is detected in input
    if len(list_of_args) > 3:
        [arguments.update({x: not default_arguments[x]["default_state"]}) for x in default_arguments.keys() if default_arguments[x]["shortcode"] in list_of_args[3:]]
    converted.update({"args": arguments})

    converted.update({"mods": []})
    if len(list_of_args) > 3:
        converted.update({"mods": [m for m in list_of_args[3:] if m in mods]})

    return converted
