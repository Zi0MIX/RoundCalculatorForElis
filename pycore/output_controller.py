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
