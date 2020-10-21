import xlrd


def gen_excel_row(excel_path, sheet_names=None):
    if sheet_names is None:
        sheet_names = []

    for sheet in xlrd.open_workbook(excel_path).sheets():
        if sheet_names:
            if sheet.name not in sheet_names:
                continue

        for row in range(sheet.nrows):
            yield sheet.row_values(row)