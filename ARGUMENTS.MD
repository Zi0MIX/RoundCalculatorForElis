# Calculator arguments

#### Mandatory arguments
Arguments at the beginning of the input, the calculator will not work without them
- `round` - Round which time you want to calculate (1 - 255)
- `players` - Amount of players you want round times for (1 - 4)

#### Optional arguments
Arguments that are optional, that can change behaviour of the calculator
| ARGUMENT | CALL | DEFAULT STATE | EFFECT |
| --- | --- | --- | --- |
| `break` | `-b` | `true` | Enable clear row between outputs. |
| `clear` | `-c` | `false` | Enable printing raw time. |
| `detailed` | `-d` | `false` | Enable printing time values in ms. |
| `lower_time` | `-l` | `false` | In case `nodecimals` is used, the time will be rounded down instead of up. |
| `nodecimal` | `-n` | `true` | Disable decimals in time output, seconds will be round up. Has no effect if used with `detailed`. |
| `perfect_times` | `-p` | `false` | Instead of giving round times, it shows perfect times up to that round. If used with `range`, will print perfect times for all rounds up to the selected one. |
| `range` | `-r` | `false` | Whether to print out times up to provided round. |
| `speedrun_time` | `-s` | `false` | Shows time accordingly to split rules as oppose to actual round starts. |
| `teleport_time` | `-t` | `true` | Add time it takes for dogs to appear on the map to mitigate spawncap problem on later dog rounds. |

- `break` is enabled by default as it increases readability.
- `nodecimals` is enabled by default, as the GSC function responsible for round ends clocks every 1 second on normal rounds, however you can still kill zombies with accuracy up to 50ms.
- `teleport time` is enabled by default, as the true result is closer to values with this argument, neither are however, perfect.

#### Custom calculator arguments
Those arguments are for advanced calculator functions and will cancel optional arguments. They were made specifically for one scenario and usually aren't needed
| ARGUMENT | CALL | EFFECT |
| --- | --- | --- |
| debug | `-db` | Produces richer print meant for debugging the calculation. |
| debug dogs | `-ddb` | Produces richer print meant for debugging calculation for dog rounds. |
| post spawnrate | `-ps` | Prints processed spawnrate values after rounding. |
| raw spawnrate | `-rs` | Prints raw spawnrate values emulating gsc function. |
| zombie count | `-zc` | Prints zombie counts. |
