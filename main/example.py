from dataclasses import dataclass, field

class MyRandomClass:
    def __init__(self, data: list, description: str) -> None:
        self.data = data
        self.desctiption = description

@dataclass
class FirstInterface:
    name: str
    len_to_calculate: int = field(init=False)

@dataclass
class SecondInterface:
    random_aggregation: MyRandomClass
    processed: str = field(init=False)

@dataclass
class TestImplementation(FirstInterface, SecondInterface):

    def __post_init__(self):
        self.len_to_calculate = len(self.name)
        self.processed = f'{self.random_aggregation.desctiption}: {self.random_aggregation.data}'
        self.__repr__()


my_random = MyRandomClass([1, 2, 3], 'three numbers')

test = TestImplementation(my_random, 'some name')

print(test)

