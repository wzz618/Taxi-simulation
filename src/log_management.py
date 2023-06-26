import os
from time import strftime


class log_management:
    def __init__(self, current_dir=os.path.dirname(os.path.abspath(__file__)), doc_name=strftime("%Y-%m-%d %H'%M'%S")):
        """
        初始化
        :param current_dir: string
            日志信息的目录，默认目录是当前py文件的目录地址
        :param doc_name: string
            日志信息的文件名，默认文件名称是年月日+时间
        """
        self._document_path = self.get_document_path(current_dir, doc_name)  # 当前存储文件的路径
        self.is_print = True

    def get_document_path(self, current_dir, doc_name):
        """
        生成日志文件的路径
        :param doc_name: string
            日志文件的名字
        :param current_dir: string
            系统文件的目录
        :return: string
            日志文件的绝对位置
        """
        if current_dir.split('\\')[-1] in ['Log', 'log']:
            doc_path = '\\{}.txt'.format(doc_name)
        else:
            doc_path = '\\Log\\{}.txt'.format(doc_name)
        file_path = current_dir + doc_path
        return file_path

    def write_data(self, *args):
        """
        把事件写入到日志文件中
        :param args: 需要写入的信息
        :return: None
        """
        if not os.path.exists(os.path.dirname(self._document_path)):  # 如果文件目录不在，则创建目录
            os.mkdir(os.path.dirname(self._document_path))
        for arg in args:  # 依次写入信息
            with open(self._document_path, 'a+') as f:
                data = strftime("%Y-%m-%d %H:%M:%S") + '\t' + arg + '\n'
                f.write(data)
                if self.is_print:
                    print(data, end='')
        return None

    def write_tip(self, tip, scale=1):
        """
        在文件中增加新的标题
        :return:
        """
        with open(self._document_path, 'a+') as f:
            if scale == 1:
                tip = f'{40 * "*"} {tip} {40 * "*"}\n\t时间：{strftime("%Y-%m-%d %H:%M:%S")}\n'
            elif scale == 2:
                tip = f'{30 * "-"} {tip} || {strftime("%Y-%m-%d %H:%M:%S")} {30 * "-"}\n'
            f.write(tip)
            if self.is_print:
                print(tip, end='')
        return None


if __name__ == '__main__':
    obj = log_management()
    obj.write_data('测试信息1', '测试信息2')
