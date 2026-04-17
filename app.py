import sys
import os
import subprocess
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QFormLayout,
                             QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit,
                             QComboBox, QInputDialog, QMessageBox, QLabel,QSlider)
class ConfigManager:
    def __init__(self, file_path="./AI.ini"):
        self.file_path = file_path
        self.configs = {}
        self.load_config()
    def load_config(self):
        self.configs.clear()
        if not os.path.exists(self.file_path):
            self.configs = {
                "默认参数": {"path": "llama-server",
                            "model": "",
                            "ngl": "100",
                            "ncmoe": "0",
                            "content": "10240"
            }}
            self.save_all_configs()
            return
        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()
        blocks = content.split("----------")
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.splitlines()
            if not lines:
                continue
            name_line = lines[0].strip()
            if not name_line.startswith("-----") or not name_line.endswith("-----"):
                continue
            config_name = name_line[5:-5].strip()
            params = {"model": "",
                      "path": "",
                      "ngl": "",
                      "ncmoe": "",
                      "content": ""}
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    key, value = parts
                    params[key] = value.strip()
            self.configs[config_name] = params
    def save_all_configs(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            for name, params in self.configs.items():
                f.write(f"-----{name}-----\n")
                f.write(f"model   {params.get('model', '')}\n")
                f.write(f"path   {params.get('path', '')}\n")
                f.write(f"ngl   {params.get('ngl', '')}\n")
                f.write(f"ncmoe   {params.get('ncmoe', '')}\n")
                f.write(f"content   {params.get('content', '')}\n")
                f.write("----------\n\n")
    def add_new_config(self, config_name, params):
        if config_name in self.configs:
            return False
        self.configs[config_name] = params
        self.save_all_configs()
        return True
    def update_current_config(self, old_name, new_name, params):
        if old_name not in self.configs:
            return False
        if old_name != new_name and new_name in self.configs:
            return False
        del self.configs[old_name]
        self.configs[new_name] = params
        self.save_all_configs()
        return True
class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("app.png")) 
        self.setWindowTitle("Llama.cpp启动器")
        self.setFixedSize(300, 400)
        self.config_manager = ConfigManager()
        self.config_list = list(self.config_manager.configs.keys())
        self.current_config = 0
        self.init_ui()
        self.load_ini()
    def init_ui(self):
        window = QWidget()
        self.setCentralWidget(window)
        window.setStyleSheet("background-color: #F8F9FA; border-radius: 12px;")
        main_layout = QVBoxLayout(window)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20,20,20,20)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        self.left_button = QPushButton("◀")
        self.config_label = QPushButton("配置参数")
        self.config_label.setEnabled(False)
        self.right_button = QPushButton("▶")
        button_style = """
        QPushButton {
            background-color: #E9ECEF;
            border-radius: 5px;
            padding: 10px 15px;
            font-size: 12pt;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #DEE2E6;
        }
        """
        self.left_button.setStyleSheet(button_style)
        self.right_button.setStyleSheet(button_style)
        self.config_label.setStyleSheet(button_style)
        top_layout.addWidget(self.left_button)
        top_layout.addWidget(self.config_label,1)
        top_layout.addWidget(self.right_button)
        main_layout.addLayout(top_layout)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        input_style = """
        QLineEdit, QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #DEE2E6;
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 8pt;
            min-height: 10px;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #74C0FC;
            outline: none;
        }
        """
        label_style = "font-size: 10pt; color: #212529; font-weight: 500;"
        path_label = QLabel("启动方式")
        path_label.setStyleSheet(label_style)
        self.edit_path = QComboBox()
        self.edit_path.setStyleSheet(input_style)
        form_layout.addRow(path_label, self.edit_path)
        model_label = QLabel("模型选择")
        model_label.setStyleSheet(label_style)
        self.choose_model = QComboBox()
        self.choose_model.setStyleSheet(input_style)
        form_layout.addRow(model_label, self.choose_model)
        slider_style="""
            QSlider::groove:horizontal {
                background: #DEE2E6;
                height: 5px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #74C0FC;
                width: 12px;
                height: 8px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #4DABF7;
            }
        """
        ngl_label = QLabel("GPU卸载")
        ngl_label.setStyleSheet(label_style)
        self.edit_ngl = QLineEdit()
        self.edit_ngl.setStyleSheet(input_style)
        self.edit_ngl.setPlaceholderText("0-100")
        self.slider_ngl = QSlider(Qt.Horizontal)
        self.slider_ngl.setRange(0, 100)
        self.slider_ngl.setFixedWidth(130)
        self.slider_ngl.setStyleSheet(slider_style)
        slider_ngl_layout = QHBoxLayout()
        slider_ngl_layout.addWidget(self.slider_ngl)
        slider_ngl_layout.addWidget(self.edit_ngl)
        form_layout.addRow(ngl_label, slider_ngl_layout)
        self.slider_ngl.valueChanged.connect(
            lambda val: self.edit_ngl.setText(str(val))
        )
        self.edit_ngl.textChanged.connect(
            lambda text: self.slider_ngl.setValue(int(text)) if text.isdigit() else None
        )
        ncmoe_label = QLabel("CPU卸载")
        ncmoe_label.setStyleSheet(label_style)
        self.edit_ncmoe = QLineEdit()
        self.edit_ncmoe.setStyleSheet(input_style)
        self.edit_ncmoe.setPlaceholderText("0-100")
        self.slider_ncmoe = QSlider(Qt.Horizontal)
        self.slider_ncmoe.setRange(0, 100)
        self.slider_ncmoe.setFixedWidth(130)
        self.slider_ncmoe.setStyleSheet(slider_style)
        slider_ncmoe_layout = QHBoxLayout()
        slider_ncmoe_layout.addWidget(self.slider_ncmoe)
        slider_ncmoe_layout.addWidget(self.edit_ncmoe)
        form_layout.addRow(ncmoe_label, slider_ncmoe_layout)
        self.slider_ncmoe.valueChanged.connect(
            lambda val: self.edit_ncmoe.setText(str(val))
        )
        self.edit_ncmoe.textChanged.connect(
            lambda text: self.slider_ncmoe.setValue(int(text)) if text.isdigit() else None
        )
        content_label = QLabel("上下文")
        content_label.setStyleSheet(label_style)
        self.edit_content = QLineEdit()
        self.edit_content.setStyleSheet(input_style)
        self.slider_content = QSlider(Qt.Horizontal)
        self.slider_content.setRange(0, 256000)
        self.slider_content.setFixedWidth(130)
        self.slider_content.setStyleSheet(slider_style)
        slider_content_layout = QHBoxLayout()
        slider_content_layout.addWidget(self.slider_content)
        slider_content_layout.addWidget(self.edit_content)
        form_layout.addRow(content_label, slider_content_layout)
        self.slider_content.valueChanged.connect(
            lambda val: self.edit_content.setText(str(val))
        )
        self.edit_content.textChanged.connect(
            lambda text: self.slider_content.setValue(int(text)) if text.isdigit() else None
        )
        main_layout.addLayout(form_layout)
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(30)
        self.save_button = QPushButton("保存")
        self.start_button = QPushButton("启动")
        sast_button_style = """
        QPushButton {
            background-color: #E9ECEF;
            border-radius: 10px;
            padding: 8px 10px;
            font-size: 10pt;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #DEE2E6;
        }
        """
        self.save_button.setStyleSheet(sast_button_style)
        self.start_button.setStyleSheet(sast_button_style)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.start_button)
        main_layout.addLayout(self.button_layout)
        self.left_button.clicked.connect(self.prev_config)
        self.right_button.clicked.connect(self.next_config)
        self.save_button.clicked.connect(self.save_config)
        self.start_button.clicked.connect(self.start_llama)
    def load_ini(self):
        model_dir = "./model"
        os.makedirs(model_dir, exist_ok=True)
        models = [file for file in os.listdir(model_dir) if file.lower().endswith(".gguf")]
        self.choose_model.addItems(models)
        if not self.config_list:
            return
        config_name = self.config_list[self.current_config]
        self.edit_path.addItems(["llama-cli","llama-server"])
        params = self.config_manager.configs[config_name]
        self.config_label.setText(config_name)
        self.edit_ngl.setText(params.get("ngl", ""))
        self.edit_ncmoe.setText(params.get("ncmoe", ""))
        self.edit_content.setText(params.get("content", ""))
        model_name = params.get("model", "")
        if model_name:
            index = self.choose_model.findText(model_name)
            if index >= 0:
                self.choose_model.setCurrentIndex(index)
            else:
                self.choose_model.setCurrentIndex(-1)
                self.choose_model.clear()
                self.choose_model.addItem("模型未找到或已删除")
        else:
            self.choose_model.setCurrentIndex(0)
        self.edit_path.setEnabled(True)
        self.choose_model.setEnabled(True)
        self.edit_ngl.setReadOnly(False)
        self.edit_ncmoe.setReadOnly(False)
        self.edit_content.setReadOnly(False)
    def prev_config(self):
        if self.current_config > 0:
            self.current_config -= 1
            self.load_ini()
    def next_config(self):
        if self.current_config < len(self.config_list) - 1:
            self.current_config += 1
            self.load_ini()
    def save_config(self):
        current_config_name = self.config_list[self.current_config]
        params = {
            "model": self.choose_model.currentText().strip(),
            "path": self.edit_path.currentText().strip(),
            "ngl": self.edit_ngl.text().strip(),
            "ncmoe": self.edit_ncmoe.text().strip(),
            "content": self.edit_content.text().strip()
        }
        if current_config_name == "默认参数":
            name, ok = QInputDialog.getText(self, "新建配置", "新配置名称")
            if not ok or not name.strip():
                return
            if self.config_manager.add_new_config(name.strip(), params):
                self.config_list = list(self.config_manager.configs.keys())
                QMessageBox.information(self, "成功", f"已新建配置：{name.strip()}")
                self.current_config = self.config_list.index(name.strip())
                self.load_ini()
            else:
                QMessageBox.warning(self, "提示", "该配置名称已存在！")
        else:
            name, ok = QInputDialog.getText(self, "修改配置", "新配置名称",
                                          text=current_config_name)
            if not ok:
                return
            new_name = name.strip() or current_config_name
            if self.config_manager.update_current_config(current_config_name, new_name, params):
                old_index = self.current_config
                self.config_list = list(self.config_manager.configs.keys())
                if new_name in self.config_list:
                    self.current_config = self.config_list.index(new_name)
                else:
                    self.current_config = old_index
                self.load_ini()
                QMessageBox.information(self, "成功", f"配置已更新：{new_name}")
            else:
                QMessageBox.warning(self, "错误", "配置更新失败！可能是新名称已存在。")
    def start_llama(self):
        model = self.choose_model.currentText().strip()
        path = self.edit_path.currentText().strip()
        ngl = self.edit_ngl.text().strip()
        ncmoe = self.edit_ncmoe.text().strip()
        content = self.edit_content.text().strip()
        if not model:
            QMessageBox.warning(self, "错误", "请选择模型文件！")
            return
        cmd = [f".\\main\\{path}"]
        cmd.append(f"-m .\\model\\{model}")
        try:
            if int(ngl) != 0:
                cmd.append(f"-ngl {ngl}")
            if int(ncmoe) != 0:
                cmd.append(f"-ncmoe {ncmoe}")
            if int(content) != 0:
                cmd.append(f"-c {content}")
        except ValueError:
            QMessageBox.warning(self, "错误", "数字参数必须输入有效整数！")
            return
        full_cmd = " ".join(cmd)
        subprocess.Popen(f"start cmd.exe /k {full_cmd}", shell=True)
        self.close()
if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    window = GUI()
    window.show()
    sys.exit(app.exec_())