def map_translator(map_code: str) -> str:
    from config import DEFAULT_MAP_TRANSLATIONS
    from pycore.api_handler import apiconfing_defined, get_apiconfig

    if apiconfing_defined():
        api_translations = get_apiconfig("custom_translations")

        if map_code in api_translations.keys():
            return api_translations[map_code]

    if map_code in DEFAULT_MAP_TRANSLATIONS.keys():
        return DEFAULT_MAP_TRANSLATIONS[map_code]

    return map_code


def get_readable_time(round_time: float, args: dict) -> str:
    h, m, s, ms = 0, 0, 0, int(round_time * 1000)

    while ms > 999:
        s += 1
        ms -= 1000
    while s > 59:
        m += 1
        s -= 60
    # Do not reduce minutes to hours if even_time is on
    if not args["even_time"]:
        while m > 59:
            h += 1
            m -= 60

    dec = f".{str(ms).zfill(3)}"
    # Clear decimals and append a second, this way it's always rounding up
    if args["nodecimal"] and not args["lower_time"]:
        dec = ""
        s += 1
        if s > 59:
            m += 1
            s -= 60
            if m > 59:
                h += 1
                m -= 60
    # Otherwise just clear decimals, it then rounds down
    elif args["nodecimal"]:
        dec = ""

    if not h and not m:
        new_time = f"{s}{dec} seconds"
    elif not h:
        new_time = f"{str(m).zfill(2)}:{str(s).zfill(2)}{dec}"
    else:
        new_time = f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}{dec}"

    if args["even_time"]:
        new_time = f"{str(m).zfill(2)}:{str(s).zfill(2)}"

    return new_time


def return_error(nolist: bool = False) -> dict | list[dict]:
    from traceback import format_exc

    if nolist:
        return {"type": "error", "message": str(format_exc())}
    return [{"type": "error", "message": str(format_exc())}]


def get_answer_blueprint() -> dict:
    """Check outputs.MD for reference"""
    from config import ANSWER_BLUEPRINT
    return ANSWER_BLUEPRINT


def display_results(results: list[dict], save_only: bool = False):
    from config import COL, RES
    from pycore.arg_controller import get_args, load_args

    def save_results_locally(to_save: list, path_override: str = "") -> None:
        import os.path
        from config import CYA, RES
        from time import localtime, time
        try:
            import PySimpleGUI as sg
        except ModuleNotFoundError:
            sg = None

        output = "\n".join(to_save)

        if path_override:
            path = path_override
        elif sg is None:
            print(f"{CYA}Enter path to where you want to save the file in{RES}")
            path = str(input("> "))
        else:
            while True:
                save_folder = sg.popup_get_folder("Save as: ", keep_on_top=True)

                if save_folder is None:
                    print("Cancelled saving results.")
                    return

                path = save_folder
                break

        t = localtime(time())
        a_filename = f"zm_round_calculator_{str(t[0]).zfill(4)}-{str(t[1]).zfill(2)}-{str(t[2]).zfill(2)}_{str(t[3]).zfill(2)}-{str(t[4]).zfill(2)}-{str(t[5]).zfill(2)}.txt"
        with open(os.path.join(path, a_filename), "w", encoding="utf-8") as newfile:
            newfile.write(output)

        return
    

    def print_results(results: list, arg_break: bool) -> None:
        if save_only:
            return

        for result in results:
            print(result)
            if arg_break:
                print()


    readable_results = []

    # If entered from error handler in api, args will not be defined, and they don't need to
    try:
        get_args()
    except (NameError, UnboundLocalError):
        load_args()

    for res in results:

        # Assemble print
        zm_word = "zombies"
        if res["type"] == "error":
            readable_result = f"An error occured, if your inputs are correct, please contact the creator and provide error message.\n{res['message']}"
            readable_results.append(readable_result)

        elif res["type"] == "round_time":
            enemies = res["zombies"]
            if get_args("hordes"):
                zm_word = "hordes"
                enemies = res["hordes"]

            if get_args("clear"):
                readable_result = res["time_output"]
            else:
                readable_result = f"Round {COL}{res['round']}{RES} will spawn in {COL}{res['time_output']}{RES} and has {COL}{enemies}{RES} {zm_word}. (Spawnrate: {COL}{res['spawnrate']}{RES} / Network frame: {COL}{res['network_frame']}{RES})."

            readable_results.append(readable_result)

        elif res["type"] == "perfect_times":
            if get_args("clear"):
                readable_result = res["time_output"]
            else:
                readable_result = f"Perfect time to round {COL}{res['round']}{RES} is {COL}{res['time_output']}{RES} on {COL}{res['map_name']}{RES}."

            readable_results.append(readable_result)

        elif res["type"] == "mod":
            readable_result = res["message"]
            readable_results.append(readable_result)

    print_results(readable_results, get_args("break"))

    if get_args("save"):
        save_results_locally([str(st).replace(COL, "").replace(RES, "") for st in readable_results])

    return
