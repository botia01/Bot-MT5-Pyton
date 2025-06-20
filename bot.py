import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from conexion.mt5 import ConectorMT5
from estrategias.base import EstrategiaBase
from estilos import Estilos

class InterfazTrading:
    """
    Interfaz gráfica para el bot de trading
    """
    def __init__(self):
        """
        Inicializa la interfaz gráfica
        """
        self.root = tk.Tk()
        self.root.title("Bot de Trading MT5")
        self.root.geometry("800x600")  # Aumentando el tamaño para un mejor diseño
        
        # Configurar el estilo general
        self.estilos = Estilos()
        self.root.configure(bg=self.estilos.obtener_color('fondo'))
        
        # Crear el conector
        self.conector = ConectorMT5()
        
        # Inicializar la estrategia
        self.estrategia = None
        self.estrategia_seleccionada = None
        
        # Crear widgets
        self.crear_interfaz()

    def mostrar_mensaje(self, mensaje):
        """
        Muestra un mensaje en el área de mensajes
        """
        self.txt_mensajes.config(state='normal')
        self.txt_mensajes.insert(tk.END, f"{mensaje}\n")
        self.txt_mensajes.see(tk.END)
        self.txt_mensajes.config(state='disabled')

    def seleccionar_estrategia(self, event):
        """
        Maneja la selección de estrategia
        """
        seleccion = self.cmb_estrategia.get()
        if seleccion:
            if seleccion == 'Estrategia Base':
                self.estrategia_seleccionada = seleccion
                self.mostrar_mensaje(f"Estrategia seleccionada: {seleccion}")
            else:
                self.estrategia_seleccionada = None
                self.mostrar_mensaje("Estrategia no válida")

    def cambiar_divisa(self, event):
        """
        Actualiza la divisa seleccionada
        """
        try:
            seleccion = self.cmb_divisa.get()
            if seleccion:
                # Extraer el nombre de la divisa (antes del " - ")
                nombre_divisa = seleccion.split(" - ")[0]
                self.conector.par_divisas = nombre_divisa
                self.mostrar_mensaje(f"Divisa seleccionada: {nombre_divisa}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar divisa: {str(e)}")

    def crear_interfaz(self):
        """
        Crea los elementos de la interfaz gráfica con un diseño moderno y atractivo
        """
        # Configurar el grid principal
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Columna izquierda con fondo más claro
        left_frame = ttk.Frame(main_frame, style='EstiloFrame.TFrame')
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(20, 10), pady=20)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Frame de conexión con diseño moderno
        conexion_frame = ttk.LabelFrame(left_frame, text="Conexión", padding="15 10")
        conexion_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 15))
        
        # Botón de conectar con diseño moderno
        self.btn_conectar = ttk.Button(conexion_frame, text="Conectar", command=self.conectar)
        self.btn_conectar.grid(row=0, column=0, pady=10, padx=10)
        self.estilos.aplicar_estilo(self.btn_conectar, 'conectar')
        
        # Estilo especial para el botón de conectar usando el objeto estilos
        self.estilos.estilo.configure('Conectar.TButton',
                             padding='10 5',
                             font=('Segoe UI', 10, 'bold'))
        
        # Frame de información con diseño moderno
        info_frame = ttk.LabelFrame(left_frame, text="Información", padding="15 10")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 15))
        
        # Organizar información en dos columnas con diseño moderno
        ttk.Label(info_frame, text="Estado:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.lbl_estado = ttk.Label(info_frame, text="Desconectado")
        self.lbl_estado.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.estilos.aplicar_estilo(self.lbl_estado, 'estado')
        
        ttk.Label(info_frame, text="Cuenta:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.lbl_cuenta = ttk.Label(info_frame, text="-")
        self.lbl_cuenta.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.estilos.aplicar_estilo(self.lbl_cuenta, 'info')
        
        ttk.Label(info_frame, text="Balance:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.lbl_balance = ttk.Label(info_frame, text="-")
        self.lbl_balance.grid(row=2, column=1, sticky=tk.W, padx=5)
        self.estilos.aplicar_estilo(self.lbl_balance, 'info')
        
        ttk.Label(info_frame, text="Equity:").grid(row=3, column=0, sticky=tk.W, padx=5)
        self.lbl_equity = ttk.Label(info_frame, text="-")
        self.lbl_equity.grid(row=3, column=1, sticky=tk.W, padx=5)
        self.estilos.aplicar_estilo(self.lbl_equity, 'info')
        
        # Frame de configuración con diseño moderno
        config_frame = ttk.LabelFrame(left_frame, text="Configuración", padding="15 10")
        config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 15))
        
        # Organizar configuración en dos columnas con diseño moderno
        ttk.Label(config_frame, text="Divisa:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.cmb_divisa = ttk.Combobox(config_frame, state="readonly")
        self.cmb_divisa.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        self.cmb_divisa.bind('<<ComboboxSelected>>', self.cambiar_divisa)
        
        ttk.Label(config_frame, text="Estrategia:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.cmb_estrategia = ttk.Combobox(config_frame, state="readonly")
        self.cmb_estrategia.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        self.cmb_estrategia['values'] = ['Estrategia Base']  # Por ahora solo tenemos la estrategia base
        self.cmb_estrategia.bind('<<ComboboxSelected>>', self.seleccionar_estrategia)
        
        # Columna derecha con fondo más claro
        right_frame = ttk.Frame(main_frame, style='EstiloFrame.TFrame')
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 20), pady=20)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Frame de control del bot con diseño moderno
        control_frame = ttk.LabelFrame(right_frame, text="Control del Bot", padding="15 10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 15))
        
        # Botón para encender/apagar el bot con diseño moderno
        self.btn_bot = ttk.Button(control_frame, text="Start Bot", command=self.toggle_bot)
        self.btn_bot.grid(row=0, column=0, columnspan=2, pady=10, padx=10)
        self.btn_bot.state(['disabled'])
        self.estilos.aplicar_estilo(self.btn_bot, 'bot')
        
        # Etiqueta para mostrar el estado del bot con diseño moderno
        ttk.Label(control_frame, text="Estado del Bot:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.lbl_estado_bot = ttk.Label(control_frame, text="Apagado")
        self.lbl_estado_bot.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.estilos.aplicar_estilo(self.lbl_estado_bot, 'estado')
        
        # Frame de estadísticas con diseño moderno
        estadisticas_frame = ttk.LabelFrame(right_frame, text="Estadísticas", padding="15 10")
        estadisticas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 15))
        
        # Organizar estadísticas con diseño moderno
        ttk.Label(estadisticas_frame, text="Ganancias:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.lbl_ganancias = ttk.Label(estadisticas_frame, text="0.00")
        self.lbl_ganancias.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.estilos.aplicar_estilo(self.lbl_ganancias, 'ganancias')
        
        ttk.Label(estadisticas_frame, text="Pérdidas:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.lbl_perdidas = ttk.Label(estadisticas_frame, text="0.00")
        self.lbl_perdidas.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.estilos.aplicar_estilo(self.lbl_perdidas, 'perdidas')
        
        # Área para mostrar mensajes del bot con diseño moderno
        self.txt_mensajes = tk.Text(right_frame, height=10, width=50, bg='#262626', fg='white')
        self.txt_mensajes.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 15))
        self.txt_mensajes.config(state='disabled')
        
        # Configurar el estilo de los widgets
        self.estilos.aplicar_estilo(main_frame, 'frame')
        self.estilos.aplicar_estilo(left_frame, 'frame')
        self.estilos.aplicar_estilo(right_frame, 'frame')
        self.estilos.aplicar_estilo(conexion_frame, 'frame')
        self.estilos.aplicar_estilo(info_frame, 'frame')
        self.estilos.aplicar_estilo(config_frame, 'frame')
        self.estilos.aplicar_estilo(control_frame, 'frame')
        self.estilos.aplicar_estilo(estadisticas_frame, 'frame')

    def conectar(self):
        """
        Conecta con MetaTrader 5
        """
        try:
            if self.conector.conectado:
                self.conector.desconectar()
                self.mostrar_mensaje("Desconectado de MetaTrader 5")
            else:
                self.conector.conectar()
                self.mostrar_mensaje("Conectado a MetaTrader 5")
                
                # Actualizar la lista de divisas disponibles
                divisas = self.conector.obtener_divisas_disponibles()
                self.cmb_divisa['values'] = [f"{nombre} - {descripcion}" for nombre, descripcion in divisas]
                
                # Establecer el valor por defecto
                if divisas:
                    self.cmb_divisa.set(divisas[0][0])
                    self.cambiar_divisa(None)
                
            self.actualizar_interfaz(self.conector.conectado)
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar: {str(e)}")

    def actualizar_interfaz(self, conectado):
        """
        Actualiza la interfaz según el estado de conexión
        """
        if conectado:
            self.lbl_estado.config(text="Conectado", foreground="green")
            self.btn_conectar.config(text="Desconectar")
            self.btn_bot.state(['!disabled'])
            
            # Actualizar información de cuenta
            try:
                info = self.conector.obtener_info_cuenta()
                self.lbl_cuenta.config(text=str(info.login))
                self.lbl_balance.config(text=f"{info.balance:.2f}")
                self.lbl_equity.config(text=f"{info.equity:.2f}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener información de cuenta: {str(e)}")
        else:
            self.lbl_estado.config(text="Desconectado", foreground="red")
            self.btn_conectar.config(text="Conectar")
            self.limpiar_info_cuenta()
            self.btn_bot.state(['disabled'])

    def limpiar_info_cuenta(self):
        """
        Limpia la información de cuenta
        """
        self.lbl_cuenta.config(text="-")
        self.lbl_balance.config(text="-")
        self.lbl_equity.config(text="-")

    def toggle_bot(self):
        """
        Alterna el estado del bot (encendido/apagado)
        """
        try:
            if self.btn_bot['text'] == "Start Bot":
                # Encender el bot
                self.encender_bot()
            else:
                # Apagar el bot
                self.apagar_bot()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar el estado del bot: {str(e)}")

    def encender_bot(self):
        """
        Enciende el bot y actualiza la interfaz
        """
        # Validar que haya una estrategia seleccionada
        if not self.estrategia_seleccionada:
            messagebox.showwarning("Advertencia", "Debe seleccionar una estrategia")
            return
            
        # Validar que esté conectado
        if not self.conector.conectado:
            messagebox.showwarning("Advertencia", "Debe estar conectado a MT5")
            return
            
        # Crear la estrategia seleccionada
        if self.estrategia_seleccionada == 'Estrategia Base':
            self.estrategia = EstrategiaBase(self.conector)
        else:
            messagebox.showerror("Error", "Estrategia no válida")
            return
            
        self.btn_bot.config(text="Stop Bot")
        self.lbl_estado_bot.config(text="Encendido", foreground="green")
        self.mostrar_mensaje("Bot iniciado correctamente")
        
        # Iniciar la estrategia
        self.estrategia.iniciar()
        
        # Inicializar estadísticas
        self.actualizar_estadisticas(0.0, 0.0)

    def actualizar_estadisticas(self, ganancias, perdidas):
        """
        Actualiza los valores de las estadísticas
        
        Args:
            ganancias: Monto total de ganancias
            perdidas: Monto total de pérdidas
        """
        self.lbl_ganancias.config(text=f"{ganancias:.2f}")
        self.lbl_perdidas.config(text=f"{perdidas:.2f}")

    def apagar_bot(self):
        """
        Apaga el bot y actualiza la interfaz
        """
        if self.estrategia:
            self.estrategia.detener()
        
        self.btn_bot.config(text="Start Bot")
        self.lbl_estado_bot.config(text="Apagado", foreground="red")
        self.mostrar_mensaje("Bot detenido")
        
        # Limpiar la estrategia
        self.estrategia = None

    def iniciar(self):
        """
        Inicia la interfaz gráfica
        """
        self.root.mainloop()

if __name__ == "__main__":
    app = InterfazTrading()
    app.iniciar()
