import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Qt

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(300, 300)
        self.setMouseTracking(True)
        self.cen = QWidget()
        self.cen.setMouseTracking(True)
        self.setCentralWidget(self.cen)

    def get_edge(self, pos):
        border = 10
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        
        edges = Qt.Edges()
        if x < border: edges |= Qt.LeftEdge
        if x > w - border: edges |= Qt.RightEdge
        if y < border: edges |= Qt.TopEdge
        if y > h - border: edges |= Qt.BottomEdge
        return edges

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edges = self.get_edge(event.pos())
            if edges:
                self.windowHandle().startSystemResize(edges)
            else:
                self.windowHandle().startSystemMove()

    def mouseMoveEvent(self, event):
        edges = self.get_edge(event.pos())
        if edges == (Qt.TopEdge | Qt.LeftEdge) or edges == (Qt.BottomEdge | Qt.RightEdge):
            self.setCursor(Qt.SizeFDiagCursor)
        elif edges == (Qt.TopEdge | Qt.RightEdge) or edges == (Qt.BottomEdge | Qt.LeftEdge):
            self.setCursor(Qt.SizeBDiagCursor)
        elif edges in (Qt.TopEdge, Qt.BottomEdge):
            self.setCursor(Qt.SizeVerCursor)
        elif edges in (Qt.LeftEdge, Qt.RightEdge):
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

app = QApplication(sys.argv)
w = TestWindow()
w.show()
# sys.exit(app.exec())
print("OK")
