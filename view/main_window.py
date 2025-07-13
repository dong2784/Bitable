import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QApplication, QButtonGroup, QPushButton
from PySide6.QtUiTools import QUiLoader


class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        ui_loader = QUiLoader()
        self._main_widget = ui_loader.load("view/ui/main_window.ui")
        self.setCentralWidget(self._main_widget)

        self.setWindowTitle(f"Bitable - {version}")
        self.setWindowIcon(QIcon('view/icon/main.png'))
        self._value = 0

        self._pb_bit_group = QButtonGroup(self)
        self._pb_bit_group.setExclusive(False)
        self._prepare_button_group()

        self._connect()

        self._refreshing = False

    @classmethod
    def exec(cls, version):
        app = QApplication()
        inst = cls(version)
        inst.show()
        sys.exit(app.exec())

    def _prepare_button_group(self):
        for i in range(64):
            obj = self._main_widget.findChild(QPushButton, f"pb_bit_{i}")
            if isinstance(obj, QPushButton):
                self._pb_bit_group.addButton(obj, i)

    def _connect(self):
        mw = self._main_widget
        mw.le_value_hex.textChanged.connect(lambda text: self._on_le_value_changed(text, 16))
        mw.le_value_dec.textChanged.connect(lambda text: self._on_le_value_changed(text, 10))
        mw.le_value_oct.textChanged.connect(lambda text: self._on_le_value_changed(text, 8))
        mw.le_value_bin.textChanged.connect(lambda text: self._on_le_value_changed(text, 2))
        mw.le_calculate.returnPressed.connect(self._on_calculate)
        mw.pb_clear_calculate.clicked.connect(mw.tb_calculate.clear)
        mw.pb_op_all_0.clicked.connect(lambda: self._set_value(0))
        mw.pb_op_all_1.clicked.connect(lambda: self._set_value(0xFFFF_FFFF_FFFF_FFFF))
        mw.pb_op_all_r.clicked.connect(self._set_all_r)
        mw.pb_op_range_extract.clicked.connect(self._extract_range)
        mw.pb_op_range_0.clicked.connect(self._set_range_0)
        mw.pb_op_range_1.clicked.connect(self._set_range_1)
        mw.pb_op_range_r.clicked.connect(self._set_range_r)
        mw.pb_op_left_shift.clicked.connect(self._left_shift)
        mw.pb_op_right_shift.clicked.connect(self._right_shift)
        self._pb_bit_group.idToggled.connect(self._on_pb_bit_toggled)

    def _refresh(self):
        if self._refreshing:
            return

        self._refreshing = True

        mw = self._main_widget
        mw.le_value_hex.blockSignals(True)
        mw.le_value_hex.setText(f"{self._value:X}")
        mw.le_value_hex.blockSignals(False)

        mw.le_value_dec.blockSignals(True)
        mw.le_value_dec.setText(f"{self._value}")
        mw.le_value_dec.blockSignals(False)

        mw.le_value_oct.blockSignals(True)
        mw.le_value_oct.setText(f"{self._value:o}")
        mw.le_value_oct.blockSignals(False)

        mw.le_value_bin.blockSignals(True)
        mw.le_value_bin.setText(f"{self._value:b}")
        mw.le_value_bin.blockSignals(False)

        for i in range(64):
            button = self._pb_bit_group.button(i)
            checked = (((self._value >> i) & 1) == 1)
            val = "0"
            if checked:
                val = "1"
            button.setText(val)
            button.setChecked(checked)

        self._refreshing = False

    def _on_pb_bit_toggled(self, id, checked):
        if checked:
            val = '1'
            self._value |= (1 << id)
        else:
            val = '0'
            self._value &= (~(1 << id))

        self._pb_bit_group.button(id).setText(val)
        self._refresh()

    def _on_le_value_changed(self, text, base):
        try:
            self._set_value(int(text, base))
            self._refresh()
        except:
            pass

    def _on_calculate(self):
        mw = self._main_widget
        content = mw.le_calculate.text().strip()
        mw.tb_calculate.append(f"<<< {content}")
        try:
            v = eval(content)
            mw.tb_calculate.append(f">>> {v}")
            self._set_value(int(v) & 0xFFFF_FFFF_FFFF_FFFF)
        except Exception as e:
            mw.tb_calculate.append(f">>> syntax error {e}")

    def _set_value(self, value:int):
        self._value = value & 0xFFFF_FFFF_FFFF_FFFF
        self._refresh()

    def _get_range(self):
        mw = self._main_widget
        low = mw.sb_op_range_low.value()
        high = mw.sb_op_range_high.value()
        if low > high:
            low, high = high, low
        return low, high

    def _get_range_mask(self, low, high):
        mask = 0
        for _ in range(high - low + 1):
            mask <<= 1
            mask |= 1
        mask <<= low
        return mask

    def _set_all_r(self):
        mask = self._get_range_mask(0, 63)
        self._set_value(self._value ^ mask)

    def _extract_range(self):
        low, high = self._get_range()
        mask = self._get_range_mask(low, high)
        self._set_value((self._value & mask) >> low)

    def _set_range_0(self, val):
        low, high = self._get_range()
        mask = self._get_range_mask(low, high)
        self._set_value((self._value & (~mask)))

    def _set_range_1(self, val):
        low, high = self._get_range()
        mask = self._get_range_mask(low, high)
        self._set_value((self._value | mask))

    def _set_range_r(self):
        low, high = self._get_range()
        mask = self._get_range_mask(low, high)
        self._set_value(self._value ^ mask)

    def _left_shift(self):
        self._set_value(self._value << self._main_widget.sb_op_shift_val.value())

    def _right_shift(self):
        self._set_value(self._value >> self._main_widget.sb_op_shift_val.value())
