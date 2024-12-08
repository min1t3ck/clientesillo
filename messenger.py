from PyQt6.QtWidgets import QMainWindow, QDialog, QMessageBox
from Ui_principal import *
from Ui_conectar import *
from PyQt6.uic import loadUi
from PyQt6.QtCore import QThread, pyqtSignal
import sys
import socket

from Ui_Primera import * 




class Primera(QDialog, Ui_DialogPrim):
    def __init__(self, *args, **kwargs):
        super(Primera, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.btn1.clicked.connect(self.abrir_principal)  # Botón Siguiente
        #eliminé la segunda ventana JAJAJA no tiene sentido poner contraseñas

    
        
    def abrir_principal(self):
        """Cerrar esta ventana para continuar con Principal."""
        user = ventana_primera.Usuario.text()
        if  user:
            server = '18.119.116.177'
            port = 80
            self.coneccion = ThreadSocket(server, int(port), user)
            self.coneccion.start()  
            self.accept() #para retornar un valor true y poder evaluarlo en la sentencia if
        else:    
             QMessageBox.warning(self, "No hay usuario", "Ingrese un usuario")



#-----------------------------------------------------------------------------------------------------------

class ThreadSocket(QThread):					#TrheadSoked es una subclase de Qtread
    global connected        #Al ser global es visible para todos los métodos
    signal_message = pyqtSignal(str)
    def __init__(self, host, port, name):
        global connected    #Se hace referencia a la variable global connected 
        super().__init__()  #llama al constructor de la super clase Qthred para que se construya el hilo de manera habitual
        server.connect((host, port)) #conecta el soket a la direccion dada y el puerto dado. Es posible referenciar al obejto soker "server" por que if __name__ = "__name__" lo hace global y accede a traves de la resolucion de variables por ámbito del intérprete
        connected = True
        server.send(bytes(f"<name>{name}", 'utf-8'))

    def run(self):#run() es un método que se sobreescribe con lo que tú quieres que haga el hilo al ejecutarse
        global connected# #recupera la variable gloibal connected para su uso
        try:
            while connected:
                message = server.recv(BUFFER_SIZE)#SE QUEDA ESPERANDO un mensaje del servidor
                if message:
                    self.signal_message.emit(message.decode("utf-8"))
                else:
                    self.signal_message.emit("<!!disconected!!>")
                    break
                
        except ...:
            self.signal_message.emit("<!!error!!>")
        finally:
            server.close()
            connected = False
        
    def stop(self):
        global connected
        connected = False
        self.wait()



class MainWindow(QMainWindow, Ui_Messenger):
    def __init__(self, socket_thread,*parent, **flags) -> None:
        super().__init__(*parent, **flags)
        self.setupUi(self)
        self.coneccion = socket_thread
        self.coneccion.signal_message.connect(self.mensage_entrante)
        
        #self.actionConectar.triggered.connect(self.showDialog) #hace referencia a la pestañita de conectar
        self.actionSalir.triggered.connect(self.salir)          #hace referencia a la pestañita para salir
        #self.coneccion = None #Variable de instancia creada dentro del constructor para el control para un Hilo
        self.btnSend.clicked.connect(self.mensaje_saliente)       #si se presiona el botón asociado
        self.txtSend.returnPressed.connect(self.mensaje_saliente)   #si se presiona Enter (que buen detalle)
        self.setWindowTitle("Messenger - Conectado") #Define (dentro de la funcion __init__) como aparecerá el titulo al iniciar la ventana
        
    def mensaje_saliente(self):
        str = self.txtSend.text()   #str <= El mensaje dentro de la caja
        if str != "" and connected:
            server.send(bytes(str, 'utf-8'))
            self.txtSend.clear()
            self.mensage_entrante("<Tú> " + str + '\n')
            
        
    def salir(self):
        exit()
        
        
    def mensage_entrante(self, mensaje):
        self.txtMsgs.setPlainText(self.txtMsgs.toPlainText() + mensaje)
        self.txtMsgs.verticalScrollBar().setValue(self.txtMsgs.verticalScrollBar().maximum())
        
    #def showDialog(self):
        #dialog = MiDialogo(self)    #muestra la ventana de diálogo
        #resp = dialog.exec()        #Inicializa el bucle de eventos
        #Al ser una ventanita de dialogos, se puede cerrar con una x o con una palomita
        #si se cierra con una palomita, .exec() devuelve un valor boleano TRUE
        #if resp == True:
            #server = dialog.txtServer.text()    #server <= texto que contiene y lo castea
            #user = dialog.txtUser.text()
            #port = dialog.txtPort.text()
            #if server and not server.isspace() and port and port.isnumeric():   #Si server no es un espacio en blanco y el puerto es numérico               self.coneccion = ThreadSocket(server, int(port), user)
                #self.coneccion = ThreadSocket(server, int(port), user)#se crea el hilo para la conexion
                
                #self.coneccion.signal_message.connect(self.mensage_entrante)  #cada vez que llegue una señal de mensaje se mandará a llamr a la función "mensaje entrante" cuyo arguento de la señal de tipo str es compatible y se incluirá automáticamente en el argumento esperado por la función mensaje_entrante 
                
                #self.coneccion.start()  #Inicializa el Hilo
            


#class MiDialogo(QDialog, Ui_Dialog):    #Representa la ventana de dialogo
    #def __init__(self, parent=None):
        #super().__init__(parent)
        #self.setupUi(self)  
        #loadUi("dialogo.ui", self)


#-------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    BUFFER_SIZE = 1024  # Usamos un número pequeño para tener una respuesta rápida
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crea un objeto soket
    connected = False #connected es una variable global
    app = QtWidgets.QApplication(sys.argv)
    while True:
        # Instanciar y mostrar `Primera`
        ventana_primera = Primera()
        resultado = ventana_primera.exec()  # Bloquea hasta cerrar `Primera`

        if resultado == QDialog.DialogCode.Accepted:
            # Abrir `Principal` si el usuario presionó "Siguiente"
            ventana_principal = MainWindow(ventana_primera.coneccion)
            ventana_principal.show()
            break  # Salimos del bucle para no volver a abrir `Primera`
        else:
            # Salimos del programa si la ventana `Primera` se cierra con la "X"
            sys.exit()

    sys.exit(app.exec())