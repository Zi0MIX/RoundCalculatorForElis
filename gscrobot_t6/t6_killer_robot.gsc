#include maps\mp\zombies\_zm_utility;
#include maps\mp\zombies\_zm;
#include common_scripts\utility;

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
    level.round_wait_func = ::RoundWaitNew;
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
            print("diff = " + getTime() + " - " + last_kill + " = " + (getTime() - last_kill));
            last_kill = int(getTime());
        }
    }
}

TimeBetweenRoundOver()
{
    while (true)
    {
        level waittill("between_round_over");
        rb = int(getTime());
        print("Trigger 'between_round_over' of round " + level.round_number + ": " + rb);
    }
}

TimeEvents()
{
    self thread TimeBetweenRoundOver();
    while (true)
    {
        level waittill("start_of_round");
        rs = int(getTime());
        rnd = level.round_number;
        print("Trigger 'start_of_round' of round " + rnd + ": " + rs);

        level waittill("end_of_round");
        re = int(getTime());
        print("Trigger 'end_of_round' of round " + rnd + ": " + re);
        print("Round " + rnd + " took: " + (int(getTime()) - rs));
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
        level waittill("between_round_over");
        print("level.zombie_vars['zombie_spawn_delay']: " + level.zombie_vars["zombie_spawn_delay"]);
    }
}

RoundWaitNew()
{
    func_enter = int(getTime());

    level endon( "restart_round" );
    wait 1;

    if ( flag( "dog_round" ) )
    {
        wait 7;

        while ( level.dog_intermission )
            wait 0.5;

        print("round_wait() start: " + func_enter + " / returned at: " + int(getTime()));

        increment_dog_round_stat( "finished" );

    }
    else
    {
        while ( true )
        {
            should_wait = 0;

            if ( isdefined( level.is_ghost_round_started ) && [[ level.is_ghost_round_started ]]() )
                should_wait = 1;
            else
                should_wait = get_current_zombie_count() > 0 || level.zombie_total > 0 || level.intermission;

            if ( !should_wait )
                return;

            if ( flag( "end_round_wait" ) )
                return;

            wait 1.0;
        }
    }
}
