def days_to_target(starting_population, target_population):
    count = 0
    while starting_population < target_population:
        starting_population = starting_population * 2
        count += 1
    print(count)
    return()


def print_shopping_list(shopping_list):
    for i in shopping_list:
        print(f'[] {i}')
        

def check_speed(speed):
    if speed <= 50:
        print('Ok.')
    elif speed > 50:
        print("Too fast!")
        if speed >= 75:
            print("Licence suspended.")

# while True:
#     x = int(input("Speed: "))
#     if x == "":
#         break
#     check_speed(x)

# days_to_target(float(input("start: ")), int(input("end: ")))

def draw_out_string(string):
    for x in string:
        print(x * len(string))

def breakingRecords(scores):
    current_max = scores[0]
    current_min = scores[0]
    record_br = []e>

    for x in scores:
        x = int(x)
        if x > current_max:
            record_br.append(0)
            current_max = x
        elif x < current_min:
            record_br.append(1)
            current_min = x
    print(record_br)

def countApplesAndOranges(s, t, a, b, apples, oranges):
    ttla = 0
    ttlo = 0
    validList = []
    for x in range(s,t+1):
        validList.append(x)
    for apple in apples:
        if a + apple in validList:
            ttla += 1
    for orange in oranges:
        if b + orange in validList:
            ttlo += 1
    print(ttla)
    print(ttlo)

# s = int(input("House point one: "))
# t = int(input("House point two: "))
# a = int(input("Apple tree point: "))
# b = int(input("Orange tree point: "))
# apple = [5, -4, 2, -10, 9]
# orange = [5, -4, 2, -10, 9]
# countApplesAndOranges


def countKeyChanges(s):
    count = 0
    s = s.lower()
    for x in range(len(s) - 1):
        if s[x] != s[x + 1]:
            count += 1
    print(count)

# countKeyChanges("AaAabaaA")


def climbStairs(n):
    if n <= 1:
        return 1
    x = [1] * (n + 1)

    for y in range(2, n+1):
        x[y] = x[y - 1] + x[y - 2]
    return sum(x)

print(climbStairs(121727)) 
