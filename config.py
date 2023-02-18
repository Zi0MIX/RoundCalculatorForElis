COL, RES, YEL, GRE, RED, CYA = "", "", "", "", "", ""
DEC = 3

# Time from "initial_blackscreen_passed" to "start_of_round" triggers
RND_WAIT_INITIAL = 8.25
# Time from "end_of_round" to "start_of_round"
RND_WAIT_END = 12.50
# Time from "end_of_round" to "between_round_over"
RND_WAIT_BETWEEN = RND_WAIT_END - 2.5
# Time difference between "start_of_round" trigger and new round number appearing
RND_BETWEEN_NUMBER_FLAG = 4.0

ZOMBIE_MAX_AI = 24
ZOMBIE_AI_PER_PLAYER = 6

# Perfect dog rounds, r5 then all 4 rounders
DOGS_PERFECT = [int(x) for x in range(256) if x % 4 == 1 and x > 4]
# 0.05 from ingame timing, code says 7 dot
DOGS_WAIT_START = 7.05
# Time from last dog killed to RND_WAIT_END
DOGS_WAIT_END = 8
# Time between dog spawning to dog appearing on the map
DOGS_WAIT_TELEPORT = 1.5

MAP_LIST = tuple("zm_prototype", "zm_asylum", "zm_sumpf", "zm_factory", "zm_theater", "zm_pentagon", "zm_cosmodrome", "zm_coast", "zm_temple", "zm_moon", "zm_transit", "zm_nuked", "zm_highrise", "zm_prison", "zm_buried", "zm_tomb")
MAP_DOGS = tuple("zm_sumpf", "zm_factory", "zm_theater")
MAP_DOCTOR = tuple("zm_pentagon")
MAP_MONKEYS = tuple("zm_cosmodrome")
MAP_LEAPERS = tuple("zm_highrise")

DEFAULT_ARGUMENTS = {
    "break": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Break",
        "shortcode": "-b",
        "default_state": True,
        "exp": "Display an empty line between results."
    },
    "clear": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Clear output",
        "shortcode": "-c",
        "default_state": False,
        "exp": "Show only numeric output as oppose to complete sentences. Use for datasets."
    },
    "detailed": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Detailed",
        "shortcode": "-d",
        "default_state": False,
        "exp": "Show time in miliseconds instead of formatted string."
    },
    "even_time": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Even time",
        "shortcode": "-e",
        "default_state": False,
        "exp": "Time output always has 5 symbols."
    },
    "hordes": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Hordes",
        "shortcode": "-h",
        "default_state": False,
        "exp": "Show the amount of hordes instead of the amount of zombies in the output."
    },
    "insta_rounds": {
        "use_in_web": True,
        "require_map": True,
        "require_special_round": False,
        "readable_name": "Insta Rounds",
        "shortcode": "-i",
        "default_state": True,
        "exp": "Add information about instakill rounds to the output."
    },
    "lower_time": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Lower Time",
        "shortcode": "-l",
        "default_state": False,
        "exp": "Change seconds rounding to go down instead of up."
    },
    "nodecimal": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Nodecimal",
        "shortcode": "-n",
        "default_state": True,
        "exp": "Show time without decimals."
    },
    "perfect_times": {
        "use_in_web": True,
        "require_map": True,
        "require_special_round": False,
        "readable_name": "Perfect times",
        "shortcode": "-p",
        "default_state": False,
        "exp": "Instead of perfect round times, display perfect split times for choosen map."
    },
    "prenades": {
        "use_in_web": False,    # Arg is not yet usable
        "require_map": True,
        "require_special_round": False,
        "readable_name": "Prenades",
        "shortcode": "-P",
        "default_state": False,
        "exp": "Instead of perfect round times, display amount of prenades."
    },
    "range": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Range",
        "shortcode": "-r",
        "default_state": False,
        "exp": "Show results for all rounds leading to selected number."
    },
    "remix": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Remix",
        "shortcode": "-x",
        "default_state": False,
        "exp": "Use spawn and zombie logic applied in 5and5s mod Remix."
    },
    "save": {
        "use_in_web": False,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Save",
        "shortcode": "-v",
        "default_state": False,
        "exp": "Save output to text file."
    },
    "special_rounds": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Special rounds",
        "shortcode": "-S",
        "default_state": False,
        "exp": "Add own set of special rounds to perfect times predictor to maps that support it."
    },
    "speedrun_time": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Speedrun time",
        "shortcode": "-s",
        "default_state": False,
        "exp": "Show times accordingly to speedrun rules, round end is on number transition instead of when zombies start spawning."
    },
    "teleport_time": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "Teleport time",
        "shortcode": "-t",
        "default_state": True,
        "exp": "Adds dog appearance time to perfect dog rounds accordingly to the pattern: 't * dogs / (2 * players))'"
    },
    "waw_spawnrate": {
        "use_in_web": True,
        "require_map": False,
        "require_special_round": False,
        "readable_name": "World at War Spawnrate",
        "shortcode": "-w",
        "default_state": False,
        "exp": "Apply higher initial spawnrate value from WaW's maps Nacht, Verruckt and Shino."
    }
}


DEFAULT_MAP_TRANSLATIONS = {
    "zm_prototype": "Nacht Der Untoten",
    "zm_asylum": "Verruckt",
    "zm_sumpf": "Shi No Numa",
    "zm_factory": "Der Riese",
    "zm_theater": "Kino Der Toten",
    "zm_pentagon": "FIVE",
    "zm_cosmodrome": "Ascension",
    "zm_coast": "Call of the Dead",
    "zm_temple": "Shangri-La",
    "zm_moon": "Moon",
    "zm_transit": "Tranzit",
    "zm_nuked": "Nuketown",
    "zm_highrise": "Die Rise",
    "zm_prison": "Mob of the Dead",
    "zm_buried": "Buried",
    "zm_tomb": "Origins",
}

DEFAULT_APICONFIG = {
    "own_print": True,
    "arg_overrides": {},
    "new_rules": {},
    "custom_translations": {}
}

CONFLICTING_ARGUMENTS: list[dict] = [{

}]

MODIFIER_DEFINITIONS: dict = {
    "-db": "debugclasses",
    "-sp": "spawnrates",
    "-zc": "zombiecount",
    "-zh": "zombiehealth",
    "-ir": "instarounds",
    "-ex": "exception",
    "-pr": "prenades",
}

# Wildcard is a text enclosed in curly braces inside of patterns, value is a key in calculated_data or calculator_data dictionary in assemble_output()
WILDCARDS_TRANSLATION = {
    "ROUND_NUMBER": "round",
    "PLAYERS": "players",
    "ENEMIES": "enemies",
    "ENEMY_HEALTH": "enemy_health",
    "SPAWNRATE": "spawnrate",
    "NETWORK_FRAME": "network_frame",
    "ROUND_TIME": "round_time",
    "GAME_TIME": "game_time",
    "INSTAROUND": "is_insta_round",
    "MAP_CODE": "map_code",
    "MAP_NAME": "map_name",
    "IS_SPECIAL_ROUND": "is_special_round",
    "SPECIAL_AVERAGE": "spec_round_average",
    "SPECIAL_ROUNDS": "num_of_spec_rounds",
    "PRENADES": "prenades",
    "ZOMBIE_ROUND": "zombie_round",
    "DOG_ROUND": "dog_round",
    "DOCTOR_ROUND": "doctor_round",
    "MONKEY_ROUND": "monkey_round",
    "LEAPER_ROUND": "leaper_round",
    "PRENADES_ROUND": "prenades_round"
}

DEFAULT_PATTERNS = {
    "round_times": "Round {ROUND_NUMBER} will spawn in {ROUND_TIME} and has {ENEMIES} {ENEMY_TYPE}. Spawnrate: {SPAWNRATE} Network frame: {NETWORK_FRAME}",
    "perfect_times": "Perfect time to round {ROUND_NUMBER} for {PLAYERS} players is {GAME_TIME} on {MAP_NAME}",
    "debugclasses": "zombie_round={ZOMBIE_ROUND}\ndog_round={DOG_ROUND}\ndoctor_round={DOCTOR_ROUND}\nmonkey_round={MONKEY_ROUND}\nleaper_round={LEAPER_ROUND}\n{PRENADES_ROUND}",
    "spawnrates": "{SPAWNRATE}",
    "zombiecount": "{ENEMIES}",
    "zombiehealth": "{ENEMY_HEALTH}",
    "instarounds": "{INSTAROUND}",
    "exception": "{EXCEPTION}",
    "prenades": "{PRENADES}",
}

CLEAR_PATTERNS = {
    "round_times": "{ROUND_TIME}",
    "perfect_times": "{GAME_TIME}",
}