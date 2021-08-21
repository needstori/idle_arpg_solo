import random

from stats import Stats
from stat_holder import StatHolder
from item import Item


class Character:
    def __init__(self):
        self.stats = StatHolder()
        self.stats.active = True
        self.currentItem: Item() = None
        self.level = 1

        # Add base stats per level
        base_max_health = 10 + (self.level - 1) * 5
        self.stats.add_stat(Stats.MAXIMUM_HEALTH, base_max_health)

    def __str__(self):
        print_string = "\n"
        print_string += "Character Stats:\n"
        for stat_name, stat_value in self.stats.get_existing_stats():
            print_string += f"{stat_name}: {stat_value}\n"
        return print_string

    def alive(self):
        return self.get_current_health() > 0

    def full_restore(self):
        self.stats.clear_stat(Stats.CURRENT_HEALTH)
        self.stats.add_stat(Stats.CURRENT_HEALTH, self.stats.get_stat(Stats.MAXIMUM_HEALTH))

    def attack(self, target_character: 'Character'):
        min_damage = self.stats.get_stat(Stats.MIN_DAMAGE)
        max_damage = self.stats.get_stat(Stats.MAX_DAMAGE)
        damage_roll = random.randrange(min_damage, max_damage + 1)
        damage = max(damage_roll - target_character.stats.get_stat(Stats.DEFENCE), 0)
        target_character.stats.remove_stat(Stats.CURRENT_HEALTH, damage)

    def get_current_health(self):
        return self.stats.get_stat(Stats.CURRENT_HEALTH)

    def remove_item(self):
        if self.currentItem is None:
            return None

        current_item = self.currentItem

        for stat_name, stat_value in current_item.stats.get_existing_stats():
            self.stats.remove_stat(stat_name, stat_value)

        return current_item

    def equip_item(self, to_equip: Item):
        old_item = None

        if self.currentItem is not None:
            old_item = self.remove_item()

        for stat_name, stat_value in to_equip.stats.get_existing_stats():
            self.stats.add_stat(stat_name, stat_value)

        self.currentItem = to_equip

        return old_item

    def level_up(self):
        if self.level < 100:
            self.level += 1
            self.stats.add_stat(Stats.MAXIMUM_HEALTH, 5)

    def level_down(self):
        if self.level > 1:
            self.level -= 1
            self.stats.remove_stat(Stats.MAXIMUM_HEALTH, 5)
