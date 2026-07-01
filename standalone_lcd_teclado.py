#!/usr/bin/env python3
"""
PCS3732 – Aula 08 | Desafio Standalone
Calculadora Binária com Teclado Matricial 4×4 + Display LCD I2C
Plataforma: Raspberry Pi 3

Hardware necessário:
  - Teclado matricial 4×4
  - Display LCD 16×2 com módulo I2C PCF8574 (endereço padrão: 0x27)

Dependências:
  pip install smbus2 RPi.GPIO --break-system-packages

Pinagem GPIO (BCM):
  Linhas do teclado : GPIO 18, 23, 24, 25  (saída)
  Colunas do teclado: GPIO 12, 16, 20, 21  (entrada, pull-up)
  LCD I2C SDA       : GPIO 2  (pino físico 3)
  LCD I2C SCL       : GPIO 3  (pino físico 5)
  Habilitar I2C     : sudo raspi-config → Interface Options → I2C → Enable
"""

import time
import sys

# Guard de importação: só importa RPi.GPIO e smbus2 se estivermos no Rasp3
try:
    import RPi.GPIO as GPIO
    import smbus2
    HARDWARE_OK = True
except ImportError:
    HARDWARE_OK = False
    print("  AVISO: RPi.GPIO / smbus2 não disponíveis.")
    print("  Executando em modo simulação (PC). Instale no Raspberry Pi 3.")
    print()


# ══════════════════════════════════════════════════════════════════════════════
#  DRIVER LCD I2C (PCF8574 – 4 bits)
# ══════════════════════════════════════════════════════════════════════════════

LCD_ADDR    = 0x27   # endereço I2C padrão; tente 0x3F se não funcionar
LCD_CHR     = 1      # modo dado
LCD_CMD     = 0      # modo comando
LCD_BACKLIGHT = 0x08 # bit de backlight
ENABLE      = 0b00000100

LCD_LINE_1 = 0x80   # endereço DDRAM linha 1
LCD_LINE_2 = 0xC0   # endereço DDRAM linha 2


class LcdI2C:
    """Driver minimalista para LCD HD44780 via expansor PCF8574 no barramento I2C."""

    def __init__(self, addr=LCD_ADDR, bus_num=1):
        if not HARDWARE_OK:
            self._sim = True
            return
        self._sim = False
        self.bus = smbus2.SMBus(bus_num)
        self.addr = addr
        self._init_lcd()

    def _byte_lcd(self, data):
        self.bus.write_byte(self.addr, data)

    def _toggle_enable(self, data):
        time.sleep(0.0005)
        self._byte_lcd(data | ENABLE)
        time.sleep(0.0005)
        self._byte_lcd(data & ~ENABLE)
        time.sleep(0.0005)

    def _send(self, data, mode):
        """Envia byte em dois nibbles (4-bit mode)."""
        high = mode | LCD_BACKLIGHT | (data & 0xF0)
        low  = mode | LCD_BACKLIGHT | ((data << 4) & 0xF0)
        self._toggle_enable(high)
        self._toggle_enable(low)

    def _init_lcd(self):
        self._send(0x33, LCD_CMD)
        self._send(0x32, LCD_CMD)
        self._send(0x06, LCD_CMD)  # cursor move direction
        self._send(0x0C, LCD_CMD)  # display on, cursor off
        self._send(0x28, LCD_CMD)  # 4-bit, 2 lines, 5×8 dots
        self._send(0x01, LCD_CMD)  # clear display
        time.sleep(0.002)

    def clear(self):
        if self._sim:
            print("  [LCD] <clear>")
            return
        self._send(0x01, LCD_CMD)
        time.sleep(0.002)

    def escrever(self, texto, linha=1):
        """Escreve texto na linha 1 ou 2, truncando a 16 caracteres."""
        texto = str(texto)[:16].ljust(16)
        if self._sim:
            print(f"  [LCD L{linha}] {texto}")
            return
        addr = LCD_LINE_1 if linha == 1 else LCD_LINE_2
        self._send(addr, LCD_CMD)
        for ch in texto:
            self._send(ord(ch), LCD_CHR)

    def mensagem(self, linha1="", linha2=""):
        self.clear()
        self.escrever(linha1, 1)
        self.escrever(linha2, 2)


# ══════════════════════════════════════════════════════════════════════════════
#  DRIVER TECLADO MATRICIAL 4×4
# ══════════════════════════════════════════════════════════════════════════════

LINHAS_GPIO = [18, 23, 24, 25]
COLUNAS_GPIO = [12, 16, 20, 21]

MAPA_TECLAS = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D'],
]
# Mapeamento de teclas especiais do teclado matricial:
#   A → + (soma)
#   B → - (subtração)
#   C → * (multiplicação)
#   D → / (divisão)
#   # → ! (fatorial)
#   * → = (executar / confirmar)
MAPA_FUNCOES = {
    'A': '+', 'B': '-', 'C': '*', 'D': '/', '#': '!', '*': '=',
}


class TecladoMatricial:
    def __init__(self):
        if not HARDWARE_OK:
            self._sim = True
            return
        self._sim = False
        GPIO.setmode(GPIO.BCM)
        for r in LINHAS_GPIO:
            GPIO.setup(r, GPIO.OUT, initial=GPIO.HIGH)
        for c in COLUNAS_GPIO:
            GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def ler_tecla(self) -> str | None:
        """Varredura de matriz linha×coluna. Retorna tecla pressionada ou None."""
        if self._sim:
            return None
        for i, linha in enumerate(LINHAS_GPIO):
            GPIO.output(linha, GPIO.LOW)
            for j, col in enumerate(COLUNAS_GPIO):
                if GPIO.input(col) == GPIO.LOW:
                    GPIO.output(linha, GPIO.HIGH)
                    time.sleep(0.05)   # debounce
                    return MAPA_TECLAS[i][j]
            GPIO.output(linha, GPIO.HIGH)
        return None

    def aguardar_tecla(self, timeout_s=30) -> str | None:
        """Bloqueia até uma tecla ser pressionada ou timeout."""
        if self._sim:
            return input("  [SIM teclado] > ").strip() or None
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            k = self.ler_tecla()
            if k:
                return k
            time.sleep(0.01)
        return None

    def cleanup(self):
        if not self._sim:
            GPIO.cleanup()


# ══════════════════════════════════════════════════════════════════════════════
#  NÚCLEO ARITMÉTICO (copiado do calculadora_rasp3.py para autossuficiência)
# ══════════════════════════════════════════════════════════════════════════════

def mascara(n):  return (1 << n) - 1

def soma(a, b, n):
    r = a + b; m = mascara(n)
    return r & m, r > m

def sub(a, b, n):
    r = a - b
    return r & mascara(n), r < 0

def mul(a, b, n):
    r = a * b; m = mascara(n)
    return r & m, r > m

def fat(a, n):
    if a > 20: return None, True
    r = 1
    for i in range(2, a + 1): r *= i
    m = mascara(n)
    return r & m, r > m

def div(a, b, n):
    if b == 0: return None, True
    return (a // b) & mascara(n), False


# ══════════════════════════════════════════════════════════════════════════════
#  INTERFACE STANDALONE
# ══════════════════════════════════════════════════════════════════════════════
# Fluxo de entrada via teclado matricial:
#   1. Digite o primeiro operando (dígitos 0-9, confirme com *)
#   2. Pressione a tecla de operação (A=+, B=-, C=×, D=÷, #=!)
#   3. [Para binário] Digite o segundo operando e confirme com *
#   4. Resultado exibido no LCD por 3 segundos, depois volta ao início


class CalculadoraStandalone:
    def __init__(self, n_bits=4):
        self.n_bits  = n_bits
        self.lcd     = LcdI2C()
        self.teclado = TecladoMatricial()
        self.max_val = mascara(n_bits)

    def _ler_numero(self, prompt_lcd: str) -> int | None:
        """Coleta dígitos do teclado até '*' (confirmar) ou '#' (cancelar)."""
        self.lcd.mensagem(prompt_lcd, "* = OK  # = DEL")
        buffer = ""
        while True:
            k = self.teclado.aguardar_tecla()
            if k is None:
                return None
            if k == '*':
                if buffer == "":
                    return None
                try:
                    v = int(buffer)
                    if 0 <= v <= self.max_val:
                        return v
                    self.lcd.mensagem("Fora do range!", f"Max={self.max_val}")
                    time.sleep(1.5)
                    buffer = ""
                    self.lcd.mensagem(prompt_lcd, "* = OK  # = DEL")
                except ValueError:
                    buffer = ""
            elif k == '#':
                buffer = buffer[:-1]
                self.lcd.escrever(buffer.ljust(16), 2)
            elif k in "0123456789":
                if len(buffer) < 3:
                    buffer += k
                    self.lcd.escrever(buffer.ljust(16), 2)
            # Ignora A,B,C,D durante digitação de número

    def _exibir_resultado(self, linha1: str, linha2: str):
        self.lcd.mensagem(linha1[:16], linha2[:16])
        time.sleep(3)

    def loop(self):
        self.lcd.mensagem("PCS3732 Calc", f"{self.n_bits}-bit ARM")
        time.sleep(2)

        while True:
            # Passo 1: primeiro operando
            self.lcd.mensagem("Operando A:", "* conf | # del")
            a = self._ler_numero("Operando A:")
            if a is None:
                continue

            # Passo 2: operação
            self.lcd.mensagem(f"A={a}  Op?", "A+B-C*D/#!")
            op_key = None
            while op_key not in ('A', 'B', 'C', 'D', '#'):
                op_key = self.teclado.aguardar_tecla()

            op = MAPA_FUNCOES[op_key]

            # Fatorial é unário
            if op == '!':
                r, ov = fat(a, self.n_bits)
                if r is None or ov:
                    self._exibir_resultado(f"{a}! OVERFLOW", f">{self.n_bits}bits")
                else:
                    import math as _m
                    self._exibir_resultado(f"{a}!={_m.factorial(a)}", f"bin:{r:0{self.n_bits}b}")
                continue

            # Passo 3: segundo operando
            b = self._ler_numero(f"A={a} {op} B=?")
            if b is None:
                continue

            # Passo 4: calcular
            if op == '+':
                r, flag = soma(a, b, self.n_bits)
                flag_str = "OVERFLOW" if flag else f"bin:{r:0{self.n_bits}b}"
                self._exibir_resultado(f"{a}+{b}={a+b}", flag_str)
            elif op == '-':
                r, flag = sub(a, b, self.n_bits)
                flag_str = "NEGATIVO" if flag else f"bin:{r:0{self.n_bits}b}"
                self._exibir_resultado(f"{a}-{b}={a-b}", flag_str)
            elif op == '*':
                r, flag = mul(a, b, self.n_bits)
                flag_str = "OVERFLOW" if flag else f"bin:{r:0{self.n_bits}b}"
                self._exibir_resultado(f"{a}x{b}={a*b}", flag_str)
            elif op == '/':
                r, flag = div(a, b, self.n_bits)
                if flag:
                    self._exibir_resultado("DIV/ZERO!", "Sem trap HW")
                else:
                    self._exibir_resultado(f"{a}/{b}={a//b}", f"rst:{a%b} bin:{r:0{self.n_bits}b}")

    def __del__(self):
        try:
            self.teclado.cleanup()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Calculadora Standalone LCD+Teclado")
    parser.add_argument("--bits", type=int, default=4, choices=[4, 8],
                        help="Largura de bits (padrão: 4)")
    args = parser.parse_args()

    print(f"Iniciando calculadora standalone – {args.bits} bits")
    print("Hardware:", "OK (Raspberry Pi)" if HARDWARE_OK else "SIMULAÇÃO (PC)")
    print("Pressione Ctrl+C para encerrar.\n")

    calc = CalculadoraStandalone(n_bits=args.bits)
    try:
        calc.loop()
    except KeyboardInterrupt:
        calc.lcd.mensagem("Encerrando...", "")
        time.sleep(1)
        calc.lcd.clear()
        print("\nEncerrado.")


if __name__ == "__main__":
    main()
