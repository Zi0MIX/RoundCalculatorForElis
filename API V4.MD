# Overview

ZM-RoundCalculator can be used as backend.

# Call

To call the program, function `api()` must be invoked from `zm_calculator.py`.
`api()` takes one argument. It can either take a dictionary object with all the necessary inputs, or a string path to a JSON file that contains all the necessary inputs.

# API Input

Below is an example for API call

```json
{
    "mode": "api",
    "data": {
        "round": "255",
        "players": "1",
        "map_code": "zm_prototype"
    },
    "output_types": {
        "round_times": {
            "pattern": "Round {{ROUND_NUMBER}} will spawn in {{TIME_OF_SPAWN}} and has {{ZOMBIES}}. Spawnrate: {{SPAWNRATE}} Network frame: {{NETWORK_FRAME}}",
            "use_color_placeholders": true
        },
        "perfect_times": {
            "pattern": "Perfect time to round {{ROUND_NUMBER}} is {{PERFECT_ROUND_TIME}} on {{MAP_NAME}}",
            "use_color_placeholders": true
        }
    },
    "arguments": {
        "range": true
    },
    "modifier": null
}
```

## Main keys

| Key | Mandatory | Type | Explanation |
| --- | --- | --- | --- |
| "mode" | YES | string | Pass string 'api'. |
| "data" | YES | JSON | Dataset for the calculator to work with. |
| "output_types" | YES | JSON | This definition is used to assemble output from the program. |
| "arguments" | YES | JSON | Pass arguments to the program that change the behaviour and/or output. |
| "modifier" | NO | string or null | Pass flag with a modifier, if there isn't one, pass `null`. |

## Keys - "data"

| Key | Mandatory | Type | Default | Explanation |
| --- | --- | --- | --- |
| "round" | YES | string or int | - | Number representing which round is suppose to be processed. |
| "players" | YES | string or int | - | Number of players the calculator should use for calculation |
| "map_code" | NO | string or null | - | Code of map needed for certain types of calculations. It is recommended to always pass it on, in case it's not selected, pass `null`. |

## Keys - "output_types"

| Key | Mandatory | Type | Default | Explanation |
| --- | --- | --- | --- |
| "pattern" | YES | string | - | Pattern used to generate answer from the program. |
| "use_color_placeholders" | NO | boolean | `true` | If this flag is set to true, special keywords will be insert in the answer from API, `{{COLOR_START}}` and `{{COLOR_END}}`, that then can be used to color code answers in the front end. |
