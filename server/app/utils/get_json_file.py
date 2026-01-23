import os


def get_chat_filenames_without_extension(dir: str):
    """获取根目录下chat文件夹中的文件名（去除后缀）"""
    # 获取项目根目录路径 - 需要多向上一级到达server目录
    current_file_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 得到 app 目录
    project_root = os.path.dirname(current_file_dir)  # 再向上一级得到 server 目录
    chat_dir = os.path.join(project_root, "chat_history", dir)

    # 检查目录是否存在
    if not os.path.exists(chat_dir):
        return []

    # 获取目录下所有文件
    files = os.listdir(chat_dir)
    # 去除文件扩展名，只保留文件名
    filenames_without_ext = []
    for file in files:
        if os.path.isfile(os.path.join(chat_dir, file)):  # 确保是文件而不是子目录
            filename, ext = os.path.splitext(file)
            filenames_without_ext.append(filename)

    return filenames_without_ext
