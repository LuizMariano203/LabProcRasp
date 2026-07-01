#!/usr/bin/env python3
"""
PCS3732 - Laboratório de Processadores | Aula 08
Calculadora Binária - Raspberry Pi 3 (ARM Cortex-A53)

Entrada : teclado USB conectado ao Rasp3
Saída   : monitor via HDMI-VGA

Operações suportadas (valores de 0 a 15 para 4 bits):
  +   soma
  -   subtração
  *   multiplicação
  !   fatorial (unário, ex: "5!")
  /   divisão (com tratamento de divisão por zero)

Uso:
  python3 calculadora_rasp3.py
  python3 calculadora_rasp3.py --bits 8    # modo 8 bits (0–255)
"""

import sys
import argparse

# ──────────────────────────────────────────────────────────────────────────────
# Constantes de configuração de bits
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_BITS = 4


# ──────────────────────────────────────────────────────────────────────────────
# Núcleo aritmético – todas as operações trabalham com inteiros Python puros
# (precisão arbitrária); a máscara de bits é aplicada ao final para simular
# o comportamento de registradores de N bits.
# ──────────────────────────────────────────────────────────────────────────────

def mascara(n_bits: int) -> int:
    """Retorna a máscara de N bits. Ex: 4 bits → 0xF (15)."""
    return (1 << n_bits) - 1


def op_soma(a: int, b: int, n_bits: int) -> dict:
    resultado_completo = a + b
    mask = mascara(n_bits)
    resultado = resultado_completo & mask
    overflow = resultado_completo > mask
    return {
        "resultado": resultado,
        "overflow": overflow,
        "negativo": False,
        "descricao": f"{a} + {b} = {resultado}" + (" [OVERFLOW]" if overflow else ""),
    }


def op_subtracao(a: int, b: int, n_bits: int) -> dict:
    resultado_completo = a - b
    mask = mascara(n_bits)
    negativo = resultado_completo < 0
    # Representação em complemento de 2 para N bits
    resultado = resultado_completo & mask
    return {
        "resultado": resultado,
        "overflow": False,
        "negativo": negativo,
        "descricao": (
            f"{a} - {b} = {resultado_completo}"
            + (f"  (complemento-2 {n_bits}b: {resultado:#0{n_bits+2}b})" if negativo else "")
        ),
    }


def op_multiplicacao(a: int, b: int, n_bits: int) -> dict:
    resultado_completo = a * b
    mask = mascara(n_bits)
    resultado = resultado_completo & mask
    overflow = resultado_completo > mask
    return {
        "resultado": resultado,
        "overflow": overflow,
        "negativo": False,
        "descricao": f"{a} × {b} = {resultado_completo}" + (" [OVERFLOW]" if overflow else ""),
    }


def op_fatorial(a: int, n_bits: int) -> dict:
    if a < 0:
        return {"resultado": None, "overflow": False, "negativo": False,
                "descricao": "ERRO: fatorial indefinido para números negativos"}
    if a > 20:
        return {"resultado": None, "overflow": True, "negativo": False,
                "descricao": f"ERRO: {a}! excede limite de representação"}

    resultado_completo = 1
    for i in range(2, a + 1):
        resultado_completo *= i

    mask = mascara(n_bits)
    resultado = resultado_completo & mask
    overflow = resultado_completo > mask
    return {
        "resultado": resultado,
        "overflow": overflow,
        "negativo": False,
        "descricao": (
            f"{a}! = {resultado_completo}"
            + (f" [OVERFLOW em {n_bits} bits, resultado truncado: {resultado}]" if overflow else "")
        ),
    }


def op_divisao(a: int, b: int, n_bits: int) -> dict:
    """
    Divisão inteira com tratamento explícito de divisão por zero.

    RISC-V (RV32M): DIVU retorna 2^XLEN−1 para divisão por zero (sem trap).
    ARM (AArch64):  UDIV com divisor zero retorna 0 (sem trap, comportamento definido).
    Esta implementação adota sinalização via flag para máxima clareza didática.
    """
    if b == 0:
        return {
            "resultado": None,
            "overflow": False,
            "negativo": False,
            "divisao_zero": True,
            "descricao": (
                f"ERRO: divisão por zero ({a} / 0)\n"
                "  → RISC-V (RV32M): DIVU retornaria 0xFFFFFFFF\n"
                "  → ARM AArch64:    UDIV retornaria 0\n"
                "  → Esta impl.:     operação cancelada; aguardando novo input."
            ),
        }

    quociente = a // b
    resto = a % b
    mask = mascara(n_bits)
    resultado = quociente & mask
    return {
        "resultado": resultado,
        "overflow": False,
        "negativo": False,
        "divisao_zero": False,
        "descricao": f"{a} ÷ {b} = {quociente}  (resto: {resto})",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Parser de expressões
# ──────────────────────────────────────────────────────────────────────────────

def parse_fatorial(expr: str):
    """Aceita '5!' ou '! 5'."""
    expr = expr.strip()
    if expr.endswith("!"):
        return int(expr[:-1].strip()), None
    partes = expr.split("!")
    if len(partes) == 2:
        return int(partes[1].strip()), None
    raise ValueError(f"Formato inválido para fatorial: '{expr}'")


def parse_binaria(expr: str, n_bits: int):
    """
    Interpreta uma expressão como:
      '5 + 3'  '1010 + 0011'  (aceita decimal ou binário com prefixo 0b/b)
      '5!'     '! 5'
    Retorna (operador, operando_a, operando_b_ou_None).
    """
    expr = expr.strip()
    ops = ["+", "-", "*", "/"]
    max_val = mascara(n_bits)

    # Fatorial
    if "!" in expr:
        a, _ = parse_fatorial(expr)
        if not (0 <= a <= max_val):
            raise ValueError(f"Operando {a} fora do intervalo [0, {max_val}] para {n_bits} bits")
        return "!", a, None

    # Operação binária
    for op in ops:
        if op in expr:
            partes = expr.split(op, 1)
            a_str, b_str = partes[0].strip(), partes[1].strip()

            def parse_num(s):
                if s.startswith("0b") or s.startswith("b"):
                    return int(s.lstrip("b").lstrip("0b"), 2)
                return int(s)

            a, b = parse_num(a_str), parse_num(b_str)
            if not (0 <= a <= max_val):
                raise ValueError(f"Operando A={a} fora do intervalo [0, {max_val}]")
            if not (0 <= b <= max_val):
                raise ValueError(f"Operando B={b} fora do intervalo [0, {max_val}]")
            return op, a, b

    raise ValueError(f"Expressão não reconhecida: '{expr}'. Use: A op B  ou  N!")


# ──────────────────────────────────────────────────────────────────────────────
# Formatação de saída
# ──────────────────────────────────────────────────────────────────────────────

def formatar_resultado(op_str: str, a, b, res: dict, n_bits: int) -> str:
    sep = "─" * 50
    linhas = [
        sep,
        f"  Operação  : {op_str}",
    ]
    if b is not None:
        linhas.append(f"  Operandos : A = {a}  (bin: {a:0{n_bits}b})  |  B = {b}  (bin: {b:0{n_bits}b})")
    else:
        linhas.append(f"  Operando  : {a}  (bin: {a:0{n_bits}b})")

    linhas.append(f"  Resultado : {res['descricao']}")

    if res.get("resultado") is not None:
        r = res["resultado"]
        linhas.append(f"  Binário   : {r:0{n_bits}b}")
        linhas.append(f"  Hex       : 0x{r:0{(n_bits+3)//4}X}")

    flags = []
    if res.get("overflow"):   flags.append("OVERFLOW")
    if res.get("negativo"):   flags.append("NEGATIVO")
    if res.get("divisao_zero"): flags.append("DIV/ZERO")
    if flags:
        linhas.append(f"  Flags     : {', '.join(flags)}")

    linhas.append(sep)
    return "\n".join(linhas)


# ──────────────────────────────────────────────────────────────────────────────
# Loop principal (REPL)
# ──────────────────────────────────────────────────────────────────────────────

BANNER = r"""
╔══════════════════════════════════════════════════════╗
║   PCS3732 – Calculadora Binária  │  Raspberry Pi 3  ║
║   ARM Cortex-A53 (AArch64)                          ║
╚══════════════════════════════════════════════════════╝
  Operações: A + B  │  A - B  │  A * B  │  A / B  │  N!
  Digite 'bits N' para mudar largura  │  'ajuda'  │  'sair'
"""

AJUDA = """
AJUDA – Exemplos de entrada
  4 + 3          → soma decimal
  0b0101 + 0011  → soma binária (prefixo 0b ou b)
  7 - 10         → subtração (resultado negativo sinalizado)
  3 * 5          → multiplicação
  12 / 4         → divisão inteira
  5!             → fatorial (também aceita: ! 5)
  bits 8         → muda para 8 bits (operandos 0–255)
  bits 4         → volta para 4 bits
  sair           → encerra o programa
"""


def main():
    parser = argparse.ArgumentParser(description="Calculadora Binária – Raspberry Pi 3")
    parser.add_argument("--bits", type=int, default=DEFAULT_BITS,
                        choices=[4, 8, 16, 32, 64],
                        help="Largura de bits inicial (padrão: 4)")
    args = parser.parse_args()
    n_bits = args.bits

    print(BANNER)
    print(f"  Modo inicial: {n_bits} bits  (operandos de 0 a {mascara(n_bits)})\n")

    while True:
        try:
            entrada = input(f"[{n_bits}b] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Encerrando calculadora. Até logo!")
            sys.exit(0)

        if not entrada:
            continue

        if entrada.lower() in ("sair", "exit", "quit"):
            print("  Encerrando calculadora. Até logo!")
            break

        if entrada.lower() == "ajuda":
            print(AJUDA)
            continue

        # Comando 'bits N'
        if entrada.lower().startswith("bits"):
            partes = entrada.split()
            if len(partes) == 2 and partes[1].isdigit():
                novo = int(partes[1])
                if novo in (4, 8, 16, 32, 64):
                    n_bits = novo
                    print(f"  → Modo alterado: {n_bits} bits  (operandos 0–{mascara(n_bits)})\n")
                else:
                    print("  ERRO: escolha bits entre 4, 8, 16, 32 ou 64.\n")
            else:
                print("  Uso: bits 4 | bits 8 | bits 16 | bits 32 | bits 64\n")
            continue

        # Processamento da expressão
        try:
            op, a, b = parse_binaria(entrada, n_bits)
        except ValueError as e:
            print(f"  ERRO de sintaxe: {e}\n  Digite 'ajuda' para exemplos.\n")
            continue

        op_label = {"+": "Soma", "-": "Subtração", "*": "Multiplicação",
                    "/": "Divisão", "!": "Fatorial"}[op]

        if op == "+":
            res = op_soma(a, b, n_bits)
        elif op == "-":
            res = op_subtracao(a, b, n_bits)
        elif op == "*":
            res = op_multiplicacao(a, b, n_bits)
        elif op == "/":
            res = op_divisao(a, b, n_bits)
        elif op == "!":
            res = op_fatorial(a, n_bits)

        print(formatar_resultado(op_label, a, b, res, n_bits))
        print()


if __name__ == "__main__":
    main()
