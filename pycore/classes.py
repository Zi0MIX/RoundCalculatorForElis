import numpy as np
import config as cfg
from dataclasses import dataclass


@dataclass
class ZombieRound:
    number: int
    players: int
    map_code: str


    def __post_init__(self):
        self.set_enemy_type()
        self.get_network_frame()
        self.get_zombies()
        self.get_spawn_delay()
        self.get_round_time()
        self.get_zombie_health()


    def get_game(self):
        from pycore.arg_controller import get_args
        self.game_code = get_args("game")
        if self.game_code is None:
            for k, v in cfg.GAME_TITLES.items():
                if self.map_code in v["maps"]:
                    self.game_code = k

        # This should only occur in scenarios where game title is not necessary
        if self.game_code is None:
            self.game_code = ""

        self.game_title = "Undefined title"
        if self.game_code:
            try:
                self.game_title = cfg.GAME_TITLES[self.game_code]
            except Exception:
                pass


    def set_enemy_type(self, enemy_type: str = "zombies"):
        self.enemy_type = enemy_type


    def get_network_frame(self):
        self.network_frame = 0.05
        if self.players == 1:
            self.network_frame = 0.10

        return


    def get_round_spawn_delay(self, raw_delay: np.float32) -> np.float32:
        """Function uses Numpy to emulate Game Engine behavior\n
        Takes float32 `raw_delay` arugment and returns float32 value"""

        self.raw_spawn_delay = np.format_float_positional(raw_delay, min_digits=16)

        if raw_delay < 0.01:
            raw_delay = 0.01

        inside = str(raw_delay).split(".")

        if not len(inside[1]):
            real_decimals = ["0", "0"]
        elif len(inside[1]) == 1:
            real_decimals = [inside[1], "0"]
        else:
            real_decimals = [str(x) for x in inside[1]][:2]

            if len(inside[1]) > 2:
                # Round decimals outside of the scope in a normal way
                dec = reversed([int(x) for x in inside[1]][2:])
                # decimals = []
                remember = 0

                for x in dec:
                    x += remember
                    remember = 0

                    if x >= 5:
                        # decimals.append("0")
                        remember = 1
                    # else:
                    #     decimals.append("0")

                if remember:
                    real_decimals[1] = str(int(real_decimals[1]) + 1)
                    if real_decimals[1] == "10":
                        real_decimals[0] = str(int(real_decimals[0]) + 1)
                        real_decimals[1] = "0"

        # Round decimals in the scope to 0.05 following GSC way
        if real_decimals[1] in ("0", "1", "2"):
            real_decimals[1] = "0"
        elif real_decimals[1] in ("3", "4", "5", "6", "7"):
            real_decimals[1] = "5"
        else:
            real_decimals[1] = "0"
            real_decimals[0] = str(int(real_decimals[0]) + 1)

            if real_decimals[0] == "10":
                real_decimals[0] = "0"
                inside[0] = str(int(inside[0]) + 1)

        inside[1] = "".join(real_decimals)
        # print(f"{inside} / original: {str(self.raw_spawn_delay).split('.')}")

        return np.float32(".".join(inside))


    def get_spawn_delay(self):
        """Function uses Numpy to emulate Game Engine behavior"""
        from pycore.arg_controller import get_args

        self.spawn_delay = np.float32(2.0)
        self.raw_spawn_delay = np.float32(2.0)

        if get_args("remix"):
            self.spawn_delay = 1.0
            self.raw_spawn_delay = 1.0
        # if get_args("waw_spawnrate"):
        #     self.spawn_delay = 3.0
        #     self.raw_spawn_delay = 3.0

        if self.number > 1:
            for _ in range(1, self.number):
                self.spawn_delay *= np.float32(0.95)

            self.spawn_delay = self.get_round_spawn_delay(self.spawn_delay)

            if self.spawn_delay < 0.1:
                self.spawn_delay = np.float32(0.1)

        self.spawn_delay = round(float(self.spawn_delay), 2)

        return


    def get_zombies(self):
        from pycore.arg_controller import get_args

        multiplier = self.number / 5
        if multiplier < 1:
            multiplier = 1.0
        elif self.number >= 10:
            multiplier *= (self.number * 0.15)

        if self.players == 1:
            temp = int(cfg.ZOMBIE_MAX_AI + (0.5 * cfg.ZOMBIE_AI_PER_PLAYER * multiplier))
        else:
            temp = int(cfg.ZOMBIE_MAX_AI + ((self.players - 1) * cfg.ZOMBIE_AI_PER_PLAYER * multiplier))

        self.enemies = temp
        if self.number < 2:
            self.enemies = int(temp * 0.25)
        elif self.number < 3:
            self.enemies = int(temp * 0.3)
        elif self.number < 4:
            self.enemies = int(temp * 0.5)
        elif self.number < 5:
            self.enemies = int(temp * 0.7)
        elif self.number < 6:
            self.enemies = int(temp * 0.9)

        self.hordes = round(self.enemies / 24, 2)

        # if get_args("waw_spawnrate") and self.players == 1 and self.enemies > 24:
        #     self.enemies = 24

        return


    def extract_decimals(self):
        dec = "0"
        # '> 0' could result in 00000001 triggering the expression
        if int(str(self.raw_time).split(".")[1]) >= 1:
            dec = str(self.raw_time).split(".")[1][:3]

        while len(dec) < cfg.DEC:
            dec += "0"
        self.decimals = dec

        return


    def get_round_time(self):
        delay = self.spawn_delay + self.network_frame
        self.raw_time = (self.enemies * delay) - delay
        self.round_time = round(self.raw_time, 2)

        # self.extract_decimals()

        return


    def get_zombie_health(self):
        """Function uses Numpy to emulate Game Engine behavior"""

        self.is_insta_round = False
        self.health = np.int32(150)
        self.health_162 = None

        for r in range(2, self.number + 1):
            if r < 10:
                self.health += np.int32(100)
            else:
                self.health += np.int32(np.float32(self.health) * np.float32(0.1))

        if (self.health <= np.int32(150)) and (self.number > 1):
            self.is_insta_round = True

            # print(f"DEV: Round: {r} / Health: {self.health}")


    def remove_instas(self):
        if self.health_162 is None:
            health = np.int32(150)
            for r in range(2, 163):
                if r < 10:
                    health += np.int32(100)
                else:
                    health += np.int32(np.float32(self.health) * np.float32(0.1))
            self.health_162 = health

        if self.is_insta_round:
            self.health = self.health_162


@dataclass
class DogRound(ZombieRound):
    special_rounds: int


    def __post_init__(self):
        self.set_enemy_type("dogs")
        self.get_network_frame()
        self.get_dogs()
        self.get_teleport_time()
        self.get_dog_spawn_delay()
        self.get_total_delay()
        self.round_up()


    def get_dogs(self):
        self.enemies = self.players * 8

        if self.special_rounds < 3:
            self.enemies = self.players * 6

        return


    def get_teleport_time(self):
        # Seems to be the best indication of representing spawncap accurately, at least in case of solo when comparing to actual gameplay
        self.teleport_time = cfg.DOGS_WAIT_TELEPORT * (self.enemies / (2 * self.players))
        return


    def get_dog_spawn_delay(self):
        self.spawn_delay = 1.50

        if self.special_rounds == 1:
            self.spawn_delay = 3.00
        elif self.special_rounds == 2:
            self.spawn_delay = 2.50
        elif self.special_rounds == 3:
            self.spawn_delay = 2.00

        return


    def get_total_delay(self):
        self.raw_time = 0
        self.delays = []
        for i in range(1, self.enemies):
            delay = self.get_round_spawn_delay(self.spawn_delay - (i / self.enemies))

            self.raw_time += delay
            self.delays.append(delay)

        self.raw_time = round(self.raw_time, 2)


    def round_up(self):
        # round_wait() function clocks every .5 seconds
        time_in_ms = round(self.raw_time * 1000)
        if not time_in_ms % 500:
            self.round_time = self.raw_time
            return

        self.round_time = ((time_in_ms - (time_in_ms % 500)) + 500) / 1000
        return
    

    def add_teleport_time(self):
        # Call if dog teleport time should be added for each dog on class level
        self.round_time += self.teleport_time
        return
    

@dataclass
class DoctorRound(ZombieRound):
    # FIVE
    pass


@dataclass
class MonkeyRound(ZombieRound):
    # Ascension
    pass


@dataclass
class LeaperRound(ZombieRound):
    # Die Rise
    pass


@dataclass
class PrenadesRound(ZombieRound):
    radius: float = None
    extra_damage: int = None


    def __post_init__(self):
        self.get_game()
        self.set_enemy_type()
        self.get_nade_type()
        self.translate_nade_type()
        self.get_zombie_health()
        self.remove_instas()
        self.explosives_handler()


    def get_nade_type(self):
        self.grenade_type = "frag"

        if self.map_code is not None:
            for k, v in cfg.GRENADETYPES.items():
                if self.map_code in v:
                    self.grenade_type = k


    def translate_nade_type(self):
        if self.grenade_type == "german":
            self.grenade_name = "Stielhandgranate"
        else:
            self.grenade_name = self.grenade_type.capitalize()


    def explosives_handler(self):
        """Function uses Numpy to emulate Game Engine behavior.\n
        Available nade types are `frag`, `german`, `semtex`"""

        nadecfg = self.get_nadeconfig()

        # Get average radius or else pickup override value. Important to pass float to the function call
        if not isinstance(self.radius, float):
            self.radius = np.float32((nadecfg["max_radius"] + nadecfg["min_radius"]) / 2)
        else:
            self.radius = np.float32(self.radius)

        # It has to wait until radius is defined
        bmx_damage = self.get_bmx_damage()
        self.nade_damage = np.int32(bmx_damage)

        current_health = np.int32(self.health)
        nades = 0

        # Deal with bigger numbers for high rounds
        # 400_000 and 450_000 are the fastest for computation
        number_of_nades = np.int32(400_000) // self.recalculate_damage(1, nadecfg)
        while current_health > np.int32(450_000):
            current_health -= self.recalculate_damage(number_of_nades, nadecfg)
            nades += number_of_nades
            # print(f"DEV: nades: {nades} / number_of_nades: {number_of_nades} / current_health: {current_health}")

        # Get exact number when number is already low
        if self.extra_damage is None:
            damage_per_iter = self.recalculate_damage(1, nadecfg)
        else:
            damage_per_iter = self.extra_damage + self.number

        while (damage_per_iter / current_health * np.int32(100) < np.int32(10)) and (current_health > np.int32(150)):
            # print(f"DEV: percent: {self.nade_damage / current_health * 100}% / current_health: {current_health}")
            current_health -= damage_per_iter
            nades += 1
            if self.extra_damage is not None:
                damage_per_iter = self.recalculate_damage(1, nadecfg)

        self.prenades = nades

        # print(f"DEV: Bmx damage: {bmx_damage}")
        # print(f"DEV: Nade damage: {self.nade_damage}")
        # print(f"DEV: Prenades on {self.number}: {self.prenades}")


    def get_nadeconfig(self) -> dict:
        nadeconfigs = {
            "frag": {
                "max_radius": np.float32(256.0),
                "min_radius": np.float32(0.0),
                "max_damage": np.int32(300),
                "min_damage": np.int32(75),
                "damage_extra_max": np.int32(200),
                "damage_extra_min": np.int32(100),
            },
            "german": {
                "max_radius": np.float32(256.0),
                "min_radius": np.float32(0.0),
                "max_damage": np.int32(200),
                "min_damage": np.int32(50),
                "damage_extra_max": np.int32(200),
                "damage_extra_min": np.int32(100),
            },
            "semtex": {
                "max_radius": np.float32(256.0),
                "min_radius": np.float32(0.0),
                "max_damage": np.int32(300),
                "min_damage": np.int32(55),
                "damage_extra_max": np.int32(200),
                "damage_extra_min": np.int32(100),
            },
        }

        return nadeconfigs[self.grenade_type]
    

    def get_bmx_damage(self) -> np.int32:
        if self.grenade_type == "frag":
            return np.int32(np.float32(-0.880) * np.float32(self.radius) + np.int32(300))
        elif self.grenade_type == "german":
            return np.int32(np.float32(-0.585) * np.float32(self.radius) + np.int32(200))
        elif self.grenade_type == "semtex":
            return np.int32(np.float32(-0.958) * np.float32(self.radius) + np.int32(300))
        else:
            raise Exception(f"Could not set BMX damage value for nade type {self.grenade_type}")


    def recalculate_damage(self, no_of_nades: int, nadeconfig: dict) -> np.int32:
        import random

        new_damage = np.int32(0)
        for _ in range(no_of_nades):
            average = np.int32((nadeconfig["damage_extra_min"] + nadeconfig["damage_extra_max"]) // 2)
            # average_quater = np.int32((nadeconfig["damage_extra_min"] + average) // 2)
            # dmg_random = np.int32(random.randint(nadeconfig["damage_extra_min"], nadeconfig["damage_extra_max"]))

            new_damage += self.nade_damage + average + np.int32(self.number)

        return new_damage
