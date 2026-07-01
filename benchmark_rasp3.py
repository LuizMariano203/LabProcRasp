#!/usr/bin/env python3
"""
PCS3732 - Laboratório de Processadores | Aula 08
Benchmark de Tempo de Resposta – Raspberry Pi 3

Mede o tempo de execução (ns) das operações +, -, *, ! para
larguras de 4 a 64 bits com N=30 amostras, calculando média e σ.
Exporta os resultados em CSV e imprime tabela no terminal.

Uso:
  python3 benchmark_rasp3.py
  python3 benchmark_rasp3.py --amostras 50 --saida resultados_rasp3.csv
"""

import time
import math
import csv
import argparse
import sys
import os

# Importa o núcleo aritmético da calculadora
sys.path.insert(0, os.path.dirname(__file__))
from calculadora_rasp3 import (
    op_soma, op_subtracao, op_multiplicacao, op_fatorial, op_divisao
)

# ──────────────────────────────────────────────────────────────────────────────
# Configuração do benchmark
# ──────────────────────────────────────────────────────────────────────────────

LARGURAS_BITS = [4, 8, 16, 32, 64]
N_AMOSTRAS_DEFAULT = 30

# Operandos representativos para cada largura (valor máximo para estressar)
def operandos(n_bits: int):
    max_val = (1 << n_bits) - 1
    a = max_val          # ex: 4b → 15
    b = max_val // 2     # ex: 4b → 7
    return a, b


# ──────────────────────────────────────────────────────────────────────────────
# Medição de tempo (CLOCK_MONOTONIC via time.perf_counter_ns)
# ──────────────────────────────────────────────────────────────────────────────

def medir_ns(fn) -> int:
    """Executa fn() uma vez e retorna o tempo em nanosegundos."""
    t0 = time.perf_counter_ns()
    fn()
    t1 = time.perf_counter_ns()
    return t1 - t0


def benchmark_operacao(fn, n: int) -> dict:
    """
    Executa fn() n vezes, descartando a primeira amostra (warm-up).
    Retorna dict com amostras, média e desvio padrão.
    """
    # Warm-up
    medir_ns(fn)

    amostras = [medir_ns(fn) for _ in range(n)]
    media = sum(amostras) / n
    variancia = sum((x - media) ** 2 for x in amostras) / n
    sigma = math.sqrt(variancia)
    ic95 = 1.96 * sigma / math.sqrt(n)

    return {
        "amostras": amostras,
        "media_ns": media,
        "sigma_ns": sigma,
        "ic95_ns": ic95,
        "min_ns": min(amostras),
        "max_ns": max(amostras),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Operações a medir
# ──────────────────────────────────────────────────────────────────────────────

def montar_suite(n_bits: int):
    a, b = operandos(n_bits)
    # Para fatorial: usa valor adequado ao tamanho do resultado
    fat_n = min(n_bits, 12)   # 12! = 479001600, cabe em 32b; 20! em 64b

    return [
        ("Soma",          lambda: op_soma(a, b, n_bits)),
        ("Subtracao",     lambda: op_subtracao(a, b, n_bits)),
        ("Multiplicacao", lambda: op_multiplicacao(a, b, n_bits)),
        ("Fatorial",      lambda: op_fatorial(fat_n, n_bits)),
        ("Divisao",       lambda: op_divisao(a, b, n_bits)),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Formatação de tabela
# ──────────────────────────────────────────────────────────────────────────────

COL = [16, 6, 14, 14, 14, 14, 14]

def linha_header():
    campos = ["Operação", "Bits", "Média (ns)", "σ (ns)", "IC95± (ns)", "Mín (ns)", "Máx (ns)"]
    return "  " + " │ ".join(f"{c:<{w}}" for c, w in zip(campos, COL))

def linha_sep():
    return "  " + "─┼─".join("─" * w for w in COL)

def linha_dados(operacao, n_bits, r):
    valores = [
        operacao, str(n_bits),
        f"{r['media_ns']:.1f}",
        f"{r['sigma_ns']:.1f}",
        f"{r['ic95_ns']:.1f}",
        f"{r['min_ns']}",
        f"{r['max_ns']}",
    ]
    return "  " + " │ ".join(f"{v:<{w}}" for v, w in zip(valores, COL))


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Benchmark calculadora – Rasp3")
    parser.add_argument("--amostras", type=int, default=N_AMOSTRAS_DEFAULT,
                        help=f"Número de amostras por operação (padrão: {N_AMOSTRAS_DEFAULT})")
    parser.add_argument("--saida", type=str, default="benchmark_rasp3.csv",
                        help="Arquivo CSV de saída")
    parser.add_argument("--bits", nargs="+", type=int, default=LARGURAS_BITS,
                        help="Larguras de bits a testar (padrão: 4 8 16 32 64)")
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║  PCS3732 – Benchmark  │  Raspberry Pi 3 (ARM Cortex-A53)       ║")
    print(f"║  Amostras por operação: {args.amostras:<4}  │  Plataforma: {sys.platform:<12}  ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    resultados = []   # Para CSV

    print(linha_header())
    print(linha_sep())

    for n_bits in args.bits:
        suite = montar_suite(n_bits)
        for nome_op, fn in suite:
            sys.stdout.write(f"  Medindo {nome_op:14s} {n_bits:2d} bits... ")
            sys.stdout.flush()
            r = benchmark_operacao(fn, args.amostras)
            print(f"μ={r['media_ns']:.1f} ns  σ={r['sigma_ns']:.1f} ns")
            resultados.append({
                "plataforma": "Raspberry Pi 3",
                "operacao": nome_op,
                "bits": n_bits,
                "amostras": args.amostras,
                "media_ns": round(r["media_ns"], 2),
                "sigma_ns": round(r["sigma_ns"], 2),
                "ic95_ns": round(r["ic95_ns"], 2),
                "min_ns": r["min_ns"],
                "max_ns": r["max_ns"],
                "dados_brutos": ";".join(str(x) for x in r["amostras"]),
            })
        print(linha_sep())

    # Tabela final formatada
    print("\n── TABELA RESUMO ──────────────────────────────────────────────────")
    print(linha_header())
    print(linha_sep())
    for r in resultados:
        print(linha_dados(r["operacao"], r["bits"], {
            "media_ns": r["media_ns"], "sigma_ns": r["sigma_ns"],
            "ic95_ns": r["ic95_ns"], "min_ns": r["min_ns"], "max_ns": r["max_ns"],
        }))
    print()

    # Exportar CSV
    caminho_csv = os.path.join(os.path.dirname(__file__), args.saida)
    campos_csv = ["plataforma","operacao","bits","amostras",
                  "media_ns","sigma_ns","ic95_ns","min_ns","max_ns","dados_brutos"]
    with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos_csv)
        w.writeheader()
        w.writerows(resultados)

    print(f"  ✓ Resultados exportados para: {caminho_csv}")
    print()


if __name__ == "__main__":
    main()
