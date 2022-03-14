from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,QWidget,QCheckBox
import sys

class Window(QMainWindow):
    
    def __init__(self):
        super(Window,self).__init__()
        self.setGeometry(50,50,500,300)
        self.setWindowTitle("StockGUI")
        self.home()
    
    def home(self):
        btn = QPushButton("Graphs",self)
        btn.clicked.connect(self.stocks_page)
        btn.clicked.connect(btn.deleteLater)
        btn.move(0,0)
        btn.resize(100,100)
        self.show()
    
    def stocks_page(self):
        tickers = ['AAPL','MSFT','FB','AMZN','CLOV','ANVS']
        
        print("Entered stock_page")
        pass

def run():
    app = QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

run()