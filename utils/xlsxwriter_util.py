from typing import List, Any

import xlsxwriter
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet


def create_worksheet(write_file_path: str, header_columns: Any) -> tuple[Workbook, Worksheet]:
    """
            创建一个Worksheet.

            参数:
                write_file_path: 写入文件路径.
                columns: 写入数据表头字段
            注意：数据从第一行开始写入
            """
    workbook = xlsxwriter.Workbook(write_file_path, {'constant_memory': True})
    worksheet = workbook.add_worksheet("data")
    # 写 ExcelHeader
    header_format = workbook.add_format({
        'bold': True,  # 加粗
        'font_color': 'black',  # 字体颜色
        'bg_color': '#92D050',  # 背景颜色
    })
    worksheet.write_row('A1', header_columns, header_format)

    return workbook, worksheet
