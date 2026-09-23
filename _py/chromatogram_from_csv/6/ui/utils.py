# ui/utils.py
import tkinter as tk

class ToolTip:
    """Класс для создания всплывающих подсказок при наведении на виджет."""
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None) -> None:
        self.schedule()

    def leave(self, event=None) -> None:
        self.unschedule()
        self.hidetip()

    def schedule(self) -> None:
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self) -> None:
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def showtip(self, event=None) -> None:
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", "8", "normal"))
        label.pack(ipadx=3, ipady=1)

    def hidetip(self) -> None:
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()