#!/usr/bin/env python3
"""
PCS3732 – Aula 08 | Comparador de Benchmarks ARM vs RISC-V
Lê os CSVs gerados pelo benchmark_rasp3.py e pelo ESP32 (copiado
via serial/ampy) e gera tabela comparativa + análise estatística.

Uso:
  python3 comparar_benchmarks.py \
      --rasp benchmark_rasp3.csv \
      --esp32 benchmark_esp32.csv

O CSV do ESP32 deve ter o mesmo formato (pode ser gerado colando os
dados do monitor serial em um arquivo com o mesmo cabeçalho do Rasp3,
adaptando a unidade: o ESP32 mede em µs, converta para ns ×1000).
"""

import csv
import math
import argparse
import os
import sys


# ──────────────────────────────────────────────────────────────────────────────
# Leitura de CSV
# ──────────────────────────────────────────────────────────────────────────────

def ler_csv(caminho: str) -> list[dict]:
    if not os.path.exists(caminho):
        print(f"  AVISO: arquivo não encontrado: {caminho}")
        return []
    with open(caminho, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def agrupar(linhas: list[dict]) -> dict:
    """Índice por (operacao, bits) → linha."""
    return {(r["operacao"], r["bits"]): r for r in linhas}


# ──────────────────────────────────────────────────────────────────────────────
# Análise estatística
# ──────────────────────────────────────────────────────────────────────────────

def t_test_welch(m1, s1, n1, m2, s2, n2) -> float:
    """Estatística t de Welch para duas amostras independentes."""
    if s1 == 0 and s2 == 0:
        return float("inf") if m1 != m2 else 0.0
    denom = math.sqrt((s1 ** 2 / n1) + (s2 ** 2 / n2))
    if denom == 0:
        return 0.0
    return abs(m1 - m2) / denom


def speedup(rasp_ns: float, esp32_ns: float) -> str:
    if esp32_ns == 0:
        return "—"
    ratio = esp32_ns / rasp_ns
    if ratio > 1:
        return f"Rasp3 {ratio:.1f}× mais rápido"
    elif ratio < 1:
        return f"ESP32 {1/ratio:.1f}× mais rápido"
    return "Empate"


# ──────────────────────────────────────────────────────────────────────────────
# Impressão
# ──────────────────────────────────────────────────────────────────────────────

SEP = "═" * 90

def print_tabela(rasp: dict, esp32: dict):
    print(f"\n{SEP}")
    print("  COMPARATIVO RASP3 (ARM) vs ESP32 (RISC-V)  │  Unidade: nanosegundos (ns)")
    print(SEP)
    header = f"  {'Op':<14} {'Bits':>5} │ {'Rasp3 μ':>11} {'Rasp3 σ':>10} │ {'ESP32 μ':>11} {'ESP32 σ':>10} │ {'Speedup':<28} │ t-Welch"
    print(header)
    print("─" * 90)

    ops = ["Soma", "Subtracao", "Multiplicacao", "Fatorial", "Divisao"]
    bits_list = ["4", "8", "16", "32", "64"]
    N = 30  # default

    for op in ops:
        for bits in bits_list:
            chave = (op, bits)
            r_row = rasp.get(chave)
            e_row = esp32.get(chave)

            r_med  = float(r_row["media_ns"]) if r_row else None
            r_sig  = float(r_row["sigma_ns"]) if r_row else None
            e_med  = float(e_row["media_ns"]) if e_row else None
            e_sig  = float(e_row["sigma_ns"]) if e_row else None

            r_str  = f"{r_med:>10.1f}" if r_med is not None else f"{'N/D':>10}"
            rs_str = f"{r_sig:>10.1f}" if r_sig is not None else f"{'N/D':>10}"
            e_str  = f"{e_med:>10.1f}" if e_med is not None else f"{'N/D':>10}"
            es_str = f"{e_sig:>10.1f}" if e_sig is not None else f"{'N/D':>10}"

            if r_med is not None and e_med is not None:
                sp = speedup(r_med, e_med)
                t = t_test_welch(r_med, r_sig or 0, N, e_med, e_sig or 0, N)
                t_str = f"{t:.2f}"
            else:
                sp = "dados insuficientes"
                t_str = "—"

            print(f"  {op:<14} {bits:>5} │ {r_str} {rs_str} │ {e_str} {es_str} │ {sp:<28} │ {t_str}")
        print("─" * 90)

    print()
    print("  Interpretação do t de Welch:")
    print("  t > 2.0 → diferença estatisticamente significativa (p < 0.05 aprox.)")
    print()


def print_analise(rasp: dict, esp32: dict):
    print(f"{SEP}")
    print("  ANÁLISE QUALITATIVA DOS RESULTADOS")
    print(SEP)

    conclusoes = [
        ("Números grandes (64 bits)",
         "O Rasp3 (ARM 64-bit) processa operandos de 64 bits nativamente em um único ciclo "
         "(instrução ADD/MUL AArch64). O ESP32 (RISC-V 32-bit) requer múltiplas instruções "
         "encadeadas com carry, gerando overhead proporcional à largura do operando."),

        ("Determinismo temporal",
         "O ESP32 em modo baremetal apresenta desvio padrão menor (σ baixo) porque não há "
         "agendador preemptivo. No Rasp3, o Linux introduz jitter por context-switching e "
         "interrupções de hardware do SO."),

        ("Frequência de clock",
         "O Rasp3 opera a 1.2 GHz vs ~240 MHz do ESP32, fator ~5×. Para operações simples "
         "(4–8 bits) isso pode compensar a penalidade de overhead do Linux."),

        ("Divisão por zero",
         "RISC-V RV32M: DIVU por zero retorna 0xFFFFFFFF sem gerar exceção de hardware "
         "(comportamento definido na especificação). ARM AArch64: UDIV por zero retorna 0 "
         "sem trap. Ambas as arquiteturas exigem verificação por software antes da instrução."),

        ("Fatorial e overflow",
         "Para N! com N > 12, o resultado excede 32 bits. O ESP32 precisa de aritmética "
         "multiprecisão em software; o Rasp3 calcula nativamente até 20! (≈ 2.4×10^18 < 2^64)."),
    ]

    for titulo, texto in conclusoes:
        print(f"\n  ▶ {titulo}")
        # Quebra manual de linha a cada ~75 chars
        palavras = texto.split()
        linha = "    "
        for palavra in palavras:
            if len(linha) + len(palavra) + 1 > 88:
                print(linha)
                linha = "    " + palavra + " "
            else:
                linha += palavra + " "
        if linha.strip():
            print(linha)
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Comparador de benchmarks ARM vs RISC-V")
    parser.add_argument("--rasp",  default="benchmark_rasp3.csv",
                        help="CSV do Raspberry Pi 3")
    parser.add_argument("--esp32", default="benchmark_esp32.csv",
                        help="CSV do ESP32 (mesma estrutura, unidade ns)")
    args = parser.parse_args()

    rasp_dir  = os.path.join(os.path.dirname(__file__), args.rasp)
    esp32_dir = os.path.join(os.path.dirname(__file__), args.esp32)

    rasp_linhas  = ler_csv(rasp_dir)
    esp32_linhas = ler_csv(esp32_dir)

    if not rasp_linhas and not esp32_linhas:
        print("  Nenhum CSV encontrado. Execute primeiro benchmark_rasp3.py no Rasp3")
        print("  e exporte os dados do ESP32 para benchmark_esp32.csv.")
        print("  Gerando tabela com dados de exemplo para demonstração...\n")
        # Dados de exemplo para demo
        rasp_linhas = [
            {"operacao":"Soma","bits":"4","media_ns":"312","sigma_ns":"18","ic95_ns":"6","min_ns":"290","max_ns":"350","dados_brutos":""},
            {"operacao":"Subtracao","bits":"4","media_ns":"298","sigma_ns":"15","ic95_ns":"5","min_ns":"280","max_ns":"330","dados_brutos":""},
            {"operacao":"Multiplicacao","bits":"4","media_ns":"345","sigma_ns":"22","ic95_ns":"8","min_ns":"310","max_ns":"400","dados_brutos":""},
            {"operacao":"Fatorial","bits":"4","media_ns":"520","sigma_ns":"35","ic95_ns":"13","min_ns":"480","max_ns":"600","dados_brutos":""},
        ]
        esp32_linhas = [
            {"operacao":"Soma","bits":"4","media_ns":"4200","sigma_ns":"120","ic95_ns":"43","min_ns":"4000","max_ns":"4500","dados_brutos":""},
            {"operacao":"Subtracao","bits":"4","media_ns":"4150","sigma_ns":"110","ic95_ns":"39","min_ns":"4000","max_ns":"4400","dados_brutos":""},
            {"operacao":"Multiplicacao","bits":"4","media_ns":"4800","sigma_ns":"150","ic95_ns":"54","min_ns":"4600","max_ns":"5200","dados_brutos":""},
            {"operacao":"Fatorial","bits":"4","media_ns":"9500","sigma_ns":"300","ic95_ns":"107","min_ns":"9000","max_ns":"10200","dados_brutos":""},
        ]

    rasp  = agrupar(rasp_linhas)
    esp32 = agrupar(esp32_linhas)

    print_tabela(rasp, esp32)
    print_analise(rasp, esp32)


if __name__ == "__main__":
    main()
