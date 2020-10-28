'''
levels dict for bookmark
'''

import re

level_dict = {
    'level0': {
        'I': r'[IVX]+',
        '第1章': r'第\d+章',
        '第I章': r'第[IVX]+章',
        '第一章': r'第[一二三四五六七八九十百千]+章',
    },

    'level1': {
        '1.1': r'\d+\.\d+',
        '第1节': r'第\d+节',
        '第一节': r'第[一二三四五六七八九十百千]+节',
    },
    'level2': {
        '1.1.1': r'\d+\.\d+\.\d+',
    }
}

def get_level_re(level, level_example):
    level_re = ''
    
    if level_example:
        try:
            level_re = level_dict[level][level_example]
        except:
            print("[-]: Get level re failed.")
            level_re = ''

    return level_re

def main():
    print(get_level_re('level0', "第1章"))
    print(re.match(get_level_re('level0', "第1章"), "第2章"))

if __name__ == '__main__':
    main()