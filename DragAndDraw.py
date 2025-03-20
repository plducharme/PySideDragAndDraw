from abc import ABC, abstractmethod

from PySide6.QtGui import QPixmap, QDrag, QPainter
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QGridLayout
from PySide6.QtCore import Qt, QMimeData, QObject, QTimer
import math


class DragAndDraw(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag and Draw")
        self.canvas_pixmap = QPixmap(800, 800)
        self.libelle_container = Canvas(fenetre_principale=self)
        self.libelle_container.setPixmap(self.canvas_pixmap)
        self.central_widget = QWidget()
        self.disposition_principale = QGridLayout()
        self.disposition_principale.addWidget(self.libelle_container, 0, 0)
        self.panel_objets = QGridLayout()
        self.label_pente = DragItem("Pente")
        self.panel_objets.addWidget(self.label_pente, 0, 0)
        self.label_balle = DragItem("Balle")
        self.panel_objets.addWidget(self.label_balle, 1, 0)
        self.disposition_principale.addLayout(self.panel_objets, 0, 1)
        self.central_widget.setLayout(self.disposition_principale)
        self.setCentralWidget(self.central_widget)
        self.simulation = Simulation(self.libelle_container)
        self.timer = QTimer()
        self.timer.timeout.connect(self.dessiner)
        self.timer.start(100)

    def dessiner(self):
        self.simulation.dessiner()
        self.libelle_container.setPixmap(self.simulation.canvas.pixmap())


class Canvas(QLabel):
    def __init__(self, *args, **kwargs):
        self.fenetre_principale = kwargs.pop("fenetre_principale")
        super().__init__(*args, **kwargs)
        self.setFixedSize(800, 800)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event, /):
        print("dragEnterEvent: canvas")
        event.accept()

    def dragLeaveEvent(self, event, /):
        print("dragLeaveEvent: canvas")
        event.accept()

    def dropEvent(self, event, /):
        widget = event.source()
        print("Drop Event: ", widget.text())
        position_x = int(event.position().x())
        position_y = int(event.position().y())
        print("Drop Position: ", position_x, position_y)
        if widget.text() == "Pente":
            self.fenetre_principale.simulation.objets.append(Pente(position_x, position_y, 45))
        elif widget.text() == "Balle":
            self.fenetre_principale.simulation.objets.append(Balle(position_x, position_y, 25))


class DragItem(QLabel):
    def __init__(self, type_item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(25, 5, 25, 5)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")
        self.setGeometry(0, 0, 100, 50)
        self.setFixedSize(100, 50)
        self.setText(type_item)

    def mouseMoveEvent(self, ev, /):
        if ev.buttons() == Qt.MouseButton.LeftButton:
            mime_data = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.DropAction.MoveAction)
            self.show()


class Simulation:
    def __init__(self, canvas):
        self.canvas = canvas
        self.objets = []

    def dessiner(self):
        pixmap = self.canvas.pixmap()
        pixmap.fill(Qt.GlobalColor.white)
        for objet in self.objets:
            objet.dessiner(pixmap)
        self.canvas.setPixmap(pixmap)


class ObjetGraphique(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @abstractmethod
    def dessiner(self, pixmap):
        pass


class Pente(ObjetGraphique):

    def __init__(self, x, y, pente, longueur=100):
        super().__init__(x, y)
        self.pente = pente
        self.longueur = longueur

    def dessiner(self, pixmap):
        painter = QPainter(pixmap)
        pen = painter.pen()
        pen.setColor(Qt.GlobalColor.blue)
        if self.pente >= 0:
            painter.drawLine(self.x, self.y, self.x + self.longueur * math.cos(math.radians(self.pente)),
                             self.y + self.longueur * math.sin(math.radians(self.pente)))
        else:
            painter.drawLine(self.x, self.y, self.x + self.longueur * math.cos(math.radians(self.pente)),
                             self.y - self.longueur * math.sin(math.radians(self.pente)))
        painter.end()


class Balle(ObjetGraphique):

    def __init__(self, x, y, rayon):
        super().__init__(x, y)
        self.rayon = rayon

    def dessiner(self, pixmap):
        painter = QPainter(pixmap)
        pen = painter.pen()
        pen.setColor(Qt.GlobalColor.blue)
        painter.drawEllipse(self.x, self.y, self.rayon, self.rayon)
        painter.end()


if __name__ == "__main__":
    app = QApplication([])
    window = DragAndDraw()
    window.show()
    app.exec()
