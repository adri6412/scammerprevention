from PySide6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QLabel,
                                 QComboBox, QLineEdit, QApplication, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtCore import Qt
import os
import json
from src.utils import i18n
from src.ui.settings import SETTINGS_PATH, DATA_DIR

class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.desc_label)

    def initializePage(self):
        self.title_label.setText(i18n.get_text("wizard_welcome_title"))
        self.desc_label.setText(i18n.get_text("wizard_welcome_text"))


class FeaturePage(QWizardPage):
    def __init__(self, title_key, desc_key):
        super().__init__()
        self.title_key = title_key
        self.desc_key = desc_key
        self.layout = QVBoxLayout(self)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #004d99;")
        self.layout.addWidget(self.title_label)

        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 15px; margin-top: 15px;")
        self.layout.addWidget(self.desc_label)

        # Set up opacity effects for animation
        self.title_opacity = QGraphicsOpacityEffect()
        self.title_label.setGraphicsEffect(self.title_opacity)

        self.desc_opacity = QGraphicsOpacityEffect()
        self.desc_label.setGraphicsEffect(self.desc_opacity)

        self.title_anim = QPropertyAnimation(self.title_opacity, b"opacity")
        self.title_anim.setDuration(500)
        self.title_anim.setStartValue(0)
        self.title_anim.setEndValue(1)

        self.desc_anim = QPropertyAnimation(self.desc_opacity, b"opacity")
        self.desc_anim.setDuration(800)
        self.desc_anim.setStartValue(0)
        self.desc_anim.setEndValue(1)

    def initializePage(self):
        self.title_label.setText(i18n.get_text(self.title_key))
        self.desc_label.setText(i18n.get_text(self.desc_key))
        # Reset and start animation
        self.title_opacity.setOpacity(0)
        self.desc_opacity.setOpacity(0)
        self.title_anim.start()
        self.desc_anim.start()

class Feature1Page(FeaturePage):
    def __init__(self):
        super().__init__("wizard_feat1_title", "wizard_feat1_text")

class Feature2Page(FeaturePage):
    def __init__(self):
        super().__init__("wizard_feat2_title", "wizard_feat2_text")

class Feature3Page(FeaturePage):
    def __init__(self):
        super().__init__("wizard_feat3_title", "wizard_feat3_text")

class LanguagePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.desc_label = QLabel()
        self.layout.addWidget(self.desc_label)

        self.combo_lang = QComboBox()
        self.combo_lang.addItem("Italiano", "it")
        self.combo_lang.addItem("English", "en")

        # Set default to currently active language
        index = self.combo_lang.findData(i18n.CURRENT_LANG)
        if index >= 0:
            self.combo_lang.setCurrentIndex(index)

        self.combo_lang.currentIndexChanged.connect(self.on_lang_changed)
        self.layout.addWidget(self.combo_lang)

    def initializePage(self):
        self.title_label.setText(i18n.get_text("wizard_lang_title"))
        self.desc_label.setText(i18n.get_text("wizard_lang_text"))

    def on_lang_changed(self, index):
        code = self.combo_lang.currentData()
        i18n.set_language(code)
        # Re-initialize current page and update wizard title
        self.initializePage()
        self.wizard().setWindowTitle(i18n.get_text("wizard_title"))
        # Force wizard buttons to update
        self.wizard().update_buttons()

class RulesPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.layout.addWidget(self.desc_label)

        self.input_url = QLineEdit()
        self.layout.addWidget(self.input_url)

    def initializePage(self):
        self.title_label.setText(i18n.get_text("wizard_rules_title"))
        self.desc_label.setText(i18n.get_text("wizard_rules_text"))
        self.input_url.setPlaceholderText(i18n.get_text("wizard_rules_placeholder"))

class FinishPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.desc_label)

    def initializePage(self):
        self.title_label.setText(i18n.get_text("wizard_finish_title"))
        self.desc_label.setText(i18n.get_text("wizard_finish_text"))

class SetupWizard(QWizard):
    def __init__(self):
        super().__init__()

        self.setWizardStyle(QWizard.ModernStyle)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.resize(600, 400)

        self.welcome_page = WelcomePage()
        self.feat1_page = Feature1Page()
        self.feat2_page = Feature2Page()
        self.feat3_page = Feature3Page()
        self.lang_page = LanguagePage()
        self.rules_page = RulesPage()
        self.finish_page = FinishPage()

        self.addPage(self.welcome_page)
        self.addPage(self.feat1_page)
        self.addPage(self.feat2_page)
        self.addPage(self.feat3_page)
        self.addPage(self.lang_page)
        self.addPage(self.rules_page)
        self.addPage(self.finish_page)

        self.setWindowTitle(i18n.get_text("wizard_title"))
        self.update_buttons()

    def update_buttons(self):
        self.setButtonText(QWizard.NextButton, i18n.get_text("btn_next"))
        self.setButtonText(QWizard.BackButton, i18n.get_text("btn_back"))
        self.setButtonText(QWizard.FinishButton, i18n.get_text("btn_finish"))

    def accept(self):
        self.save_settings()
        super().accept()

    def save_settings(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        data = {}
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, 'r') as f:
                    data = json.load(f)
            except:
                pass

        data['language'] = self.lang_page.combo_lang.currentData()

        url = self.rules_page.input_url.text().strip()
        if url:
            urls = data.get('update_urls', [])
            if url not in urls:
                urls.append(url)
            data['update_urls'] = urls

        try:
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings during wizard: {e}")
