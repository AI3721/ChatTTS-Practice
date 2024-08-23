import re


class ENNormalizer():
    def __init__(self):
        return

    def fraction_to_words(self, match):
        numerator, denominator = match.groups()
        return numerator + " over " + denominator

    # 数字转为英文读法
    def num_to_english(self, num):
        result = ""
        num_str = str(num)
        units = ["", "ten", "hundred", "thousand"]
        big_units = ["", "thousand", "million", "billion", "trillion"]
        english_digits = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        need_and = False  # Indicates whether 'and' needs to be added
        part = []  # Stores each group of 4 digits
        is_first_part = True  # Indicates if it is the first part for not adding 'and' at the beginning

        # Split the number into 3-digit groups
        while num_str:
            part.append(num_str[-3:])
            num_str = num_str[:-3]

        part.reverse()
        for i, p in enumerate(part):
            p_str = ""
            digit_len = len(p)
            if int(p) == 0 and i < len(part) - 1:
                continue
            hundreds_digit = int(p) // 100 if digit_len == 3 else None
            tens_digit = int(p) % 100 if digit_len >= 2 else int(p[0] if digit_len == 1 else p[1])
            # Process hundreds
            if hundreds_digit is not None and hundreds_digit != 0:
                p_str += english_digits[hundreds_digit] + " hundred"
                if tens_digit != 0:
                    p_str += " and "
            # Process tens and ones
            if 10 < tens_digit < 20:  # Teens exception
                teen_map = {
                    11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
                    16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen"
                }
                p_str += teen_map[tens_digit]
            else:
                tens_map = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
                tens_val = tens_digit // 10
                ones_val = tens_digit % 10
                if tens_val >= 2:
                    p_str += tens_map[tens_val] + (" " + english_digits[ones_val] if ones_val != 0 else "")
                elif tens_digit != 0 and tens_val < 2:  # When tens_digit is in [1, 9]
                    p_str += english_digits[tens_digit]
            
            if p_str and not is_first_part and need_and:
                result += " and "
            result += p_str
            if i < len(part) - 1 and int(p) != 0:
                result += " " + big_units[len(part) - i - 1] + ", "
            is_first_part = False
            if int(p) != 0:
                need_and = True
        
        return result.capitalize()

    def normalize_sentence(self, sentence: str) -> str:
        point=' point '
        sentence = re.sub(r'(\d)\,(\d)', r'\1\2', sentence)
        sentence = re.sub(r'(\d+)\s*\+', r'\1 plus ', sentence)
        sentence = re.sub(r'(\d+)\s*\-', r'\1 minus ', sentence)
        sentence = re.sub(r'(\d+)\s*[\*x]', r'\1 times ', sentence)
        sentence = re.sub(r'((?:\d+\.)?\d+)\s*/\s*(\d+)', self.fraction_to_words, sentence)

        numtext=[' zero ',' one ',' two ',' three ',' four ',' five ',' six ',' seven ',' eight ',' nine ']
        number_list=re.findall(r'((\d+)(?:\.(\d+))?%?)', sentence)
        if len(number_list)>0:
            for m,dc in enumerate(number_list):
                if len(dc[1])>16:
                    continue
                int_text= self.num_to_english(dc[1])
                if len(dc)>2 and dc[2]:
                    int_text+=point+"".join([numtext[int(i)] for i in dc[2]])
                if dc[0][-1]=='%':
                    int_text=f' the pronunciation of  {int_text}'
                sentence=sentence.replace(dc[0],int_text)

        return sentence.replace('1',' one ').replace('2',' two ').replace('3',' three ').replace('4',' four ').replace('5',' five ').replace('6',' six ').replace('7','seven').replace('8',' eight ').replace('9',' nine ').replace('0',' zero ').replace('=',' equals ')
