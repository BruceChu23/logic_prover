import pandas as pd
import re

class Logic_prover:

    # 1.生成真值表
    def get_sort(self, e: list):
        n = len(e)
        num_eles = 2 ** n
        lst = [bin(i).lstrip('0b') for i in range(num_eles)]
        lst = ['0' * (n - len(i)) + i for i in lst]
        df = pd.DataFrame()
        for i in range(n):
            df[e[i]] = [int(t[i]) for t in lst]
        return df

    # 2.逻辑运算定义
    def not_(self, a: int):
        return 1 - a
    def and_(self, a: int, b: int):
        return a & b
    def or_(self, a: int, b: int):
        return a | b
    def ipl_(self, a: int, b: int):
        return int(a <= b)
    def eql_(self, a: int, b: int):
        return int(a == b)

    # 3.获取表达式中的变量
    def get_variables(self, expression: str):
        return list(sorted(set(re.findall(r'[a-zA-Z]', expression))))

    # 4.计算
    def evaluate_expression(self, expression: str, row: dict):
        # i.先处理最内层的括号
        while '(' in expression:
            expression = re.sub(r'\(([^()]+)\)', 
                                lambda m: str(self.evaluate_expression(m.group(1), row)),
                                expression)
        # ii.替换变量为当前行的值
        for var in self.get_variables(expression):
            expression = expression.replace(var, str(row[var]))
        # iii.按操作优先级计算，由高到低为：~ ^ & -> <->
        if '<->' in expression:
            a, b = expression.split('<->', maxsplit=1)
            return self.eql_(self.evaluate_expression(a.strip(), row), self.evaluate_expression(b.strip(), row))
        if '->' in expression:
            a, b = expression.split('->', maxsplit=1)
            return self.ipl_(self.evaluate_expression(a.strip(), row), self.evaluate_expression(b.strip(), row))
        if '&' in expression:
            a, b = expression.split('&', maxsplit=1)
            return self.or_(self.evaluate_expression(a.strip(), row), self.evaluate_expression(b.strip(), row))
        if '^' in expression:
            a, b = expression.split('^', maxsplit=1)
            return self.and_(self.evaluate_expression(a.strip(), row), self.evaluate_expression(b.strip(), row))
        if '~' in expression:
            return self.not_(self.evaluate_expression(expression[1:].strip(), row))
        # 如果是单个值，直接返回
        return int(expression)

    # 5.计算所有行的结果
    # 可选参数，可以输出成真式
    def evaluate(self, expression: str, True_=False):
        variables = self.get_variables(expression)
        df = self.get_sort(variables)
        df[expression] = df.apply(lambda row: self.evaluate_expression(expression, row), axis=1)
        return df[df[expression] == 1] if True_ else df

# 使用示例
if __name__ == '__main__':
    logic_prover = Logic_prover()
    expression = "(p->q)^(~r->p)"
    result_df = logic_prover.evaluate(expression)
    print(result_df)
