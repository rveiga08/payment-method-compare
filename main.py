import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QFileDialog
)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class PaymentComparisonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comparador de Pagamento vs CDB")
        self.setGeometry(100, 100, 800, 600)

        self.setup_ui()
        self.history = []

    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        # Widgets de entrada
        self.avista_label = QLabel("Valor do Produto à Vista:")
        self.avista_input = QLineEdit()
        self.avista_input.setPlaceholderText("Ex: 1500.50")
        self.total_label = QLabel("Valor Total da Compra Parcelada:")
        self.total_input = QLineEdit()
        self.total_input.setPlaceholderText("Ex: 1800.75")
        self.parcelas_label = QLabel("Número de Parcelas:")
        self.parcelas_input = QLineEdit()
        self.parcelas_input.setPlaceholderText("Ex: 12")
        self.valor_parcela_label = QLabel("Valor de Cada Parcela:")
        self.valor_parcela_input = QLineEdit()
        self.valor_parcela_input.setPlaceholderText("Ex: 150.06")

        self.compare_button = QPushButton("Comparar")
        self.compare_button.clicked.connect(self.compare_payments)

        # Adicionar entradas ao layout
        input_layout.addWidget(self.avista_label)
        input_layout.addWidget(self.avista_input)
        input_layout.addWidget(self.total_label)
        input_layout.addWidget(self.total_input)
        input_layout.addWidget(self.parcelas_label)
        input_layout.addWidget(self.parcelas_input)
        input_layout.addWidget(self.valor_parcela_label)
        input_layout.addWidget(self.valor_parcela_input)
        input_layout.addWidget(self.compare_button)

        # Tabela de histórico
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Valor à Vista", "Valor Total Parcelado", "Parcelas", "Rendimento CDB", "Melhor Opção"
        ])

        # Gráficos
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(["Linha", "Coluna"])
        self.chart_combo.currentIndexChanged.connect(self.update_chart)

        self.chart_view = QLabel("Gráfico será exibido aqui")
        self.chart_view.setAlignment(Qt.AlignCenter)

        # Botões adicionais
        self.export_button = QPushButton("Exportar Histórico")
        self.export_button.clicked.connect(self.export_history)

        # Montar layout principal
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.history_table)
        main_layout.addWidget(self.chart_combo)
        main_layout.addWidget(self.chart_view)
        main_layout.addWidget(self.export_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def compare_payments(self):
        try:
            avista = float(self.avista_input.text().replace(",", "."))
            total = float(self.total_input.text().replace(",", "."))
            parcelas = int(self.parcelas_input.text())
            valor_parcela = float(self.valor_parcela_input.text().replace(",", "."))

            # Simular rendimento do CDB
            cdb_yield = self.get_cdb_yield()
            rendimento_cdb = [avista * ((1 + cdb_yield) ** i) - avista for i in range(1, parcelas + 1)]

            total_parcelado = valor_parcela * parcelas

            melhor_opcao = "À Vista" if avista + rendimento_cdb[-1] <= total_parcelado else "Parcelado"

            # Atualizar histórico
            self.history.append((avista, total, parcelas, cdb_yield, melhor_opcao))
            self.update_history_table()
            self.update_chart()
        except ValueError:
            self.chart_view.setText("Por favor, insira valores válidos.")

    def get_cdb_yield(self):
        try:
            # Substituir por chamada real a API financeira
            return 0.012  # Simulação de rendimento mensal de 1.2%
        except requests.RequestException:
            self.chart_view.setText("Erro ao obter rendimento do CDB.")
            return 0

    def update_history_table(self):
        self.history_table.setRowCount(len(self.history))
        for row, (avista, total, parcelas, cdb_yield, melhor_opcao) in enumerate(self.history):
            self.history_table.setItem(row, 0, QTableWidgetItem(f"R$ {avista:.2f}"))
            self.history_table.setItem(row, 1, QTableWidgetItem(f"R$ {total:.2f}"))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{parcelas}"))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{cdb_yield * 100:.2f}%"))
            self.history_table.setItem(row, 4, QTableWidgetItem(melhor_opcao))

    def update_chart(self):
        chart_type = self.chart_combo.currentText()

        if not self.history:
            self.chart_view.setText("Nenhum dado disponível para gerar gráfico.")
            return

        parcelas = self.history[-1][2]
        labels = [f"Mês {i+1}" for i in range(parcelas)]
        rendimento_cdb = [
            self.history[-1][0] * ((1 + self.history[-1][3]) ** i) - self.history[-1][0]
            for i in range(1, parcelas + 1)
        ]

        plt.figure()
        if chart_type == "Linha":
            plt.plot(labels, rendimento_cdb, marker='o')
            plt.title("Rendimento ao longo dos meses")
            plt.xlabel("Meses")
            plt.ylabel("Rendimento (R$)")
        elif chart_type == "Coluna":
            plt.bar(labels, rendimento_cdb)
            plt.title("Rendimento ao longo dos meses")
            plt.xlabel("Meses")
            plt.ylabel("Rendimento (R$)")

        plt.tight_layout()
        canvas = FigureCanvas(plt.gcf())
        self.chart_view.setPixmap(canvas.grab())

    def export_history(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Histórico", "", "CSV Files (*.csv)")
        if not path:
            return

        try:
            with open(path, "w") as file:
                file.write("Valor à Vista,Valor Total Parcelado,Parcelas,Rendimento CDB,Melhor Opção\n")
                for avista, total, parcelas, cdb_yield, melhor_opcao in self.history:
                    file.write(f"{avista},{total},{parcelas},{cdb_yield * 100:.2f},{melhor_opcao}\n")
        except Exception as e:
            self.chart_view.setText(f"Erro ao salvar histórico: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaymentComparisonApp()
    window.show()
    sys.exit(app.exec_())
