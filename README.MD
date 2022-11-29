# Program
ZM Round Calculator is a little tool, initially meant to just provide perfect round end times for round speedrunners in Black Ops and Black Ops 2 zombies. It has gained some weight since then.
- Values tested against real life scenarios in Black Ops and Black Ops 2. 
    * For BO2 Plutonium it assumes you're running a correct Spawn Fix (yes it's still neeeded, no the ones that were made originally are not fixing the issue), you can use [First Room Fix](https://github.com/Zi0MIX/T6-FIRST-ROOM-FIX).
- Check [ARGUMENTS](https://github.com/Zi0MIX/ZM-RoundCalculator/blob/main/ARGUMENTS.MD) file for more info on arguments.
- You can see some useful data obtained via this program on [this spreadsheet](https://docs.google.com/spreadsheets/d/1Uqs-PKVD_CKicYV1kncH9591prKiomFae2t4cb-qAEI/edit?usp=sharing).
- Check out [web version](https://zi0mix.github.io/) of this program.

### Perfect times calculations
- Maps without special rounds should be accurate to the second
- Maps with dogs are implemented, but may require more tuning, for now some assumptions were made, some feedback would be appreciated
- Maps with other special rounds are not yet implemented

# Credits
- Furret for helping with figuring out and testing actual spawns behaviour.
- JezuzLizard for filling some knowledge gaps in terms of GSC behaviour.
- BanMyXb0x for helping with analysing stuff.
- Yojurt and Huth for testing.

# Dependencies
- One outside library is required, only if program is run manually via interpreter. If used as API (either called via terminal or through web), this dependency is not needed.
    * [colorama](https://pypi.org/project/colorama/).