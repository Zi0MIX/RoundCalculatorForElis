#include common_scripts\utility;
#include maps\mp\_utility;
#include maps\mp\zombies\_zm_utility;
#include maps\mp\zombies\_zm_net;
#include maps\mp\zombies\_zm_laststand;
#include maps\mp\zombies\_zm_ai_basic;
#include maps\mp\animscripts\zm_utility;
#include maps\mp\animscripts\zm_shared;
#include maps\mp\zombies\_zm_audio;
#include maps\mp\zombies\_zm_blockers;
#include maps\mp\animscripts\zm_death;
#include maps\mp\animscripts\zm_run;
#include maps\mp\zombies\_zm_powerups;
#include maps\mp\zombies\_zm_score;
#include maps\mp\zombies\_zm_pers_upgrades;
#include maps\mp\zombies\_zm_stats;
#include maps\mp\zombies\_zm_pers_upgrades_functions;
#include maps\mp\zombies\_zm;
#include maps\mp\zombies\_zm_spawner;
#include maps\mp\zombies\_zm_weapons;
#include maps\mp\zombies\_zm_ai_faller;

main()
{
    replaceFunc(maps\mp\zombies\_zm::ai_calculate_health, ::ai_debug_health);
}

ai_debug_health()
{
    level.zombie_health = level.zombie_vars["zombie_health_start"];

    for ( i = 2; i <= 255; i++ )
    {
        if ( i >= 10 )
        {
            old_health = level.zombie_health;
            level.zombie_health += int( level.zombie_health * level.zombie_vars["zombie_health_increase_multiplier"] );

            if ( level.zombie_health < old_health )
            {
                level.zombie_health = old_health;
                break;
            }
        }
        else
            level.zombie_health = int( level.zombie_health + level.zombie_vars["zombie_health_increase"] );
    }

    zombie_health = 150;
    for ( i = 2; i <= 255; i++ )
    {
        if ( i >= 10 )
        {
            old_health = zombie_health;
            zombie_health += int( zombie_health * level.zombie_vars["zombie_health_increase_multiplier"] );

            if ( zombie_health < old_health )
            {
                zombie_health = old_health;
            }
        }
        else
            zombie_health = int( zombie_health + level.zombie_vars["zombie_health_increase"] );

        print("ZM Health on round " + i + ": " + zombie_health);
    }
}