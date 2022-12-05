# General
Round Calculator can now be used as API. Check out my [web interface](https://zi0mix.github.io/) built as an example.
You can use it as part of your own project, but make sure to credit me and link the original repository: `https://github.com/Zi0MIX/ZM-RoundCalculator`

## Examples of use
- Standalone script on a server, can be called via terminal, in that case it is required to pass arguments as argvs
    * Example: `python zm_calculator.py str 30 3 -r`
- Implementation into a web application via [pyscript](https://pyscript.net/). In this case arguments are passed directly to a wrapping function as dictionary(json)
    * Example: `api_output = main_api(arguments_from_ui)`

## General info
API has 2 main input methods, `argv` and `main_api()` call
- `argv` is essentially just passing arguments to the program via command line, simply typing them right after the name of the program.
- `main_api()` is a function to be called from outside systems (it's also used in argv implementation under the hood).

## Argv input

Syntax:
```<script_name> <round_number> <player_number> <map_name> (<arguments> <mods>)```
Example:
```python zm_calculator.py 30 1 zm_buried -r -b```

| ARGV | DATA RANGE | DESCRIPTION |
| --- | --- | --- |
| `script_name` | name_of_script.extension | Name of the script on your local computer. Can be a Python file or exe. |
| `round_numer` | 1-255 | Defines round number. There is no in-program valuidation, do it on your end, or not. |
| `player_number` | 1-4 | Defines number of players. There is no in-program validation, do it on your end, or not. |
| `map_name` | any | Is is required to pass a map name while using this format. However, unless `perfect_times` argument is used, valid map code is not necessary, therefore you can pass any placeholder instead. |
| `arguments` | any | Optional arguments to be passed accordingly to [ARGUMENTS.MD](https://github.com/Zi0MIX/ZM-RoundCalculator/blob/main/ARGUMENTS.MD) document. Passing the argument will change it's default state. |
| `mods` | any | Optional mods to be passed accordingly to [ARGUMENTS.MD](https://github.com/Zi0MIX/ZM-RoundCalculator/blob/main/ARGUMENTS.MD) document. The program will only support one mod at a time, however more can be passed, they'll just have no effect. |
| `spec_rounds` | - | Currently not supported for CLI calls. |

## Functions
Some of the functions used in main program can succesfully be used in UI to obtain helpful information. Those functions are:
| CALL | ARGUMENTS | OUTPUT |
| --- | --- | --- |
| `get_answer_blueprint()` | - | Returns an example answer from the program in dictionary(json) format, every output from the program will follow the same pattern, as they're all assembled using this function. |
| `get_arguments()` | - | Returns dictionary(json) containing nested dictionaries with properties of each argument. Check details below. |
| `get_mods()` | - | Returns a list of strings contaitning custom mod flags. If one or more of those mods are detected in input, the program will abandon it's normal workflow and apply a mod. |
| `map_translator()` | `map_code`:`str` | Returns the name of the map in readable format. Supports all maps from global variable `MAP_LIST`. |

## Global variables
| VARIABLE | TYPE | DESCRIPTION |
| --- | --- | --- |
| `OWN_PRINT` | `bool` | Controls the use of built in function responsible for displaying results. It's recommended to keep it on `False` for web implementation and handle output yourself, as you'll have no control over the format of the output. The program will still return data normally after printing it.
| `MAP_LIST` | `tuple`(array) | Controls which maps are accepted if `perfect_times` argument is used. Do not modify unless you're also implementing changes in the calculator itself. |
| `MAP_DOGS` | `tuple`(array) | Controls which maps are maps with dog rounds. |

## Api Config
Api config is a file that can be used for changing certain behaviours of the program, as listed below.

<table>
    <tr>
        <td>KEY</td>
        <td>TYPE</td>
        <td>CONTENT</td>
    </tr>
    <tr>
        <td><code>own_print</code></td>
        <td><code>bool</code></td>
        <td>Used to toggle <code>OWN_PRINT</code> variable.</td>
    </tr>
    <tr>
        <td><code>arg_overrides</code></td>
        <td><code>json</code></td>
        <td>
            Here you can define overrides for default properties of each argument. Inside of this key define json with following structure: Example:
<pre lang="json">
{
    "break": {
        "use_in_web": false,
        "exp": "It's empty line innit"
    }
}
</pre>
        </td>
    </tr>
    <tr>
        <td><code>new_rules</code></td>
        <td><code>json</code></td>
        <td>
            Define additional rules for argument conflicts. Example:
<pre lang="json">
{
    "my_new_rule1": {
        "master": "perfect_times",
        "slave": "detailed",
        "eval_true": true
    }
}
</pre>
        </td>
    </tr>
    <tr>
        <td><code>custom_translations</code></td>
        <td><code>json</code></td>
        <td>
            Apply your own translations to <code>map_translator()</code> function. Example:
<pre lang="json">
{
    "my_custom_map": "Best map",
    "his_custom_map": "Bad map"
}
</pre>
        </td>
    </tr>
</table>

Example config file looking like this:
```json
{
    "api": {
        "own_print": true,
        "arg_overrides": {
            "break": {
                "use_in_web": false,
                "exp": "It's empty line innit"
            }
        },
        "new_rules": {
            "my_new_rule1": {
                "master": "perfect_times",
                "slave": "detailed",
                "eval_true": true
            }
        },
        "custom_translations": {
            "my_custom_map": "Best map",
            "his_custom_map": "Bad map"
        }
    }
}
```

## Arguments
Current list of arguments is available [here](https://github.com/Zi0MIX/ZM-RoundCalculator/blob/main/ARGUMENTS.MD).
- Arguments to be handled in UI
    * Those arguments are used in the program only if it's own function for assembling the output is used, if you're handling the output yourself, you have to support those arguments in UI.
    * Check column `TYPE` in `Optional arguments` table in the doc linked above. Arguments listed as `UI` require handling outside of the main program.
- Conflicts
    * Some arguments conflict with others, or simply won't work unless certain combination of other arguments is achieved. It's briefly explained in the description of each argument, if you require more informations about conflicts, please check out `curate_arguments()` function in the program.
- `use_in_web`
    * If you want to use provided mechanism for determining which arguments are to be used in UI, but want to use different set than what is defined, head to `get_arguments()` function and modify boolean under the key `use_in_web` for the argument you wish to modify.
- `special_rounds`
    * Recommended use is to keep this argument disabled for web ui, and the pass is as `True` to keep the functionality on at all times, then manage it by controlling what is passed as special round (look in `Type json`). Altermatively manage it from UI, will allow for dynamic input windows and such.

### Structure of argument dictionary

```json
"argument_key": {
    "use_in_web": "bool",
    "readable_name": "str",
    "shortcode": "str",
    "default_state": "bool",
    "exp": "str"
}
```
- `use_in_web` - Can be used to determine whether the argument shows in your interface.
- `readable_name` - Can be used to get a readable name for each argument, recommended solution for the scenario where new arguments are implemented.
- `shortcode` - Shortcode used to toggle the state of the argument in terminal implementations.
- `default_state` - Provides default state for each argument, selecting an argument will toggle the default state.
- `exp` - Short explanation of what the argument is doing.
    

## Output
Program outputs data as an array of dictionaries(jsons). Structure:
```json
[{
    "type": "str",
    "mod": "str",
    "message": "str",
    "round": "int",
    "players": "int",
    "zombies": "int",
    "hordes": "float",
    "time_seconds": "float",
    "time_output": "str",
    "special_average": "float",
    "spawnrate": "float",
    "raw_spawnrate": "float",
    "network_frame": "float",
    "map_name": "str",
    "class_content": "dict"
}, ...]
```
If not changed by arguments, current format for in-program outputs goes as is:
- Perfect round times:
`Round <round> will spawn in <time_output> and has <zombies> zombies. (Spawnrate: <spawnrate> / Network frame: <network_frame>).`
- Perfect times:
`Perfect time to round <round> is <time_output> on <map_name>.`</br>
You can preserve this format or come up with your own.

| KEY | TYPE | DATA | DESCRIPTION |
| --- | --- | --- | --- |
| `type` | `str` | `blueprint`, `round_time`, `perfect_times`, `mod`, `error` | Informs what kind of data is returned (doesn't change the structure of the dictionary). |
| `mod` | `str` | available mods | Flag of the mod that is used. |
| `message` | `str` | any | String to be displayed for `mod` and `error` types. |
| `round` | `int` | 1-255 | Round number. |
| `players` | `int` | 1-4 | Player number. |
| `zombies` | `int` | 0+ | Zombies number. |
| `hordes` | `float` | any | Number of hordes. |
| `time_seconds` | `float` | any | Numeric value for time in seconds. |
| `time_output` | `str` | any | Time value to be print out. |
| `special_average` | `float` | any | The average of special rounds. |
| `spawnrate` | `float` | any | Spawnrate in seconds. |
| `raw_spawnrate` | `float` | any | Raw spawnrate in seconds. |
| `network_frame` | `float` | `0.05` / `0.10` | Network frame value. |
| `map_name` | `str` | func `map_translator()` | Returns name of the map. |
| `class_content` | `dict` | all class vars | Dump of all variables of the class used in the calculation (for debugging). |
