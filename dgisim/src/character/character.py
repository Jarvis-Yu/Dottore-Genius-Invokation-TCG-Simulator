from dgisim.src.helper.level_print import level_print_single

class Character:
    def defeated(self) -> bool:
        raise Exception("Not Implemented")

    def __str__(self) -> str:
        return self.to_string(0)
    
    def to_string(self, indent: int) -> str:
        return level_print_single("BaseCharacter", indent)

class Keqing(Character):
    pass

class Kaeya(Character):
    pass

class Oceanid(Character):
    pass