import time
from random import seed

from kivy.app import App
from kivy.uix.widget import Widget

from character import Character
from stats import Stats
from world_area import WorldArea
from item import Item


seed(time.time())


player = Character()
player.stats.add_stat(Stats.MIN_DAMAGE, 1)
player.stats.add_stat(Stats.MAX_DAMAGE, 3)
player.stats.add_stat(Stats.DEFENCE, 2)

monster = Character()
monster.stats.add_stat(Stats.MIN_DAMAGE, 1)
monster.stats.add_stat(Stats.MAX_DAMAGE, 3)


# Make an item and add it to the player
new_item = Item()
new_item.stats.add_stat(Stats.MAXIMUM_HEALTH, 5)
print(player.equip_item(new_item))

# Make another item and add it to the player. First item should be removed
second_item = Item()
second_item.stats.add_stat(Stats.MAX_DAMAGE, 3)
print(player.equip_item(second_item))

# Generate a basic world area
new_area = WorldArea()
new_area.populate([monster], 10)

current_monster = new_area.get_next_monster()

print(player)

while current_monster is not None and player.alive():

    while current_monster.alive() and player.alive():
        player.attack(current_monster)
        current_monster.attack(player)

    if not current_monster.alive():
        print("Monster died")

    if not player.alive():
        print("Player died")
    current_monster = new_area.get_next_monster()

print(player)
print(f"Monsters killed: {new_area.get_dead_monsters()}/{new_area.get_total_monsters()}")


class IdleArpgUI(Widget):
    pass


class IdleArpgApp(App):
    def build(self):
        return IdleArpgUI()

IdleArpgApp().run()
