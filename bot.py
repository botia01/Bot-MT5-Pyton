import tkinter as tk
from tkinter import ttk, messagebox
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
        
        # Inicializar conector (se actualizará cuando se seleccione el modo)
        
        # Variables de control
        self.par_divisa = tk.StringVar(value=self.config.get("par_defecto", "EURUSD"))
        self.estrategia_seleccionada = tk.StringVar()
        self.simulacion = tk.BooleanVar(value=self.config.get("modo_simulacion", False))
        self.bot_encendido = False
        
        # Inicializar estilos
        self.estilos = Estilos()
        
        # Crear interfaz
        self.crear_interfaz()
        
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

    def inicializar_estrategia(self):
        """
        Inicializa la estrategia seleccionada
        """
        try:
            estrategia_actual = self.config.get("estrategia", "")
            if estrategia_actual:
                self.estrategia_seleccionada.set(estrategia_actual)
                # Crear la estrategia usando el registro
                self.estrategia = crear_estrategia(estrategia_actual, self.conector)
                if self.estrategia:
                    self.mostrar_alerta(f"Estrategia inicializada: {estrategia_actual}")
                    self.logger.log_info(f"Estrategia inicializada: {estrategia_actual}")
                else:
                    raise ValueError(f"Estrategia no válida: {estrategia_actual}")
        except Exception as e:
            error_msg = f"Error al inicializar estrategia: {str(e)}"
            self.mostrar_alerta(error_msg, tipo='error')
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
            
            # Aplicar estilo según el tipo de mensaje
            if tipo == 'error':
                self.txt_mensajes.tag_add('error', f'{self.txt_mensajes.index(tk.END)}-2l', f'{self.txt_mensajes.index(tk.END)}-1l')
            elif tipo == 'warning':
                self.txt_mensajes.tag_add('warning', f'{self.txt_mensajes.index(tk.END)}-2l', f'{self.txt_mensajes.index(tk.END)}-1l')
            else:
                self.txt_mensajes.tag_add('info', f'{self.txt_mensajes.index(tk.END)}-2l', f'{self.txt_mensajes.index(tk.END)}-1l')
                
            self.txt_mensajes.config(state='disabled')
            
            # Mostrar alerta si es un error o advertencia
            if tipo in ['error', 'warning']:
                mostrar_alerta(mensaje, tipo)
            
        except Exception as e:
            error_msg = f"Error al mostrar mensaje: {str(e)}"
            self.logger.log_error(error_msg)
            print(error_msg)

    def cambiar_divisa(self, event):
        """
        Actualiza la divisa seleccionada
        """
        try:
            divisa = self.cmb_divisa.get()
            if divisa:
                self.par_divisa.set(divisa)  # Usar el nombre del par directamente
                self.conector.par_divisas = divisa
                self.mostrar_mensaje(f"Divisa seleccionada: {divisa}")
        except Exception as e:
            self.logger.log_error(f"Error al cambiar divisa: {str(e)}")
            self.mostrar_alerta(f"Error al cambiar divisa: {str(e)}", "error")

    def seleccionar_estrategia(self, event):
        """
        Maneja la selección de estrategia
        """
        seleccion = self.cmb_estrategia.get()
        if seleccion:
            try:
                # Crear la estrategia usando el registro
                self.estrategia = crear_estrategia(seleccion, self.conector)
                if self.estrategia:
                    self.estrategia_seleccionada.set(seleccion)
                    self.mostrar_alerta(f"Estrategia seleccionada: {seleccion}")
                    self.logger.log_info(f"Estrategia seleccionada: {seleccion}")
                else:
                    raise ValueError(f"Estrategia no válida: {seleccion}")
            except Exception as e:
                error_msg = f"Error al seleccionar estrategia: {str(e)}"
                self.mostrar_alerta(error_msg, "error")
                self.logger.log_error(error_msg)
                self.estrategia = None
                self.estrategia_seleccionada.set("")

    def actualizar_modo_conexion(self):
        """
        Actualiza el modo de conexión según el checkbox de simulación
        """
        try:
            if self.simulacion.get():
                self.conector = SimuladorMT5()
            else:
                self.conector = ConectorMT5()
            self.actualizar_interfaz(False)  # Limpiar información de cuenta
            self.mostrar_alerta("Modo de conexión actualizado", "info")
        except Exception as e:
            error_msg = f"Error al actualizar el modo de conexión: {str(e)}"
            self.mostrar_alerta(error_msg, "error")
            self.logger.log_error(error_msg)

    def conectar(self):
        """
        Establece o desconecta la conexión con MetaTrader 5
        """
        try:
            if not self.conectado:
                # Conectar
                self.btn_conectar.config(text="Desconectar")
                # Inicializar conector
                if not self.conector:
                    if self.simulacion.get():
                        self.conector = SimuladorMT5()
                    else:
                        self.conector = ConectorMT5()
                
                if self.conector.conectar():
                    self.conectado = True
                    self.actualizar_interfaz(True)
                    self.mostrar_alerta("Conectado exitosamente", "info")
                    self.logger.log_info("Conexión exitosa")
                    
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
                            self.mostrar_alerta(f"Error al procesar información de cuenta: {str(e)}", "error")
                    return True
                else:
                    self.mostrar_alerta("Error al conectar", "error")
                    return False
            else:
                # Desconectar
                self.btn_conectar.config(text="Conectar")
                if self.conector.desconectar():
                    self.conectado = False
                    self.actualizar_interfaz(False)
                    self.mostrar_alerta("Desconectado exitosamente", "info")
                    self.logger.log_info("Desconexión exitosa")
                    return True
                else:
                    self.mostrar_alerta("Error al desconectar", "error")
                    return False
        except Exception as e:
            error_msg = f"Error en la conexión: {str(e)}"
            self.mostrar_alerta(error_msg, "error")
            self.logger.log_error(error_msg)
            return False

    def actualizar_interfaz(self, conectado):
        """
        Actualiza la interfaz según el estado de conexión
        """
        try:
            if conectado:
                self.lbl_estado.config(text="Conectado", foreground="green")
                self.btn_conectar.config(text="Desconectar")
                self.btn_bot.state(['!disabled'])  # Habilitar botón Start
                
                # Actualizar combos
                if isinstance(self.conector, ConectorMT5):
                    # Para MT5 real
                    try:
                        # Obtener divisas y extraer solo los nombres
                        divisas = self.conector.obtener_divisas_disponibles()
                        nombres_divisas = [divisa[0] for divisa in divisas] if divisas else []
                        self.cmb_divisa['values'] = nombres_divisas
                        if nombres_divisas:
                            self.cmb_divisa.set(nombres_divisas[0])  # Establecer primera divisa por defecto
                    except Exception as e:
                        self.logger.log_error(f"Error al obtener divisas: {str(e)}")
                        self.mostrar_mensaje(f"Error al obtener divisas: {str(e)}", tipo='error')
                        self.cmb_divisa['values'] = []
                        self.cmb_divisa.set('')
                else:
                    # Para simulación
                    self.cmb_divisa['values'] = ["EURUSD", "GBPUSD", "USDJPY"]
                    self.cmb_divisa.set("EURUSD")
                
                # Actualizar estrategias
                try:
                    estrategias = obtener_estrategias_disponibles()
                    self.cmb_estrategia['values'] = estrategias
                    if estrategias:
                        self.cmb_estrategia.set(estrategias[0])  # Establecer primera estrategia por defecto
                except Exception as e:
                    self.logger.log_error(f"Error al obtener estrategias: {str(e)}")
                    self.mostrar_mensaje(f"Error al obtener estrategias: {str(e)}", tipo='error')
                    self.cmb_estrategia['values'] = []
                    self.cmb_estrategia.set('')
                
                self.mostrar_alerta("Conectado exitosamente", "info")
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
                self.cmb_divisa['values'] = []
                self.cmb_divisa.set('')
                self.cmb_estrategia['values'] = []
                self.cmb_estrategia.set('')
        except Exception as e:
            error_msg = f"Error al actualizar interfaz: {str(e)}"
            self.mostrar_alerta(error_msg, "error")
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
            self.apagar_bot()

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

    def crear_interfaz(self):
        """
        Crea los elementos de la interfaz gráfica con un diseño moderno y atractivo
        """
        try:
            # Crear el frame principal
            main_frame = ttk.Frame(self.root)
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
            
            # Organizar en dos columnas principales
            left_frame = ttk.LabelFrame(main_frame, text="Conexión y Configuración", padding="15 10")
            left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))

            # Agregar checkbox para modo simulación
            chk_simulacion = ttk.Checkbutton(left_frame, text="Modo Simulación", 
                                           variable=self.simulacion,
                                           command=self.actualizar_modo_conexion)
            chk_simulacion.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
            
            # Frame para conexión
            frame_conexion = ttk.Frame(left_frame)
            frame_conexion.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
            
            # Estado de conexión
            ttk.Label(frame_conexion, text="Estado:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            self.lbl_estado = ttk.Label(frame_conexion, text="Desconectado", foreground="red")
            self.lbl_estado.grid(row=0, column=1, sticky=tk.W)
            
            # Botón de conexión
            self.btn_conectar = ttk.Button(frame_conexion, text="Conectar", command=self.conectar)
            self.btn_conectar.grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
            
            # Frame para configuración
            frame_config = ttk.LabelFrame(left_frame, text="Configuración", padding="10 5")
            frame_config.grid(row=2, column=0, sticky=(tk.W, tk.E))
            
            # Par de divisas
            ttk.Label(frame_config, text="Divisa:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            self.cmb_divisa = ttk.Combobox(frame_config, textvariable=self.par_divisa, width=10, state='readonly')
            self.cmb_divisa.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            self.cmb_divisa.bind('<<ComboboxSelected>>', self.cambiar_divisa)
            self.cmb_divisa['values'] = []  # Iniciar sin valores
            self.cmb_divisa.set('')  # Iniciar vacío
            
            # Estrategia
            ttk.Label(frame_config, text="Estrategia:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            self.cmb_estrategia = ttk.Combobox(frame_config, textvariable=self.estrategia_seleccionada, width=15, state='readonly')
            self.cmb_estrategia.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
            self.cmb_estrategia.bind('<<ComboboxSelected>>', self.seleccionar_estrategia)
            self.cmb_estrategia['values'] = []  # Iniciar sin valores
            self.cmb_estrategia.set('')  # Iniciar vacío
            
            # Inicializar estrategias disponibles
            estrategias = obtener_estrategias_disponibles()
            self.cmb_estrategia['values'] = estrategias
            
            # Frame para el bot
            frame_bot = ttk.LabelFrame(left_frame, text="Control del Bot", padding="10 5")
            frame_bot.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
            
            # Estado del bot
            ttk.Label(frame_bot, text="Estado del Bot:").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.lbl_estado_bot = ttk.Label(frame_bot, text="Apagado", foreground="red")
            self.lbl_estado_bot.grid(row=0, column=1, sticky=tk.W, padx=5)
            
            # Botón de control del bot
            self.btn_bot = ttk.Button(frame_bot, text="Start Bot", command=self.toggle_bot)
            self.btn_bot.grid(row=0, column=2, sticky=tk.W, padx=5)
            self.btn_bot.state(['disabled'])
            
            # Frame para información de cuenta
            frame_cuenta = ttk.LabelFrame(left_frame, text="Información de Cuenta", padding="10 5")
            frame_cuenta.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
            
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
            
            # Frame para el bot
            frame_bot = ttk.LabelFrame(left_frame, text="Control del Bot", padding="10 5")
            frame_bot.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
            
            # Estado del bot
            ttk.Label(frame_bot, text="Estado del Bot:").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.lbl_estado_bot = ttk.Label(frame_bot, text="Apagado", foreground="red")
            self.lbl_estado_bot.grid(row=0, column=1, sticky=tk.W, padx=5)
            
            # Botón de control del bot
            self.btn_bot = ttk.Button(frame_bot, text="Start Bot", command=self.toggle_bot)
            self.btn_bot.grid(row=0, column=2, sticky=tk.W, padx=5)
            self.btn_bot.state(['disabled'])
            
            # Frame para estadísticas
            frame_estadisticas = ttk.LabelFrame(left_frame, text="Estadísticas", padding="10 5")
            frame_estadisticas.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
            
            # Ganancias
            ttk.Label(frame_estadisticas, text="Ganancias:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            self.lbl_ganancias = ttk.Label(frame_estadisticas, text="0.00", style='Estadisticas.TLabel')
            self.lbl_ganancias.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Pérdidas
            ttk.Label(frame_estadisticas, text="Pérdidas:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            self.lbl_perdidas = ttk.Label(frame_estadisticas, text="0.00", style='Estadisticas.TLabel')
            self.lbl_perdidas.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
            
            # Verificar que los labels estén inicializados
            if not hasattr(self, 'lbl_ganancias') or not hasattr(self, 'lbl_perdidas'):
                raise ValueError("Error: Los labels de estadísticas no se inicializaron correctamente")
            
            # Frame para mensajes
            right_frame = ttk.LabelFrame(main_frame, text="Mensajes del Bot", padding="15 10")
            right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configurar el grid para que se expanda
            main_frame.grid_rowconfigure(0, weight=1)
            main_frame.grid_columnconfigure(1, weight=1)
            
            # Área para mostrar mensajes del bot con diseño moderno
            self.txt_mensajes = tk.Text(right_frame, height=10, width=50, bg='#262626', fg='white')
            self.txt_mensajes.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configurar tags para diferentes tipos de mensajes
            self.txt_mensajes.tag_configure('info', foreground='#00FF00')
            self.txt_mensajes.tag_configure('error', foreground='#FF0000')
            self.txt_mensajes.tag_configure('warning', foreground='#FFA500')
            self.txt_mensajes.config(state='disabled')
            
            # Mostrar mensaje de inicio
            self.mostrar_mensaje("Sistema iniciado correctamente", tipo='info')
            
            # Configurar el combobox con un valor por defecto
            self.cmb_divisa['values'] = ["EURUSD", "GBPUSD", "USDJPY"]  # Lista por defecto
            self.cmb_divisa.set("EURUSD")  # Valor por defecto
            
            # Configurar el combobox de estrategias con las estrategias disponibles
            self.cmb_estrategia['values'] = obtener_estrategias_disponibles()
            self.cmb_estrategia.set(obtener_estrategias_disponibles()[0])  # Valor por defecto
            
            self.logger.log_info("Interfaz creada exitosamente")
            
        except Exception as e:
            error_msg = f"Error al crear interfaz: {str(e)}"
            self.mostrar_alerta(error_msg, tipo='error')
            self.logger.log_error(error_msg)
            raise Exception(error_msg)  # Propagar el error para que se vea en la consola

    def limpiar_info_cuenta(self):
        """
        Limpia la información de cuenta
        """
        self.lbl_cuenta.config(text="-")
        self.lbl_balance.config(text="-")
        self.lbl_equity.config(text="-")

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
