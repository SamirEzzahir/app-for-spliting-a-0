'''
class Person:
    def __init__(self, name, age):
        self.name = name    # attach data to the object
        self.age = age

# create an object
p = Person("Samir", 25)

print(p.name)  # Samir
print(p.age)   # 25


class Person:
    name: str     # just a type hint, no value
    age: int      # same here

# create an object


p = Person

p.age = 25
p.name = "samir"

print(p.name)  # Samir
print(p.age)   # 25

'''
from  scapy import all  

listFriends = ["samir","zaki","kamal","jamal","bilal"]


for i in range(len(listFriends)):
    print(listFriends[i])


print("-------------")
age = 10
if age >= 18:
    print("adult")
else:
    print("child")

print("-------------")

for i in range(5):
    print(i)

print("-------------")

while age > 0:
    print(age)
    age -= 1
    