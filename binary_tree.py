from nltk.tokenize import word_tokenize
from string import punctuation
import json


def read_file(filename):  # читает файлы формата .txt и .json, для остальных возырвщвет None
    with open(filename, encoding='utf-8') as f:
        if filename.endswith('.txt'):
            return f.read()
        if filename.endswith('.json'):
            return json.load(f)
    return None


def write_file(data, filename):  # создает файлы формата .txt и .json, для остальных не делает ничего
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(data)


def text_tokens(text):  # возвращает список токенов из текста (без пунктуации)
    punctuation_lst = [_ for _ in punctuation] + ['—', '«', '»', '...']
    tokens = [token.lower() for token in word_tokenize(text) if token not in punctuation_lst]
    return tokens


def small_rotation(node, mode):  # node - а-вершина, выполняет малое левое/правое вращение
    if mode == "left":
        node_a = [node[0], node[1], node[2][1]]
        node_b = [node[2][0], node_a, node[2][2]]
        return node_b
    elif mode == "right":
        node_a = [node[0], node[1][2], node[2]]
        node_b = [node[1][0], node[1][1], node_a]
        return node_b


def big_rotation(node, mode):  # node - a-вершина, выполняет большое правое/левое вращение
    if mode == "left":
        node_a = [node[0], node[1], node[2][1][1]]
        node_b = [node[2][0], node[2][1][2], node[2][2]]
        node_c = [node[2][1][0], node_a, node_b]
        return node_c
    elif mode == "right":
        node_b = [node[1][0], node[1][1], node[1][2][1]]
        node_a = [node[0], node[1][2][2], node[2]]
        node_c = [node[1][2][0], node_b, node_a]
        return node_c


def get_depth(root, depth=0):  # возвращает глубину поддерева, для листа - 1, для None - 0
    if root:
        depth = max(get_depth(root[1], depth), get_depth(root[2], depth)) + 1   # возвращает максимальную глубину
    return depth                                                                           # поддерева


def make_rotation(root):  # проверяет, выполняется ли условие для вращение у конкретной вершины
    if (get_depth(root[2]) - get_depth(root[1]) == 2) and (get_depth(root[2][1]) <= get_depth(root[2][2])):
        root = small_rotation(root, "left")
    elif (get_depth(root[1]) - get_depth(root[2]) == 2) and (get_depth(root[1][2]) <= get_depth(root[1][1])):
        root = small_rotation(root, "right")
    elif (get_depth(root[2]) - get_depth(root[1]) == 2) and (get_depth(root[2][1]) > get_depth(root[2][2])):
        root = big_rotation(root, "left")
    elif (get_depth(root[1]) - get_depth(root[2]) == 2) and (get_depth(root[1][2]) > get_depth(root[1][1])):
        root = big_rotation(root, "right")
    return root


def check_tree(root):  # проверяет дерево
    if root:
        if (not root[1]) and (not root[2]):  # если лист, то проверять нечего, выходим
            return root
        elif get_depth(root) > 3:  # если глубина больше трех, то проверяем все поддеревья
            root[1] = check_tree(root[1])
            root[2] = check_tree(root[2])
        root = make_rotation(root)  # каждый раз выходя из рекурсии, проверяем, нужно ли вращение
    return root


def compare_n_grams(lhs, rhs):  # сравнение N-грам, проверяет больше ли lhs, чем rhs
    if len(lhs) < len(rhs):  # итерацию выполняем по тому списку, который короче
        for key, value in enumerate(lhs):
            if value != rhs[key]:
                return value > rhs[key]
        return False  # если мы долшли до конца короткого списка, а отличий не найдено, то короткий меньше
    else:
        for key, value in enumerate(rhs):
            if value != lhs[key]:
                return value < lhs[key]
        return True


def add_to_node(node, value):
    if node[0][0] == value:  # такое значение уже есть в в дереве
        node[0][1] += 1  # увеличиваем частоту встречаемости на один
        return
    if not compare_n_grams(value, node[0][0]):      # значение меньше вершины
        if not node[1]:  # левого потомка нет
            node[1] = [[value, 1], None, None]
        else:  # левый потомок есть, рекурсия
            add_to_node(node[1], value)
    else:
        if not node[2]:
            node[2] = [[value, 1], None, None]
        else:
            add_to_node(node[2], value)


def add_to_tree(root, value):
    if (not root) or (root == []):  # если нет корня, создаем
        return [[value, 1], None, None]
    add_to_node(root, value)  # добавляем вершину в дерево
    return root


def work_with_n_grams(text):  # основная функция для получения n-грам и добавления их в дерево, возвращает дерево
    tree = []
    for key, value in enumerate(text):
        for i in range(2, len(text) - key + 1):
            n_gram = text[key:key + i]
            tree = add_to_tree(tree, n_gram)
            if (i + key % 2 == 0) and (key % 2 == 0) or (i + key % 2 == 1) and (key % 2 == 1):
                tree = check_tree(tree)  # проверяем дерево на каждом втором шаге (на стыке может быть подряд)
    tree = check_tree(tree)  # проверяем дерево на случай, если последнее добавление не проверяли
    return tree


def print_element(element, filename=''):  # для удобства изменения вывода
    s = ' '.join(element[0]) + '\t' + str(element[1]) + '\n'
    if filename != '':
        write_file(s, filename)
    else:
        print(s)


def print_staff_element(element, filename=''):  # для удобства изменения вывода
    s = ' '.join(element) + '\n'
    s = s.upper()
    if filename != '':
        write_file(s, filename)
    else:
        print(s)


def write_tree(root, filename='', previous_key=''):
    if root:
        if root[1]:
            previous_key = write_tree(root[1], filename, previous_key)  # сначала пишем всех потомков меньше данного
        if len(root[0][0]) == 2:  # добавляем саму вершину
            key_value = root[0][0] + ['']
        else:
            key_value = root[0][0][0:3]
        if previous_key == key_value:
            print_element(root[0], filename)  # значения уже упорядлчены, так что просто добавляем
        else:
            print_staff_element(['-'*10], filename)
            print_staff_element(key_value, filename)
            print_staff_element(['-'*10], filename)
            print_element(root[0], filename)
        if root[2]:
            key_value = write_tree(root[2], filename, key_value)  # пишем всех потомков больше данного
        return key_value


def main():
    filename = input('Пожалуйста, введите имя файла с текстом: \n')
    text = read_file(filename)
    text = text_tokens(text)
    tree = work_with_n_grams(text)
    filename = input('Пожалуйста, введите имя файла для записи результатов: \n')
    write_tree(tree, filename)


if __name__ == '__main__':
    main()
