function aepocraft:gamerules

effect give @a mining_fatigue infinite 3 true
execute as @a run attribute @s attack_speed modifier add aepocraft:effect.mining_fatigue 0.6666666666666666 add_multiplied_total
