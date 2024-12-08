from Ui_msn_v1 import *
from Ui_Primera import * 
from Ui_Privado import *
from Ui_Grupos import *



from PyQt6.QtWidgets import QMainWindow, QDialog, QApplication, QMessageBox, QWidget
from PyQt6.QtCore import QThread, pyqtSignal
import sys
import socket



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
 
 



#/////////////////////Primera Ventana (Inicio sesion)////////////////

class Primera(QDialog, Ui_DialogPrim):
    def __init__(self, *args, **kwargs):
        super(Primera, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.btn1.clicked.connect(self.abrir_principal)  # Botón Siguiente
        #eliminé la segunda ventana JAJAJA no tiene sentido poner contraseñas

    
        
    def abrir_principal(self):
        """Cerrar esta ventana para continuar con Principal."""
        user = ventana_primera.Usuario.text()
        print(user.isspace())
        if  user:
            port = 3003
            self.coneccion = ThreadSocket('18.119.116.177', int(port), user)
            self.coneccion.start()  
            self.accept()
        else:    
             QMessageBox.warning(self, "No hay usuario", "Ingrese un usuario")




    def closeEvent(self, event):
        """Cerrar todo el programa si se cierra esta ventana."""
        QApplication.instance().quit()  # Garantiza salida completa
        event.accept()
#////////////////////////////////////////////////////////////////////////



        
#////////////////////////VENTANA (PRI)ncipal//////////////////////////////
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, socket_thread,*parent, **flags) -> None:
        super().__init__(*parent, **flags)
        self.setupUi(self)
        self.coneccion = socket_thread
        self.coneccion.signal_message.connect(self.mensaje_entrante)
        
        self.usuarios_conectados = []
        
        self.msgSend.clicked.connect(self.mensaje_saliente)
        self.msgWrite.returnPressed.connect(self.mensaje_saliente)
        
        #botones auxiliares pra probar las ventanas de privado y grupal
        self.btn_Private.clicked.connect(self.mensajePrivado)
        self.btn_Group.clicked.connect(self.mensajeGrupo)

        self.btn_Tereneitor.clicked.connect(self.terreneitor)
        
        

    def mensaje_saliente(self):
        str = self.msgWrite.text()
        if str != "" and connected:
            server.send(bytes(str, 'utf-8'))
            self.msgWrite.clear()
            self.mensaje_entrante("<Tú> " + str + '\n')
            
            
            
    def mensaje_entrante(self, mensaje):
        if mensaje.startswith("<list_response>"):
        
            usuarios = mensaje.removeprefix("<list_response>").removesuffix("</list_response>")
            self.usuarios_conectados = usuarios.split(",") if usuarios else []
            print("Usuarios conectados:", self.usuarios_conectados)
        else:
            
            self.msgView.setPlainText(self.msgView.toPlainText() + mensaje)
            self.msgView.verticalScrollBar().setValue(self.msgView.verticalScrollBar().maximum())
            
    
    
    def MostrarAdvertencia(self, texto):
        """Mostrar advertencia al usuario en caso de errores"""
        QMessageBox.warning(self, "Advertencia", texto)


    #abre privado
    def mensajePrivado(self):
        self.ventana_privada = Privado(self) 
        self.ventana_privada.show() 
    
    
    #abre grupal
    def mensajeGrupo(self):
        self.ventana_privada = Grupo(self) 
        self.ventana_privada.show() 
      
        
    def terreneitor(self):
        self.ventana_terreneitor = Terrene(self)
        self.ventana_terreneitor.show()



#Ventana Mensaje privado        
class Privado(QDialog, Ui_Privado):
    signal_enviar = pyqtSignal(str, str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.btn_Close.clicked.connect(self.cerrarVentana)

    def cerrarVentana(self):
        self.close()



#Ventana mensaje grupal
class Grupo(QDialog, Ui_Grupo):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)        
        self.btn_Close.clicked.connect(self.cerrarVentana)

    def cerrarVentana(self):
        self.close()


  
  

if __name__ == "__main__":
    BUFFER_SIZE = 1024  # Usamos un número pequeño para tener una respuesta rápida
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False
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

    