"""
安卓版桌面计算器 —— Kivy 实现
与桌面版（Tkinter）计算逻辑完全一致，仅重写了界面层。

构建 APK：在装有 buildozer 的 Linux 环境中执行  buildozer android debug
"""

import re

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex

# ---------- 颜色主题（与桌面版一致） ----------
BG = get_color_from_hex("#ffffff")
FG = get_color_from_hex("#222222")
HIST = get_color_from_hex("#9a9a9a")
BTN_NUM = get_color_from_hex("#f2f3f5")
BTN_OP = get_color_from_hex("#ffb84d")
BTN_FN = get_color_from_hex("#e3e6e8")
BTN_EQ = get_color_from_hex("#3a8ee6")
COLORS = {"num": BTN_NUM, "op": BTN_OP, "fn": BTN_FN, "eq": BTN_EQ}

# 按钮布局：5 行 × 4 列
LAYOUT = [
    ("C", "fn"), ("⌫", "fn"), ("%", "fn"), ("÷", "op"),
    ("7", "num"), ("8", "num"), ("9", "num"), ("×", "op"),
    ("4", "num"), ("5", "num"), ("6", "num"), ("−", "op"),
    ("1", "num"), ("2", "num"), ("3", "num"), ("+", "op"),
    ("±", "fn"), ("0", "num"), (".", "num"), ("=", "eq"),
]


def display_label(text, font_size, color, height):
    """右侧对齐的显示标签（Kivy 需要 text_size 才能生效 halign）"""
    lbl = Label(text=text, halign="right", valign="middle",
                font_size=font_size, bold=True, color=color,
                size_hint_y=None, height=height)
    lbl.bind(size=lambda *_a: setattr(lbl, "text_size", (lbl.width, None)))
    return lbl


class CalculatorBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [12, 12]
        self.spacing = 10

        self.expression = ""          # 当前输入的表达式（内部统一 + - * /）
        self.just_calculated = False  # 刚算出结果，再输数字时清空重来

        # 显示区（上）
        display_box = BoxLayout(orientation="vertical", size_hint=(1, 0.34))
        self.history_label = display_label("", "18sp", HIST, 40)
        self.display_label = display_label("0", "56sp", FG, 140)
        display_box.add_widget(self.history_label)
        display_box.add_widget(self.display_label)
        self.add_widget(display_box)

        # 按钮区（下）
        grid = GridLayout(cols=4, spacing=8, size_hint=(1, 0.66))
        for text, kind in LAYOUT:
            is_eq = kind == "eq"
            btn = Button(
                text=text, font_size="26sp", bold=True,
                background_color=COLORS[kind], background_normal="",
                color=(1, 1, 1, 1) if is_eq else FG,
                on_release=lambda _b, t=text: self.press(t),
            )
            grid.add_widget(btn)
        self.add_widget(grid)

    # ---------- 按键分发 ----------
    def press(self, key):
        if key in "0123456789":
            self._append(key)
        elif key == ".":
            self._append_dot()
        elif key in ("+", "−", "×", "÷"):
            self._append_operator({"+": "+", "−": "-", "×": "*", "÷": "/"}[key])
        elif key == "%":
            self._percent()
        elif key == "±":
            self._toggle_sign()
        elif key == "C":
            self._clear()
        elif key == "⌫":
            self._backspace()
        elif key == "=":
            self._calculate()

    # ---------- 具体操作（与桌面版相同） ----------
    def _append(self, digit):
        if self.just_calculated:
            self.expression = ""
            self.just_calculated = False
        self.expression += digit
        self._refresh()

    def _append_dot(self):
        if self.just_calculated:
            self.expression = ""
            self.just_calculated = False
        last_num = re.search(r"(\d+(\.\d*)?)$", self.expression)
        if last_num and "." in last_num.group(1):
            return
        if not self.expression or self.expression[-1] in "+-*/":
            self.expression += "0."
        else:
            self.expression += "."
        self._refresh()

    def _append_operator(self, op):
        self.just_calculated = False
        if not self.expression:
            if op == "-":
                self.expression = "-"
            return
        if self.expression[-1] in "+-*/":
            self.expression = self.expression[:-1] + op
        else:
            self.expression += op
        self._refresh()

    def _percent(self):
        self.expression = re.sub(
            r"(\d+(?:\.\d+)?)$",
            lambda m: f"({float(m.group(1)) / 100})",
            self.expression,
        )
        self._refresh()

    def _toggle_sign(self):
        if re.fullmatch(r"-?\d+(\.\d+)?", self.expression):
            self.expression = (
                self.expression[1:] if self.expression.startswith("-")
                else "-" + self.expression
            )
            self._refresh()

    def _clear(self):
        self.expression = ""
        self.just_calculated = False
        self.history_label.text = ""
        self.display_label.text = "0"

    def _backspace(self):
        self.expression = self.expression[:-1]
        self.just_calculated = False
        self._refresh()

    def _calculate(self):
        if not self.expression:
            return
        try:
            result = self._safe_eval(self.expression)
            result = self._clean_number(result)
            self.history_label.text = (
                self.expression.replace("*", "×").replace("/", "÷")
                .replace("-", "−") + " ="
            )
            self.display_label.text = str(result)
            self.expression = str(result)
            self.just_calculated = True
        except ZeroDivisionError:
            self.display_label.text = "除数不能为 0"
            self.expression = ""
            self.just_calculated = True
        except Exception:
            self.display_label.text = "表达式错误"
            self.expression = ""
            self.just_calculated = True

    def _safe_eval(self, expr):
        if not re.fullmatch(r"[0-9+\-*/().% ]+", expr):
            raise ValueError("非法表达式")
        return eval(expr, {"__builtins__": {}}, {})

    @staticmethod
    def _clean_number(num):
        if isinstance(num, float):
            num = round(num, 10)
            if num.is_integer():
                return int(num)
        return num

    def _refresh(self):
        shown = self.expression.replace("*", "×").replace("/", "÷").replace("-", "−")
        self.history_label.text = shown
        self.display_label.text = shown if shown else "0"


class CalculatorApp(App):
    title = "桌面计算器"

    def build(self):
        Window.clearcolor = BG
        return CalculatorBox()


if __name__ == "__main__":
    CalculatorApp().run()
#（注：内容由AI生成）
