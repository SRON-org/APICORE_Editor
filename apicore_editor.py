import sys
import json
import os
import sys
import subprocess, webbrowser
import logging

# 配置日志系统
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("apicore_editor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("APICORE_Editor")

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox, QSpinBox, 
    QPushButton, QFileDialog, QTabWidget, QGroupBox, QListWidget, 
    QListWidgetItem, QMessageBox, QScrollArea, QSplitter
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont

class QMessageBoxEx(QMessageBox):
    def information(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Icons", "APICORE_Pass.png")))
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

class APICoreEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置全局样式表
        if os.path.exists(os.path.join(os.path.dirname(__file__), "css/modern.css")):
            css = open(os.path.join(os.path.dirname(__file__), "css/modern.css"), "r", encoding="utf-8").read()
            self.setStyleSheet(css)
            logger.info("成功加载样式表 css/modern.css")
        else:
            logger.warning("未找到样式表文件 css/modern.css 将使用默认样式。")
            QMessageBox.warning(self, "警告", "未找到样式表文件 css/modern.css 将使用默认样式。", QMessageBox.Ok)
        
        self.current_file = None
        self.init_ui()
        
    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("APICORE 配置文件编辑器")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "Icons", "APICORE_Editor.png")))
        self.resize(1000, 700)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建标签页
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 创建基本配置标签页
        self.create_basic_config_tab()
        
        # 创建参数配置标签页
        self.create_parameters_tab()
        
        # 创建响应配置标签页
        self.create_response_tab()
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
        
    def create_menu_bar(self):
        # 创建菜单栏
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        # 新建文件动作
        new_action = file_menu.addAction("新建")
        new_action.triggered.connect(self.new_file)
        
        # 打开文件动作
        open_action = file_menu.addAction("打开")
        open_action.triggered.connect(self.open_file)
        
        # 保存文件动作
        save_action = file_menu.addAction("保存")
        save_action.triggered.connect(self.save_file)
        
        # 另存为动作
        save_as_action = file_menu.addAction("另存为")
        save_as_action.triggered.connect(self.save_file_as)
        
        file_menu.addSeparator()
        
        # 验证配置动作
        validate_action = file_menu.addAction("验证配置")
        validate_action.triggered.connect(lambda _: self.validate_config(True))
        
        #文档菜单
        wiki_menu = menu_bar.addMenu("文档")
        create_action = wiki_menu.addAction("创建配置文件")
        create_action.triggered.connect(lambda: webbrowser.open("https://github.com/SRON-org/APICORE/wiki/Create-a-New-APICORE-Configuration-File"))
        
        complete_action = wiki_menu.addAction("复杂路径配置")
        complete_action.triggered.connect(lambda: webbrowser.open("https://github.com/SRON-org/APICORE/wiki/Complex-Configuration"))
        
        wiki_menu.addSeparator()
        
        repo_action = wiki_menu.addAction("APICORE 仓库")
        repo_action.triggered.connect(lambda: webbrowser.open("https://github.com/SRON-org/APICORE"))
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        repo_action_2 = help_menu.addAction("前往仓库")
        repo_action_2.triggered.connect(lambda: webbrowser.open("https://github.com/SRON-org/APICORE_Editor"))
        
        # 关于动作
        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(self.show_about)
        
    def create_basic_config_tab(self):
        # 创建基本配置标签页
        basic_config_tab = QWidget()
        basic_layout = QVBoxLayout(basic_config_tab)
        
        # 设置内边距
        basic_layout.setContentsMargins(20, 20, 20, 20)
        basic_layout.setSpacing(15)
        
        # 创建分组框
        basic_group = QGroupBox("基本信息")
        basic_group_layout = QVBoxLayout(basic_group)
        basic_group_layout.setSpacing(12)
        
        # friendly_name
        friendly_name_layout = QHBoxLayout()
        friendly_name_label = QLabel("API接口名称 (*)")
        friendly_name_label.setMinimumWidth(120)
        self.friendly_name_edit = QLineEdit()
        self.friendly_name_edit.setPlaceholderText("请输入API接口的名称")
        friendly_name_layout.addWidget(friendly_name_label)
        friendly_name_layout.addWidget(self.friendly_name_edit)
        basic_group_layout.addLayout(friendly_name_layout)
        
        # intro
        intro_layout = QHBoxLayout()
        intro_label = QLabel("API接口简介")
        intro_label.setMinimumWidth(120)
        self.intro_edit = QTextEdit()
        self.intro_edit.setMaximumHeight(80)
        self.intro_edit.setPlaceholderText("请输入API接口的简要描述，不超过15个字符")
        intro_layout.addWidget(intro_label)
        intro_layout.addWidget(self.intro_edit)
        basic_group_layout.addLayout(intro_layout)
        
        # icon
        icon_layout = QHBoxLayout()
        icon_label = QLabel("API接口图标URL")
        icon_label.setMinimumWidth(120)
        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText("请输入API接口图标URL，或使用右侧工具转换后粘贴")
        self.icon_converter_btn = QPushButton("转换图片")
        self.icon_converter_btn.setFixedWidth(100)
        self.icon_converter_btn.clicked.connect(self.open_image_converter)
        icon_layout.addWidget(icon_label)
        icon_layout.addWidget(self.icon_edit)
        icon_layout.addWidget(self.icon_converter_btn)
        basic_group_layout.addLayout(icon_layout)
        
        # link
        link_layout = QHBoxLayout()
        link_label = QLabel("API接口链接 (*)")
        link_label.setMinimumWidth(120)
        self.link_edit = QLineEdit()
        self.link_edit.setPlaceholderText("请输入API接口的URL链接")
        link_layout.addWidget(link_label)
        link_layout.addWidget(self.link_edit)
        basic_group_layout.addLayout(link_layout)
        
        # func
        func_layout = QHBoxLayout()
        func_label = QLabel("HTTP请求方法 (*)")
        func_label.setMinimumWidth(120)
        self.func_combo = QComboBox()
        self.func_combo.addItems(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        self.func_combo.setFixedWidth(120)
        func_layout.addWidget(func_label)
        func_layout.addWidget(self.func_combo)
        basic_group_layout.addLayout(func_layout)
        
        # APICORE_version - 改为下拉框
        version_layout = QHBoxLayout()
        version_label = QLabel("APICORE 版本 (*)")
        version_label.setMinimumWidth(120)
        self.version_combo = QComboBox()
        self.version_combo.addItem("1.0")
        self.version_combo.setFixedWidth(80)
        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_combo)
        basic_group_layout.addLayout(version_layout)
        
        # 添加分组框到标签页
        basic_layout.addWidget(basic_group)
        basic_layout.addStretch()
        
        # 添加预览配置按钮
        preview_btn = QPushButton("预览当前配置")
        preview_btn.setMinimumHeight(35)
        preview_btn.clicked.connect(self.preview_config)
        basic_layout.addWidget(preview_btn)
        
        # 添加标签页到标签控件
        self.tabs.addTab(basic_config_tab, "基本配置")
        
    def create_parameters_tab(self):
        # 创建参数配置标签页
        parameters_tab = QWidget()
        parameters_layout = QHBoxLayout(parameters_tab)
        parameters_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建左侧参数列表
        left_widget = QWidget()
        left_widget.setMinimumWidth(220)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(10)
        
        list_label = QLabel("参数列表")
        list_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(list_label)
        
        self.parameters_list = QListWidget()
        self.parameters_list.setAlternatingRowColors(True)
        left_layout.addWidget(self.parameters_list)
        
        # 添加参数按钮
        add_param_btn = QPushButton("添加参数")
        add_param_btn.setMinimumHeight(30)
        add_param_btn.clicked.connect(self.add_parameter)
        left_layout.addWidget(add_param_btn)
        
        # 创建右侧参数详情
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(10)
        
        self.param_details_group = QGroupBox("参数详情")
        param_details_layout = QVBoxLayout(self.param_details_group)
        param_details_layout.setSpacing(12)
        
        # 参数类型
        type_layout = QHBoxLayout()
        type_label = QLabel("参数类型 (*)")
        type_label.setMinimumWidth(100)
        self.param_type_combo = QComboBox()
        self.param_type_combo.addItems(["integer", "boolean", "list", "string", "enum"])
        self.param_type_combo.setFixedWidth(120)
        self.param_type_combo.currentTextChanged.connect(self.on_param_type_changed)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.param_type_combo)
        type_layout.addStretch()
        param_details_layout.addLayout(type_layout)
        
        # 参数名称
        name_layout = QHBoxLayout()
        name_label = QLabel("参数关键字")
        name_label.setMinimumWidth(100)
        self.param_name_edit = QLineEdit()
        self.param_name_edit.setPlaceholderText("输入API请求参数的关键字")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.param_name_edit)
        param_details_layout.addLayout(name_layout)
        
        # 友好名称
        friendly_name_layout = QHBoxLayout()
        friendly_label = QLabel("友好名称 (*)")
        friendly_label.setMinimumWidth(100)
        self.param_friendly_name_edit = QLineEdit()
        self.param_friendly_name_edit.setPlaceholderText("输入参数在UI上显示的名称")
        friendly_name_layout.addWidget(friendly_label)
        friendly_name_layout.addWidget(self.param_friendly_name_edit)
        param_details_layout.addLayout(friendly_name_layout)
        
        # 是否必需
        required_layout = QHBoxLayout()
        required_label = QLabel("是否必需")
        required_label.setMinimumWidth(100)
        self.param_required_check = QCheckBox()
        self.param_required_check.setChecked(True)
        required_layout.addWidget(required_label)
        required_layout.addWidget(self.param_required_check)
        required_layout.addStretch()
        param_details_layout.addLayout(required_layout)
        
        # 是否启用
        enable_layout = QHBoxLayout()
        enable_label = QLabel("是否启用")
        enable_label.setMinimumWidth(100)
        self.param_enable_check = QCheckBox()
        self.param_enable_check.setChecked(True)
        enable_layout.addWidget(enable_label)
        enable_layout.addWidget(self.param_enable_check)
        enable_layout.addStretch()
        param_details_layout.addLayout(enable_layout)
        
        # 整数类型特有的最小值和最大值
        self.min_value_layout = QHBoxLayout()
        min_label = QLabel("最小值 (*)")
        min_label.setMinimumWidth(100)
        self.param_min_value_spin = QSpinBox()
        self.param_min_value_spin.setRange(-2147483648, 2147483647)
        self.param_min_value_spin.setFixedWidth(150)
        self.min_value_layout.addWidget(min_label)
        self.min_value_layout.addWidget(self.param_min_value_spin)
        self.min_value_layout.addStretch()
        param_details_layout.addLayout(self.min_value_layout)
        
        self.max_value_layout = QHBoxLayout()
        max_label = QLabel("最大值 (*)")
        max_label.setMinimumWidth(100)
        self.param_max_value_spin = QSpinBox()
        self.param_max_value_spin.setRange(-2147483648, 2147483647)
        self.param_max_value_spin.setValue(100)
        self.param_max_value_spin.setFixedWidth(150)
        self.max_value_layout.addWidget(max_label)
        self.max_value_layout.addWidget(self.param_max_value_spin)
        self.max_value_layout.addStretch()
        param_details_layout.addLayout(self.max_value_layout)
        
        # 列表类型特有的分割符
        self.split_str_layout = QHBoxLayout()
        split_label = QLabel("列表分割符 (*)")
        split_label.setMinimumWidth(100)
        self.param_split_str_edit = QLineEdit()
        self.param_split_str_edit.setPlaceholderText("例如: , 或 ; 或 |")
        self.param_split_str_edit.setFixedWidth(100)
        self.split_str_layout.addWidget(split_label)
        self.split_str_layout.addWidget(self.param_split_str_edit)
        self.split_str_layout.addStretch()
        param_details_layout.addLayout(self.split_str_layout)
        
        # 枚举类型特有的值列表
        self.enum_values_layout = QVBoxLayout()
        enum_label = QLabel("枚举值 (用逗号分隔)")
        self.param_enum_values_edit = QTextEdit()
        self.param_enum_values_edit.setMaximumHeight(70)
        self.param_enum_values_edit.setPlaceholderText("例如: value1,value2,value3")
        self.enum_values_layout.addWidget(enum_label)
        self.enum_values_layout.addWidget(self.param_enum_values_edit)
        param_details_layout.addLayout(self.enum_values_layout)
        
        # 枚举类型特有的友好值列表
        self.friendly_values_layout = QVBoxLayout()
        friendly_val_label = QLabel("友好名称 (用逗号分隔)")
        self.param_friendly_values_edit = QTextEdit()
        self.param_friendly_values_edit.setMaximumHeight(70)
        self.param_friendly_values_edit.setPlaceholderText("例如: 选项1,选项2,选项3")
        self.friendly_values_layout.addWidget(friendly_val_label)
        self.friendly_values_layout.addWidget(self.param_friendly_values_edit)
        param_details_layout.addLayout(self.friendly_values_layout)
        
        # 字符串类型特有的默认值
        self.string_value_layout = QHBoxLayout()
        string_label = QLabel("默认值")
        string_label.setMinimumWidth(100)
        self.param_string_value_edit = QLineEdit()
        self.param_string_value_edit.setPlaceholderText("输入字符串默认值")
        self.string_value_layout.addWidget(string_label)
        self.string_value_layout.addWidget(self.param_string_value_edit)
        param_details_layout.addLayout(self.string_value_layout)
        
        # 布尔类型特有的默认值
        self.boolean_value_layout = QHBoxLayout()
        bool_label = QLabel("默认值")
        bool_label.setMinimumWidth(100)
        self.param_boolean_value_combo = QComboBox()
        self.param_boolean_value_combo.addItems(["true", "false"])
        self.param_boolean_value_combo.setFixedWidth(100)
        self.boolean_value_layout.addWidget(bool_label)
        self.boolean_value_layout.addWidget(self.param_boolean_value_combo)
        self.boolean_value_layout.addStretch()
        param_details_layout.addLayout(self.boolean_value_layout)
        
        # 整数类型特有的默认值
        self.integer_value_layout = QHBoxLayout()
        int_label = QLabel("默认值")
        int_label.setMinimumWidth(100)
        self.param_integer_value_spin = QSpinBox()
        self.param_integer_value_spin.setRange(-2147483648, 2147483647)
        self.param_integer_value_spin.setFixedWidth(150)
        self.integer_value_layout.addWidget(int_label)
        self.integer_value_layout.addWidget(self.param_integer_value_spin)
        self.integer_value_layout.addStretch()
        param_details_layout.addLayout(self.integer_value_layout)
        
        # 列表类型特有的默认值
        self.list_value_layout = QVBoxLayout()
        list_label = QLabel("默认值 (用逗号分隔)")
        self.param_list_value_edit = QTextEdit()
        self.param_list_value_edit.setMaximumHeight(70)
        self.param_list_value_edit.setPlaceholderText("例如: item1,item2,item3")
        self.list_value_layout.addWidget(list_label)
        self.list_value_layout.addWidget(self.param_list_value_edit)
        param_details_layout.addLayout(self.list_value_layout)
        
        # 更新和删除按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.update_param_btn = QPushButton("更新参数")
        self.update_param_btn.setMinimumWidth(100)
        self.update_param_btn.setMinimumHeight(30)
        self.update_param_btn.clicked.connect(self.update_parameter)
        self.delete_param_btn = QPushButton("删除参数")
        self.delete_param_btn.setMinimumWidth(100)
        self.delete_param_btn.setMinimumHeight(30)
        self.delete_param_btn.clicked.connect(self.delete_parameter)
        buttons_layout.addWidget(self.update_param_btn)
        buttons_layout.addWidget(self.delete_param_btn)
        param_details_layout.addLayout(buttons_layout)
        
        right_layout.addWidget(self.param_details_group)
        right_layout.addStretch()
        
        # 添加左右两侧到标签页
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([220, 700])
        parameters_layout.addWidget(splitter)
        
        # 初始化参数类型相关控件的显示
        self.on_param_type_changed(self.param_type_combo.currentText())
        
        # 添加标签页到标签控件
        self.tabs.addTab(parameters_tab, "参数配置")
        
        # 连接参数列表的选择信号
        self.parameters_list.itemClicked.connect(self.on_parameter_selected)
        
    def create_response_tab(self):
        # 创建响应配置标签页
        response_tab = QWidget()
        response_layout = QVBoxLayout(response_tab)
        response_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        
        # 图像配置
        image_group = QGroupBox("图像配置")
        image_layout = QVBoxLayout(image_group)
        image_layout.setSpacing(12)
        image_layout.setContentsMargins(10, 20, 10, 10)  # 增加顶部边距以避免标题被遮挡
        
        # content_type
        content_type_layout = QHBoxLayout()
        content_type_label = QLabel("图像类型 (*)")
        content_type_label.setMinimumWidth(120)
        self.image_content_type_combo = QComboBox()
        self.image_content_type_combo.addItems(["URL", "BINARY"])
        self.image_content_type_combo.setFixedWidth(120)
        self.image_content_type_combo.currentTextChanged.connect(self.on_image_content_type_changed)
        content_type_layout.addWidget(content_type_label)
        content_type_layout.addWidget(self.image_content_type_combo)
        content_type_layout.addStretch()
        image_layout.addLayout(content_type_layout)
        
        # path
        path_layout = QHBoxLayout()
        self.image_path_label = QLabel("图像路径 (*)")
        self.image_path_label.setMinimumWidth(120)
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("请输入图像在响应中的JSON路径")
        path_layout.addWidget(self.image_path_label)
        path_layout.addWidget(self.image_path_edit)
        image_layout.addLayout(path_layout)
        
        # 初始化时根据当前类型设置路径标签
        self.on_image_content_type_changed(self.image_content_type_combo.currentText())
        
        # is_list
        is_list_layout = QHBoxLayout()
        is_list_label = QLabel("是否是图像列表")
        is_list_label.setMinimumWidth(120)
        self.image_is_list_check = QCheckBox()
        is_list_layout.addWidget(is_list_label)
        is_list_layout.addWidget(self.image_is_list_check)
        is_list_layout.addStretch()
        image_layout.addLayout(is_list_layout)
        
        # is_base64
        is_base64_layout = QHBoxLayout()
        is_base64_label = QLabel("是否base64编码")
        is_base64_label.setMinimumWidth(120)
        self.image_is_base64_check = QCheckBox()
        is_base64_layout.addWidget(is_base64_label)
        is_base64_layout.addWidget(self.image_is_base64_check)
        is_base64_layout.addStretch()
        image_layout.addLayout(is_base64_layout)
        
        scroll_layout.addWidget(image_group)
        
        # 其他数据配置
        others_group = QGroupBox("其他数据配置")
        others_layout = QVBoxLayout(others_group)
        others_layout.setSpacing(12)
        others_layout.setContentsMargins(10, 20, 10, 10)  # 增加顶部边距以避免标题被遮挡
        
        # 数据组列表
        data_groups_layout = QVBoxLayout()
        group_list_label = QLabel("数据组")
        group_list_label.setStyleSheet("font-weight: bold;")
        data_groups_layout.addWidget(group_list_label)
        
        group_list_h_layout = QHBoxLayout()
        self.data_groups_list = QListWidget()
        self.data_groups_list.setAlternatingRowColors(True)
        self.data_groups_list.setMinimumHeight(150)
        group_list_h_layout.addWidget(self.data_groups_list)
        data_groups_layout.addLayout(group_list_h_layout)
        
        # 将数据组布局添加到主布局
        others_layout.addLayout(data_groups_layout)
        
        # 添加数据组按钮
        add_group_btn = QPushButton("添加数据组")
        add_group_btn.clicked.connect(self.add_data_group)
        others_layout.addWidget(add_group_btn)
        
        # 数据组详情
        self.data_group_details_group = QGroupBox("数据组详情")
        data_group_details_layout = QVBoxLayout(self.data_group_details_group)
        data_group_details_layout.setSpacing(10)
        data_group_details_layout.setContentsMargins(10, 20, 10, 10)  # 增加顶部边距以避免标题被遮挡
        
        # 友好名称
        group_friendly_name_layout = QHBoxLayout()
        group_name_label = QLabel("数据组名称")
        group_name_label.setMinimumWidth(100)
        self.group_friendly_name_edit = QLineEdit()
        self.group_friendly_name_edit.setPlaceholderText("输入数据组的名称")
        group_friendly_name_layout.addWidget(group_name_label)
        group_friendly_name_layout.addWidget(self.group_friendly_name_edit)
        data_group_details_layout.addLayout(group_friendly_name_layout)
        
        # 数据项列表
        data_items_layout = QVBoxLayout()
        item_list_label = QLabel("数据项")
        item_list_label.setStyleSheet("font-weight: bold;")
        data_items_layout.addWidget(item_list_label)
        
        item_list_h_layout = QHBoxLayout()
        self.data_items_list = QListWidget()
        self.data_items_list.setAlternatingRowColors(True)
        self.data_items_list.setMinimumHeight(120)
        item_list_h_layout.addWidget(self.data_items_list)
        data_items_layout.addLayout(item_list_h_layout)
        data_group_details_layout.addLayout(data_items_layout)
        
        # 添加数据项按钮
        add_item_btn = QPushButton("添加数据项")
        add_item_btn.clicked.connect(self.add_data_item)
        data_group_details_layout.addWidget(add_item_btn)
        
        # 数据项详情
        self.data_item_details_group = QGroupBox("数据项详情")
        data_item_details_layout = QVBoxLayout(self.data_item_details_group)
        data_item_details_layout.setSpacing(10)
        data_item_details_layout.setContentsMargins(10, 20, 10, 10)  # 增加顶部边距以避免标题被遮挡
        
        # 友好名称
        item_friendly_name_layout = QHBoxLayout()
        item_name_label = QLabel("数据项名称")
        item_name_label.setMinimumWidth(100)
        self.item_friendly_name_edit = QLineEdit()
        self.item_friendly_name_edit.setPlaceholderText("输入数据项的名称")
        item_friendly_name_layout.addWidget(item_name_label)
        item_friendly_name_layout.addWidget(self.item_friendly_name_edit)
        data_item_details_layout.addLayout(item_friendly_name_layout)
        
        # 路径
        item_path_layout = QHBoxLayout()
        item_path_label = QLabel("数据路径")
        item_path_label.setMinimumWidth(100)
        self.item_path_edit = QLineEdit()
        self.item_path_edit.setPlaceholderText("输入数据在响应中的JSON路径")
        item_path_layout.addWidget(item_path_label)
        item_path_layout.addWidget(self.item_path_edit)
        data_item_details_layout.addLayout(item_path_layout)
        
        # 数据类型
        item_type_layout = QHBoxLayout()
        item_type_label = QLabel("数据类型")
        item_type_label.setMinimumWidth(100)
        self.item_type_combo = QComboBox()
        self.item_type_combo.setMinimumWidth(120)
        # 只保留string和list两个选项
        self.item_type_combo.addItems(["string", "list"])
        item_type_layout.addWidget(item_type_label)
        item_type_layout.addWidget(self.item_type_combo)
        data_item_details_layout.addLayout(item_type_layout)
        
        # 图像数量与列表长度相同复选框
        self.item_one_to_one_mapping_layout = QHBoxLayout()
        self.item_one_to_one_mapping_label = QLabel("图像数量与列表长度相同")
        self.item_one_to_one_mapping_label.setMinimumWidth(180)
        self.item_one_to_one_mapping_check = QCheckBox()
        # 默认禁用并取消勾选
        self.item_one_to_one_mapping_check.setDisabled(True)
        self.item_one_to_one_mapping_check.setChecked(False)
        self.item_one_to_one_mapping_layout.addWidget(self.item_one_to_one_mapping_label)
        self.item_one_to_one_mapping_layout.addWidget(self.item_one_to_one_mapping_check)
        self.item_one_to_one_mapping_layout.addStretch()
        data_item_details_layout.addLayout(self.item_one_to_one_mapping_layout)
        
        # 连接数据类型变更信号
        self.item_type_combo.currentTextChanged.connect(self.on_item_type_changed)
        
        # 更新和删除按钮
        item_buttons_layout = QHBoxLayout()
        item_buttons_layout.addStretch()
        self.update_item_btn = QPushButton("更新数据项")
        self.update_item_btn.setMinimumWidth(100)
        self.update_item_btn.setMinimumHeight(30)
        self.update_item_btn.clicked.connect(self.update_data_item)
        self.delete_item_btn = QPushButton("删除数据项")
        self.delete_item_btn.setMinimumWidth(100)
        self.delete_item_btn.setMinimumHeight(30)
        self.delete_item_btn.clicked.connect(self.delete_data_item)
        item_buttons_layout.addWidget(self.update_item_btn)
        item_buttons_layout.addWidget(self.delete_item_btn)
        data_item_details_layout.addLayout(item_buttons_layout)
        
        data_group_details_layout.addWidget(self.data_item_details_group)
        
        # 更新和删除数据组按钮
        group_buttons_layout = QHBoxLayout()
        group_buttons_layout.addStretch()
        self.update_group_btn = QPushButton("更新数据组")
        self.update_group_btn.setMinimumWidth(100)
        self.update_group_btn.setMinimumHeight(30)
        self.update_group_btn.clicked.connect(self.update_data_group)
        self.delete_group_btn = QPushButton("删除数据组")
        self.delete_group_btn.setMinimumWidth(100)
        self.delete_group_btn.setMinimumHeight(30)
        self.delete_group_btn.clicked.connect(self.delete_data_group)
        group_buttons_layout.addWidget(self.update_group_btn)
        group_buttons_layout.addWidget(self.delete_group_btn)
        data_group_details_layout.addLayout(group_buttons_layout)
        
        others_layout.addWidget(self.data_group_details_group)
        
        scroll_layout.addWidget(others_group)
        scroll_layout.addStretch()
        
        # 设置滚动区域
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        
        response_layout.addWidget(scroll_area)
        
        # 添加标签页到标签控件
        self.tabs.addTab(response_tab, "响应配置")
        
        # 连接列表的选择信号
        self.data_groups_list.itemClicked.connect(self.on_data_group_selected)
        self.data_items_list.itemClicked.connect(self.on_data_item_selected)
        
        # 初始化数据存储
        self.parameters = []
        self.data_groups = []
        self.current_param_index = -1
        self.current_group_index = -1
        self.current_item_index = -1
        
    def on_image_content_type_changed(self, content_type):
        # 当图像类型为binary时，图像路径无需填写
        if content_type == "BINARY":
            self.image_path_label.setText("图像路径")  # 移除必填标记
            # self.image_path_edit.setPlaceholderText("返回的图像类型为二进制时无需填写")
            # self.image_path_edit.setText("")  # 清空已填写的路径
            # self.image_path_edit.setDisabled(True)
        else:
            self.image_path_label.setText("图像路径 (*)")  # 恢复必填标记
            self.image_path_edit.setPlaceholderText("请输入图像在响应中的JSON路径")
            self.image_path_edit.setDisabled(False)
    
    def on_param_type_changed(self, param_type):
        # 根据参数类型显示或隐藏相关控件
        # 注意：QHBoxLayout没有setHidden方法，我们需要遍历布局中的所有控件来设置
        def set_layout_visibility(layout, is_visible):
            for i in range(layout.count()):
                item = layout.itemAt(i)
                widget = item.widget()
                if widget:
                    widget.setVisible(is_visible)
                     
        set_layout_visibility(self.min_value_layout, param_type == "integer")
        set_layout_visibility(self.max_value_layout, param_type == "integer")
        set_layout_visibility(self.split_str_layout, param_type == "list")
        set_layout_visibility(self.enum_values_layout, param_type == "enum")
        set_layout_visibility(self.friendly_values_layout, param_type == "enum")
        set_layout_visibility(self.string_value_layout, param_type == "string")
        set_layout_visibility(self.boolean_value_layout, param_type == "boolean")
        set_layout_visibility(self.integer_value_layout, param_type == "integer")
        set_layout_visibility(self.list_value_layout, param_type == "list")
         
        # 当类型为enum时，禁用enable复选框
        self.param_enable_check.setChecked(True)
        self.param_enable_check.setDisabled(param_type == "enum")

    def add_parameter(self):
        # 创建一个新的参数对象
        param = {
            "enable": True,
            "name": "",
            "type": "string",
            "required": True,
            "value": "",
            "friendly_value": [],
            "friendly_name": "",
            "min_value": None,
            "max_value": None,
            "split_str": None
        }
        
        # 添加到参数列表
        self.parameters.append(param)
        
        # 更新参数列表显示
        self.update_parameters_list()
        
        # 选择新添加的参数
        self.parameters_list.setCurrentRow(len(self.parameters) - 1)
        self.on_parameter_selected(self.parameters_list.currentItem())
        
    def update_parameters_list(self):
        # 清空列表
        self.parameters_list.clear()
        
        # 添加参数到列表
        for i, param in enumerate(self.parameters):
            friendly_name = param.get("friendly_name", "未命名参数")
            param_type = param.get("type", "")
            item = QListWidgetItem(f"{i+1}. {friendly_name} ({param_type})")
            self.parameters_list.addItem(item)
            
    def on_parameter_selected(self, item):
        # 获取选中的参数索引
        index = self.parameters_list.row(item)
        if index < 0 or index >= len(self.parameters):
            logger.error(f"无效的参数索引: {index}")
            return
        
        # 保存当前参数索引
        self.current_param_index = index
        
        # 获取参数对象
        param = self.parameters[index]
        
        # 填充表单
        self.param_type_combo.setCurrentText(param.get("type", "string"))
        self.param_name_edit.setText(param.get("name", ""))
        self.param_friendly_name_edit.setText(param.get("friendly_name", ""))
        self.param_required_check.setChecked(param.get("required", True))
        self.param_enable_check.setChecked(param.get("enable", True))
        
        # 根据参数类型填充特定字段
        param_type = param.get("type", "string")
        if param_type == "integer":
            self.param_min_value_spin.setValue(param.get("min_value", 0))
            self.param_max_value_spin.setValue(param.get("max_value", 100))
            self.param_integer_value_spin.setValue(param.get("value", 0))
        elif param_type == "boolean":
            self.param_boolean_value_combo.setCurrentText(str(param.get("value", False)).lower())
        elif param_type == "list":
            self.param_split_str_edit.setText(param.get("split_str", ""))
            self.param_list_value_edit.setPlainText(", ".join(param.get("value", [])))
        elif param_type == "string":
            self.param_string_value_edit.setText(param.get("value", ""))
        elif param_type == "enum":
            # 确保所有值都是字符串类型
            enum_values = [str(v) for v in param.get("value", [])]
            friendly_values = [str(v) for v in param.get("friendly_value", [])]
            self.param_enum_values_edit.setPlainText(", ".join(enum_values))
            self.param_friendly_values_edit.setPlainText(", ".join(friendly_values))
        
    def update_parameter(self):
        # 检查是否有选中的参数
        if self.current_param_index < 0 or self.current_param_index >= len(self.parameters):
            QMessageBox.warning(self, "警告", "请先选择要更新的参数")
            return
        
        # 获取参数对象
        param = self.parameters[self.current_param_index]
        
        # 更新参数对象
        param["type"] = self.param_type_combo.currentText()
        param["name"] = self.param_name_edit.text()
        param["friendly_name"] = self.param_friendly_name_edit.text()
        param["required"] = self.param_required_check.isChecked()
        
        # 当类型不是enum时，更新enable字段
        if param["type"] != "enum":
            param["enable"] = self.param_enable_check.isChecked()
        
        # 根据参数类型更新特定字段
        if param["type"] == "integer":
            param["min_value"] = self.param_min_value_spin.value()
            param["max_value"] = self.param_max_value_spin.value()
            param["value"] = self.param_integer_value_spin.value()
            param["friendly_value"] = []
            param["split_str"] = None
        elif param["type"] == "boolean":
            param["value"] = self.param_boolean_value_combo.currentText() == "true"
            param["friendly_value"] = []
            param["min_value"] = None
            param["max_value"] = None
            param["split_str"] = None
        elif param["type"] == "list":
            param["split_str"] = self.param_split_str_edit.text()
            value_text = self.param_list_value_edit.toPlainText()
            param["value"] = [v.strip() for v in value_text.split(",")] if value_text else []
            param["friendly_value"] = []
            param["min_value"] = None
            param["max_value"] = None
        elif param["type"] == "string":
            param["value"] = self.param_string_value_edit.text()
            param["friendly_value"] = []
            param["min_value"] = None
            param["max_value"] = None
            param["split_str"] = None
        elif param["type"] == "enum":
            value_text = self.param_enum_values_edit.toPlainText()
            param["value"] = [v.strip() for v in value_text.split(",")] if value_text else []
            friendly_value_text = self.param_friendly_values_edit.toPlainText()
            param["friendly_value"] = [v.strip() for v in friendly_value_text.split(",")] if friendly_value_text else []
            param["min_value"] = None
            param["max_value"] = None
            param["split_str"] = None
        
        # 更新参数列表显示
        self.update_parameters_list()
        
        # 重新选择当前参数
        self.parameters_list.setCurrentRow(self.current_param_index)
        
        QMessageBoxEx.information(self, "提示", "参数已更新")
        
    def delete_parameter(self):
        # 检查是否有选中的参数
        if self.current_param_index < 0 or self.current_param_index >= len(self.parameters):
            QMessageBox.warning(self, "警告", "请先选择要删除的参数")
            return
        
        # 确认删除
        reply = QMessageBox.question(self, "确认", "确定要删除这个参数吗？", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除参数
            self.parameters.pop(self.current_param_index)
            
            # 更新参数列表显示
            self.update_parameters_list()
            
            # 重置当前参数索引
            self.current_param_index = -1
            
            QMessageBoxEx.information(self, "提示", "参数已删除")
            
    def add_data_group(self):
        self.statusBar().showMessage("正在添加新数据组...")
        
        # 创建一个新的数据组对象
        data_group = {
            "friendly_name": "未命名数据组",
            "data": []
        }
        
        # 添加到数据组列表
        self.data_groups.append(data_group)
        
        # 更新数据组列表显示
        self.update_data_groups_list()
        
        # 选择新添加的数据组
        self.data_groups_list.setCurrentRow(len(self.data_groups) - 1)
        self.on_data_group_selected(self.data_groups_list.currentItem())
        
        self.statusBar().showMessage("已添加新数据组，请设置友好名称")
        
    def on_item_type_changed(self, text):
        # 根据数据类型启用或禁用一对一映射复选框
        if text == "list":
            self.item_one_to_one_mapping_check.setDisabled(False)
        else:
            self.item_one_to_one_mapping_check.setDisabled(True)
            self.item_one_to_one_mapping_check.setChecked(False)
        
        # 更新状态栏提示
        type_hints = {
            "string": "字符串类型：用于文本数据",
            "list": "列表类型：多个值，可以启用一对一映射",
        }
        self.statusBar().showMessage(f"数据项类型已更改为：{text} - {type_hints.get(text, '请根据类型设置相应参数')}")

    def update_data_groups_list(self):
        # 清空列表
        self.data_groups_list.clear()
        
        # 添加数据组到列表
        for i, data_group in enumerate(self.data_groups):
            friendly_name = data_group.get("friendly_name", "未命名数据组")
            item = QListWidgetItem(f"{i+1}. {friendly_name}")
            logger.info(f"添加数据组到列表: {i+1}. {friendly_name}")
            self.data_groups_list.addItem(item)
            
    def on_data_group_selected(self, item):
        # 获取选中的数据组索引
        index = self.data_groups_list.row(item)
        if index < 0 or index >= len(self.data_groups):
            return
        
        # 保存当前数据组索引
        self.current_group_index = index
        
        # 获取数据组对象
        data_group = self.data_groups[index]
        
        # 填充表单
        self.group_friendly_name_edit.setText(data_group.get("friendly_name", ""))
        
        # 更新数据项列表显示
        self.update_data_items_list()
        
        if len(self.data_items_list) > 0:
            self.data_items_list.setCurrentRow(0)
            self.on_data_item_selected(self.data_items_list.currentItem())
        
    def update_data_items_list(self):
        # 清空列表
        self.data_items_list.clear()
        
        # 检查是否有选中的数据组
        if self.current_group_index < 0 or self.current_group_index >= len(self.data_groups):
            return
        
        # 获取数据组对象
        data_group = self.data_groups[self.current_group_index]
        
        # 添加数据项到列表
        for i, data_item in enumerate(data_group.get("data", [])):
            friendly_name = data_item.get("friendly_name", "未命名数据项")
            item = QListWidgetItem(f"{i+1}. {friendly_name}")
            self.data_items_list.addItem(item)
            
    def add_data_item(self):
        # 检查是否有选中的数据组
        if self.current_group_index < 0 or self.current_group_index >= len(self.data_groups):
            QMessageBox.warning(self, "警告", "请先选择要添加数据项的数据组")
            self.statusBar().showMessage("添加数据项失败：请先选择数据组")
            return
        
        self.statusBar().showMessage("正在添加新数据项...")
        
        # 创建一个新的数据项对象，包含数据类型和one-to-one-mapping
        data_item = {
            "friendly_name": "未命名数据项",
            "path": "",
            "type": "string",  # 默认数据类型为string
            "one-to-one-mapping": False  # 默认不启用一对一映射
        }
        
        # 添加到数据项列表
        self.data_groups[self.current_group_index]["data"].append(data_item)
        
        # 更新数据项列表显示
        self.update_data_items_list()
        
        # 选择新添加的数据项
        self.data_items_list.setCurrentRow(len(self.data_groups[self.current_group_index]["data"]) - 1)
        self.on_data_item_selected(self.data_items_list.currentItem())
        
        self.statusBar().showMessage("已添加新数据项，请设置友好名称、路径和类型")
        
    def on_data_item_selected(self, item):
        # 获取选中的数据项索引
        index = self.data_items_list.row(item)
        if index < 0 or index >= len(self.data_groups[self.current_group_index]["data"]):
            return
        
        # 保存当前数据项索引
        self.current_item_index = index
        
        # 获取数据项对象
        data_item: dict = self.data_groups[self.current_group_index]["data"][index]
        logger.info(f"选择数据项: {index+1}. {data_item.get('friendly_name', '未命名数据项')}")
        
        # 填充表单
        self.item_friendly_name_edit.setText(data_item.get("friendly_name", ""))
        self.item_path_edit.setText(data_item.get("path", ""))
        
        # 设置数据类型
        item_type = data_item.get("type", "string")
        if item_type in ["string", "list"]:
            self.item_type_combo.setCurrentText(item_type)
        else:
            self.item_type_combo.setCurrentText("string")
        
        # 设置一对一映射状态
        one_to_one_mapping = data_item.get("one-to-one-mapping", False)
        self.item_one_to_one_mapping_check.setChecked(one_to_one_mapping)
        
        if "type" not in data_item and data_item.get("one-to-one-mapping", False):
            self.item_type_combo.setCurrentText("list")
            self.item_one_to_one_mapping_check.setChecked(True)
        
        # 根据数据类型启用或禁用一对一映射复选框
        self.on_item_type_changed(self.item_type_combo.currentText())
        
    def update_data_item(self):
        # 检查是否有选中的数据项
        if (self.current_group_index < 0 or self.current_group_index >= len(self.data_groups) or
            self.current_item_index < 0 or self.current_item_index >= len(self.data_groups[self.current_group_index]["data"])):
            QMessageBox.warning(self, "警告", "请先选择要更新的数据项")
            self.statusBar().showMessage("更新数据项失败：请先选择数据项")
            return
        
        self.statusBar().showMessage("正在更新数据项...")
        
        # 获取数据项对象
        data_item = self.data_groups[self.current_group_index]["data"][self.current_item_index]
        
        # 更新数据项对象
        data_item["friendly_name"] = self.item_friendly_name_edit.text()
        data_item["path"] = self.item_path_edit.text()
        data_item["type"] = self.item_type_combo.currentText()
        
        # 只有在数据类型为list且复选框被选中时才设置one-to-one-mapping为True
        if self.item_type_combo.currentText() == "list":
            data_item["one-to-one-mapping"] = self.item_one_to_one_mapping_check.isChecked()
        else:
            data_item["one-to-one-mapping"] = False
        
        # 更新数据项列表显示
        self.update_data_items_list()
        
        # 重新选择当前数据项
        self.data_items_list.setCurrentRow(self.current_item_index)
        
        QMessageBoxEx.information(self, "提示", "数据项已更新")
        self.statusBar().showMessage(f"已更新数据项：{data_item['friendly_name']}")
        
    def delete_data_item(self):
        # 检查是否有选中的数据项
        if (self.current_group_index < 0 or self.current_group_index >= len(self.data_groups) or
            self.current_item_index < 0 or self.current_item_index >= len(self.data_groups[self.current_group_index]["data"])):
            QMessageBox.warning(self, "警告", "请先选择要删除的数据项")
            self.statusBar().showMessage("删除数据项失败：请先选择数据项")
            return
        
        # 确认删除
        reply = QMessageBox.question(self, "确认", "确定要删除这个数据项吗？", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除数据项
            data_item = self.data_groups[self.current_group_index]["data"][self.current_item_index]
            item_name = data_item.get("friendly_name", "数据项")
            
            self.data_groups[self.current_group_index]["data"].pop(self.current_item_index)
            
            # 更新数据项列表显示
            self.update_data_items_list()
            
            # 重置当前数据项索引
            self.current_item_index = -1
            
            QMessageBoxEx.information(self, "提示", "数据项已删除")
            self.statusBar().showMessage(f"已删除数据项：{item_name}")
        else:
            self.statusBar().showMessage("已取消删除数据项操作")
            
    def update_data_group(self):
        # 检查是否有选中的数据组
        if self.current_group_index < 0 or self.current_group_index >= len(self.data_groups):
            QMessageBox.warning(self, "警告", "请先选择要更新的数据组")
            self.statusBar().showMessage("更新数据组失败：请先选择数据组")
            return
        
        self.statusBar().showMessage("正在更新数据组...")
        
        # 获取数据组对象
        data_group = self.data_groups[self.current_group_index]
        
        # 更新数据组对象
        data_group["friendly_name"] = self.group_friendly_name_edit.text()
        
        # 更新数据组列表显示
        self.update_data_groups_list()
        
        # 重新选择当前数据组
        self.data_groups_list.setCurrentRow(self.current_group_index)
        
        QMessageBoxEx.information(self, "提示", "数据组已更新")
        self.statusBar().showMessage(f"已更新数据组：{data_group['friendly_name']}")
        
    def delete_data_group(self):
        # 检查是否有选中的数据组
        if self.current_group_index < 0 or self.current_group_index >= len(self.data_groups):
            QMessageBox.warning(self, "警告", "请先选择要删除的数据组")
            self.statusBar().showMessage("删除数据组失败：请先选择数据组")
            return
        
        # 确认删除
        reply = QMessageBox.question(self, "确认", "确定要删除这个数据组吗？数据组内的所有数据项也将被删除！", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除数据组
            data_group = self.data_groups[self.current_group_index]
            group_name = data_group.get("friendly_name", "数据组")
            
            self.data_groups.pop(self.current_group_index)
            
            # 更新数据组列表显示
            self.update_data_groups_list()
            
            # 重置当前数据组和数据项索引
            self.current_group_index = -1
            self.current_item_index = -1
            
            # 清空数据项列表
            self.data_items_list.clear()
            
            QMessageBoxEx.information(self, "提示", "数据组已删除")
            self.statusBar().showMessage(f"已删除数据组：{group_name}（包含其中所有数据项）")
        else:
            self.statusBar().showMessage("已取消删除数据组操作")
            
    def new_file(self):
        # 确认是否保存当前文件
        if self.current_file is not None and self.config_has_changes():
            reply = QMessageBox.question(self, "确认", "是否保存当前文件？", 
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            
            if reply == QMessageBox.Cancel:
                logger.info("用户取消了新建文件操作")
                return
            elif reply == QMessageBox.Yes:
                if not self.save_file():
                    logger.warning("保存当前文件失败，取消新建文件操作")
                    return
        
        # 重置所有表单
        self.reset_all_forms()
        
        # 更新状态栏
        self.statusBar().showMessage("新建文件")
        logger.info("创建了新文件")
        
    def reset_all_forms(self):
        # 重置基本配置表单
        self.friendly_name_edit.clear()
        self.intro_edit.clear()
        self.icon_edit.clear()
        self.link_edit.clear()
        self.func_combo.setCurrentIndex(0)
        self.version_combo.setCurrentIndex(0)  # 修改为下拉框
        
        # 重置参数配置表单
        self.parameters = []
        self.current_param_index = -1
        self.update_parameters_list()
        
        # 重置响应配置表单
        self.image_content_type_combo.setCurrentIndex(0)
        self.image_path_edit.clear()
        self.image_is_list_check.setChecked(False)
        self.image_is_base64_check.setChecked(False)
        
        self.data_groups = []
        self.current_group_index = -1
        self.current_item_index = -1
        self.update_data_groups_list()
        self.data_items_list.clear()
        
        # 重置当前文件路径
        self.current_file = None
        
    def get_config_dir(self) -> str:
        from pathlib import Path
        config_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        if sys.platform.startswith('win'):
            config_dir = str(Path.home() / f'AppData{os.sep}Roaming{os.sep}wallpaper-generator-next{os.sep}EnterPoint')
        elif sys.platform.startswith('linux'):
            config_dir = str(Path.home() / f'.config{os.sep}wallpaper-generator-next{os.sep}EnterPoint')
        elif sys.platform.startswith('darwin'):
            config_dir = str(Path.home() / f'Library{os.sep}Application Support{os.sep}wallpaper-generator-next{os.sep}EnterPoint')
        else:
            config_dir = str(Path.home() / f'.config{os.sep}wallpaper-generator-next{os.sep}EnterPoint')
        
        if not os.path.exists(config_dir):
            if config_dir != os.path.dirname(os.path.realpath(sys.argv[0])) and os.path.exists(os.path.dirname(os.path.realpath(sys.argv[0]))):
                config_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
            else:
                config_dir = ""
            
        return config_dir
        
    def open_file(self):
        # 确认是否保存当前文件
        self.statusBar().showMessage("准备打开配置文件，请确认是否保存当前更改...")
        if self.current_file is not None and self.config_has_changes():
            reply = QMessageBox.question(self, "确认", "是否保存当前文件？", 
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            
            if reply == QMessageBox.Cancel:
                logger.info("用户取消了打开文件操作")
                self.statusBar().showMessage("已取消打开文件操作")
                return
            elif reply == QMessageBox.Yes:
                if not self.save_file():
                    logger.warning("保存当前文件失败，取消打开文件操作")
                    self.statusBar().showMessage("保存当前文件失败，已取消打开操作")
                    return
        
        # 打开文件对话框
        self.statusBar().showMessage("请选择要打开的 APICORE 配置文件")
        file_path, _ = QFileDialog.getOpenFileName(self, "打开 APICORE 配置文件", self.get_config_dir(), "APICORE 配置文件 (*.api.json);;JSON文件 (*.json);;所有文件 (*)")
        
        if file_path:
            # 加载文件内容
            try:
                self.statusBar().showMessage(f"正在加载文件: {os.path.basename(file_path)}...")
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 填充表单
                self.fill_forms_from_config(config)
                
                # 更新当前文件路径
                self.current_file = file_path
                
                # 更新状态栏
                self.statusBar().showMessage(f"已打开: {os.path.basename(file_path)}，系统正在验证配置...")
                logger.info(f"文件已打开: {file_path}")
                
                self.validate_config(Reminder_on_Success=False)
                self.statusBar().showMessage(f"已打开: {os.path.basename(file_path)}")
            except Exception as e:
                error_msg = f"打开文件失败: {str(e)}"
                logger.error(error_msg)
                QMessageBox.critical(self, "错误", error_msg)
                
    def fill_forms_from_config(self, config):
        # 填充基本配置表单
        self.friendly_name_edit.setText(config.get("friendly_name", ""))
        self.intro_edit.setText(config.get("intro", ""))
        self.icon_edit.setText(config.get("icon", ""))
        self.link_edit.setText(config.get("link", ""))
        
        func = config.get("func", "GET")
        if func in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            self.func_combo.setCurrentText(func)
        
        # 将版本设置为下拉框的值
        version = config.get("APICORE_version", "1.0")
        if version == "1.0":
            self.version_combo.setCurrentIndex(0)
        
        # 填充参数配置表单
        self.parameters = config.get("parameters", [])
        self.current_param_index = -1
        self.update_parameters_list()
        
        # 清空参数详情表单，即使没有参数
        self.param_type_combo.setCurrentIndex(0)
        self.param_name_edit.clear()
        self.param_friendly_name_edit.clear()
        self.param_required_check.setChecked(True)
        self.param_enable_check.setChecked(True)
        self.param_min_value_spin.setValue(0)
        self.param_max_value_spin.setValue(100)
        self.param_split_str_edit.clear()
        self.param_enum_values_edit.clear()
        self.param_friendly_values_edit.clear()
        self.param_string_value_edit.clear()
        self.param_boolean_value_combo.setCurrentIndex(0)
        self.param_integer_value_spin.setValue(0)
        self.param_list_value_edit.clear()
        
        if len(self.parameters) > 0:
            self.parameters_list.setCurrentRow(0)
            self.on_parameter_selected(self.parameters_list.currentItem())
        
        # 填充响应配置表单
        response = config.get("response", {})
        image = response.get("image", {})
        
        content_type = image.get("content_type", "URL")
        if content_type in ["URL", "BINARY"]:
            self.image_content_type_combo.setCurrentText(content_type)
        
        self.image_path_edit.setText(image.get("path", ""))
        self.image_is_list_check.setChecked(image.get("is_list", False))
        self.image_is_base64_check.setChecked(image.get("is_base64", False))
        
        self.data_groups = response.get("others", [])
        self.current_group_index = -1
        self.current_item_index = -1
        self.update_data_groups_list()
        self.data_items_list.clear()
        
        if len(self.data_groups) > 0:
            self.data_groups_list.setCurrentRow(0)
            self.on_data_group_selected(self.data_groups_list.currentItem())

    def save_file(self):
        # 如果当前文件路径不存在，调用另存为
        
        # 验证配置
        self.statusBar().showMessage("准备保存文件，正在验证配置...")
        if not self.validate_config(Reminder_on_Success=False):
            logger.warning("保存文件失败：配置验证未通过")
            self.statusBar().showMessage("保存失败：配置验证未通过，请检查配置")
            return False
        
        if self.current_file is None:
            logger.info("当前无文件路径，调用另存为")
            self.statusBar().showMessage("当前无文件路径，正在打开另存为对话框...")
            return self.save_file_as()
        
        # 保存文件
        try:
            self.statusBar().showMessage(f"正在保存文件: {os.path.basename(self.current_file)}...")
            config = self.create_config_from_forms()
            
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 更新状态栏
            self.statusBar().showMessage(f"已保存: {os.path.basename(self.current_file)}，文件保存成功")
            logger.info(f"文件已保存: {self.current_file}")
            
            return True
            
        except Exception as e:
            error_msg = f"保存文件失败: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            self.statusBar().showMessage(f"保存失败: {str(e)}")
            return False
            
    def save_file_as(self):
        # 打开文件对话框
        if not self.validate_config(Reminder_on_Success=False):
            return False
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存 APICORE 配置文件", "", "APICORE 配置文件 (*.api.json);;JSON文件 (*.json);;所有文件 (*)")
        
        if file_path:
            # 确保文件扩展名正确
            if not file_path.endswith(".api.json") and not file_path.endswith(".json"):
                file_path += ".api.json"
            
            # 更新当前文件路径
            self.current_file = file_path
            
            # 保存文件
            return self.save_file()
        
        return False
        
    def create_config_from_forms(self):
        # 创建配置对象
        config = {
            "friendly_name": self.friendly_name_edit.text(),
            "intro": self.intro_edit.toPlainText(),
            "icon": self.icon_edit.text(),
            "link": self.link_edit.text(),
            "func": self.func_combo.currentText(),
            "APICORE_version": self.version_combo.currentText(),  # 从下拉框获取版本
            "parameters": self.parameters,
            "response": {
                "image": {
                    "content_type": self.image_content_type_combo.currentText(),
                    "path": self.image_path_edit.text(),
                    "is_list": self.image_is_list_check.isChecked(),
                    "is_base64": self.image_is_base64_check.isChecked()
                },
                "others": self.data_groups
            }
        }
        
        return config
        
    def preview_config(self):
        # 创建配置对象
        config = self.create_config_from_forms()
        
        # 创建对话框
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
        from PyQt5.QtGui import QFontDatabase
        from QtHighlighters.JsonHighlighter import JsonHighlighter
        
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("预览配置")
        dialog.setWindowIcon(self.windowIcon())
        dialog.resize(800, 600)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        
        # 创建文本编辑框
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setLineWrapMode(QTextEdit.NoWrap)
        
        # 设置等宽字体
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        text_edit.setFont(font)
        
        # 添加语法高亮
        highlighter = JsonHighlighter(text_edit.document())
        
        # 设置配置内容
        config_json = json.dumps(config, ensure_ascii=False, indent=2)
        text_edit.setPlainText(config_json)
        
        # 添加文本编辑框到布局
        layout.addWidget(text_edit)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 创建关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.close)
        button_layout.addWidget(close_button)
        
        # 添加按钮布局到主布局
        layout.addLayout(button_layout)
        
        # 显示对话框
        dialog.exec_()
        
    def validate_config(self, Reminder_on_Success=True) -> bool:
        # 创建配置对象
        config = self.create_config_from_forms()
        logger.info(f"开始验证配置")
        # 验证配置
        try:
            # 基本验证
            assert config.get('APICORE_version') == '1.0', "无效的版本号"
            assert config.get('link') and config.get('func'), "缺少必要的API配置"
            assert config.get('friendly_name'), "缺少API接口名称"
            
            # 参数验证
            for param in config.get('parameters', []):
                param_type = param.get('type')
                param_name = param.get('name')
                assert param_type in ['integer', 'boolean', 'list', 'string', 'enum'], f"在参数 {param_name} 上存在无效的参数类型: {param_type}"
                
                if param_type == 'integer':
                    assert param.get('min_value') is not None, f"在参数 {param_name} 上缺少最小值"
                    assert param.get('max_value') is not None, f"在参数 {param_name} 上缺少最大值"
                    assert int(param.get('min_value')) <= int(param.get('max_value')), f"在参数 {param_name} 上最小值大于最大值"
                    assert int(param.get('value')) <= int(param.get('max_value')), f"在参数 {param_name} 上值大于最大值"
                    assert int(param.get('value')) >= int(param.get('min_value')), f"在参数 {param_name} 上值小于最小值"
                elif param_type == 'list':
                    assert param.get('split_str') is not None, f"在参数 {param_name} 上缺少分割符"
                elif param_type == 'enum':
                    assert param.get('friendly_value') is not None and len(param.get('friendly_value')) > 0, f"在参数 {param_name} 上缺少友好值列表"
                    assert param.get('value') is not None and len(param.get('value')) > 0, f"在参数 {param_name} 上缺少值列表"
                    # 验证友好值列表与值列表长度是否一致
                    assert len(param.get('friendly_value')) == len(param.get('value')), f"在参数 {param_name} 上枚举类型的友好值列表与值列表长度不匹配"
                
                assert param.get('friendly_name'), f"在参数 {param_name} 上缺少友好名称"
            
            # 响应验证
            response = config.get('response', {})
            image = response.get('image', {})
            assert image.get('content_type'), "缺少图像类型"
            if self.image_content_type_combo.currentText() != "BINARY": 
                assert image.get('path'), "缺少图像路径"
            
            if Reminder_on_Success:
                QMessageBoxEx.information(self, "提示", "配置文件验证通过")
                logger.info("配置文件验证通过")
            else:
                logger.debug("配置文件验证通过（静默模式）")
                
            return True
        except AssertionError as e:
            error_msg = f"配置文件验证失败: {str(e)}"
            logger.warning(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            return False
        except Exception as e:
            error_msg = f"验证过程发生错误: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            return False
            
    def open_image_converter(self):
        # 打开图片转换工具
        try:
            # 获取当前脚本所在目录
            if getattr(sys, 'frozen', False):
                # 构建图片转换工具的完整路径
                current_dir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])))
                converter_path = os.path.join(current_dir, "image_to_svg_base64.exe")
                # 启动图片转换工具
                subprocess.Popen(converter_path)
            else:
                # 构建图片转换工具的完整路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                converter_path = os.path.join(current_dir, "image_to_svg_base64.py")
                # 启动图片转换工具
                subprocess.Popen([sys.executable, converter_path])
            logger.info(f"图片转换工具已启动: {converter_path}")
        except Exception as e:
            error_msg = f"无法打开图片转换工具: {str(e)} \n 当前路径：{converter_path}"
            logger.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
    
    def show_about(self):
        # 显示关于对话框
        about_text = """APICORE 配置文件编辑器

版本：1.0
APICORE 版本: 1.0

一个用于创建和编辑 APICORE 配置文件的工具，
支持基本配置、参数配置和响应配置等功能。

© 2025 SRON团队"""
        
        # 创建自定义的关于对话框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("关于 APICORE 配置文件编辑器")
        msg_box.setText(about_text)
        
        # 设置图标
        icon_path = os.path.join(os.path.dirname(__file__), "Icons", "APICORE_Editor.png")
        if os.path.exists(icon_path):
            msg_box.setIconPixmap(QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # 添加按钮
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)
        
        # 显示对话框
        msg_box.exec_()
        
    def config_has_changes(self):
        """检查当前配置是否与已保存的配置不同"""
        # 如果是新文件（从未保存过），则认为有更改
        if self.current_file is None:
            # 检查是否有任何基本配置被填写
            if (self.friendly_name_edit.text() or 
                self.intro_edit.toPlainText() or 
                self.icon_edit.text() or 
                self.link_edit.text()):
                return True
            
            # 检查是否有参数被添加
            if len(self.parameters) > 0:
                return True
            
            # 检查是否有数据组被添加
            if len(self.data_groups) > 0:
                return True
            
            return False
        
        try:
            # 加载已保存的配置
            with open(self.current_file, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            
            # 获取当前配置
            current_config = self.create_config_from_forms()
            
            # 比较配置是否相同
            return json.dumps(saved_config, ensure_ascii=False, sort_keys=True) != \
                   json.dumps(current_config, ensure_ascii=False, sort_keys=True)
            
        except Exception as e:
            logger.error(f"比较配置时发生错误: {str(e)}")
            # 如果发生错误，默认认为有更改
            return True
    
    def closeEvent(self, event):
        """重写窗口关闭事件，添加保存提示"""
        # 检查配置是否有更改
        if self.config_has_changes():
            reply = QMessageBox.question(self, "确认", "是否保存当前文件？", 
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            
            if reply == QMessageBox.Cancel:
                # 取消关闭
                event.ignore()
                logger.info("用户取消了关闭窗口操作")
            elif reply == QMessageBox.Yes:
                # 保存文件
                if not self.save_file():
                    # 保存失败，取消关闭
                    event.ignore()
                    logger.warning("保存文件失败，取消关闭窗口操作")
            # 如果是No，则继续关闭
        
        # 如果没有更改或用户选择不保存，则接受关闭事件
        if not event.isAccepted():
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = APICoreEditor()
    editor.show()
    sys.exit(app.exec_())