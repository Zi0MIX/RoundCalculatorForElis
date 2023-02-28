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
        APICONFIG = dict()
        APICONFIG["api"] = DEFAULT_APICONFIG


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
        return None

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


def load_api_message_from_file(path: str) -> dict:
    from json import load

    # No need for try/except, will be caught in api()
    with open(path, "r", encoding="utf-8") as json_io:
        json_data: dict = load(json_io)

    return json_data


def verify_api_message(message: dict) -> dict:
    """Function verifies message from api. If optional arguments are missing, they're set to default values, if mandatory arguments are missing, an Exception is raised"""

    def basic_verification(key: str, content: any, type_expected: type) -> None:
        """Function verifies base properties of mandatory keys"""
        if not len(content):
            raise Exception(f"Failed api message verification: '{key}' is not defined")
        if not isinstance(content, type_expected):
            raise Exception(f"Failed api message verification: '{key}' has wrong type. Expected {type(type_expected)} got {type(content)}")


    def check_output_definitions(key: str = "output_types"):
        outputs: dict = message[key]
        basic_verification(key, outputs, dict)

        fixes = {}
        for k, definition in outputs.items():
            if "pattern" not in definition.keys():
                raise Exception(f"Failed api message verification: key 'pattern' is missing in '{key}'")
            if "use_color_placeholders" not in definition.keys():
                fixes.update({k: {"use_color_placeholders": False}})

        outputs.update(fixes)


    def check_arguments(key: str = "arguments"):
        from pycore.arg_controller import get_arguments, resolve_argument_conflict

        arguments: dict = message[key]
        if not isinstance(arguments, dict):
            raise Exception(f"Failed api message verification: '{key}' has wrong type. Expected {type(dict())} got {type(arguments)}")

        default_arguments = get_arguments()

        for k, v in default_arguments.items():
            if k not in arguments.keys():
                arguments[k] = v["default_state"]

        if apiconfing_defined():
            arguments = resolve_argument_conflict(arguments, get_apiconfig("arg_conflict_method"))
        else:
            arguments = resolve_argument_conflict(arguments)

    check_output_definitions()
    check_arguments()

    return message