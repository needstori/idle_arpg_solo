import time
from random import seed

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import (NumericProperty, ObjectProperty, StringProperty)
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.recycleview import RecycleView
from kivy.uix.behaviors import ButtonBehavior

from character import Character
from stats import Stats
from stat_holder import StatHolder
from world_area import WorldArea
from item import Item

from functools import partial


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
    inventory_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.start_button.bind(on_press=self.on_start_press)
        self.inventory_button.bind(on_press=self.on_inventory_press)

    def update_display(self, dt):
        super().update_display(dt)
        if self.game:
            self.player_display.update_character_display(self.game.player.stats)

    def on_start_press(self, instance):
        self.game.embark()
        self.manager.current = "battle_screen"

    def on_inventory_press(self, instance):
        self.game.state_transition(GameState.INVENTORY)
        self.manager.current = "inventory_screen"


class GridButton(ButtonBehavior, GridLayout):
    pass


class ItemLabel(ButtonBehavior, Label):
    pass


class ItemList(RecycleView):
    def __init__(self, **kwargs):
        super(ItemList, self).__init__(**kwargs)


class InventoryScreen(GameScreen):
    current_item_text = StringProperty("")
    player_display = ObjectProperty(None)
    player_item = Label()
    player_item_name = StringProperty("")
    item_list = ObjectProperty(None)
    navigation_embark = ObjectProperty(None)
    equip_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_item = None

        self.player_item.bind(on_press=self.show_player_items)
        self.navigation_embark.bind(on_press=self.back_to_embark)
        self.equip_button.bind(on_press=self.equip_selected)

    def display_item_from_list(self, index):
        self.selected_item = self.game.item_storage[index]
        self.update_display(0)

    def update_display(self, dt):
        super().update_display(dt)
        if self.game:
            if self.selected_item:
                item_text = self.selected_item.name + "\n"
                for stat_name, stat_value in self.selected_item.stats.get_existing_stats():
                    item_text += f"{stat_name}: {stat_value}\n"
                self.current_item_text = item_text
            if self.player_display:
                self.player_display.update_character_display(self.game.player.stats)
            if self.game.player.currentItem:
                self.player_item_name = self.game.player.currentItem.name

            self.item_list.data = [{'text': item.name, 'on_press': partial(self.display_item_from_list, index)}
                                   for index, item in enumerate(self.game.item_storage)]

    def show_player_items(self, press):
        self.selected_item = self.game.player.currentItem
        self.update_display(0)

    def equip_selected(self, press):
        if self.selected_item is None or self.game.player.currentItem == self.selected_item:
            return

        # Remove the selected item from storage and add it to the player
        new_player_item = self.selected_item
        self.game.item_storage.remove(new_player_item)
        current_player_item = self.game.player.equip_item(new_player_item)
        self.game.item_storage.append(current_player_item)

        self.update_display(0)

    def back_to_embark(self, press):
        self.game.state_transition(GameState.AT_BASE)
        self.manager.current = "embark_screen"


class GameState:
    AT_BASE = 'at_base'
    COMBAT = 'combat'
    INVENTORY = 'inventory'


class IdleArpgGame:
    def __init__(self):
        self.player = None
        self.world_area = None
        self.current_monster = None

        self.current_state = GameState.AT_BASE
        self.item_storage = []
        for i in range(10):
            new_item = Item()
            new_item.stats.add_stat(Stats.MAXIMUM_HEALTH, i)
            new_item.name = f"Item {i}"
            self.item_storage.append(new_item)

    def create_player(self):
        # Create the player
        self.player = Character()
        self.player.stats.add_stat(Stats.MIN_DAMAGE, 1)
        self.player.stats.add_stat(Stats.MAX_DAMAGE, 3)
        self.player.stats.add_stat(Stats.DEFENCE, 2)

        # Add an item to the player
        new_item = Item()
        new_item.stats.add_stat(Stats.MAXIMUM_HEALTH, 5)
        self.player.equip_item(new_item)

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
        self.screen_manager.add_widget(battle_screen)

        embark_screen = EmbarkScreen(game=self.game, name="embark_screen")
        self.screen_manager.add_widget(embark_screen)
        self.game.state_transition(GameState.AT_BASE)
        self.screen_manager.current = "embark_screen"
        embark_screen.update_display(0)

        inventory_screen = InventoryScreen(game=self.game, name="inventory_screen")
        self.screen_manager.add_widget(inventory_screen)
        # self.game.state_transition(GameState.INVENTORY)
        # self.screen_manager.current = "inventory_screen"

        # Setup the game clock and display clock
        Clock.schedule_interval(self.game.update, 1)
        Clock.schedule_interval(self.update_current_screen, 1)
        return self.screen_manager


IdleArpgApp().run()
