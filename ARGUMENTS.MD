# Calculator arguments

#### Mandatory arguments
Arguments at the beginning of the input, the calculator will not work without them
- `round` - Round which time you want to calculate (1 - 255)
- `players` - Amount of players you want round times for (1 - 4)

#### Optional arguments
Arguments that are optional, that can change behaviour of the calculator
- `range` - Whether to print out round times up to provided round. Add "-r" to the input.
- `perfect times` - Instead of giving round times, it shows perfect times up to that round. If used with `range`, will print perfect times for all rounds up to the selected one. Add "-p" to the input.
- `clear output` - Will print raw times instead of sentences. Useful for spreadsheets. Add "-c" to the input.
- `break` - If there is a clear row between entries. Add "-b" to disable this argument, as it's enabled by default.
- `detailed` - Prints miliseconds instead of readable time. Add "-d" to the input.
- `nodecimals` - Disable decimals in time output, seconds will be round up. Add "-n" to the input. Has no effect if used with `detailed`.

I didn't add any validation for those you'll just get weird results if you mess with numbers