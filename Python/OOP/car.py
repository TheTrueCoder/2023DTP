import pprint

class Car:
    speed = 0

    def __init__(self, make: str, model: str, year: int) -> None:
        self.make = make
        self.model = model
        self.year = year

    def celly(self, amount) -> None:
        self.speed += amount

    def stoppah(self, amount) -> None:
        self.speed -= amount

    def get_speed(self) -> int:
        return self.speed


my_first_car = Car("Tesla", "X", 2021)

print(my_first_car.speed)
my_first_car.celly(69)
print(my_first_car.speed)
my_first_car.stoppah(9)
print(my_first_car.speed)
my_first_car.celly(20)
print(my_first_car.get_speed())
