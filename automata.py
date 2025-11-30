from typing import List, Dict, Optional, Tuple


# Задание 1: детектор подпоследовательности с перекрывающимися вхождениями

def build_state_table(pattern: str) -> List[int]:
    """
    Строит таблицу переходов для автомата поиска подстроки
    Для каждой позиции в шаблоне определяет, в какое состояние вернуться при несовпадении

    pattern: строка-образец для поиска

    List[int]: таблица переходов между состояниями
    """
    n = len(pattern)
    state_table = [0] * n  # таблица состояний, изначально все нули
    matched_length = 0  # количество совпавших символов на текущий момент
    i = 1  # начинаем со второго символа

    while i < n:
        if pattern[i] == pattern[matched_length]:

            # символы совпали - увеличиваем длину совпадения

            matched_length += 1
            state_table[i] = matched_length
            i += 1
        else:
            if matched_length != 0:

                # откатываемся к предыдущему состоянию с частичным совпадением

                matched_length = state_table[matched_length - 1]
            else:

                # полное несовпадение - остаемся в начальном состоянии

                state_table[i] = 0
                i += 1
    return state_table


def find_pattern_occurrences(pattern: str, text: str) -> List[bool]:
    """
    Находит все вхождения pattern в text с перекрытиями используя конечный автомат

    pattern: строка-образец для поиска
    text: текст в котором ищем

    List[bool]: список, где True на позиции i означает что pattern заканчивается в text[i]
    """
    if not pattern:
        # если шаблон пустой, возвращаем все False

        return [False] * len(text)

    # строим таблицу переходов для автомата

    state_table = build_state_table(pattern)
    n, m = len(text), len(pattern)
    result = [False] * n  # результат поиска
    current_state = 0  # текущее состояние автомата (сколько символов совпало)

    for i in range(n):  # обрабатываем каждый символ текста

        # при несовпадении переходим в состояние из таблицы

        while current_state > 0 and text[i] != pattern[current_state]:
            current_state = state_table[current_state - 1]

        # проверяем совпадение текущего символа

        if text[i] == pattern[current_state]:
            current_state += 1
            if current_state == m:
                # достигли конечного состояния - нашли полное совпадение

                result[i] = True

                # возвращаемся к состоянию для поиска перекрывающихся вхождений

                current_state = state_table[current_state - 1]

                # если несовпадение и current_state==0, остаемся в начальном состоянии

    return result


# Задание 2: преобразование регулярного выражения в эквивалентный NFA (Thompson)

class NFAFragment:
    """
    Фрагмент недетерминированного конечного автомата
    Содержит начальное состояние, принимающее состояние и таблицу переходов
    """

    def __init__(self, start: int, accept: int, transitions: Dict[int, List[Tuple[Optional[str], int]]]):
        """
        start: начальное состояние фрагмента
        accept: принимающее состояние фрагмента
        transitions: таблица переходов
        """
        self.start = start
        self.accept = accept
        self.transitions = transitions


class RegexToNFAParser:
    """
    Парсер регулярных выражений в конечный автомат
    Преобразует строку регулярного выражения в эквивалентный NFA
    """

    def __init__(self, regex: str):
        """
        regex: строка регулярного выражения
        pos: текущая позиция в разборе выражения
        state_count: счетчик для генерации уникальных номеров состояний
        """

        self.regex = regex
        self.pos = 0
        self.state_count = 0

    def new_state(self) -> int:
        """
        Создает новое уникальное состояние автомата
        """

        s = self.state_count
        self.state_count += 1
        return s

    def add_transition(self, trans: Dict[int, List[Tuple[Optional[str], int]]], from_s: int, to_s: int,
                       symbol: Optional[str]):
        """
        Добавляет переход в таблицу переходов автомата.

        trans: таблица переходов
        from_s: исходное состояние
        to_s: целевое состояние
        symbol: символ перехода (None для безусловного перехода)
        """

        trans.setdefault(from_s, []).append((symbol, to_s))

    def parse(self) -> NFAFragment:
        """
        Запускает разбор регулярного выражения и возвращает готовый автомат
        """

        frag = self.parse_regex()
        return frag

    def parse_regex(self) -> NFAFragment:
        """
        Разбирает выражение с операцией ИЛИ: выражение | выражение | ...
        """

        # разбираем первый элемент

        term_frag = self.parse_term()

        # обрабатываем дополнительные элементы через ИЛИ

        while self.pos < len(self.regex) and self.regex[self.pos] == '|':
            self.pos += 1  # пропускаем символ ИЛИ
            other = self.parse_term()  # разбираем следующий элемент
            term_frag = self.union(term_frag, other)  # объединяем автоматы

        return term_frag

    def parse_term(self) -> NFAFragment:
        """
        Разбирает последовательность элементов: элемент элемент ...
        """

        elements = []

        # собираем все элементы пока не встретим специальные символы

        while self.pos < len(self.regex) and self.regex[self.pos] not in '|)':
            elements.append(self.parse_factor())

        if not elements:
            # если элементов нет - создаем автомат для пустой строки
            start = self.new_state()
            accept = self.new_state()
            trans = {}
            self.add_transition(trans, start, accept, None)  # безусловный переход
            return NFAFragment(start, accept, trans)

        # соединяем все элементы в последовательность

        frag = elements[0]
        for f in elements[1:]:
            frag = self.concatenate(frag, f)

        return frag

    def parse_factor(self) -> NFAFragment:
        """
        Разбирает элемент с возможным повторением
        """

        base = self.parse_base()  # разбираем базовый элемент

        # обрабатываем операцию повторения

        while self.pos < len(self.regex) and self.regex[self.pos] == '*':
            self.pos += 1  # пропускаем символ *
            base = self.kleene_star(base)  # применяем операцию повторения

        return base

    def parse_base(self) -> NFAFragment:
        """
        Разбирает базовый элемент: (выражение) или символ
        """

        if self.pos < len(self.regex) and self.regex[self.pos] == '(':

            # обрабатываем выражение в скобках

            self.pos += 1  # пропускаем открывающую скобку
            frag = self.parse_regex()  # разбираем внутреннее выражение

            if self.pos < len(self.regex) and self.regex[self.pos] == ')':
                self.pos += 1  # пропускаем закрывающую скобку

            return frag

        # обрабатываем одиночный символ

        c = self.regex[self.pos]
        self.pos += 1

        # создаем простой автомат для одного символа

        start = self.new_state()
        accept = self.new_state()
        trans: Dict[int, List[Tuple[Optional[str], int]]] = {}
        self.add_transition(trans, start, accept, c)  # переход по символу

        return NFAFragment(start, accept, trans)

    def concatenate(self, f1: NFAFragment, f2: NFAFragment) -> NFAFragment:
        """
        Соединяет два автомата в последовательность: первый затем второй.
        """

        # объединяем таблицы переходов

        trans = {**f1.transitions}

        for k, v in f2.transitions.items():
            trans.setdefault(k, []).extend(v)

        # соединяем принимающее состояние первого с начальным состоянием второго

        self.add_transition(trans, f1.accept, f2.start, None)

        return NFAFragment(f1.start, f2.accept, trans)

    def union(self, f1: NFAFragment, f2: NFAFragment) -> NFAFragment:
        """
        Объединяет два автомата через ИЛИ: первый | второй.
        """

        # создаем новые начальное и принимающее состояния

        start = self.new_state();
        accept = self.new_state()
        trans = {}

        # копируем все переходы из обоих автоматов

        for frag in (f1, f2):
            for k, v in frag.transitions.items():
                trans.setdefault(k, []).extend(v)

        # добавляем переходы из нового начального состояния к началам обоих автоматов

        self.add_transition(trans, start, f1.start, None)
        self.add_transition(trans, start, f2.start, None)

        # добавляем переходы от принимающих состояний к новому принимающему состоянию

        self.add_transition(trans, f1.accept, accept, None)
        self.add_transition(trans, f2.accept, accept, None)

        return NFAFragment(start, accept, trans)

    def kleene_star(self, f: NFAFragment) -> NFAFragment:
        """
        Применяет операцию повторения к автомату: фрагмент *
        """

        # создаем новые начальное и принимающее состояния

        start = self.new_state();
        accept = self.new_state()
        trans = {}

        # копируем все переходы из исходного автомата

        for k, v in f.transitions.items():
            trans.setdefault(k, []).extend(v)

        # добавляем переходы для операции повторения:
        # 1. из нового начала в старое начало

        self.add_transition(trans, start, f.start, None)

        # 2. из нового начала в новый конец (нуль повторений)

        self.add_transition(trans, start, accept, None)

        # 3. из старого конца в старое начало (повторение)

        self.add_transition(trans, f.accept, f.start, None)

        # 4. из старого конца в новый конец

        self.add_transition(trans, f.accept, accept, None)

        return NFAFragment(start, accept, trans)


def regex_to_nfa(regex: str) -> Tuple[int, Dict[int, List[Tuple[Optional[str], int]]], int, int]:
    """
    Преобразует регулярное выражение в недетерминированный конечный автомат

    regex: строка регулярного выражения

    Tuple:
        state_count: количество_состояний
        transitions: таблица_переходов
        start: начальное_состояние
        accept: принимающее_состояние
    """
    parser = RegexToNFAParser(regex)
    frag = parser.parse()
    return parser.state_count, frag.transitions, frag.start, frag.accept