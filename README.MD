# Program
- These values have been tested on BO1 and BO2, they're not validated for other games, however it's possible they're matching. For BO2 Plutonium it assumes you're running a correct Spawn Fix (yes it's still neeeded, no the ones that were made originally are not fixing the issue), you can use [First Room Fix](https://github.com/Zi0MIX/T6-FIRST-ROOM-FIX).
- Check ARGUMENTS file for more info on arguments.
- Version 1 had some issues logic wise, so on some rounds produced results could've been inaccurate, version 2 fixes that problem.
- You can see some useful data obtained via this program on [this spreadsheet](https://docs.google.com/spreadsheets/d/1Uqs-PKVD_CKicYV1kncH9591prKiomFae2t4cb-qAEI/edit?usp=sharing).

# Perfect times
- Maps without special rounds should be accurate to the second
- Maps with dogs are implemented, but may require more tuning, for now some assumptions were made, some feedback would be appreciated
- Maps with other special rounds are not yet implemented

# Credits
- Furret for helping with figuring out and testing actual spawns behaviour.
- JezuzLizard for filling some knowledge gaps in terms of GSC behaviour.
- BanMyXb0x for helping with analysing stuff.
- Yojurt and Huth for testing.

# Dependencies
- You can just run the program directly from .py file if you don't trust the exe file in releases, it requires one outside dependency, [colorama](https://pypi.org/project/colorama/).