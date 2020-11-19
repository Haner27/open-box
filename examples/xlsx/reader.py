from open_box.xlsx.reader import gen_excel_row


def print_every_row(excel_path):
    for row in gen_excel_row(excel_path):
        print(row)


if __name__ == '__main__':
    excel_path = 'use_data_group.xlsx'
    print_every_row(excel_path)