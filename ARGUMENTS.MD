# Calculator arguments

#### Mandatory arguments
Arguments at the beginning of the input, the calculator will not work without them
- `round` - Round which time you want to calculate (1 - 255)
- `players` - Amount of players you want round times for (1 - 4)

#### Optional arguments
Arguments that are optional, that can change behaviour of the calculator.
The column `TYPE` is meant for API users.
| ARGUMENT | SHORT | DEFAULT STATE | TYPE | EFFECT |
| --- | --- | --- | --- | --- |
| `--break` | `-b` | `true` | ARG | Enable clear row between outputs. |
| `--clear` | `-c` | `false` | ARG | Enable printing raw time. |
| `--detailed` | `-d` | `false` | ARG | Enable printing time values in ms. |
| `--even_time` | `-e` | `false` | ARG | Time under key `time_output` will always have the same format `MM:SS`. |
| `--game` | `-g` | `null` | KWARG | Pass a game code to this argument in order to override base detection. Useful for supporting maps other than defaults. |
| `--grenade_damage` | `-gd` | 150 | KWARG | Override extra explosives damage. Round number is going to be added to this value as per GSC formula. |
| `--grenade_radius` | `-gr` | 128.0 | KWARG | Override default average distance between zombies and the explosion. |
| `--insta_rounds` | `-i` | `true` | ARG | Attach information about instakill round to the output. |
| `--hordes` | `-h-` | `false` | ARG | Prints the amount of hordes instead of number of zombies. |
| `--lower_time` | `-l` | `false` | ARG | In case `nodecimals` is used, the time will be rounded down instead of up. |
| `--nodecimal` | `-n` | `true` | ARG | Disable decimals in time output, seconds will be round up. Has no effect if used with `detailed`. |
| `--perfect_times` | `-p` | `false` | ARG | Instead of giving round times, it shows perfect times up to that round. If used with `range`, will print perfect times for all rounds up to the selected one. |
| `--prenades` | `-P` | `false` | ARG | Instead of round times, calculate prenades for the round. Keep in mind, due to significant RNG factors in the way 3arc is calculating damage, this value will never be 100% accurate. It gains accuracy the higher the round. |
| `--range` | `-r` | `false` | ARG | Whether to print out times up to provided round. |
| `--remix` | `-x` | `false` | ARG | If logic from [Remix](https://github.com/5and5/BO1-Remix) mod is used. |
| `--save` | `-v` | `false` | ARG | If results are saved to a text file after calculation. |
| `--special_rounds` | `-S` | `false` | ARG | Instead of using best possible special round scenario (average 4.0), apply own set of special rounds.
| `--speedrun_time` | `-s` | `false` | ARG | Shows time accordingly to split rules as oppose to actual round starts. |
| `--teleport_time` | `-t` | `true` | ARG | Add time it takes for dogs to appear on the map to mitigate spawncap problem on later dog rounds. |

#### Custom calculator arguments
Those arguments are for advanced calculator functions and will cancel optional arguments. They were made specifically for one scenario and usually aren't needed

| MOD | SHORT | EXP |
| --- | --- | --- |
| `-dbc` | `--debugclasses` | Produces richer print meant for debugging the calculation. |
| `-exc` | `--exception` | For debugging, raises an exception in Python. |
| `-irn` | `--instarounds` | Print out all instakill rounds. |
| `-spr` | `--spawnrates` | Print out spawnrate for specified round or set of rounds. |
| `-zcn` | `--zombiecount` | Print out zombiecount for specified round or set of rounds. |
| `-zhp` | `--zombiehealth` | Print out zombie health for specified round or set of rounds. |
