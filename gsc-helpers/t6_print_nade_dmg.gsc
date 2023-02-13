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
    replaceFunc(maps\mp\zombies\_zm::actor_damage_override, ::actor_damage_override_notifier);
}

init()
{
    level thread listen_to_damage();
}

listen_to_damage()
{
	while (true)
	{
		level waittill("dmg_stats", damage, ent, inflictor);
		print("DMG: " + damage + " / DISTANCE: " +  distance(ent, inflictor));
	}
}

actor_damage_override( inflictor, attacker, damage, flags, meansofdeath, weapon, vpoint, vdir, shitloc, psoffsettime, boneindex )
{
    if ( !isdefined( self ) || !isdefined( attacker ) )
        return damage;

    if ( weapon == "tazer_knuckles_zm" || weapon == "jetgun_zm" )
        self.knuckles_extinguish_flames = 1;
    else if ( weapon != "none" )
        self.knuckles_extinguish_flames = undefined;

    if ( isdefined( attacker.animname ) && attacker.animname == "quad_zombie" )
    {
        if ( isdefined( self.animname ) && self.animname == "quad_zombie" )
            return 0;
    }

    if ( !isplayer( attacker ) && isdefined( self.non_attacker_func ) )
    {
        if ( isdefined( self.non_attack_func_takes_attacker ) && self.non_attack_func_takes_attacker )
            return self [[ self.non_attacker_func ]]( damage, weapon, attacker );
        else
            return self [[ self.non_attacker_func ]]( damage, weapon );
    }

    if ( !isplayer( attacker ) && !isplayer( self ) )
        return damage;

    if ( !isdefined( damage ) || !isdefined( meansofdeath ) )
        return damage;

    if ( meansofdeath == "" )
        return damage;

    old_damage = damage;
    final_damage = damage;

    if ( isdefined( self.actor_damage_func ) )
        final_damage = [[ self.actor_damage_func ]]( inflictor, attacker, damage, flags, meansofdeath, weapon, vpoint, vdir, shitloc, psoffsettime, boneindex );
/#
    if ( getdvarint( _hash_5ABA6445 ) )
        println( "Perk/> Damage Factor: " + final_damage / old_damage + " - Pre Damage: " + old_damage + " - Post Damage: " + final_damage );
#/
    if ( attacker.classname == "script_vehicle" && isdefined( attacker.owner ) )
        attacker = attacker.owner;

    if ( isdefined( self.in_water ) && self.in_water )
    {
        if ( int( final_damage ) >= self.health )
            self.water_damage = 1;
    }

    attacker thread maps\mp\gametypes_zm\_weapons::checkhit( weapon );

    if ( attacker maps\mp\zombies\_zm_pers_upgrades_functions::pers_mulit_kill_headshot_active() && is_headshot( weapon, shitloc, meansofdeath ) )
        final_damage *= 2;

    if ( isdefined( level.headshots_only ) && level.headshots_only && isdefined( attacker ) && isplayer( attacker ) )
    {
        if ( meansofdeath == "MOD_MELEE" && ( shitloc == "head" || shitloc == "helmet" ) )
            return int( final_damage );

        if ( is_explosive_damage( meansofdeath ) )
            return int( final_damage );
        else if ( !is_headshot( weapon, shitloc, meansofdeath ) )
            return 0;
    }

	if (meansofdeath == "MOD_GRENADE" || meansofdeath == "MOD_GRENADE_SPLASH")
        level notify("dmg_stats", final_damage, self.origin, inflictor.origin);
    return int( final_damage );
}
