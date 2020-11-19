from open_box.xlsx.writer import build_xlsx, xlsx_for_file

data = [
    ['hnf', 28, '男'],
    ['haner', 27, '男'],
    ['liangxiao', 28, '女'],
]

build_data = [
    {
        'sheet_name': 'Sheet1',
        'header': [
            'name',
            'age',
            'gender',
        ],
        'data': data,
    },
]


def output_excel():
    xlsx_filename = 'user1.xlsx'
    build_xlsx(xlsx_filename, build_data)


def output_excel_fp():
    xlsx_filename = 'user2.xlsx'
    fp = xlsx_for_file(build_data)
    with open(xlsx_filename, 'wb') as f:
        f.write(fp.read())


if __name__ == '__main__':
    output_excel()
    output_excel_fp()
