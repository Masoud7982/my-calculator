"""منطق ماشین‌حساب — کاملاً مستقل از Kivy تا بتوان بدون رابط گرافیکی تستش کرد.

حالت ماشین: یک انباشتگر (accumulator) + یک عملگر در انتظار + عدد در حال تایپ.
ترتیب اجرای عملیات از چپ به راست است (مثل ماشین‌حساب‌های ساده واقعی).
"""

OPERATORS = ("+", "-", "×", "÷")
MAX_ENTRY_LEN = 15


def format_number(value):
    """تبدیل نتیجه به رشته‌ی خوانا: حذف صفرهای انتهایی و گرد کردن خطای اعشار شناور."""
    if value != value or value in (float("inf"), float("-inf")):
        return "Error"
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.10f}".rstrip("0").rstrip(".")


class CalculatorLogic:
    def __init__(self):
        self.reset()

    def reset(self):
        self.display = "0"          # عددی که روی صفحه نمایش داده می‌شود
        self.accumulator = 0.0      # عدد اولِ عملیات در انتظار
        self.pending_op = None      # عملگری که هنوز اعمال نشده
        self.entry_mode = True      # True یعنی کاربر همین حالا دارد عدد تایپ می‌کند
        self.last_expression = ""   # برای نمایش «۱۲ + ۵ =» بعد از دکمه مساوی

    def press(self, key):
        if key == "C":
            self.reset()
        elif key in OPERATORS:
            self._press_operator(key)
        elif key == "=":
            self._press_equals()
        elif key.isdigit():
            self._press_digit(key)
        elif key == ".":
            self._press_dot()

    def backspace(self):
        if self.entry_mode and len(self.display) > 1:
            self.display = self.display[:-1]
        else:
            self.display = "0"
            self.entry_mode = True

    # --- بخش خصوصی -------------------------------------------------------

    def _current_value(self):
        try:
            return float(self.display)
        except ValueError:
            return 0.0

    @staticmethod
    def _apply(op, a, b):
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "×":
            return a * b
        if op == "÷":
            return None if b == 0 else a / b  # تقسیم بر صفر → خطا
        raise ValueError(f"عملگر ناشناخته: {op}")

    def _press_operator(self, op):
        if self.display == "Error":
            return
        if self.pending_op is not None and self.entry_mode:
            result = self._apply(self.pending_op, self.accumulator, self._current_value())
            if result is None:
                self.display = "Error"
                self.pending_op = None
                self.entry_mode = False
                return
            self.accumulator = result
            self.display = format_number(result)
        else:
            self.accumulator = self._current_value()
        self.pending_op = op
        self.entry_mode = False

    def _press_equals(self):
        if self.pending_op is None or self.display == "Error":
            return
        b = self._current_value()
        result = self._apply(self.pending_op, self.accumulator, b)
        if result is None:
            self.display = "Error"
        else:
            self.last_expression = (
                f"{format_number(self.accumulator)} {self.pending_op} {format_number(b)} ="
            )
            self.display = format_number(result)
            self.accumulator = result
        self.pending_op = None
        self.entry_mode = False

    def _press_digit(self, digit):
        if not self.entry_mode or self.display == "Error" or self.display == "0":
            self.display = digit
            self.entry_mode = True
        elif len(self.display) < MAX_ENTRY_LEN:
            self.display += digit

    def _press_dot(self):
        if not self.entry_mode or self.display == "Error":
            self.display = "0."
            self.entry_mode = True
        elif "." not in self.display:
            self.display += "."
