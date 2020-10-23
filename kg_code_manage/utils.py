import pandas as pd

def excel_to_dict(path):
    """
    读取excel转换成字典形式数据
    :param path: excel路径
    :return: 字典格式数据
    """

    # 创建最终返回的空字典
    df_dict = {}
    # 读取Excel文件
    df = pd.read_excel(path)

    # 替换Excel表格内的空单元格，否则在下一步处理中将会报错
    df.fillna("", inplace=True)

    df_list = []
    for i in df.index.values:
        # loc为按列名索引 iloc 为按位置索引，使用的是 [[行号], [列名]]
        df_line = df.loc[i, ['head_node', 'head_type', 'relationship', 'tail_node', 'tail_type']].to_dict()
        # 将每一行转换成字典后添加到列表
        df_list.append(df_line)
    df_dict['data'] = df_list

    return df_dict
