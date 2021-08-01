from stats import Stats


class StatHolder:
    def __init__(self):
        self.stats = {}
        self.active = False

    def has_stat(self, stat_name):
        return stat_name in self.stats

    def add_stat(self, stat_name, value_to_add):
        old_value = 0

        if not self.has_stat(stat_name):
            self.stats[stat_name] = value_to_add
        else:
            old_value = self.stats[stat_name]
            self.stats[stat_name] += value_to_add

        # Only calculate dependent stats if an active stat user
        if self.active:
            dependent_changes = Stats.calculate_dependents(stat_name, old_value, self.stats[stat_name], self)
            for stat_name, stat_value in dependent_changes.items():
                self.add_stat(stat_name, stat_value)

    def remove_stat(self, stat_name, value_to_remove):
        self.add_stat(stat_name, -value_to_remove)

    def get_stat(self, stat_name):
        if not self.has_stat(stat_name):
            return 0

        return self.stats[stat_name]

    def clear_stat(self, stat_name):
        if self.has_stat(stat_name):
            self.stats.pop(stat_name)

    def get_existing_stats(self):
        return self.stats.items()