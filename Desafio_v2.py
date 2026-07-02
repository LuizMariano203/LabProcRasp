#!/usr/bin/env python3
# -*- coding: utf-8 -*-
########################################################################
# PCS3732 - Aula 08 | Desafio Standalone
# Calculadora com Teclado Matricial 4x4 + Display LCD I2C 16x2
#
# CORRECAO DO BUG DE DEBOUNCE:
#   O Desafio.py original usava varredura GPIO manual com sleep(0.2),
#   o que nao elimina bounce de contato e registra a mesma tecla
#   multiplas vezes. Aqui usamos Keypad.Keypad que implementa uma
#   maquina de estados IDLE->PRESSED->HOLD->RELEASED e so dispara
#   uma vez por pressao (evento PRESSED com stateChanged=True).
#
# Pinagem (BCM) - igual ao MatrixKeypad.py do kit Freenove:
#   Linhas (OUT): 16, 20, 21, 26
#   Colunas (IN) : 19, 13,  6,  5
#   LCD I2C      : SDA=GPIO2, SCL=GPIO3  (endereco 0x27 ou 0x3F)
#
# Mapeamento de teclas:
#   A -> + (soma)        B -> - (subtracao)
#   C -> * (multiplic.)  D -> / (divisao)
#   # -> = (calcular)    * -> C (limpar)
#
# Uso:
#   sudo python3 Desafio_v2.py
########################################################################

import Keypad
from LCD1602 import CharLCD1602
from time import sleep

# ──────────────────────────────────────────────────────────────────────
# Configuracao do teclado matricial
# ──────────────────────────────────────────────────────────────────────

ROWS = 4
COLS = 4

KEYS = [
    '1', '2', '3', 'A',
    '4', '5', '6', 'B',
    '7', '8', '9', 'C',
    '*', '0', '#', 'D'
]

# Pinos BCM identicos ao MatrixKeypad.py do kit
ROW_PINS = [16, 20, 21, 26]   # saidas
COL_PINS = [19, 13,  6,  5]   # entradas com pull-up interno

# ──────────────────────────────────────────────────────────────────────
# Inicializacao
# ──────────────────────────────────────────────────────────────────────

keypad = Keypad.Keypad(KEYS, ROW_PINS, COL_PINS, ROWS, COLS)
keypad.setDebounceTime(50)   # 50 ms debounce na maquina de estados

lcd = CharLCD1602()
lcd.init_lcd()

# ──────────────────────────────────────────────────────────────────────
# Estado da calculadora
# ──────────────────────────────────────────────────────────────────────

numero1  = ""
numero2  = ""
operacao = None   # '+', '-', '*', '/'


# ──────────────────────────────────────────────────────────────────────
# Helpers de display
# ──────────────────────────────────────────────────────────────────────

def mostrar():
    """Atualiza o LCD com o estado atual da expressao."""
    lcd.clear()
    linha1 = numero1
    if operacao:
        linha1 += operacao
    linha1 += numero2
    lcd.write(0, 0, linha1[:16])
    lcd.write(0, 1, "#=OK  *=Limpar")


def mostrar_resultado(linha1, linha2=""):
    lcd.clear()
    lcd.write(0, 0, str(linha1)[:16])
    lcd.write(0, 1, str(linha2)[:16])


# ──────────────────────────────────────────────────────────────────────
# Acoes da calculadora
# ──────────────────────────────────────────────────────────────────────

def limpar():
    global numero1, numero2, operacao
    numero1  = ""
    numero2  = ""
    operacao = None
    mostrar()


def calcular():
    global numero1, numero2, operacao

    if numero1 == "" or numero2 == "" or operacao is None:
        mostrar_resultado("Expr incompleta", "")
        sleep(1.5)
        mostrar()
        return

    a = int(numero1)
    b = int(numero2)

    if operacao == '+':
        resultado = a + b
        label = "Resultado:"
    elif operacao == '-':
        resultado = a - b
        label = "Resultado:"
    elif operacao == '*':
        resultado = a * b
        label = "Resultado:"
    elif operacao == '/':
        if b == 0:
            mostrar_resultado("ERRO", "Div por zero!")
            sleep(2)
            limpar()
            return
        resultado = a // b
        resto     = a % b
        mostrar_resultado(f"{a}/{b}={resultado}", f"Resto: {resto}")
        sleep(3)
        limpar()
        return

    mostrar_resultado(label, str(resultado))
    sleep(3)
    limpar()


# ──────────────────────────────────────────────────────────────────────
# Loop principal
# ──────────────────────────────────────────────────────────────────────

def processar_tecla(tecla):
    """Decide o que fazer com cada tecla recebida."""
    global numero1, numero2, operacao

    if tecla == '*':          # Limpar / CE
        limpar()

    elif tecla == '#':        # Calcular / Enter
        calcular()

    elif tecla == 'A':        # Operacao: soma
        operacao = '+'
        mostrar()

    elif tecla == 'B':        # Operacao: subtracao
        operacao = '-'
        mostrar()

    elif tecla == 'C':        # Operacao: multiplicacao
        operacao = '*'
        mostrar()

    elif tecla == 'D':        # Operacao: divisao
        operacao = '/'
        mostrar()

    else:                     # Digito numerico (0-9)
        if operacao is None:
            # Limite de 7 digitos por operando para caber no LCD
            if len(numero1) < 7:
                numero1 += tecla
        else:
            if len(numero2) < 7:
                numero2 += tecla
        mostrar()


def main():
    print("PCS3732 - Calculadora Standalone iniciando...")
    limpar()

    while True:
        # getKey() so retorna um char quando o estado muda para PRESSED
        # (stateChanged=True && kstate==PRESSED), garantindo um unico
        # evento por pressao fisica. Retorna keypad.NULL ('\0') se nada.
        tecla = keypad.getKey()

        if tecla != keypad.NULL:
            print(f"Tecla: {tecla}")   # debug: aparece no terminal serial
            processar_tecla(tecla)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        lcd.clear()
        print("\nEncerrado.")
