# Calculator arguments

#### Mandatory arguments
Arguments at the beginning of the input, the calculator will not work without them
- `round` - Round which time you want to calculate (1 - 255)
- `players` - Amount of players you want round times for (1 - 4)

#### Optional arguments
Arguments that are optional, that can change behaviour of the calculator.
The column `TYPE` is meant for API users.
| ARGUMENT | CALL | DEFAULT STATE | TYPE | EFFECT |
| --- | --- | --- | --- | --- |
| `break` | `-b` | `true` | UI | Enable clear row between outputs. |
| `clear` | `-c` | `false` | UI | Enable printing raw time. |
| `detailed` | `-d` | `false` | In-Program | Enable printing time values in ms. |
| `even_time` | `-e` | `false` | In-Program | Time under key `time_output` will always have the same format `MM:SS`. |
| `insta_rounds` | `-i` | `true` | UI | Attach information about instakill round to the output. |
| `hordes` | `-h-` | `false` | UI | Prints the amount of hordes instead of number of zombies. |
| `lower_time` | `-l` | `false` | In-Program | In case `nodecimals` is used, the time will be rounded down instead of up. |
| `nodecimal` | `-n` | `true` | In-Program | Disable decimals in time output, seconds will be round up. Has no effect if used with `detailed`. |
| `perfect_times` | `-p` | `false` | In-Program | Instead of giving round times, it shows perfect times up to that round. If used with `range`, will print perfect times for all rounds up to the selected one. |
| `range` | `-r` | `false` | In-Program | Whether to print out times up to provided round. |
| `remix` | `-x` | `false` | In-Program | If logic from [Remix](https://github.com/5and5/BO1-Remix) mod is used. |
| `save` | `-v` | `false` | UI / In-Program | If results are saved to a text file after calculation.
| `special_rounds` | `-S` | `false` | UI / In-Program | Instead of using best possible special round scenario (average 4.0), apply own set of special rounds.
| `speedrun_time` | `-s` | `false` | In-Program | Shows time accordingly to split rules as oppose to actual round starts. |
| `teleport_time` | `-t` | `true` | In-Program | Add time it takes for dogs to appear on the map to mitigate spawncap problem on later dog rounds. |
| `waw_spawnrate` | `-w` | `false` | In-Program | Applies higher value of initial spawnrate equal to what is on Nacht, Verruckt and Shi No Numa in WaW versions. |

- `break` is enabled by default as it increases readability.
- `nodecimals` is enabled by default, as the GSC function responsible for round ends clocks every 1 second on normal rounds, however you can still kill zombies with accuracy up to 50ms.
- `teleport time` is enabled by default, as the true result is closer to values with this argument, neither are however, perfect.

#### Custom calculator arguments
Those arguments are for advanced calculator functions and will cancel optional arguments. They were made specifically for one scenario and usually aren't needed
- `-db` - Produces richer print meant for debugging the calculation.
- `-ddb` - Produces richer print meant for debugging calculation for dog rounds.
- `-ga` - Produces a list of argument shortcodes with definitions.
- `-ps` - Produces processed spawnrate values after rounding.
- `-rs` - Produces raw spawnrate values emulating gsc function.
- `-zc` - Produces zombie count for provided round range.
- `-exc` - For debugging, raises an exception in Python
