import copy

from character import Character
import random


class WorldArea:
    def __init__(self):
        self.monsters: list[Character] = []

    def populate(self, monster_list, monster_count):
        for index in range(monster_count):
            monster_index = random.randrange(0, len(monster_list))
            self.monsters.append(copy.deepcopy(monster_list[monster_index]))

    def get_next_monster(self):
        for monster in self.monsters:
            if monster.alive():
                return monster

        return None

    def get_total_monsters(self):
        return len(self.monsters)

    def get_dead_monsters(self):
        dead_monsters = 0
        for monster in self.monsters:
            if not monster.alive():
                dead_monsters += 1

        return dead_monsters
