from automata import find_pattern_occurrences, regex_to_nfa

# Задание 1 - поиск подстроки
res = find_pattern_occurrences("ABA", "ABABABA")
print("Результат поиска 'ABA' в 'ABABABA':", res)

# Задание 2 - преобразование регулярного выражения
n, trans, s, a = regex_to_nfa(r"^[\w\.-]+@[\w\.-]+\.\w+")
print(f"Количество состояний: {n}")
print(f"Начальное состояние: {s}")
print(f"Принимающее состояние: {a}")
print("Таблица переходов:")
for state, transitions in trans.items():
    print(f"  Состояние {state}: {transitions}")