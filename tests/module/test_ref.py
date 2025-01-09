class Food:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Food({self.name})"


class Animal:
    def __init__(self, name, age, food1, food2):
        self.name = name
        self.age = age
        self.food1 = food1
        self.food2 = food2

    def __repr__(self):
        return f"{self.name}({self.age})-f1({self.food1})-f2({self.food2})"

    def run(self):
        print(f"{self.name} is running")


a = Animal("cat", 12, Food("fish"), Food("meat"))
b = Animal("dog", 24, Food("bone"), Food("beaf"))
c = [a, b]
print(a)
print(b)


def xtest(c):
    res = []
    for item in c:
        item.food1 = item.food2
        res.append(item)
    return res


xtest(c)
print(xtest(c))
print(a)
print(b)
