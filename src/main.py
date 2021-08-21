import time
from random import seed

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import (NumericProperty, ObjectProperty)
from kivy.clock import Clock

from character import Character
from stats import Stats
from stat_holder import StatHolder
from world_area import WorldArea
from item import Item


seed(time.time())


# player = Character()
# player.stats.add_stat(Stats.MIN_DAMAGE, 1)
# player.stats.add_stat(Stats.MAX_DAMAGE, 3)
# player.stats.add_stat(Stats.DEFENCE, 2)
#
# monster = Character()
# monster.stats.add_stat(Stats.MIN_DAMAGE, 1)
# monster.stats.add_stat(Stats.MAX_DAMAGE, 3)
#
#
# # Make an item and add it to the player
# new_item = Item()
# new_item.stats.add_stat(Stats.MAXIMUM_HEALTH, 5)
# print(player.equip_item(new_item))
#
# # Make another item and add it to the player. First item should be removed
# second_item = Item()
# second_item.stats.add_stat(Stats.MAX_DAMAGE, 3)
# print(player.equip_item(second_item))
#
# # Generate a basic world area
# new_area = WorldArea()
# new_area.populate([monster], 10)
#
# current_monster = new_area.get_next_monster()
#
# print(player)
#
# while current_monster is not None and player.alive():
#
#     while current_monster.alive() and player.alive():
#         player.attack(current_monster)
#         current_monster.attack(player)
#
#     if not current_monster.alive():
#         print("Monster died")
#
#     if not player.alive():
#         print("Player died")
#     current_monster = new_area.get_next_monster()
#
# print(player)
# print(f"Monsters killed: {new_area.get_dead_monsters()}/{new_area.get_total_monsters()}")


class CharacterDisplay(GridLayout):
    maxHealth = NumericProperty(0)
    currentHealth = NumericProperty(0)
    minDamage = NumericProperty(0)
    maxDamage = NumericProperty(0)
    defence = NumericProperty(0)

    def update_character_display(self, stats: StatHolder):
        self.maxHealth = stats.get_stat(Stats.MAXIMUM_HEALTH)
        self.currentHealth = stats.get_stat(Stats.CURRENT_HEALTH)
        self.minDamage = stats.get_stat(Stats.MIN_DAMAGE)
        self.maxDamage = stats.get_stat(Stats.MAX_DAMAGE)
        self.defence = stats.get_stat(Stats.DEFENCE)


class IdleArpgUI(GridLayout):
    player_display = ObjectProperty(None)
    monster_display = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.player = Character()
        self.player.stats.add_stat(Stats.MIN_DAMAGE, 1)
        self.player.stats.add_stat(Stats.MAX_DAMAGE, 3)
        self.player.stats.add_stat(Stats.DEFENCE, 2)

        self.monster = Character()
        self.monster.stats.add_stat(Stats.MIN_DAMAGE, 1)
        self.monster.stats.add_stat(Stats.MAX_DAMAGE, 3)

        self.player_display.update_character_display(self.player.stats)
        self.monster_display.update_character_display(self.monster.stats)

    def update(self, dt):
        if self.monster.alive() and self.player.alive():
            self.player.attack(self.monster)
            self.monster.attack(self.player)
            self.player_display.update_character_display(self.player.stats)
            self.monster_display.update_character_display(self.monster.stats)


class IdleArpgApp(App):
    def build(self):
        game = IdleArpgUI()
        Clock.schedule_interval(game.update, 1)
        return game


IdleArpgApp().run()
