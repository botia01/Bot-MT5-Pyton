import tkinter as tk
from tkinter import ttk, messagebox
from conexion.mt5 import ConectorMT5
from estrategias.base import EstrategiaBase
from estilos import Estilos
from log import Logger
from config import ConfigManager
from simulacion import SimuladorMT5
import threading
import winsound
import os

class InterfazTrading:
    def __init__(self):
        """
        Inicializa la interfaz gráfica
        """
        self.root = tk.Tk()
        self.root.title("Bot de Trading MT5")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Inicializar logger y config
        self.logger = Logger()
        self.config = ConfigManager()
        
        # Inicializar conexión y estrategia
        self.conector = None
        self.estrategia = None
        self.conectado = False
        
        # Inicializar conector según modo simulación
        if self.config.get("modo_simulacion", False):
            self.conector = SimuladorMT5()
        else:
            self.conector = ConectorMT5()
        
        # Variables de control
        self.par_divisa = tk.StringVar(value=self.config.get("par_defecto", "EURUSD"))
        self.estrategia_seleccionada = tk.StringVar(value=self.config.get("estrategia", "Estrategia Base"))
        
        # Inicializar estilos
        self.estilos = Estilos()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Inicializar estrategia
        self.inicializar_estrategia()
        
        # Registrar inicio
        self.logger.log_info("Interfaz iniciada")

    def actualizar_divisas_disponibles(self):
        """
        Actualiza la lista de divisas disponibles
        """
        try:
            if self.conector and self.conectado:
                try:
                    divisas = self.conector.obtener_divisas_disponibles()
                    self.cmb_divisa['values'] = [f"{nombre} - {descripcion}" for nombre, descripcion in divisas]
                    if divisas:
                        self.cmb_divisa.set(divisas[0][0])
                        self.mostrar_mensaje("Lista de divisas actualizada", tipo='info')
                        self.logger.log_info("Lista de divisas actualizada")
                except Exception as e:
                    self.logger.log_error(f"Error al obtener divisas: {str(e)}")
                    self.mostrar_mensaje(f"Error al obtener divisas: {str(e)}", tipo='error')
            else:
                self.mostrar_mensaje("No se puede actualizar divisas: No estás conectado", tipo='warning')
                self.logger.log_warning("No se puede actualizar divisas: No conectado")
        except Exception as e:
            error_msg = f"Error al actualizar divisas: {str(e)}"
            self.mostrar_mensaje(error_msg, tipo='error')
            self.logger.log_error(error_msg)

    def inicializar_estrategia(self):
        """
        Inicializa la estrategia seleccionada
        """
        try:
            estrategia_actual = self.config.get("estrategia", "Estrategia Base")
            self.estrategia_seleccionada.set(estrategia_actual)
            self.mostrar_mensaje(f"Estrategia inicializada: {estrategia_actual}")
            self.logger.log_info(f"Estrategia inicializada: {estrategia_actual}")
        except Exception as e:
            error_msg = f"Error al inicializar estrategia: {str(e)}"
            self.mostrar_mensaje(error_msg, tipo='error')
            self.logger.log_error(error_msg)

    def mostrar_mensaje(self, mensaje, tipo='info'):
        """
        Muestra un mensaje en el área de mensajes
        
        Args:
            mensaje: Mensaje a mostrar
            tipo: Tipo de mensaje (info, error, warning)
        """
        try:
            # Registrar en log
            if tipo == 'error':
                self.logger.log_error(mensaje)
            elif tipo == 'warning':
                self.logger.log_warning(mensaje)
            else:
                self.logger.log_info(mensaje)
                
            # Mostrar en GUI
            self.txt_mensajes.config(state='normal')
            self.txt_mensajes.insert(tk.END, f"{mensaje}\n")
            self.txt_mensajes.config(state='disabled')
            self.txt_mensajes.see(tk.END)
            
            if tipo == 'error':
                self.txt_mensajes.tag_add('error', f'{self.txt_mensajes.index(tk.END)}-2l', f'{self.txt_mensajes.index(tk.END)}-1l')
            elif tipo == 'warning':
                self.txt_mensajes.tag_add('warning', f'{self.txt_mensajes.index(tk.END)}-2l', f'{self.txt_mensajes.index(tk.END)}-1l')
            else:
                self.txt_mensajes.tag_add('info', f'{self.txt_mensajes.index(tk.END)}-2l', f'{self.txt_mensajes.index(tk.END)}-1l')
                
        except Exception as e:
            error_msg = f"Error al mostrar mensaje: {str(e)}"
            self.logger.log_error(error_msg)
            print(error_msg)

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

    def conectar(self):
        """
        Establece la conexión con MetaTrader 5
        """
        try:
            if self.conectado:
                self.mostrar_mensaje("Ya estás conectado", tipo='warning')
                return False
                
            # Inicializar conector
            if self.config.get("modo_simulacion", False):
                self.conector = SimuladorMT5()
            else:
                self.conector = ConectorMT5()
                
            # Conectar
            if not self.conector.conectar():
                raise ConnectionError("No se pudo conectar a MetaTrader 5")
                
            # Obtener información de cuenta
            info = self.conector.obtener_info_cuenta()
            if info:
                try:
                    self.lbl_cuenta.config(text=str(info.login))
                    self.lbl_balance.config(text=f"{info.balance:.2f}")
                    self.lbl_equity.config(text=f"{info.equity:.2f}")
                    self.logger.log_info(f"Conexión exitosa - Balance: {info.balance:.2f}")
                except (AttributeError, TypeError) as e:
                    self.logger.log_error(f"Error al procesar información de cuenta: {str(e)}")
                    self.mostrar_mensaje(f"Error al procesar información de cuenta: {str(e)}", tipo='error')
            
            # Actualizar interfaz
            self.actualizar_interfaz(True)
            
            self.mostrar_mensaje("Conectado exitosamente", tipo='success')
            self.logger.log_success("Conexión exitosa")
            
            return True
            
        except Exception as e:
            error_msg = f"Error al conectar: {str(e)}"
            self.mostrar_mensaje(error_msg, tipo='error')
            self.logger.log_error(error_msg)
            self.actualizar_interfaz(False)
            return False

    def actualizar_interfaz(self, conectado):
        """
        Actualiza la interfaz según el estado de conexión
        """
        try:
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
                    self.logger.log_error(f"Error al obtener información de cuenta: {str(e)}")
                    self.mostrar_mensaje(f"Error al obtener información de cuenta: {str(e)}", tipo='error')
            else:
                self.lbl_estado.config(text="Desconectado", foreground="red")
                self.btn_conectar.config(text="Conectar")
                self.limpiar_info_cuenta()
                self.btn_bot.state(['disabled'])
                self.txt_mensajes.config(state='normal')
                self.txt_mensajes.delete('1.0', tk.END)
                self.txt_mensajes.config(state='disabled')
        except Exception as e:
            error_msg = f"Error al actualizar interfaz: {str(e)}"
            self.mostrar_mensaje(error_msg, tipo='error')
            self.logger.log_error(error_msg)

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

    def crear_interfaz(self):
        """
        Crea los elementos de la interfaz gráfica con un diseño moderno y atractivo
        """
        try:
            # Crear el frame principal
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Organizar en dos columnas principales
            left_frame = ttk.LabelFrame(main_frame, text="Conexión y Configuración", padding="15 10")
            left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
            
            right_frame = ttk.LabelFrame(main_frame, text="Control y Estadísticas", padding="15 10")
            right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Frame de conexión
            conexion_frame = ttk.LabelFrame(left_frame, text="Conexión", padding="10 5")
            conexion_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            # Botón de conectar con diseño moderno
            self.btn_conectar = ttk.Button(conexion_frame, text="Conectar", command=self.conectar)
            self.btn_conectar.grid(row=0, column=0, pady=10, padx=10)
            self.estilos.aplicar_estilo(self.btn_conectar, 'conectar')
            
            # Frame de información con diseño moderno
            info_frame = ttk.LabelFrame(left_frame, text="Información", padding="15 10")
            info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            # Etiquetas de estado
            ttk.Label(info_frame, text="Estado:").grid(row=0, column=0, sticky=tk.W)
            self.lbl_estado = ttk.Label(info_frame, text="Desconectado", foreground="red")
            self.lbl_estado.grid(row=0, column=1, sticky=tk.W)
            
            ttk.Label(info_frame, text="Cuenta:").grid(row=1, column=0, sticky=tk.W)
            self.lbl_cuenta = ttk.Label(info_frame, text="-")
            self.lbl_cuenta.grid(row=1, column=1, sticky=tk.W)
            
            ttk.Label(info_frame, text="Balance:").grid(row=2, column=0, sticky=tk.W)
            self.lbl_balance = ttk.Label(info_frame, text="-")
            self.lbl_balance.grid(row=2, column=1, sticky=tk.W)
            
            ttk.Label(info_frame, text="Equity:").grid(row=3, column=0, sticky=tk.W)
            self.lbl_equity = ttk.Label(info_frame, text="-")
            self.lbl_equity.grid(row=3, column=1, sticky=tk.W)
            
            # Frame de configuración
            config_frame = ttk.LabelFrame(left_frame, text="Configuración", padding="15 10")
            config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            # Selector de par de divisas
            ttk.Label(config_frame, text="Par de divisas:").grid(row=0, column=0, sticky=tk.W)
            self.cmb_divisa = ttk.Combobox(config_frame, textvariable=self.par_divisa, width=20)
            self.cmb_divisa.grid(row=0, column=1, padx=5)
            self.cmb_divisa.bind('<<ComboboxSelected>>', self.cambiar_divisa)
            
            # Selector de estrategia
            ttk.Label(config_frame, text="Estrategia:").grid(row=1, column=0, sticky=tk.W)
            self.cmb_estrategia = ttk.Combobox(config_frame, textvariable=self.estrategia_seleccionada, width=20)
            self.cmb_estrategia.grid(row=1, column=1, padx=5)
            self.cmb_estrategia.bind('<<ComboboxSelected>>', self.seleccionar_estrategia)
            self.cmb_estrategia['values'] = ['Estrategia Base']
            
            # Frame de control
            control_frame = ttk.LabelFrame(right_frame, text="Control", padding="15 10")
            control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            # Botón para controlar el bot
            self.btn_bot = ttk.Button(control_frame, text="Start Bot", command=self.toggle_bot)
            self.btn_bot.grid(row=0, column=0, pady=10, padx=10)
            self.estilos.aplicar_estilo(self.btn_bot, 'bot')
            
            # Estado del bot
            ttk.Label(control_frame, text="Estado del bot:").grid(row=1, column=0, sticky=tk.W)
            self.lbl_estado_bot = ttk.Label(control_frame, text="Apagado", foreground="red")
            self.lbl_estado_bot.grid(row=1, column=1, sticky=tk.W)
            
            # Frame de estadísticas
            estadisticas_frame = ttk.LabelFrame(right_frame, text="Estadísticas", padding="15 10")
            estadisticas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            # Estadísticas de ganancias y pérdidas
            ttk.Label(estadisticas_frame, text="Ganancias:").grid(row=0, column=0, sticky=tk.W)
            self.lbl_ganancias = ttk.Label(estadisticas_frame, text="0.00")
            self.lbl_ganancias.grid(row=0, column=1, sticky=tk.W)
            
            ttk.Label(estadisticas_frame, text="Pérdidas:").grid(row=1, column=0, sticky=tk.W)
            self.lbl_perdidas = ttk.Label(estadisticas_frame, text="0.00")
            self.lbl_perdidas.grid(row=1, column=1, sticky=tk.W)
            
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
            
            # Inicializar el área de mensajes
            self.txt_mensajes.tag_configure('info', foreground='#74b9ff')
            self.txt_mensajes.tag_configure('error', foreground='#ff4757')
            self.txt_mensajes.tag_configure('warning', foreground='#ffa502')
            
            # Mostrar mensaje de inicio
            self.mostrar_mensaje("Sistema iniciado correctamente", tipo='info')
            
            # Configurar el combobox con un valor por defecto
            self.cmb_divisa['values'] = ["EURUSD", "GBPUSD", "USDJPY"]  # Lista por defecto
            self.cmb_divisa.set("EURUSD")  # Valor por defecto
            
            self.logger.log_info("Interfaz creada exitosamente")
            
        except Exception as e:
            error_msg = f"Error al crear la interfaz: {str(e)}"
            print(f"Error crítico: {error_msg}")  # Usar print para asegurar que se vea el error
            self.logger.log_error(error_msg)
            raise Exception(error_msg)  # Propagar el error para que se vea en la consola

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
