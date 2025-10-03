from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtCore import Qt, QRegExp

# 创建JSON语法高亮器
class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(JsonHighlighter, self).__init__(parent)
        
        # 创建关键字格式
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(Qt.darkBlue)
        keyword_format.setFontWeight(75)
        
        # 创建字符串格式
        string_format = QTextCharFormat()
        string_format.setForeground(Qt.darkGreen)
        
        # 创建数字格式
        number_format = QTextCharFormat()
        number_format.setForeground(Qt.red)
        
        # 创建布尔值格式
        boolean_format = QTextCharFormat()
        boolean_format.setForeground(Qt.darkMagenta)
        boolean_format.setFontWeight(75)
        
        # 编译正则表达式
        self.highlighting_rules = [
            (QRegExp(r'"[^"]*"'), string_format),  # 字符串
            (QRegExp(r'\b\d+\b'), number_format),  # 数字
            (QRegExp(r'\btrue\b|\bfalse\b'), boolean_format),  # 布尔值
        ]
    
    def highlightBlock(self, text):
        # 应用所有高亮规则
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)