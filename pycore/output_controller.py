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


def return_error(*passthrough) -> list[dict, any]:
    from traceback import format_exc

    answer = {
        "type": "error",
        "answer": [str(format_exc(chain=False))],
    }

    return [answer] + list(passthrough)


def display_results(results: list[dict], save_only: bool = False):
    from config import COL, RES
    from pycore.arg_controller import get_args, init_args

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
        init_args()

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
