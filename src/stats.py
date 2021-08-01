class Stats:
    CURRENT_HEALTH = 'current_health'
    MAXIMUM_HEALTH = 'maximum_health'
    MIN_DAMAGE = 'min_damage'
    MAX_DAMAGE = 'max_damage'
    DEFENCE = 'defence'

    @staticmethod
    def calculate_dependents(stat_name, old_value, new_value, stat_holder):
        stat_changes = {}

        if stat_name == Stats.MAXIMUM_HEALTH:
            if stat_holder.has_stat(Stats.CURRENT_HEALTH):
                health_percentage = stat_holder.get_stat(Stats.CURRENT_HEALTH) / old_value
                new_current_health = round(new_value * health_percentage)
                stat_changes[Stats.CURRENT_HEALTH] = new_current_health - stat_holder.get_stat(Stats.CURRENT_HEALTH)
            else:
                stat_changes[Stats.CURRENT_HEALTH] = new_value

        return stat_changes
