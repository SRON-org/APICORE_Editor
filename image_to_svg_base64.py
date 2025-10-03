import sys
import os
import base64
from io import BytesIO
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                            QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QMimeData, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QIcon

# 定义后台转换线程类
class ConversionThread(QThread):
    # 定义信号，用于通知主线程转换完成
    conversion_complete = pyqtSignal(str, str)
    conversion_error = pyqtSignal(str)
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        
    def run(self):
        try:
            # 读取图片并转换为base64编码
            with open(self.image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 获取文件扩展名并确定MIME类型
            file_ext = os.path.splitext(self.image_path)[1].lower()
            mime_type = self.get_mime_type(file_ext)
            
            # 构建data URI
            data_uri = f"data:image/svg+xml;base64,{encoded_string}"
            
            # 发送完成信号
            self.conversion_complete.emit(data_uri, mime_type)
        except Exception as e:
            # 发送错误信号
            self.conversion_error.emit(str(e))
            
    def get_mime_type(self, file_ext):
        # 根据文件扩展名返回对应的MIME类型
        mime_types = {
            '.svg': 'image/svg+xml',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.bmp': 'image/bmp',
            '.gif': 'image/gif'
        }
        return mime_types.get(file_ext, 'image/svg+xml')
            


class ImageToSvgBase64Converter(QMainWindow):
    def __init__(self):
        super().__init__()
        
        if os.path.exists(os.path.join(os.path.dirname(__file__), "css/modern.css")):
            css = open(os.path.join(os.path.dirname(__file__), "css/modern.css"), "r", encoding="utf-8").read()
            self.setStyleSheet(css)
            
        self.init_ui()
        self.conversion_thread = None
        
    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("图片转SVG Base64转换器")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Icons", "APICORE_Convert.png")))
        self.resize(600, 400)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建拖拽区域
        self.drag_drop_area = QLabel("将图片拖拽到此处，或点击下方按钮选择图片")
        self.drag_drop_area.setAlignment(Qt.AlignCenter)
        self.drag_drop_area.setStyleSheet("border: 2px dashed #cccccc; border-radius: 5px; padding: 20px;")
        self.drag_drop_area.setMinimumHeight(200)
        
        # 设置拖拽属性
        self.drag_drop_area.setAcceptDrops(True)
        self.drag_drop_area.dragEnterEvent = self.on_drag_enter
        self.drag_drop_area.dropEvent = self.on_drop
        
        main_layout.addWidget(self.drag_drop_area)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 选择图片按钮
        self.select_button = QPushButton("选择图片")
        self.select_button.clicked.connect(self.select_image)
        button_layout.addWidget(self.select_button)
        
        # 转换按钮
        self.convert_button = QPushButton("转换为SVG Base64")
        self.convert_button.clicked.connect(self.convert_to_svg_base64)
        self.convert_button.setEnabled(False)  # 初始禁用
        button_layout.addWidget(self.convert_button)
        
        main_layout.addLayout(button_layout)
        
        # 创建结果文本编辑框
        main_layout.addWidget(QLabel("转换结果 (可复制):"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        main_layout.addWidget(self.result_text)
        
        # 创建复制按钮
        copy_layout = QHBoxLayout()
        self.copy_button = QPushButton("复制结果")
        self.copy_button.clicked.connect(self.copy_result)
        copy_layout.addWidget(self.copy_button)
        main_layout.addLayout(copy_layout)
        
        # 存储当前选中的图片路径
        self.current_image_path = None
        
    def on_drag_enter(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def on_drop(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.process_image(file_path)
    
    def select_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.svg);;所有文件 (*)", 
            options=options
        )
        if file_path:
            self.process_image(file_path)
    
    def process_image(self, file_path):
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", "文件不存在")
            return
        
        # 显示图片预览
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # 调整图片大小以适应显示区域
            scaled_pixmap = pixmap.scaled(
                self.drag_drop_area.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.drag_drop_area.setPixmap(scaled_pixmap)
            self.drag_drop_area.setText("")
            self.current_image_path = file_path
            self.convert_button.setEnabled(True)
        else:
            QMessageBox.warning(self, "错误", "无法加载图片文件")
    
    def convert_to_svg_base64(self):
        if not self.current_image_path:
            QMessageBox.warning(self, "错误", "请先选择图片")
            return
        
        # 检查图片大小
        file_size = os.path.getsize(self.current_image_path)
        recommended_size_mb = 2
        recommended_size_bytes = recommended_size_mb * 1024 * 1024
        max_size_mb = 5
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            reply = QMessageBox.critical(
                self, 
                "图片超大", 
                f"您选择的图片大小约为{file_size/1024/1024:.2f}MB，超过了最大的{max_size_mb}MB。\n" +
                "过大的图片转换可能会造成严重的卡顿，并且生成的Base64编码字符串超级长，几乎无法复制和保存。", 
                QMessageBox.Ok
            )
            
            return
        
        if file_size > recommended_size_bytes:
            reply = QMessageBox.warning(
                self, 
                "图片过大", 
                f"您选择的图片大小约为{file_size/1024/1024:.2f}MB，超过了建议的{recommended_size_mb}MB。\n" +
                "过大的图片转换可能会造成卡顿，并且生成的Base64编码字符串过长，不利于复制和保存。\n\n" +
                "是否继续转换？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # 禁用所有按钮
        self.select_button.setEnabled(False)
        self.convert_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        
        # 更改转换按钮文本
        original_text = self.convert_button.text()
        self.convert_button.setText("图片较大，请耐心等待……")
        
        # 创建并启动后台转换线程
        self.conversion_thread = ConversionThread(self.current_image_path)
        self.conversion_thread.conversion_complete.connect(lambda uri, mime: self.on_conversion_complete(uri, mime, original_text))
        self.conversion_thread.conversion_error.connect(lambda error: self.on_conversion_error(error, original_text))
        self.conversion_thread.finished.connect(self.conversion_thread.deleteLater)
        self.conversion_thread.start()
    
    def on_conversion_complete(self, data_uri, mime_type, original_text):
        # 显示结果
        self.result_text.setText(data_uri)
        
        # 恢复按钮状态和文本
        self.restore_ui_state(original_text)
        
        # 显示成功消息
        QMessageBox.information(self, "成功", "图片已成功转换为SVG Base64格式")
    
    def on_conversion_error(self, error, original_text):
        # 恢复按钮状态和文本
        self.restore_ui_state(original_text)
        
        # 显示错误消息
        QMessageBox.critical(self, "错误", f"转换失败: {error}")
    
    def restore_ui_state(self, original_text):
        # 恢复按钮状态
        self.select_button.setEnabled(True)
        self.convert_button.setEnabled(True)
        self.copy_button.setEnabled(not self.result_text.toPlainText().strip() == "")
        
        # 恢复转换按钮文本
        self.convert_button.setText(original_text)
    
    def copy_result(self):
        if self.result_text.toPlainText():
            clipboard = QApplication.clipboard()
            clipboard.setText(self.result_text.toPlainText())
            QMessageBox.information(self, "成功", "转换结果已复制到剪贴板")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的内容")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageToSvgBase64Converter()
    window.show()
    sys.exit(app.exec_())