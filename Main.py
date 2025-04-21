import customtkinter as ctk
from sympy import symbols, Eq, Function, rsolve, latex, Rational
import matplotlib.pyplot as plt
from PIL import Image
from customtkinter import CTkImage
import io
import threading

def generar_formula_imagen(expresion_latex):
    fig, ax = plt.subplots(figsize=(10, 2.5))  
    ax.axis("off")
    ax.text(0.5, 0.5, f"${expresion_latex}$", fontsize=32, ha='center', va='center')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300, transparent=True)
    plt.close(fig)
    buffer.seek(0)
    image = Image.open(buffer)
    image = image.resize((1000, 250), Image.Resampling.LANCZOS)  
    return CTkImage(dark_image=image, light_image=image, size=(1000, 250))

class StartView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        ctk.CTkLabel(self, text="Proyecto de Recurrencias", font=("Arial", 24)).pack(pady=40)
        ctk.CTkButton(self, text="Iniciar", command=self.controller.show_second_view).pack()

class SecondView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        ctk.CTkLabel(self, text="Expresión Cerrada de la Recurrencia", font=("Arial", 20)).pack(pady=10)

        self.m_entry = ctk.CTkEntry(self, placeholder_text="Valor de m")
        self.m_entry.pack(pady=5)

        self.coef_entry = ctk.CTkEntry(self, placeholder_text="Coeficientes ai separados por comas")
        self.coef_entry.pack(pady=5)

        self.init_entry = ctk.CTkEntry(self, placeholder_text="Valores iniciales Ci separados por comas")
        self.init_entry.pack(pady=5)

        ctk.CTkButton(self, text="Obtener expresión", command=self.calcular_expresion).pack(pady=10)

        self.imagen_label = ctk.CTkLabel(self, text="", width=1000, height=250)
        self.imagen_label.pack(pady=15)

        ctk.CTkButton(self, text="Volver", command=self.controller.show_start_view).pack(pady=10)

    def calcular_expresion(self):
        self.imagen_label.configure(text="Calculando expresión...", image=None)
        self.after(100, self._start_thread)

    def _start_thread(self):
        threading.Thread(target=self._resolver_recurrencia, daemon=True).start()

    def _resolver_recurrencia(self):
        try:
            m = int(self.m_entry.get())
            coef = [Rational(x) for x in self.coef_entry.get().split(",")]
            init_vals = [Rational(x) for x in self.init_entry.get().split(",")]

            if len(coef) != m or len(init_vals) != m:
                self._update_ui_error("Error: número de coeficientes o valores iniciales incorrecto.")
                return

            n = symbols('n', integer=True)
            f = Function('f')
            recurrence = Eq(f(n), sum(coef[i] * f(n - i - 1) for i in range(m)))
            initial_conditions = {f(i): init_vals[i] for i in range(m)}

            solution = rsolve(recurrence, f(n), initial_conditions)

            if solution is None:
                self._update_ui_error("No se pudo encontrar una solución cerrada.")
                return

            latex_expr = "f_n = " + latex(solution)
            imagen = generar_formula_imagen(latex_expr)

            self.imagen_label.after(0, lambda: self._update_ui_image(imagen))

        except Exception as e:
            self._update_ui_error(f"Error: {e}")

    def _update_ui_image(self, imagen):
        self.imagen_label.configure(image=imagen, text="")
        self.imagen_label.image = imagen

    def _update_ui_error(self, mensaje):
        self.imagen_label.after(0, lambda: self.imagen_label.configure(text=mensaje, image=None))

class AppController(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("App MVC - Recurrencias")
        self.geometry("1100x650")

        self.start_view = StartView(self, self)
        self.second_view = SecondView(self, self)

        self.show_start_view()

    def show_start_view(self):
        self.second_view.pack_forget()
        self.start_view.pack(expand=True, fill="both")

    def show_second_view(self):
        self.start_view.pack_forget()
        self.second_view.pack(expand=True, fill="both")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = AppController()
    app.mainloop()
