# ui/main_window.py
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MainWindow(tk.Tk):
    def __init__(self, controller, figure):
        super().__init__()
        self.controller = controller
        self.title("Chromatogram Professional Viewer")
        self.protocol("WM_DELETE_WINDOW", self.controller.on_close)
        
        self.canvas = FigureCanvasTkAgg(figure, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
    def redraw_canvas(self) -> None:
        self.canvas.draw_idle()