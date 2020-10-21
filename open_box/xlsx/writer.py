from io import BytesIO

import xlsxwriter


def get_format(workbook, bold=False):
    f = workbook.add_format()  # 样式
    if bold:
        f.set_bold()
    f.set_font_name('Arial')  # 字体名称
    f.set_font_size(11)  # 字体大小
    f.set_align('left')  # 水平置中
    f.set_align('vcenter')  # 垂直置中
    f.set_font_color('black')  # 字体颜色
    return f


def build_sheet(workbook, sheet_name, header, data, header_format, body_format):
    worksheet = workbook.add_worksheet(sheet_name)
    worksheet.write_row('A1', header, header_format)
    for i, item in enumerate(data):
        worksheet.write_row('A{0}'.format(i + 2), item, body_format)


def build_xlsx(xlsx_filename_or_fp, sheet_info_list):
    workbook = xlsxwriter.Workbook(xlsx_filename_or_fp)
    header_format = get_format(workbook, bold=True)
    body_format = get_format(workbook, bold=False)

    for b in sheet_info_list:
        sheet_name = b.get('sheet_name')
        header = b.get('header')
        data = b.get('data')
        build_sheet(workbook, sheet_name, header, data, header_format, body_format)

    workbook.close()


def xlsx_for_file(build_data):
    file = BytesIO()
    build_xlsx(file, build_data)
    file.seek(0)
    return file
