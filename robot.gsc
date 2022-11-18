#include maps\mp\zombies\_zm_utility;

init()
{
    level thread OnStart();
    level thread TimeEvents();
    level thread RobotHud();
    level thread ZombieSpawnDelay();
}

OnStart()
{
    level waittill("connected", player);
    player thread OnConnect();
}

OnConnect()
{
    self thread KillerRobot();
}

KillerRobot()
{
    level waittill("initial_blackscreen_passed");
    self iPrintLn("^1Killer Robot");
    last_kill = getTime();

    while (true)
    {
        wait 0.05;

        if (!get_round_enemy_array().size)
            continue;

        foreach(zombie in get_round_enemy_array())
        {
            zombie doDamage(zombie.maxhealth + 69, self.origin, self);
            print(getTime() - last_kill);
        }
    }
}

TimeEvents()
{
    while (true)
    {
        level waittill("start_of_round");
        rs = int(getTime());
        rnd = level.round_number;

        level waittill("end_of_round");
        re = int(getTime());
        print("Round " + rnd + " took: " + (int(getTime()) - rs));

        iPrintLn("End of round " + rnd + ": " + ((re - rs) / 1000));
    }
}

RobotHud()
{
    self thread ZombieCount();
    self thread ActorCount();
}

ZombieCount()
{
}

ActorCount()
{
}

ZombieSpawnDelay()
{
    while (true)
    {
        level waittill("start_of_round");
        wait_network_frame();
        print("level.zombie_vars['zombie_spawn_delay']: " + level.zombie_vars["zombie_spawn_delay"]);
    }
}