def move_matchsticks(equation):
    # 定义火柴棒的表示，将数字与对应的火柴棒数量关联起来
    matchsticks = {'0': 6, '1': 2, '2': 5, '3': 5, '4': 4, '5': 5, '6': 6, '7': 3, '8': 7, '9': 6}

    # 分割等式为左右两部分
    left, right = equation.split('=')

    # 遍历所有可能的移动方式
    for i in range(len(left)):
        # 如果当前字符是数字，则尝试移动一个火柴棒
        if left[i].isdigit():
            for digit, sticks in matchsticks.items():
                # 排除移动后的数字长度超过等式中的数字长度
                if len(left.replace(left[i], digit)) == len(left):
                    new_left = left[:i] + digit + left[i+1:]
                    new_equation = new_left + '==' + right

                    # 检查移动后的等式是否成立
                    if eval(new_equation):
                        return new_equation

    return None


equation = "5+7=7"
result = move_matchsticks(equation)

if result:
    print("火柴棒移动后的等式：", result)
else:
    print("无法通过移动火柴棒使等式成立。")