import re
from .number import *
from .phonecode import *
from .quantifier import *
from .chronology import *


class ZHNormalizer():
    def __init__(self):
        return

    def post_replace(self, sentence: str) -> str:
        sentence = sentence.replace('～', '至')
        sentence = sentence.replace('~', '至')
        sentence = sentence.replace('①', '一')
        sentence = sentence.replace('②', '二')
        sentence = sentence.replace('③', '三')
        sentence = sentence.replace('④', '四')
        sentence = sentence.replace('⑤', '五')
        sentence = sentence.replace('⑥', '六')
        sentence = sentence.replace('⑦', '七')
        sentence = sentence.replace('⑧', '八')
        sentence = sentence.replace('⑨', '九')
        sentence = sentence.replace('⑩', '十')
        sentence = sentence.replace('α', '阿尔法')
        sentence = sentence.replace('β', '贝塔')
        sentence = sentence.replace('γ', '伽玛').replace('Γ', '伽玛')
        sentence = sentence.replace('δ', '德尔塔').replace('Δ', '德尔塔')
        sentence = sentence.replace('ε', '艾普西龙')
        sentence = sentence.replace('ζ', '捷塔')
        sentence = sentence.replace('η', '依塔')
        sentence = sentence.replace('θ', '西塔').replace('Θ', '西塔')
        sentence = sentence.replace('ι', '艾欧塔')
        sentence = sentence.replace('κ', '喀帕')
        sentence = sentence.replace('λ', '拉姆达').replace('Λ', '拉姆达')
        sentence = sentence.replace('μ', '缪')
        sentence = sentence.replace('ν', '拗')
        sentence = sentence.replace('ξ', '克西').replace('Ξ', '克西')
        sentence = sentence.replace('ο', '欧米克伦')
        sentence = sentence.replace('π', '派').replace('Π', '派')
        sentence = sentence.replace('ρ', '肉')
        sentence = sentence.replace('σ', '西格玛').replace('ς', '西格玛').replace('Σ', '西格玛')
        sentence = sentence.replace('τ', '套')
        sentence = sentence.replace('υ', '宇普西龙')
        sentence = sentence.replace('φ', '服艾').replace('Φ', '服艾')
        sentence = sentence.replace('χ', '器')
        sentence = sentence.replace('ψ', '普赛').replace('Ψ', '普赛')
        sentence = sentence.replace('ω', '欧米伽').replace('Ω', '欧米伽')
        sentence = sentence.replace('+', '加')
        sentence = sentence.replace('÷', '除以')
        sentence = sentence.replace('=', '等于')
        return sentence

    # 数字转为中文读法
    def num_to_chinese(self, num):
        result = ""
        num_str = str(num)
        units = ["", "十", "百", "千"]
        big_units = ["", "万", "亿", "兆"]
        chinese_digits = "零一二三四五六七八九"
        zero_flag = False  # 标记是否需要加'零'
        part = []  # 存储每4位的数字

        # 将数字按每4位分组
        while num_str:
            part.append(num_str[-4:])
            num_str = num_str[:-4]

        for i in range(len(part)):
            part_str = ""
            part_zero_flag = False
            for j in range(len(part[i])):
                digit = int(part[i][j])
                if digit == 0:
                    part_zero_flag = True
                else:
                    if part_zero_flag or (zero_flag and i > 0 and not result.startswith(chinese_digits[0])):
                        part_str += chinese_digits[0]
                        zero_flag = False
                        part_zero_flag = False
                    part_str += chinese_digits[digit] + units[len(part[i]) - j - 1]
            if part_str.endswith("零"):
                part_str = part_str[:-1]  # 去除尾部的'零'
            if part_str:
                zero_flag = True
            if i > 0 and not set(part[i]) <= {'0'}:  # 如果当前部分不全是0，则加上相应的大单位
                result = part_str + big_units[i] + result
            else:
                result = part_str + result

        # 处理输入为0的情况或者去掉开头的零
        result = result.lstrip(chinese_digits[0])
        if not result:
            return chinese_digits[0]
        return result

    def normalize_sentence(self, sentence: str) -> str:
        sentence = re.sub(r'(0\d+)\-(\d{3,})\-(\d{3,})', r'\1杠\2杠\3', sentence,re.I)
        sentence = re.sub(r'(0\d+)\-(\d{3,})', r'\1杠\2', sentence,re.I)
        sentence = re.sub(r'(\d+)\s*[\*xX]\s*(\d+)', r'\1 乘 \2', sentence,re.I)
        # sentence = re.sub(r'(\d+)\s*\-', r'\1 减', sentence)

        numtext=['零','一','二','三','四','五','六','七','八','九']
        number_list=re.findall(r'((\d+)(?:\.(\d+))?%?)', sentence)
        if len(number_list)>0:
            for m,dc in enumerate(number_list):
                n_len=len(dc[1])
                #手机号/座机号 超大数 亿内的数 0开头的数，不做处理
                if n_len>16 or n_len<9 or (n_len==11 and str(dc[1])[0]=='1') or str(dc[1])[0]=='0':
                    continue
                int_text=self.num_to_chinese(dc[1])
                if len(dc)>2 and dc[2]:
                    int_text+="点"+"".join([numtext[int(i)] for i in dc[2]])
                if dc[0][-1]=='%':
                    int_text=f'百分之{int_text}'
                sentence=sentence.replace(dc[0],int_text)

        sentence = RE_DATE.sub(replace_date, sentence)
        sentence = RE_DATE2.sub(replace_date2, sentence)
        sentence = RE_TIME.sub(replace_time, sentence)
        sentence = RE_TIME_RANGE.sub(replace_time, sentence)

        sentence = replace_measure(sentence)
        sentence = RE_FRAC.sub(replace_frac, sentence)
        sentence = RE_PERCENTAGE.sub(replace_percentage, sentence)
        sentence = RE_TEMPERATURE.sub(replace_temperature, sentence)

        sentence = RE_RANGE.sub(replace_range, sentence)
        sentence = RE_TELEPHONE.sub(replace_phone, sentence)
        sentence = RE_MOBILE_PHONE.sub(replace_mobile, sentence)
        sentence = RE_NATIONAL_UNIFORM_NUMBER.sub(replace_phone, sentence)

        sentence = RE_DECIMAL_NUM.sub(replace_number, sentence)
        sentence = RE_INTEGER.sub(replace_negative_num, sentence)
        sentence = RE_POSITIVE_QUANTIFIERS.sub(replace_positive_quantifier,sentence)
        sentence = RE_DEFAULT_NUM.sub(replace_default_num, sentence)
        sentence = RE_NUMBER.sub(replace_number, sentence)

        return self.post_replace(sentence)
