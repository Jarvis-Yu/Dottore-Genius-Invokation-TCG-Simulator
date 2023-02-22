from dgisim.src.helper.level_print import level_print_single

class Character:
    def defeated(self) -> bool:
        # TODO
        return False

    def name(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return self.to_string(0)
    
    def to_string(self, indent: int) -> str:
        return level_print_single(self.name(), indent)

class Keqing(Character):
    pass

class Kaeya(Character):
    pass

class Oceanid(Character):
    pass