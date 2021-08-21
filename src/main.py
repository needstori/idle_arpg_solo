import time
from random import seed

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import (NumericProperty, ObjectProperty, StringProperty)
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen

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


class WorldAreaDisplay(Label):
    areaName = StringProperty("")
    defeatedMonsters = NumericProperty(0)
    totalMonsters = NumericProperty(0)

    def update_display(self, area_name, defeated_monsters, total_monsters):
        self.areaName = area_name
        self.defeatedMonsters = defeated_monsters
        self.totalMonsters = total_monsters

class GameScreen(Screen):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game

    def update_display(self, dt):
        pass


class BattleScreen(GameScreen):
    player_display = ObjectProperty(None)
    monster_display = ObjectProperty(None)
    world_area_display = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.update_display(0)

    def update_display(self, dt):
        super().update_display(dt)
        if self.game.player:
            self.player_display.update_character_display(self.game.player.stats)
        if self.game.current_monster:
            self.monster_display.update_character_display(self.game.current_monster.stats)
        if self.game.world_area:
            self.world_area_display.update_display("Forest", self.game.world_area.get_dead_monsters(),
                                                   self.game.world_area.get_total_monsters())


class EmbarkScreen(GameScreen):
    player_display = ObjectProperty(None)
    start_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.start_button.bind(on_press=self.on_start_press)

    def update_display(self, dt):
        super().update_display(dt)
        if self.game:
            self.player_display.update_character_display(self.game.player.stats)

    def on_start_press(self, instance):
        self.game.embark()
        self.manager.current = "battle_screen"


class GameState:
    AT_BASE = 'at_base'
    COMBAT = 'combat'


class IdleArpgGame:
    def __init__(self):
        self.player = None
        self.world_area = None
        self.current_monster = None

        self.current_state = GameState.AT_BASE

    def create_player(self):
        # Create the player
        self.player = Character()
        self.player.stats.add_stat(Stats.MIN_DAMAGE, 1)
        self.player.stats.add_stat(Stats.MAX_DAMAGE, 3)
        self.player.stats.add_stat(Stats.DEFENCE, 2)

    def create_world_area(self):
        # Create a world area
        self.world_area = WorldArea()

        monster = Character()
        monster.stats.add_stat(Stats.MIN_DAMAGE, 1)
        monster.stats.add_stat(Stats.MAX_DAMAGE, 3)
        self.world_area.populate([monster], 3)

        self.current_monster = self.world_area.get_next_monster()

    def embark(self):
        self.state_transition(GameState.COMBAT)
        self.create_world_area()

    def state_transition(self, new_state):
        old_state = self.current_state

        if new_state == GameState.AT_BASE:
            if self.player:
                self.player.full_restore()
        self.current_state = new_state

    def update(self, dt):
        if self.current_state == GameState.COMBAT:
            if not self.player:
                return
            if not self.current_monster:
                if not self.world_area:
                    return
                if self.world_area.area_complete():
                    print("Player Won")
                    self.state_transition(GameState.AT_BASE)
                    return
            if self.player.alive():
                if self.current_monster.alive():
                    self.player.attack(self.current_monster)
                    self.current_monster.attack(self.player)
                else:
                    self.current_monster = self.world_area.get_next_monster()
            else:
                print("Player Dead")
                self.state_transition(GameState.AT_BASE)
        elif self.current_state == GameState.AT_BASE:
            pass



class IdleArpgApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.screen_manager = None
        self.game = None

    def update_current_screen(self, dt):
        # Check for current game state and change screen if change came from game
        if self.game.current_state == GameState.AT_BASE and \
                self.screen_manager.current is not "embark_screen":
            self.screen_manager.current = "embark_screen"
        self.screen_manager.current_screen.update_display(dt)

    def build(self):

        # Create the game state
        self.game = IdleArpgGame()
        self.game.create_player()

        self.screen_manager = ScreenManager()
        battle_screen = BattleScreen(game=self.game, name="battle_screen")
        # battle_screen.update_display()
        self.screen_manager.add_widget(battle_screen)

        embark_screen = EmbarkScreen(game=self.game, name="embark_screen")
        self.screen_manager.add_widget(embark_screen)
        self.screen_manager.current = "embark_screen"
        embark_screen.update_display(0)

        # Setup the game clock and display clock
        Clock.schedule_interval(self.game.update, 1)
        Clock.schedule_interval(self.update_current_screen, 1)
        return self.screen_manager


IdleArpgApp().run()
