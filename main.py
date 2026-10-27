"""ماشین‌حساب ساده چهار عمل اصلی (+ − × ÷) ساخته‌شده با Kivy.

اجرا روی کامپیوتر:  python main.py
روی اندروید: خروجی buildozer (فایل APK).
"""

from functools import partial

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex

from calculator import CalculatorLogic, format_number

Window.clearcolor = get_color_from_hex("#14141B")

BG_BUTTON = "#26262F"
BG_OPERATOR = "#FF9F0A"
BG_CLEAR = "#FF453A"
BG_EQUALS = "#30D158"
FG_WHITE = "#FFFFFF"
FG_DARK = "#1B1B22"

# سطرهای صفحه‌کلید ۴ ستونه (بدون دکمه = ؛ آن یک سطر جدا و پهن دارد)
KEYPAD = [
    ["7", "8", "9", "÷"],
    ["4", "5", "6", "×"],
    ["1", "2", "3", "-"],
    ["C", "0", ".", "+"],
]

KEY_COLOR = {
    "÷": (BG_OPERATOR, FG_DARK),
    "×": (BG_OPERATOR, FG_DARK),
    "-": (BG_OPERATOR, FG_DARK),
    "+": (BG_OPERATOR, FG_DARK),
    "C": (BG_CLEAR, FG_WHITE),
    "=": (BG_EQUALS, FG_DARK),
}


class CalcButton(Button):
    """دکمه‌ی گرد با پس‌زمینه‌ی رسم‌شده روی canvas و فونت متناسب با ارتفاع."""

    def __init__(self, text, **kwargs):
        self._bg_hex = kwargs.pop("bg_color", BG_BUTTON)
        fg_hex = kwargs.pop("fg_color", FG_WHITE)
        super().__init__(text=text, bold=True, **kwargs)
        self.color = get_color_from_hex(fg_hex)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.font_size = sp(26)
        with self.canvas.before:
            self._bg_instr = Color(*get_color_from_hex(self._bg_hex))
            self._rect = RoundedRectangle(radius=[dp(16)])
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(size=self._adapt_font)
        self.bind(state=self._update_state)

    def _update_canvas(self, *_args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _adapt_font(self, _widget, height):
        self.font_size = max(sp(18), height * 0.38)

    def _update_state(self, _widget, state):
        factor = 0.65 if state == "down" else 1.0
        self._bg_instr.rgba = [c * factor for c in get_color_from_hex(self._bg_hex)]


class DisplayPanel(BoxLayout):
    """نمایشگر: سطر کوچکِ عبارت در انتظار + سطر بزرگِ عدد جاری."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=[dp(14), dp(6)], **kwargs)
        self.expression = Label(
            halign="right", valign="bottom",
            font_size=sp(18), color=(1, 1, 1, 0.55), text="",
        )
        self.value = Label(
            halign="right", valign="top", bold=True,
            font_size=sp(52), color=(1, 1, 1, 1), text="0",
        )
        for label in (self.expression, self.value):
            label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
        self.add_widget(self.expression)
        self.add_widget(self.value)


class CalculatorApp(App):
    title = "Calculator"

    def build(self):
        self.logic = CalculatorLogic()

        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))

        self.panel = DisplayPanel(size_hint_y=0.24)
        root.add_widget(self.panel)

        grid = GridLayout(cols=4, spacing=dp(10), size_hint_y=0.64)
        for row in KEYPAD:
            for symbol in row:
                bg, fg = KEY_COLOR.get(symbol, (BG_BUTTON, FG_WHITE))
                grid.add_widget(
                    CalcButton(symbol, bg_color=bg, fg_color=fg,
                               on_press=partial(self.press, symbol))
                )
        root.add_widget(grid)

        root.add_widget(
            CalcButton("=", bg_color=BG_EQUALS, fg_color=FG_DARK,
                       size_hint_y=0.12, on_press=partial(self.press, "="))
        )

        Window.bind(on_key_down=self._on_key_down)
        self._refresh()
        return root

    # --- رویدادها ---------------------------------------------------------

    def press(self, symbol, *_args):
        self.logic.press(symbol)
        self._refresh()

    def _on_key_down(self, _window, key, _scancode, codepoint, _modifiers):
        # پشتیبانی از کیبورد برای تست راحت روی کامپیوتر
        char = codepoint if isinstance(codepoint, str) else ""
        if char and char in "0123456789.":
            self.press(char)
        elif char in ("+", "-", "*", "/"):
            self.press({"+": "+", "-": "-", "*": "×", "/": "÷"}[char])
        elif key in (13, 271) or char == "=":
            self.press("=")
        elif key in (8, 127):
            self.logic.backspace()
            self._refresh()
        elif char in ("c", "C"):
            self.press("C")

    def _refresh(self):
        self.panel.value.text = self.logic.display
        if self.logic.pending_op is not None:
            self.panel.expression.text = (
                f"{format_number(self.logic.accumulator)} {self.logic.pending_op}"
            )
        elif self.logic.last_expression and not self.logic.entry_mode:
            self.panel.expression.text = self.logic.last_expression
        else:
            self.panel.expression.text = ""


if __name__ == "__main__":
    CalculatorApp().run()
