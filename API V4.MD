# Overview

ZM-RoundCalculator can be used as backend.

# Call

To call the program, function `api()` must be invoked from `zm_calculator.py`.
`api()` takes one argument. It can either take a dictionary object with all the necessary inputs, or a string path to a JSON file that contains all the necessary inputs.

# API Input

Below is an example for API call

```json
{
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
    }
}
```

## Main keys

| Key | Mandatory | Type | Explanation |
| --- | --- | --- | --- |
| "output_types" | YES | JSON | This definition is used to assemble output from the program. |
| "arguments| | NO | JSON | Pass arguments to the program that change the behaviour and/or output. |

## Keys - "output_types"

| Key | Mandatory | Type | Default | Explanation |
| --- | --- | --- | --- |
| "pattern" | YES | string | - | Pattern used to generate answer from the program. |
| "use_color_placeholders" | NO | boolean | `true` | If this flag is set to true, special keywords will be insert in the answer from API, `{{COLOR_START}}` and `{{COLOR_END}}`, that then can be used to color code answers in the front end. |