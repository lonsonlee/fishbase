# coding=utf-8
"""

``fish_data`` 包含的是一些与数据信息相关的函数，比如银行卡、身份证信息的生成和校验。

在我们进行一些开发测试、功能测试、自动化测试、压力测试等场景下，都需要模拟身份证、银行卡等信息。
fish_data 中的函数就是用在这样的场景。注意，这些函数不会生成真实的身份证和银行卡号。


"""

# 2018.12.9 v1.1.3 created

import re
import sqlite3
import os


# 2018.12.18
def sqlite_query(db, sql, params):

    dir_path = os.path.dirname(os.path.abspath(__file__))

    conn = sqlite3.connect(os.path.join(dir_path, 'db', db))

    cursor = conn.cursor()

    cursor.execute(sql, params)

    values = cursor.fetchall()

    cursor.close()
    conn.close()

    return values


# 计算身份证号码的校验位
# ---
# 2018.12.12 create by David.Yi, add in v1.1.4 github issue #143
def get_idcard_checkcode(id_number_str):
    """
    计算身份证号码的校验位；

    :param:
        * id_number_str: (string) 身份证号的前17位，比如 3201241987010100
    :returns:
        * 返回类型 (tuple)
        * flag: (bool) 如果身份证号格式正确，返回 True；格式错误，返回 False
        * checkcode: 计算身份证前17位的校验码

    举例如下::

        from fishbase.fish_data import *

        print('--- fish_data get_idcard_checkcode demo ---')

        # id number
        id1 = '32012419870101001'
        print(id1, get_idcard_checkcode(id1)[1])

        # id number
        id2 = '13052219840731647'
        print(id2, get_idcard_checkcode(id2)[1])

        print('---')


    输出结果::
        --- fish_data get_idcard_checkcode demo ---
        32012419870101001 5
        13052219840731647 1
        ---

    """

    # 判断长度，如果不是 17 位，直接返回失败
    if len(id_number_str) != 17:
        return False, -1

    id_regex = '[1-9][0-9]{14}([0-9]{2}[0-9X])?'

    if not re.match(id_regex, id_number_str):
        return False, -1

    items = [int(item) for item in id_number_str]

    # 加权因子表
    factors = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)

    # 计算17位数字各位数字与对应的加权因子的乘积
    copulas = sum([a * b for a, b in zip(factors, items)])

    # 校验码表
    check_codes = ('1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2')

    checkcode = check_codes[copulas % 11].upper()

    return True, checkcode


# 检查身份证号码是否能通过校验规则
# ---
# 2018.12.9 create by David Yi, add in v1.1.3, github issue #137
# 2018.12.13 edit, v1.1.4 github issue #145
# original source: https://zhuanlan.zhihu.com/p/24449773
def check_id_number(id_number):
    """
    检查身份证号码是否符合校验规则；

    :param:
        * id_number: (string) 身份证号，比如 32012419870101001
    :returns:
        * 返回类型 (tuple)，当前有一个值，第一个为 flag，以后第二个值会返回具体校验不通过的详细错误
        * flag: (bool) 如果身份证号码校验通过，返回 True；如果身份证校验不通过，返回 False

    举例如下::

        from fishbase.fish_data import *

        print('--- fish_data is_valid_id_number demo ---')

        # id number false
        id1 = '320124198701010012'
        print(id1, is_valid_id_number(id1)[0])

        # id number true
        id2 = '130522198407316471'
        print(id2, is_valid_id_number(id2)[0])

        print('---')

    输出结果::

        --- fish_data is_valid_id_number demo ---
        320124198701010012 False
        130522198407316471 True
        ---

    """
    if isinstance(id_number, int):
        id_number = str(id_number)

    # 调用函数计算身份证前面17位的 checkcode
    result = get_idcard_checkcode(id_number[0:17])

    # 返回第一个 flag 是错误的话，表示身份证格式错误，直接透传返回，第二个为获得的校验码
    flag = result[0]
    checkcode = result[1]

    if not flag:
        return flag,

    # 判断校验码是否正确
    return checkcode == id_number[-1].upper(),


# 输入包含省份、城市、地区信息的内容，返回地区编号，也就是身份证编码中的前6位内容
# ---
# 2018.12.14 12.16 create by David Yi, add in v1.1.4, github issue #139
def get_zonecode_by_area(area_str, match_type='EXACT', result_type='LIST'):
    """
    输入包含省份、城市、地区信息的内容，返回地区编号；

    :param:
        * area_str: (string) 要查询的区域，省份、城市、地区信息，比如 北京市
        * match_type: (string) 查询匹配模式，默认值 'EXACT'，表示精确匹配，可选 'FUZZY'，表示模糊查询
        * result_type: (string) 返回结果数量类型，默认值 'LIST'，表示返回列表，可选 'SINGLE_STR'，返回结果的第一个地区编号字符串
    :returns:
        * 返回类型 根据 resule_type 决定返回类型是列表或者单一字符串，列表中包含元组
        比如：[('110000', '北京市')]，元组中的第一个元素是地区码，第二个元素是对应的区域内容
        结果最多返回 20 个。

    举例如下::

        from fishbase.fish_data import *

        print('--- fish_data get_zonecode_by_area demo ---')

        result = get_zonecode_by_area(area_str='北京市')
        print(result)

        # 模糊查询
        result = get_zonecode_by_area(area_str='西安市', match_type='FUZZY')
        print(result)

        result0 = []
        for i in result:
            result0.append(i[0])

        print('---西安市---')
        print(len(result0))
        print(result0)

        # 模糊查询, 结果返回设定 single_str
        result = get_zonecode_by_area(area_str='西安市', match_type='FUZZY', result_type='SINGLE_STR')
        print(result)

        # 模糊查询, 结果返回设定 single_str，西安市 和 西安 的差别
        result = get_zonecode_by_area(area_str='西安', match_type='FUZZY', result_type='SINGLE_STR')
        print(result)

        print('---')

    输出结果::

        --- fish_data get_zonecode_by_area demo ---
        [('110000', '北京市')]
        130522198407316471 True

        ---西安市---
        11
        ['610100', '610101', '610102', '610103', '610104', '610111', '610112', '610113', '610114', '610115', '610116']

        610100
        220403
        ---

    """
    values = []

    if match_type == 'EXACT':
        values = sqlite_query('fish_data.sqlite',
                              'select zone, note from cn_idcard where note = :area', {"area": area_str})
    if match_type == 'FUZZY':
        values = sqlite_query('fish_data.sqlite',
                              'select zone, note from cn_idcard where note like :area', {"area": '%' + area_str + '%'})

    # result_type 结果数量判断处理

    if result_type == 'LIST':
        # 如果返回记录多，大于 20 项，只返回前面 20 个结果
        if len(values) > 20:
            values = values[0:20]

        return values

    if result_type == 'SINGLE_STR':
        if len(values) == 0:
            return ''
        if len(values) > 0:
            value_str = values[0][0]
            return value_str


# 输入银行、借记贷记卡种类，返回有效的卡 bin
# ---
# 2018.12.17 create by David Yi, add in v1.1.4, github issue #149
def get_cardbin_by_bank(bank, card_type):
    """
    输入银行、借记贷记卡种类，返回有效的卡 bin；

    :param:
        * bank: (string) 要查询的银行代号，比如 ICBC, CMB
        * card_type: (string) 银行卡类型，比如 CC 表示信用卡
    :returns:
        * 返回 cardbin, bank, 银行卡类型type, 银行卡长度 length，
        一条记录为一个 tuple (a, b, c, d)，然后组成 list 返回

    举例如下::

        from fishbase.fish_data import *

        print('--- fish_data get_cardbin_by_bank demo ---')

        result = get_cardbin_by_bank('CMB', 'DC')
        print(result)

        print('---')

    输出结果::

        --- fish_data get_cardbin_by_bank demo ---

        [('410062', 'CMB', 'DC', 16), ('468203', 'CMB', 'DC', 16), ...
        ---

    """
    values = sqlite_query('fish_data.sqlite',
                          'select bin,bank,card_type,length from cn_cardbin where bank=:bank and card_type=:card_type',
                          {"bank": bank, "card_type": card_type})

    return values


# 计算银行卡校验位
# ---
# 2018.12.18 create by David Yi, v1.1.4, github issue #154
def get_bankcard_checkcode(card_number_str):
    """
    计算银行卡校验位；

    :param:
        * card_number_str: (string) 要查询的银行卡号
    :returns:
        checkcode: (string) 银行卡的校验位

    举例如下::

        from fishbase.fish_data import *

        print('--- fish_data get_bankcard_checkcode demo ---')

        # 不能放真的卡信息，有风险
        print(get_bankcard_checkcode('439188000699010'))

        print('---')

    输出结果::

        --- fish_data get_bankcard_checkcode demo ---
        9
        ---

    """
    total = 0
    even = True

    for item in card_number_str[-1::-1]:
        item = int(item)
        if even:
            item <<= 1
        if item > 9:
            item -= 9
        total += item
        even = not even

    checkcode = (10 - (total % 10)) % 10

    return str(checkcode)


# 检查银行卡校验位是否正确
# ---
# 2018.12.18 create by David Yi, v1.1.4, github issue #155
def check_bankcard(card_number_str):
    """
    检查银行卡校验位是否正确；

    :param:
        * card_number_str: (string) 要查询的银行卡号
    :returns:
        返回结果：(bool) True or False

    举例如下::

        from fishbase.fish_data import *

        print('--- fish_data check_bank_card demo ---')

        # 不能放真的卡信息，有风险
        print(check_bankcard('4391880006990100'))

        print('---')

    输出结果::

        --- fish_data check_bank_card demo ---
        False
        ---

    """

    if isinstance(card_number_str, int):
        card_number_str = str(card_number_str)

    checkcode = card_number_str[-1]

    result = get_bankcard_checkcode(card_number_str[0:-1])

    return checkcode == result


# 输入银行名称，返回银行代码
# ---
# 2018.12.18 create by David Yi, add in v1.1.4, github issue #159
def get_bank_by_name(bankname):
    """
    银行名称，返回银行代码；

    :param:
        * bankname: (string) 要查询的银行 名称，比如 招商银行
    :returns:
        * 返回 银行代号bank , 银行名称 bankname，
        一条记录为一个 tuple (a, b)，然后组成 list 返回

    举例如下::

        from fishbase.fish_data import *

        print('--- fish_data get_bank_by_name demo ---')

        print(get_bank_by_name('招商银行'))

        print('---')

    输出结果::

        --- fish_data get_bank_by_name demo ---
        [('CMB', '招商银行')]
        ---

    """
    values = sqlite_query('fish_data.sqlite',
                          'select bank,bankname from cn_bankname where bankname=:bankname',
                          {"bankname": bankname})

    return values