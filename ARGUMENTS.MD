# Calculator arguments

#### Mandatory arguments
Arguments at the beginning of the input, the calculator will not work without them
- `round` - Round which time you want to calculate (1 - 255)
- `players` - Amount of players you want round times for (1 - 4)

#### Optional arguments
Arguments that are optional, that can change behaviour of the calculator
| ARGUMENT | CALL | EFFECT |
| `break` | `-b` | Defines if there is a clear row between entries. Argument enabled by default, use to disable.|
| `clear output` | `-c` | Prints raw times instead of sentences. Useful for spreadsheets.|
| `detailed` | `-d` | Prints miliseconds instead of readable time.|
| `lower time` | `-l` | In case `nodecimals` is used, the time will be rounded down instead of up. Has no effect otherwise.|
| `nodecimals` | `-n` | Disable decimals in time output, seconds will be round up. Has no effect if used with `detailed`.|
| `perfect times` | `-p` | Instead of giving round times, it shows perfect times up to that round. If used with `range`, will print perfect times for all rounds up to the selected one.|
| `range` | `-r` | Whether to print out times up to provided round.|
| `speedrun time` | `-s` | Shows time accordingly to split rules as oppose to actual round starts. Argument enabled by default, use to disable.|

#### Custom calculator arguments
Those arguments are for advanced calculator functions and will cancel optional arguments. They were made specifically for one scenario and usually aren't needed
| ARGUMENT | CALL | EFFECT |
| `post spawnrate` | `-ps` | Prints processed spawnrate values after rounding.|
| `raw spawnrate` | `-rs` | Prints raw spawnrate values emulating gsc function.|
| `zombie count` | `-zc` | Prints zombie counts.|

I didn't add any validation for those you'll just get weird results if you mess with numbers