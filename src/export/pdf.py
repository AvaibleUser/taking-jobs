import tempfile
from tkinter import filedialog, messagebox

from fpdf import FPDF
from matplotlib import pyplot as plt


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Reporte de Horarios Generados', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def export_pdf(self, classrooms, periods, data, reports):
        self.classrooms = classrooms
        self.periods = periods
        self.data = data
        self.reports = reports

        pdf = PDF(orientation='L')
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        title_style = {'family': 'Arial', 'style': 'B', 'size': 12}

        pdf.set_font(**title_style)
        pdf.cell(0, 10, 'Distribución de Horarios', 0, 1)

        col_widths = [30] + [40 for _ in self.classrooms]

        pdf.set_fill_color(200, 220, 255)
        columns = ["Hora"] + self.classrooms
        for i, col in enumerate(columns):
            pdf.cell(col_widths[i], 10, col, border=1, align='C')
        pdf.ln()

        pdf.set_fill_color(255, 255, 255)
        for i, period in enumerate(self.periods):
            pdf.multi_cell(col_widths[0], 10, period, border=1, align='C')
            for j, cl in enumerate(self.classrooms):
                pdf.multi_cell(
                    col_widths[j], 10, self.data[i + 1][cl], border=1, align='C')
            pdf.ln()

        pdf.add_page()
        self._agregar_grafica_pdf(pdf, self.reports.conflicts_per_generation,
                                  "Evolución de Conflictos por Generación")
        self._agregar_grafica_pdf(pdf, self.reports.avg_fitnesses,
                                  "Evolución de la Aptitud Promedio")

        pdf.add_page()
        pdf.set_font(**title_style)
        pdf.cell(0, 10, 'Métricas Generales', 0, 1)

        parsed_data = [
            ("Tiempo ejecución promedio:",
             f"{self.reports.avg_durations:.2f} s"),
            ("Tiempo total ejecución:",
             f"{self.reports.total_duration:.2f} s"),
            ("Generaciones totales:", str(self.reports.total_generations)),
            ("Cursos continuos:",
             f"{self.reports.consecutive_courses_percent:.2f}%"),
            ("Memoria usada:",
             f"{self.reports.memory_consumption / 1024 / 1024:.2f} MB")
        ]

        pdf.set_font('Arial', size=10)
        for titulo, valor in parsed_data:
            pdf.cell(100, 10, titulo, border=0)
            pdf.cell(0, 10, valor, border=0)
            pdf.ln()

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="reporte.pdf"
        )
        if filepath:
            pdf.output(filepath)
            messagebox.showinfo("Éxito", "PDF exportado correctamente")

    def _agregar_grafica_pdf(self, pdf, datos, titulo):
        fig = plt.figure(figsize=(12, 4))
        ax = fig.add_subplot(111)
        ax.plot(datos)
        ax.set_xlabel("Generación")
        ax.set_ylabel("Valor")
        ax.set_title(titulo)

        with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, dpi=150, bbox_inches='tight')
            plt.close(fig)

            pdf.image(tmpfile.name, x=10, w=pdf.w - 20)
            pdf.ln(10)
