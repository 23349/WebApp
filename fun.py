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
        
days_to_target(float(input("start: ")), int(input("end: ")))
