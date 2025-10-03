<div align="center">

<image src="https://github.com/user-attachments/assets/a39e8058-020b-4346-ac07-3f14a4c311f7" height="86"/>

# APICORE_Editor

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Python版本](https://img.shields.io/badge/Python-3.8%2B-brightgreen)
![版本号](https://img.shields.io/badge/Version-1.0.0-orange)

The graphical configuration file editor for APICORE

#### [Main Repo](https://github.com/SRON-org/APICORE)

</div>

## 介绍

APICORE_Editor 一个使用PyQt5开发的图形化 APICORE 配置文件编辑器，用于创建和编辑符合 APICORE 规范的API配置文件。

## 功能特性

- **基本配置编辑**：编辑API接口名称、简介、图标URL或base64、链接、请求方法等基本信息
- **参数配置管理**：支持添加、编辑、删除各种类型的参数（integer、boolean、list、string、enum）
- **响应配置管理**：配置图像提取和其他数据的解析规则
- **配置文件验证**：验证配置文件是否符合APICORE规范
- **文件操作**：新建、打开、保存、另存为配置文件
- **状态栏帮助**：在操作过程中提供实时的状态栏提示信息
- **智能保存提示**：新建、打开新文件和关闭窗口时自动检测配置是否有更改并提示保存
- **美观的界面**：现代化css样式表

## 安装依赖

编辑器使用Python和PyQt5开发，请确保已安装这些依赖：

### 方法1：使用requirements.txt安装

```bash
pip install -r requirements.txt
```

### 方法2：手动安装

```bash
pip install PyQt5>=5.15.0
pip install Pillow>=8.0.0
pip install numpy>=1.20.0
pip install scipy>=1.6.0
```

## 使用方法

1. 运行编辑器：

```bash
python apicore_editor.py
```

2. 在编辑器中编辑 APICORE 配置文件：
   - **基本配置**标签页：填写API的基本信息
   - **参数配置**标签页：添加和管理API的请求参数
   - **响应配置**标签页：配置API响应的解析规则
   
3. 使用图片转换工具：
   - 在基本配置标签页中，点击"转换图片"按钮可以打开图片转换工具
   - 该工具可以将普通图片转换为SVG或Base64格式，方便在API配置中使用

4. 保存配置文件：
   - 点击菜单栏的"文件" -> "保存"或"另存为"
   - 建议使用`.api.json`作为文件扩展名

5. 验证配置文件：
   - 点击菜单栏的"文件" -> "验证配置"
   - 编辑器会检查配置是否符合APICORE规范并显示结果

## 注意事项

- 带`(*)`标记的字段为必需字段
- 参数类型为`enum`时，`enable`字段无效
- 使用`验证配置`功能可以检查配置文件是否符合规范
- 保存文件时建议使用`.api.json`扩展名
- 状态栏会显示当前操作的提示信息，帮助您了解操作状态
- 关闭窗口时，如果配置有更改，系统会提示您是否保存当前文件

## 示例

编辑器内置了符合APICORE规范的配置文件示例，您可以通过"新建"文件并填写相关信息来创建自己的配置文件。

## 关于 APICORE 配置规范

APICORE 是一个统一的API配置解决方案，通过声明式配置文件实现：

- **广泛兼容性**：APICORE规范自身具有强大的可扩展性，无论是各种参数或响应格式都可以轻松兼容
- **简明易读性**：APICORE的标准参数关键词均为日常生活中的通俗用语，简单易懂
- **描述标准化**：APICORE专注于解决多个应用程序之间API配置管理中的碎片化问题

### 配置文件结构

APICORE配置文件为JSON格式，包含以下主要部分：

```json
{
    "friendly_name": "", // API接口名称
    "intro": "", // API接口简介
    "icon": "", // API接口图标URL
    "link": "", // API接口链接
    "func": "", // HTTP请求方法
    "APICORE_version": "1.0", // APICORE版本
    "parameters": [], // API请求参数配置列表
    "response": {} // API响应解析配置
}
```

更多详细的配置说明，请参考 [APICORE.wiki](https://github.com/SRON-org/APICORE/wiki) 文件夹下的文档。

## 关于 APICORE

APICORE 是由 [SRON团队](https://github.com/SRON-org) 研发的统一API配置解决方案，更多信息请查看 [Main Repo](https://github.com/SRON-org/APICORE)
