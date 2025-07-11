import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging
import MetaTrader5 as mt5
import time
import winsound
import os

from utils.funciones import validar_par_divisa, calcular_retornos, calcular_sharpe_ratio, calcular_drawdown, validar_volumen, calcular_pips, convertir_timeframe, calcular_lote
from estrategias.base import EstrategiaBase
from estrategias.cruce_ma import CruceMedias
from estrategias.rsi import EstrategiaRSI
from estrategias.registro import obtener_estrategias_disponibles, crear_estrategia
from log import Logger
from config import ConfigManager
from estilos import Estilos
from conexion.mt5 import ConectorMT5
from simulacion import SimuladorMT5

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
        
        # Variables de control
        self.par_divisa = tk.StringVar(value=self.config.get("par_defecto", "EURUSD"))
        self.estrategia_seleccionada = tk.StringVar()
        self.simulacion = tk.BooleanVar(value=self.config.get("modo_simulacion", False))
        self.bot_encendido = False
        
        # Inicializar estilos
        self.estilos = Estilos()
        
        # Crear interfaz y registrar inicio
        self.crear_interfaz()
        self.logger.log_info("Interfaz iniciada")
        
        # Cargar estrategias disponibles
        self.cargar_estrategias()

    def mostrar_alerta(self, mensaje, tipo='info'):
        """
        Muestra una alerta al usuario
        
        Args:
            mensaje: Mensaje a mostrar
            tipo: Tipo de alerta (info, warning, error)
        """
        try:
            if tipo == 'error':
                messagebox.showerror("Error", mensaje)
            elif tipo == 'warning':
                messagebox.showwarning("Advertencia", mensaje)
            else:
                messagebox.showinfo("Información", mensaje)
                
            # Sonido de alerta
            winsound.Beep(1000, 500)  # Frecuencia 1000Hz, duración 500ms
        except Exception as e:
            print(f"Error al mostrar alerta: {str(e)}")

    def crear_interfaz(self):
        """
        Crea los elementos de la interfaz gráfica con un diseño moderno y atractivo
        """
        try:
            # Crear el notebook principal
            self.notebook = ttk.Notebook(self.root)
            self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

            # Crear las pestañas
            self.tab_conexion = ttk.Frame(self.notebook)
            self.tab_config = ttk.Frame(self.notebook)
            self.tab_estadisticas = ttk.Frame(self.notebook)
            self.tab_registros = ttk.Frame(self.notebook)

            # Añadir las pestañas al notebook
            self.notebook.add(self.tab_conexion, text="Conexión")
            self.notebook.add(self.tab_config, text="Configuración")
            self.notebook.add(self.tab_estadisticas, text="Estadísticas")
            self.notebook.add(self.tab_registros, text="Registros")

            # Configurar el grid para que se expanda correctamente
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(0, weight=1)

            # Configurar las pestañas
            self.configurar_pestaña_conexion()
            self.configurar_pestaña_configuracion()
            self.configurar_pestaña_estadisticas()
            self.configurar_pestaña_registros()

        except Exception as e:
            self.logger.log_error(f"Error al crear la interfaz: {str(e)}")
            messagebox.showerror("Error", f"Error al crear la interfaz: {str(e)}")

    def configurar_pestaña_conexion(self):
        """Configura la pestaña de conexión"""
        try:
            # Frame principal para la pestaña de conexión
            frame_conexion = ttk.Frame(self.tab_conexion)
            frame_conexion.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Frame para los controles de conexión
            frame_controles = ttk.LabelFrame(frame_conexion, text="Conexión", padding="10 5")
            frame_controles.pack(fill=tk.X, padx=5, pady=5)

            # Checkbutton para modo simulación
            chk_simulacion = ttk.Checkbutton(frame_controles, text="Modo Simulación", 
                                            variable=self.simulacion, 
                                            command=self.actualizar_modo_conexion)
            chk_simulacion.pack(anchor=tk.W, padx=5, pady=5)

            # Label para mostrar el modo actual
            self.lbl_modo = ttk.Label(frame_controles, text="Modo: Real")
            self.lbl_modo.pack(anchor=tk.W, padx=5, pady=5)

            # Frame para estado y botón de conexión
            frame_estado = ttk.Frame(frame_controles)
            frame_estado.pack(fill=tk.X, pady=(0, 10))

            # Estado de conexión
            ttk.Label(frame_estado, text="Estado:").pack(side=tk.LEFT, padx=(0, 5))
            self.lbl_estado = ttk.Label(frame_estado, text="Desconectado", foreground="red")
            self.lbl_estado.pack(side=tk.LEFT)

            # Botón de conexión
            self.btn_conectar = ttk.Button(frame_estado, text="Conectar", command=self.conectar)
            self.btn_conectar.pack(side=tk.LEFT, padx=(10, 0))

        except Exception as e:
            self.logger.log_error(f"Error al configurar pestaña de conexión: {str(e)}")
            messagebox.showerror("Error", f"Error al configurar pestaña de conexión: {str(e)}")

    def configurar_pestaña_configuracion(self):
        """Configura la pestaña de configuración"""
        frame_config = ttk.Frame(self.tab_config)
        frame_config.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame para configuración
        frame_config_principal = ttk.LabelFrame(frame_config, text="Configuración", padding="10 5")
        frame_config_principal.pack(fill=tk.BOTH, expand=True)

        # Par de divisas
        ttk.Label(frame_config_principal, text="Divisa:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cmb_divisa = ttk.Combobox(frame_config_principal, textvariable=self.par_divisa, width=10, state='readonly')
        self.cmb_divisa.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.cmb_divisa.bind('<<ComboboxSelected>>', self.cambiar_divisa)
        self.cmb_divisa['values'] = []  # Iniciar sin valores
        self.cmb_divisa.set('')  # Iniciar vacío

        # Estrategia
        ttk.Label(frame_config_principal, text="Estrategia:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.cmb_estrategia = ttk.Combobox(frame_config_principal, textvariable=self.estrategia_seleccionada, width=15, state='readonly')
        self.cmb_estrategia.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.cmb_estrategia.bind('<<ComboboxSelected>>', self.seleccionar_estrategia)
        self.cmb_estrategia['values'] = []  # Iniciar sin valores
        self.cmb_estrategia.set('')  # Iniciar vacío

        # Frame para información de cuenta
        frame_cuenta = ttk.LabelFrame(frame_config, text="Información de Cuenta", padding="10 5")
        frame_cuenta.pack(fill=tk.X, pady=(10, 0))

        # Cuenta
        ttk.Label(frame_cuenta, text="Cuenta:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.lbl_cuenta = ttk.Label(frame_cuenta, text="")
        self.lbl_cuenta.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Balance
        ttk.Label(frame_cuenta, text="Balance:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.lbl_balance = ttk.Label(frame_cuenta, text="")
        self.lbl_balance.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Equity
        ttk.Label(frame_cuenta, text="Equity:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.lbl_equity = ttk.Label(frame_cuenta, text="")
        self.lbl_equity.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Frame para control del bot
        frame_bot = ttk.LabelFrame(frame_config, text="Control del Bot", padding="10 5")
        frame_bot.pack(fill=tk.X, pady=(10, 0))

        # Estado del bot
        ttk.Label(frame_bot, text="Estado del Bot:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.lbl_estado_bot = ttk.Label(frame_bot, text="Apagado", foreground="red")
        self.lbl_estado_bot.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Botón de control del bot
        self.btn_bot = ttk.Button(frame_bot, text="Start Bot", command=self.toggle_bot)
        self.btn_bot.grid(row=0, column=2, sticky=tk.W, padx=5)
        self.btn_bot.state(['disabled'])

    def configurar_pestaña_estadisticas(self):
        """Configura la pestaña de estadísticas"""
        frame_estadisticas = ttk.Frame(self.tab_estadisticas)
        frame_estadisticas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame para estadísticas principales
        frame_principal = ttk.LabelFrame(frame_estadisticas, text="Estadísticas Principales", padding="10 5")
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Ganancias
        ttk.Label(frame_principal, text="Ganancias:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.lbl_ganancias = ttk.Label(frame_principal, text="0.00")
        self.lbl_ganancias.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        # Pérdidas
        ttk.Label(frame_principal, text="Pérdidas:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.lbl_perdidas = ttk.Label(frame_principal, text="0.00")
        self.lbl_perdidas.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Balance Neto
        ttk.Label(frame_principal, text="Balance Neto:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.lbl_balance_neto = ttk.Label(frame_principal, text="0.00")
        self.lbl_balance_neto.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

    def configurar_pestaña_registros(self):
        """Configura la pestaña de registros"""
        try:
            # Frame para los registros
            frame_registros = ttk.Frame(self.tab_registros)
            frame_registros.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Crear el widget de logs
            self.txt_logs = scrolledtext.ScrolledText(frame_registros, height=15)
            self.txt_logs.pack(fill=tk.BOTH, expand=True)

            # Configurar los estilos para los mensajes
            self.txt_logs.tag_configure('info', foreground='black')
            self.txt_logs.tag_configure('warning', foreground='orange')
            self.txt_logs.tag_configure('error', foreground='red')
            
            # Añadir mensaje de bienvenida
            self.mostrar_mensaje("Bienvenido al Bot de Trading MT5")
            
            # Configurar el área de texto como de solo lectura
            self.txt_logs.config(state='disabled')
            
        except Exception as e:
            error_msg = f"Error al configurar pestaña de registros: {str(e)}"
            self.logger.log_error(error_msg)
            self.mostrar_alerta(error_msg, "error")

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
                        # No seleccionar automáticamente una divisa
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

    def cargar_estrategias(self):
        """Carga las estrategias disponibles en el combobox"""
        try:
            # Definir manualmente las estrategias disponibles
            estrategias = ["Cruce Medias", "RSI"]
            if not hasattr(self, 'cmb_estrategia'):
                # Crear el combobox si no existe
                self.cmb_estrategia = ttk.Combobox(self.tab_config, textvariable=self.estrategia_seleccionada, width=15, state='readonly')
                self.cmb_estrategia.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
                
            self.cmb_estrategia['values'] = estrategias
            if estrategias:
                self.cmb_estrategia.set(estrategias[0])  # Seleccionar la primera estrategia por defecto
                self.estrategia_seleccionada.set(estrategias[0])
                self.mostrar_mensaje(f"Estrategias cargadas: {', '.join(estrategias)}")
        except Exception as e:
            self.logger.log_error(f"Error al cargar estrategias: {str(e)}")
            self.mostrar_alerta(f"Error al cargar estrategias: {str(e)}", "error")

    def inicializar_estrategia(self):
        """
        Inicializa la estrategia seleccionada
        """
        try:
            # Verificar que hay un conector
            if not self.conector:
                self.mostrar_alerta("No hay conector disponible", "error")
                return
                
            estrategia_actual = self.estrategia_seleccionada.get()
            if not estrategia_actual:
                estrategias = self.cmb_estrategia['values']
                if estrategias:
                    estrategia_actual = estrategias[0]
                    self.cmb_estrategia.set(estrategia_actual)
                    self.estrategia_seleccionada.set(estrategia_actual)
                else:
                    self.mostrar_alerta("No hay estrategias disponibles", "error")
                    return
            
            # Verificar que hay una divisa seleccionada
            divisa = self.par_divisa.get()
            if not divisa:
                self.mostrar_alerta("Debe seleccionar una divisa", "warning")
                return
            
            # Crear la estrategia usando el método estático de la clase
            try:
                self.estrategia = crear_estrategia(estrategia_actual, self.conector, self)
                if self.estrategia:
                    self.estrategia.configurar_divisa(divisa)
                    self.estrategia.iniciar()
                    self.mostrar_alerta(f"Estrategia inicializada: {estrategia_actual}")
                    self.logger.log_info(f"Estrategia inicializada: {estrategia_actual}")
                else:
                    self.mostrar_alerta(f"No se pudo crear la estrategia: {estrategia_actual}", "error")
                    
            except Exception as e:
                error_msg = f"Error al crear estrategia {estrategia_actual}: {str(e)}"
                self.mostrar_alerta(error_msg, "error")
                self.logger.log_error(error_msg)
                self.estrategia = None
                
        except Exception as e:
            error_msg = f"Error al inicializar estrategia: {str(e)}"
            self.mostrar_alerta(error_msg, "error")
            self.logger.log_error(error_msg)

    def toggle_bot(self):
        """
        Alterna el estado del bot (encendido/apagado)
        """
        try:
            # Verificar que hay una estrategia seleccionada
            if not self.estrategia_seleccionada.get():
                self.mostrar_alerta("Debe seleccionar una estrategia", "warning")
                return
            
            # Verificar que hay una divisa seleccionada
            if not self.par_divisa.get():
                self.mostrar_alerta("Debe seleccionar una divisa", "warning")
                return
            
            # Verificar que está conectado
            if not self.conector or not self.conector.conectado:
                self.mostrar_alerta("Debe estar conectado a MT5", "warning")
                return
            
            # Verificar que los labels de estadísticas existen
            if not hasattr(self, 'lbl_ganancias') or not hasattr(self, 'lbl_perdidas'):
                self.mostrar_alerta("Error: Los labels de estadísticas no están inicializados", "error")
                return
            
            if self.bot_encendido:
                # Apagar el bot
                self.apagar_bot()
            else:
                # Encender el bot
                self.encender_bot()
                
        except Exception as e:
            error_msg = f"Error al cambiar el estado del bot: {str(e)}"
            self.mostrar_alerta(error_msg, "error")
            self.logger.log_error(error_msg)
            # Asegurar que el bot se apague en caso de error
            self.bot_encendido = False
            self.apagar_bot()

    def encender_bot(self):
        """
        Enciende el bot y actualiza la interfaz
        """
        try:
            estrategia_actual = self.estrategia_seleccionada.get()
            divisa_actual = self.par_divisa.get()
            
            # Validar selecciones
            if not estrategia_actual:
                self.mostrar_alerta("Debe seleccionar una estrategia", "warning")
                return
            if not divisa_actual:
                self.mostrar_alerta("Debe seleccionar una divisa", "warning")
                return
            if not self.conector.conectado:
                self.mostrar_alerta("Debe estar conectado a MT5", "warning")
                return
            
            # Primero apagar el bot si está encendido
            if self.bot_encendido:
                self.apagar_bot()
            
            # Crear la estrategia seleccionada
            self.estrategia = crear_estrategia(estrategia_actual, self.conector, self)
            if not self.estrategia:
                self.mostrar_alerta(f"Estrategia no válida: {estrategia_actual}", "error")
                return
            
            # Configurar la divisa
            self.estrategia.configurar_divisa(divisa_actual)
            
            # Iniciar la estrategia
            self.estrategia.iniciar()
            
            # Actualizar estado
            self.bot_encendido = True
            
            # Crear y ejecutar el hilo de la estrategia
            self.hilo_estrategia = threading.Thread(target=self.ejecutar_estrategia, daemon=True)
            self.hilo_estrategia.start()
            
            # Actualizar interfaz
            self.btn_bot.config(text="Stop Bot", state='normal')
            self.lbl_estado_bot.config(text="Encendido", foreground="green")
            self.mostrar_mensaje("Bot iniciado correctamente")
            
        except Exception as e:
            error_msg = f"Error al iniciar el bot: {str(e)}"
            self.mostrar_alerta(error_msg, "error")
            self.logger.log_error(error_msg)
            # Asegurar que el bot se apague en caso de error
            self.bot_encendido = False
            self.apagar_bot()

    def actualizar_estadisticas(self, ganancias, perdidas):
        """
        Actualiza los valores de las estadísticas
        
        Args:
            ganancias: Monto total de ganancias
            perdidas: Monto total de pérdidas
        """
        self.lbl_ganancias.config(text=f"{ganancias:.2f}")
        self.lbl_perdidas.config(text=f"{perdidas:.2f}")

    def ejecutar_estrategia(self):
        """
        Método que ejecuta la estrategia en un bucle continuo
        """
        try:
            if not self.estrategia:
                self.logger.log_error("Estrategia no inicializada")
                self.apagar_bot()
                return
                
            if not self.estrategia.activo:
                self.logger.log_info("Estrategia no activa")
                return

            try:
                self.estrategia.ejecutar()
                # Obtener estadísticas de la estrategia
                ganancias = getattr(self.estrategia, 'ganancias', 0.0)
                perdidas = getattr(self.estrategia, 'perdidas', 0.0)
                
                # Actualizar interfaz con las estadísticas
                self.actualizar_estadisticas(ganancias, perdidas)
                
                # Esperar un segundo antes de la siguiente ejecución
                time.sleep(1)
                
            except Exception as e:
                self.logger.log_error(f"Error en la ejecución de la estrategia: {str(e)}")
                self.mostrar_alerta(f"Error en la estrategia: {str(e)}", "error")
                # Intentar continuar si es un error temporal
                time.sleep(5)
                
        except Exception as e:
            error_msg = f"Error crítico en la ejecución del bot: {str(e)}"
            self.logger.log_error(error_msg)
            self.mostrar_alerta(error_msg, "error")
            # Asegurar que el bot se apague completamente
            if hasattr(self, 'hilo_estrategia') and self.hilo_estrategia.is_alive():
                self.hilo_estrategia.join()
            self.bot_encendido = False
            self.apgar_bot()

    def apagar_bot(self):
        """
        Apaga el bot y actualiza la interfaz
        """
        try:
            # Detener la estrategia si existe
            if self.estrategia:
                self.estrategia.detener()
                self.estrategia = None
            
            # Detener el hilo si está corriendo
            if hasattr(self, 'hilo_estrategia') and self.hilo_estrategia.is_alive():
                self.bot_encendido = False
                self.hilo_estrategia.join()
                del self.hilo_estrategia
            
            # Actualizar interfaz
            self.btn_bot.config(text="Start Bot", state='normal')
            self.lbl_estado_bot.config(text="Apagado", foreground="red")
            self.mostrar_mensaje("Bot detenido")
            
            # Actualizar estado
            self.bot_encendido = False
            
        except Exception as e:
            self.logger.log_error(f"Error al detener el bot: {str(e)}")
            self.mostrar_alerta(f"Error al detener el bot: {str(e)}", "error")
            # Asegurar que el estado visual se actualice
            self.lbl_estado_bot.config(text="Apagado", foreground="red")
            self.bot_encendido = False

    def seleccionar_estrategia(self, event=None):
        """
        Maneja la selección de una estrategia
        """
        try:
            estrategia_seleccionada = self.estrategia_seleccionada.get()
            if estrategia_seleccionada:
                # Si hay una estrategia activa, detenerla primero
                if self.estrategia:
                    self.estrategia.detener()
                    self.estrategia = None
                
                # Crear la nueva estrategia
                self.estrategia = crear_estrategia(estrategia_seleccionada, self.conector, self)
                if self.estrategia:
                    self.mostrar_alerta(f"Estrategia seleccionada: {estrategia_seleccionada}", "info")
                    # Si hay una divisa seleccionada, configurarla
                    divisa_actual = self.par_divisa.get()
                    if divisa_actual:
                        self.estrategia.configurar_divisa(divisa_actual)
                else:
                    self.mostrar_alerta(f"No se pudo crear la estrategia: {estrategia_seleccionada}", "error")
            else:
                self.mostrar_alerta("Debe seleccionar una estrategia válida", "warning")
                
        except Exception as e:
            error_msg = f"Error al seleccionar estrategia: {str(e)}"
            self.mostrar_alerta(error_msg, "error")
            self.logger.log_error(error_msg)

    def mostrar_mensaje(self, mensaje, tipo='info'):
        """
        Muestra un mensaje en el área de logs
        
        Args:
            mensaje: Mensaje a mostrar
            tipo: Tipo de mensaje (info, warning, error)
        """
        try:
            # Añadir el mensaje al área de logs
            self.txt_logs.insert(tk.END, f"{mensaje}\n", tipo)
            # Desplazar automáticamente el scroll
            self.txt_logs.see(tk.END)
            # Registrar el mensaje en el logger
            if tipo == 'info':
                self.logger.log_info(mensaje)
            elif tipo == 'warning':
                self.logger.log_warning(mensaje)
            elif tipo == 'error':
                self.logger.log_error(mensaje)
            
        except Exception as e:
            error_msg = f"Error al mostrar mensaje: {str(e)}"
            self.logger.log_error(error_msg)
            print(f"Error interno: {error_msg}")

    def cambiar_divisa(self, event=None):
        """
        Maneja el cambio de divisa seleccionada
        """
        try:
            nueva_divisa = self.par_divisa.get()
            if nueva_divisa:
                # Si hay una estrategia activa, actualizar su divisa
                if self.estrategia:
                    self.estrategia.configurar_divisa(nueva_divisa)
                    self.mostrar_alerta(f"Divisa cambiada a {nueva_divisa}", "info")
                else:
                    self.par_divisa.set(nueva_divisa)
            else:
                self.mostrar_alerta("Debe seleccionar una divisa válida", "warning")
        except Exception as e:
            error_msg = f"Error al cambiar divisa: {str(e)}"
            self.mostrar_alerta(error_msg, "error")
            self.logger.log_error(error_msg)

    def conectar(self):
        """Maneja la conexión a MetaTrader 5"""
        try:
            # Crear el conector apropiado
            if self.simulacion.get():
                self.conector = SimuladorMT5()
            else:
                self.conector = ConectorMT5()

            # Conectar
            if self.conector.conectar():
                self.conectado = True
                self.lbl_estado.config(text="Conectado", foreground="green")
                self.mostrar_alerta("Conexión exitosa", "info")
                self.logger.log_info("Conexión exitosa")
                
                # Obtener información de cuenta usando el método correcto de MT5
                info_cuenta = self.conector.obtener_info_cuenta()
                if info_cuenta:
                    self.lbl_cuenta.config(text=str(info_cuenta.login))
                    self.lbl_balance.config(text=f"{info_cuenta.balance:,.2f}")
                    self.lbl_equity.config(text=f"{info_cuenta.equity:,.2f}")
                
                # Actualizar lista de divisas
                self.actualizar_divisas_disponibles()
                
                # Cargar y mostrar las estrategias disponibles
                self.cargar_estrategias()
                
                # Inicializar la estrategia seleccionada
                self.inicializar_estrategia()
                
                # Habilitar el botón de control del bot
                self.btn_bot.state(['!disabled'])
                
            else:
                self.conectado = False
                self.lbl_estado.config(text="Desconectado", foreground="red")
                self.mostrar_alerta("Error al conectar", "error")
                self.logger.log_error("Error al conectar")
                
        except Exception as e:
            error_msg = f"Error al conectar: {str(e)}"
            self.mostrar_alerta(error_msg, "error")
            self.logger.log_error(error_msg)
            self.lbl_estado.config(text="Error", foreground="red")

    def actualizar_modo_conexion(self):
        """
        Actualiza el modo de conexión (real o simulación)
        """
        try:
            # Actualizar el modo visualmente
            modo = "Simulación" if self.simulacion.get() else "Real"
            self.lbl_modo.config(text=f"Modo: {modo}")
            self.logger.log_info(f"Modo de conexión cambiado a {modo}")
            
            # Si hay una conexión activa, desconectar y reconectar
            if self.conectado:
                self.conector.desconectar()
                self.conectado = False
                self.lbl_estado.config(text="Desconectado", foreground="red")
                
                # Crear nuevo conector según el modo
                if self.simulacion.get():
                    self.conector = SimuladorMT5()
                else:
                    self.conector = ConectorMT5()
                
                # Reconectar
                if self.conector.conectar():
                    self.conectado = True
                    self.lbl_estado.config(text="Conectado", foreground="green")
                    self.mostrar_alerta("Conexión reconectada", "info")
                    
                    # Actualizar información
                    self.actualizar_divisas_disponibles()
                    self.cargar_estrategias()
                    self.inicializar_estrategia()
                    self.btn_bot.state(['!disabled'])
                else:
                    self.mostrar_alerta("Error al reconectar", "error")
            
        except Exception as e:
            error_msg = f"Error al cambiar modo de conexión: {str(e)}"
            self.mostrar_alerta(error_msg, "error")
            self.logger.log_error(error_msg)

    def iniciar(self):
        """
        Inicia la interfaz gráfica
        """
        try:
            self.crear_interfaz()
            self.root.mainloop()
        except Exception as e:
            error_msg = f"Error al iniciar la interfaz: {str(e)}"
            self.logger.log_error(error_msg)
            messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    app = InterfazTrading()
    app.iniciar()
