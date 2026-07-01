from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import Flowable

OUTPUT = "/sessions/determined-laughing-wozniak/mnt/outputs/Planejamento_PCS3732_Aula08.pdf"

W, H = A4

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=2.5*cm,
    rightMargin=2.5*cm,
    topMargin=2.2*cm,
    bottomMargin=2.2*cm,
    title="Planejamento Pré-Aula – PCS3732 Aula 08",
    author="Luiz Mariano",
)

# ─── Styles ────────────────────────────────────────────────────────────────────
BASE = "Helvetica"         # Arial equivalent in ReportLab
BASE_B = "Helvetica-Bold"
BASE_I = "Helvetica-Oblique"

def S(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=styles[parent], fontName=BASE, fontSize=12, **kw)
    return s

styles = getSampleStyleSheet()

titulo_doc  = ParagraphStyle("TituloDoc",  fontName=BASE_B, fontSize=16, alignment=TA_CENTER, spaceAfter=4)
subtitulo   = ParagraphStyle("Subtitulo",  fontName=BASE,   fontSize=12, alignment=TA_CENTER, spaceAfter=2)
secao       = ParagraphStyle("Secao",      fontName=BASE_B, fontSize=13, spaceBefore=14, spaceAfter=4,
                              textColor=colors.HexColor("#1F3864"), borderPad=2)
subsecao    = ParagraphStyle("Subsecao",   fontName=BASE_B, fontSize=12, spaceBefore=8, spaceAfter=3)
normal      = ParagraphStyle("Normal12",   fontName=BASE,   fontSize=12, leading=16, alignment=TA_JUSTIFY, spaceAfter=4)
normal_l    = ParagraphStyle("NormalL",    fontName=BASE,   fontSize=12, leading=16, alignment=TA_LEFT,    spaceAfter=4)
italic      = ParagraphStyle("Italic12",   fontName=BASE_I, fontSize=12, leading=16, alignment=TA_JUSTIFY, spaceAfter=4)
code_style  = ParagraphStyle("Code",       fontName="Courier", fontSize=10, leading=13, leftIndent=12,
                              backColor=colors.HexColor("#F2F2F2"), spaceAfter=6, spaceBefore=4,
                              borderPad=4, borderColor=colors.HexColor("#CCCCCC"), borderWidth=0.5)
caption     = ParagraphStyle("Caption",    fontName=BASE_I, fontSize=10, alignment=TA_CENTER, spaceAfter=6)
abnt_ref    = ParagraphStyle("ABNTRef",    fontName=BASE,   fontSize=11, leading=15, alignment=TA_JUSTIFY,
                              leftIndent=0, spaceAfter=4)
label_bold  = ParagraphStyle("LabelBold",  fontName=BASE_B, fontSize=12, leading=14, spaceAfter=2)
rodape      = ParagraphStyle("Rodape",     fontName=BASE_I, fontSize=9,  alignment=TA_CENTER,
                              textColor=colors.grey)

def hr(): return HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#1F3864"), spaceAfter=6)
def sp(h=6): return Spacer(1, h)

# ─── TABLE helpers ──────────────────────────────────────────────────────────────
def tbl_style(header_color="#1F3864"):
    return TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  colors.HexColor(header_color)),
        ("TEXTCOLOR",    (0,0), (-1,0),  colors.white),
        ("FONTNAME",     (0,0), (-1,0),  BASE_B),
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("FONTNAME",     (0,1), (-1,-1), BASE),
        ("ALIGN",        (0,0), (-1,-1), "LEFT"),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#EEF2F8")]),
        ("GRID",         (0,0), (-1,-1), 0.4, colors.HexColor("#AAAAAA")),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ])

def req_table(rows):
    col_w = [3.5*cm, 4.5*cm, 4.5*cm, 2.5*cm]
    data = [[Paragraph(c, ParagraphStyle("th", fontName=BASE_B, fontSize=10, textColor=colors.white, leading=13))
             for c in ["Requisito","Teste Planejado","Resultado Esperado","Status"]]]+\
           [[Paragraph(str(c), ParagraphStyle("td", fontName=BASE, fontSize=10, leading=13))
             for c in r] for r in rows]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(tbl_style())
    return t

def bench_table(rows):
    col_w = [3*cm, 2.8*cm, 2.8*cm, 2.8*cm, 3.1*cm]
    data = [[Paragraph(c, ParagraphStyle("th", fontName=BASE_B, fontSize=10, textColor=colors.white, leading=13))
             for c in ["Operação / Bits","Rasp3 μs (média)","Rasp3 σ","ESP32 μs (média)","ESP32 σ"]]]+\
           [[Paragraph(str(c), ParagraphStyle("td", fontName=BASE, fontSize=10, leading=13))
             for c in r] for r in rows]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(tbl_style())
    return t

def diff_table(rows):
    col_w = [4.5*cm, 3.3*cm, 3.3*cm, 4.4*cm]
    data = [[Paragraph(c, ParagraphStyle("th", fontName=BASE_B, fontSize=10, textColor=colors.white, leading=13))
             for c in ["Característica","ESP32 (RISC-V 32-bit)","Raspberry Pi 3 (ARM 64-bit)","Impacto Prático"]]]+\
           [[Paragraph(str(c), ParagraphStyle("td", fontName=BASE, fontSize=10, leading=13))
             for c in r] for r in rows]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(tbl_style())
    return t

# ══════════════════════════════════════════════════════════════════════════════
#  STORY
# ══════════════════════════════════════════════════════════════════════════════
story = []

# ─── CAPA / CABEÇALHO ──────────────────────────────────────────────────────────
story += [
    Paragraph("Escola Politécnica da USP – PCS3732", subtitulo),
    Paragraph("Laboratório de Processadores", subtitulo),
    sp(6),
    hr(),
    sp(4),
    Paragraph("DOCUMENTO DE PLANEJAMENTO PRÉ-AULA", titulo_doc),
    Paragraph("Aula 08 – Arquiteturas em Duelo: Calculadora Binária ARM vs. RISC-V", titulo_doc),
    sp(4),
    hr(),
    sp(10),
]

# Tabela de identificação
id_data = [
    [Paragraph("Aluno:", label_bold),      Paragraph("Luiz Mariano", normal_l),
     Paragraph("NUSP:", label_bold),        Paragraph("", normal_l)],
    [Paragraph("Data:", label_bold),       Paragraph("01/07/2026", normal_l),
     Paragraph("Turma:", label_bold),       Paragraph("", normal_l)],
    [Paragraph("Plataformas:", label_bold),Paragraph("Raspberry Pi 3 (ARM Cortex-A53) | ESP32 (RISC-V 32-bit)", normal_l),
     Paragraph("", normal_l),              Paragraph("", normal_l)],
]
id_tbl = Table(id_data, colWidths=[3*cm, 5.5*cm, 2*cm, 5*cm])
id_tbl.setStyle(TableStyle([
    ("FONTSIZE",     (0,0),(-1,-1), 12),
    ("TOPPADDING",   (0,0),(-1,-1), 4),
    ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ("LEFTPADDING",  (0,0),(-1,-1), 0),
    ("SPAN",(1,2),(3,2)),
    ("LINEBELOW",(0,0),(-1,-1),0.3,colors.lightgrey),
]))
story += [id_tbl, sp(14)]

# ══════════════════════════════════════════════════════════════════════════════
#  SEÇÃO 2 – LEITURA PRÉ-AULA
# ══════════════════════════════════════════════════════════════════════════════
story += [
    Paragraph("2. LEITURA PRÉ-AULA E FUNDAMENTAÇÃO TEÓRICA", secao), hr(),
    Paragraph("2.1 Contextualização Histórica e Arquitetural", subsecao),
    Paragraph(
        "A evolução dos processadores parte do ENIAC (anos 1940, 18.000 válvulas, ~5.000 ops/s) até a cisão "
        "CISC/RISC nos anos 1980. O projeto Intel 4004 (1971) inaugurou a era do microprocessador integrado. "
        "A divergência entre instruções densas (x86/CISC) e instruções reduzidas ultrarrápidas (RISC) define "
        "o campo contemporâneo: domínio ARM em dispositivos móveis e embarcados versus a ascensão do padrão "
        "aberto RISC-V (PATTERSON; WATERMAN, 2017).", normal),
    Paragraph("2.2 Raspberry Pi 3 – ARM Cortex-A53 (AArch64)", subsecao),
    Paragraph(
        "O Raspberry Pi 3 Model B utiliza o SoC Broadcom BCM2837, com quad-core ARM Cortex-A53 a 1,2 GHz "
        "operando em modo de 64 bits (AArch64). A ISA ARMv8-A suporta pipeline out-of-order de 8 estágios, "
        "ponto flutuante IEEE 754, e instruções SIMD (NEON). Para operações aritméticas de inteiros de 64 bits "
        "o processador executa em único ciclo de clock instruções como ADD, SUB e MUL. A saída de vídeo é "
        "gerenciada pelo VideoCore IV via barramento HDMI, adaptado para VGA no laboratório "
        "(RASPBERRY PI FOUNDATION, 2016).", normal),
    Paragraph("2.3 ESP32 – RISC-V 32-bit (Xtensa LX6 / ESP32-C3)", subsecao),
    Paragraph(
        "O ESP32 (variante RISC-V, e.g. ESP32-C3) adota a ISA RISC-V RV32IMC: registradores de 32 bits, "
        "conjunto base de inteiros (I), extensão de multiplicação/divisão (M) e instruções comprimidas (C). "
        "Opera em modo baremetal (sem SO), com controle direto de interrupções de hardware e determinismo "
        "temporal. Números superiores a 32 bits exigem múltiplas instruções encadeadas com carry "
        "(ESPRESSIF, 2023; WATERMAN et al., 2019).", normal),
    Paragraph("2.4 Diagrama Comparativo de Fluxo de I/O", subsecao),
    Paragraph(
        "Conforme a matriz diagnóstica da aula (slide DOC ID: LAB-ARCH-002), os paradigmas de I/O diferem "
        "fundamentalmente:", normal),
]

io_data = [
    ["Paradigma","Caminho do Dado","Caminho da Saída","Latência Dominante"],
    ["ESP32 Webserver","Teclado → TCP/IP (WiFi) → ESP32","ESP32 → HTTP → Browser","Rede (~10–100 ms)"],
    ["Rasp3 Local","Teclado → USB HID → Linux → App","App → framebuffer HDMI → Monitor","SO (~1–5 ms)"],
]
io_tbl_data = [[Paragraph(c, ParagraphStyle("th2", fontName=BASE_B, fontSize=10, textColor=colors.white, leading=13))
                for c in io_data[0]]]+\
              [[Paragraph(c, ParagraphStyle("td2", fontName=BASE, fontSize=10, leading=13))
                for c in r] for r in io_data[1:]]
io_tbl = Table(io_tbl_data, colWidths=[3.2*cm, 4.8*cm, 4.8*cm, 2.7*cm], repeatRows=1)
io_tbl.setStyle(tbl_style())
story += [io_tbl, sp(8)]

story += [
    Paragraph("2.5 Escalabilidade para N Bits", subsecao),
    Paragraph(
        "O slide LAB-ARCH-003 evidencia a diferença de escalabilidade: o Rasp3 processa inteiros de 64 bits "
        "nativamente em um único ciclo; o ESP32 (32 bits) precisa de múltiplas instruções encadeadas "
        "(soma parcial baixa + carry + soma parcial alta) para operandos além de 32 bits, gerando "
        "overhead proporcional à largura do dado.", normal),
    Paragraph("2.6 Fluxo da ULA (Unidade Lógica Aritmética)", subsecao),
    Paragraph(
        "O fluxograma LAB-ARCH-005 descreve o pipeline lógico: (1) Interrupção/polling do teclado; "
        "(2) Decodificador de OpCode seleciona operação (+, -, *, !, /); (3) Execução na ULA com "
        "verificação de flags (negativo, overflow, divisão por zero); (4) Conversão binário→ASCII; "
        "(5) Envio ao framebuffer de vídeo (HDMI-VGA). A multiplicação é implementada via shift+adição; "
        "o fatorial exige loop iterativo com monitoramento de overflow.", normal),
]

# ══════════════════════════════════════════════════════════════════════════════
#  SEÇÃO 3 – REQUISITOS
# ══════════════════════════════════════════════════════════════════════════════
story += [
    PageBreak(),
    Paragraph("3. REQUISITOS FUNCIONAIS E NÃO FUNCIONAIS", secao), hr(),
    Paragraph("3.1 Requisitos Funcionais (RF)", subsecao),
]

rf_rows = [
    ["RF01 – Entrada 4 bits",
     "Digitar valor binário '1111' pelo teclado",
     "Registrador armazena decimal 15; exibição imediata no monitor",
     "[ ] Pendente"],
    ["RF02 – Soma (+)",
     "Calcular 0101 + 0011",
     "Resultado 8 (1000) exibido sem overflow",
     "[ ] Pendente"],
    ["RF03 – Subtração (−)",
     "Calcular 0101 − 0111",
     "Resultado −2 com flag N (negativo) ativo",
     "[ ] Pendente"],
    ["RF04 – Multiplicação (*)",
     "Calcular 0011 × 0011",
     "Resultado 9 via shift+adição",
     "[ ] Pendente"],
    ["RF05 – Fatorial (!)",
     "Calcular 4! e 5!",
     "4! = 24; 5! = 120; overflow sinalizado para n > 5 em 4 bits",
     "[ ] Pendente"],
    ["RF06 – Divisão (/)",
     "Calcular 0110 / 0010; depois 0110 / 0000",
     "Quociente 3; divisão por zero exibe aviso e retorna ao loop",
     "[ ] Pendente"],
    ["RF07 – Saída HDMI",
     "Executar qualquer operação com monitor VGA conectado",
     "Resultado visível no monitor em ≤ 100 ms",
     "[ ] Pendente"],
    ["RF08 – Benchmark N bits",
     "Repetir operações para 4, 8, 16, 32, 64 bits (≥30 amostras)",
     "Tabela com média e desvio padrão por operação/largura/plataforma",
     "[ ] Pendente"],
]
story += [req_table(rf_rows), sp(8)]

story += [Paragraph("3.2 Requisitos Não Funcionais (RNF)", subsecao)]
rnf_rows = [
    ["RNF01 – Estabilidade de Erro",
     "Inserir operação inválida (ex: A/0, entrada > 4 bits)",
     "Sistema exibe aviso; sem kernel panic; retorna ao prompt",
     "[ ] Pendente"],
    ["RNF02 – Reprodutibilidade",
     "Executar benchmark 30 vezes consecutivas",
     "Desvio padrão < 10% da média",
     "[ ] Pendente"],
    ["RNF03 – Portabilidade de Código",
     "Compilar mesmo código C/Assembly em Rasp3 e ESP32",
     "Apenas flag de compilação alvo muda (aarch64 vs. riscv32)",
     "[ ] Pendente"],
    ["RNF04 – GitHub/Versionamento",
     "Verificar histórico de commits desde Semana 1",
     "README com instruções de build; sem commits únicos finais",
     "[ ] Pendente"],
]
story += [req_table(rnf_rows), sp(10)]

# ══════════════════════════════════════════════════════════════════════════════
#  SEÇÃO 4 – ARQUITETURA E DESIGN
# ══════════════════════════════════════════════════════════════════════════════
story += [
    Paragraph("4. ARQUITETURA E DESIGN DA SOLUÇÃO", secao), hr(),
    Paragraph("4.1 Estrutura do Código – Calculadora Raspberry Pi 3 (ARM/Python+C)", subsecao),
    Paragraph(
        "A implementação no Rasp3 opera sobre Linux (Raspberry Pi OS). O programa lê do stdin "
        "(teclado USB via driver HID do kernel), processa a operação e imprime no stdout que é "
        "enviado ao framebuffer HDMI. A estrutura modular é:", normal),
]

story += [
    Paragraph(
        "main.c → parse_input() → dispatch_op() → [add|sub|mul|fact|div]() → print_result()", code_style),
    Paragraph(
        "Para o benchmark de tempo de resposta utiliza-se clock_gettime(CLOCK_MONOTONIC) com "
        "resolução de nanosegundos, medindo 30 amostras por operação/tamanho de dado para calcular "
        "média (μ) e desvio padrão (σ = √(Σ(xᵢ−μ)²/N)).", normal),
    Paragraph("4.2 Código de Referência – Operações 4 bits (C)", subsecao),
]

code_c = """\
#include <stdio.h>
#include <time.h>
#include <stdint.h>
#include <stdlib.h>

typedef uint8_t u4;  /* 4-bit emulado em 8 bits */

u4  op_add (u4 a, u4 b) { return (a + b) & 0xF; }
u4  op_sub (u4 a, u4 b) { return (a - b) & 0xF; }
u4  op_mul (u4 a, u4 b) { return (a * b) & 0xF; }
int op_fact(u4 a)       { int r=1; for(u4 i=2;i<=a;i++) r*=i; return r; }
int op_div (u4 a, u4 b) {
    if (b == 0) { fprintf(stderr,"ERRO: div/0\\n"); return -1; }
    return a / b;
}
long bench_ns(u4 a, u4 b, char op) {
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    switch(op){
        case '+': op_add(a,b);  break;
        case '-': op_sub(a,b);  break;
        case '*': op_mul(a,b);  break;
        case '!': op_fact(a);   break;
        case '/': op_div(a,b);  break;
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    return (t1.tv_sec-t0.tv_sec)*1e9+(t1.tv_nsec-t0.tv_nsec);
}"""
story += [Paragraph(code_c, code_style)]

story += [
    Paragraph("4.3 Assembly ARM (AArch64) – Rotina de Multiplicação", subsecao),
    Paragraph(
        "Gerado via IA generativa e validado no simulador CPUlator (cpulator.01xz.net) com "
        "target ARMv8 / AArch64:", normal),
]
code_arm = """\
/* mul4bit: X0 = operando A (4 bits), X1 = operando B (4 bits)
   Retorna: X0 = resultado (4 bits, truncado)              */
mul4bit:
    MUL   X2, X0, X1        // X2 = A * B (64 bits)
    AND   X0, X2, #0xF      // trunca para 4 bits
    RET"""
story += [Paragraph(code_arm, code_style)]

story += [
    Paragraph("4.4 Assembly RISC-V (RV32IM) – Rotina Equivalente", subsecao),
    Paragraph(
        "Gerado via IA generativa e validado no simulador RARS (RISC-V Assembler and Runtime Simulator):", normal),
]
code_rv = """\
# mul4bit: a0 = A (4 bits), a1 = B (4 bits)
# Retorna: a0 = resultado (4 bits)
mul4bit:
    mul   a2, a0, a1        # a2 = A * B (32 bits)
    andi  a0, a2, 0xF       # trunca para 4 bits
    ret"""
story += [Paragraph(code_rv, code_style)]

story += [
    Paragraph("4.5 Tratamento de Divisão por Zero", subsecao),
    Paragraph(
        "Na implementação em C (Rasp3), verifica-se b == 0 antes da divisão, exibindo mensagem "
        "de erro e retornando −1 (código sentinela). O laço principal aguarda novo input sem "
        "encerrar o processo. Em Assembly ARM, utiliza-se a instrução UDIV com verificação "
        "prévia via CBZ (compare and branch if zero). Em RISC-V, utiliza-se DIV com checagem "
        "por beqz (branch if equal zero). Ambas as arquiteturas tratam divisão por zero em "
        "software, pois RISC-V não gera exceção de hardware nesse caso (conforme especificação "
        "RV32M — resultado é −1 para DIVU por zero); ARM tampouco gera trap para divisão por "
        "zero em modo usuário (WATERMAN et al., 2019).", normal),
]

# ══════════════════════════════════════════════════════════════════════════════
#  SEÇÃO 5 – MÉTODO EXPERIMENTAL
# ══════════════════════════════════════════════════════════════════════════════
story += [
    PageBreak(),
    Paragraph("5. MÉTODO EXPERIMENTAL E BENCHMARK", secao), hr(),
    Paragraph("5.1 Ciclo Iterativo (Especificar → Sintetizar → Simular → Embarcar → Depurar)", subsecao),
    Paragraph(
        "Conforme o ciclo LAB-ARCH (slide 10): (1) Especificar RFs e RNFs (seção 3); "
        "(2) Sintetizar o código C e Assembly com auxílio de IA generativa; "
        "(3) Simular no CPUlator (ARM) e no RARS (RISC-V) validando estado de registradores; "
        "(4) Embarcar: compilar com gcc (aarch64-linux-gnu) no Rasp3 e com riscv32-unknown-elf-gcc "
        "no ESP32; (5) Depurar sinais elétricos e saída no monitor físico.", normal),
    Paragraph("5.2 Protocolo de Benchmark", subsecao),
    Paragraph(
        "Para cada operação (soma, subtração, multiplicação, fatorial) e para cada largura de dado "
        "(4, 8, 16, 32, 64 bits) coletam-se N = 30 amostras de tempo de execução. "
        "Calcula-se média μ e desvio padrão σ. O intervalo de confiança de 95% é μ ± 1,96·σ/√N. "
        "A tabela abaixo é o template a ser preenchido durante o laboratório:", normal),
]

bench_rows = [
    ["Soma / 4b",  "[preencher]","[σ]","[preencher]","[σ]"],
    ["Soma / 32b", "[preencher]","[σ]","[preencher]","[σ]"],
    ["Soma / 64b", "[preencher]","[σ]","[preencher]","[σ]"],
    ["Sub / 4b",   "[preencher]","[σ]","[preencher]","[σ]"],
    ["Sub / 32b",  "[preencher]","[σ]","[preencher]","[σ]"],
    ["Mul / 4b",   "[preencher]","[σ]","[preencher]","[σ]"],
    ["Mul / 32b",  "[preencher]","[σ]","[preencher]","[σ]"],
    ["Fat(n=4) / 4b","[preencher]","[σ]","[preencher]","[σ]"],
    ["Fat(n=12) / 32b","[preencher]","[σ]","[preencher]","[σ]"],
]
story += [bench_table(bench_rows), sp(6)]

story += [
    Paragraph("5.3 Hipóteses para Diferenças Esperadas nos Resultados", subsecao),
    Paragraph(
        "Espera-se que o Rasp3 supere o ESP32 em operações com dados > 32 bits, pois sua palavra "
        "nativa de 64 bits elimina instruções de carry encadeadas. Para 4 bits ambas as plataformas "
        "devem apresentar tempos similares (operação trivial dentro de registradores). O fatorial "
        "de valores maiores (n > 12) deve evidenciar o custo de overflow handling e o overhead do "
        "sistema operacional Linux no Rasp3 versus o determinismo baremetal do ESP32. "
        "O desvio padrão esperado é maior no Rasp3 devido ao agendamento preemptivo do Linux "
        "(TANENBAUM; BOS, 2015).", normal),
]

# ══════════════════════════════════════════════════════════════════════════════
#  SEÇÃO 5.4 – COMPARAÇÃO ARM vs RISC-V
# ══════════════════════════════════════════════════════════════════════════════
story += [
    Paragraph("5.4 Comparação Arquitetural ARM vs. RISC-V (Questão 5)", subsecao),
]

diff_rows = [
    ["Largura de palavra","32 bits (overhead para >32b)","64 bits nativo","Rasp3 superior em dados grandes"],
    ["ISA","RISC-V RV32IMC (aberta)","ARMv8-A (proprietária)","RISC-V: customização livre"],
    ["Pipeline","In-order (simples)","Out-of-order 8 estágios","ARM mais eficiente em IPC"],
    ["Paradigma I/O","WiFi TCP/IP (webserver)","GPIO + HDMI local","ESP32: latência de rede (~ms)"],
    ["Camada de sistema","Baremetal/RTOS","Linux + kernel","ESP32: determinismo; Rasp3: abstração"],
    ["Divisão por zero","Sem trap (resultado −1 por spec)","Sem trap (verificação SW)","Ambos requerem check manual"],
    ["Clock","240 MHz (ESP32)","1,2 GHz (Rasp3)","Rasp3 5× mais rápido em frequência"],
    ["Consumo","~0,3 W (IoT)","~4 W (uso geral)","ESP32 vence em eficiência energética"],
]
story += [diff_table(diff_rows), sp(8)]

story += [
    Paragraph(
        "Para números grandes, o Raspberry Pi 3 é mais eficiente porque sua palavra nativa de "
        "64 bits permite processar operandos de até 64 bits em uma única instrução (ADD, MUL, UDIV), "
        "enquanto o ESP32 (32 bits) requer múltiplas instruções encadeadas com gerenciamento de carry "
        "para cada operação além de 32 bits. Além disso, o pipeline out-of-order do Cortex-A53 "
        "permite execução especulativa, ocultando latências de memória "
        "(HENNESSY; PATTERSON, 2019).", normal),
]

# ══════════════════════════════════════════════════════════════════════════════
#  SEÇÃO 6 – DESAFIO STANDALONE
# ══════════════════════════════════════════════════════════════════════════════
story += [
    Paragraph("6. DESAFIO STANDALONE – TECLADO MATRICIAL + LCD I2C", secao), hr(),
    Paragraph(
        "O desafio avançado (slide LAB-ARCH-008) consiste em desacoplar a calculadora do PC, "
        "utilizando teclado matricial físico (multiplexação GPIO linha/coluna) e display LCD com "
        "comunicação I2C (apenas 2 fios: SDA e SCL, versus 8+ paralelos). O barramento I2C "
        "reduz drasticamente a contagem de pinos mas exige drivers de baixo nível para envio de "
        "bytes de controle (endereço I2C 0x27 típico para módulo PCF8574).", normal),
    Paragraph("6.1 Pinagem GPIO – Teclado Matricial 4×4", subsecao),
]

gpio_data = [
    ["Função","GPIO Rasp3","Direção","Descrição"],
    ["Linha 1 (R1)","GPIO 18","Saída","Varredura de linha"],
    ["Linha 2 (R2)","GPIO 23","Saída","Varredura de linha"],
    ["Linha 3 (R3)","GPIO 24","Saída","Varredura de linha"],
    ["Linha 4 (R4)","GPIO 25","Saída","Varredura de linha"],
    ["Col 1 (C1)","GPIO 12","Entrada (pull-up)","Leitura de coluna"],
    ["Col 2 (C2)","GPIO 16","Entrada (pull-up)","Leitura de coluna"],
    ["Col 3 (C3)","GPIO 20","Entrada (pull-up)","Leitura de coluna"],
    ["Col 4 (C4)","GPIO 21","Entrada (pull-up)","Leitura de coluna"],
]
gpio_tbl_data = [[Paragraph(c, ParagraphStyle("th3", fontName=BASE_B, fontSize=10, textColor=colors.white, leading=13))
                  for c in gpio_data[0]]]+\
               [[Paragraph(c, ParagraphStyle("td3", fontName=BASE, fontSize=10, leading=13))
                 for c in r] for r in gpio_data[1:]]
gpio_tbl = Table(gpio_tbl_data, colWidths=[3*cm, 3*cm, 3*cm, 6.5*cm], repeatRows=1)
gpio_tbl.setStyle(tbl_style())
story += [gpio_tbl, sp(8)]

story += [
    Paragraph("6.2 Código Python de Referência – I2C LCD + Teclado Matricial", subsecao),
]
code_standalone = """\
import smbus2, RPi.GPIO as GPIO, time

# --- I2C LCD (PCF8574, endereço 0x27) ---
LCD_ADDR = 0x27
bus = smbus2.SMBus(1)

def lcd_send(data, mode):
    high = mode | (data & 0xF0)       | 0x08  # backlight ON
    low  = mode | ((data << 4) & 0xF0)| 0x08
    for nibble in [high, low]:
        bus.write_byte(LCD_ADDR, nibble | 0x04)   # Enable=1
        time.sleep(1e-4)
        bus.write_byte(LCD_ADDR, nibble & ~0x04)  # Enable=0

def lcd_print(text):
    for ch in text: lcd_send(ord(ch), 0x01)  # RS=1: dados

# --- Teclado matricial 4×4 ---
ROWS = [18,23,24,25]; COLS = [12,16,20,21]
KEYS = [['1','2','3','A'],['4','5','6','B'],
        ['7','8','9','C'],['*','0','#','D']]
GPIO.setmode(GPIO.BCM)
for r in ROWS: GPIO.setup(r, GPIO.OUT, initial=GPIO.HIGH)
for c in COLS: GPIO.setup(c, GPIO.IN,  pull_up_down=GPIO.PUD_UP)

def scan_key():
    for i,r in enumerate(ROWS):
        GPIO.output(r, GPIO.LOW)
        for j,c in enumerate(COLS):
            if GPIO.input(c)==GPIO.LOW:
                GPIO.output(r, GPIO.HIGH)
                return KEYS[i][j]
        GPIO.output(r, GPIO.HIGH)
    return None"""
story += [Paragraph(code_standalone, code_style), sp(6)]

# ══════════════════════════════════════════════════════════════════════════════
#  SEÇÃO 7 – LIÇÕES APRENDIDAS (a preencher em sala)
# ══════════════════════════════════════════════════════════════════════════════
story += [
    PageBreak(),
    Paragraph("7. LIÇÕES APRENDIDAS E RESULTADOS INTERMEDIÁRIOS", secao), hr(),
    Paragraph("(Esta seção deve ser preenchida durante e após o laboratório)", italic),
    sp(8),
]

la_data = [
    ["Atividade","Resultado Obtido","Dificuldades / Observações","Evidência"],
    ["1 – Impl. 4 bits Rasp3","","","Print/foto"],
    ["2 – Benchmark N bits","","","Tabela de dados"],
    ["3 – Sim. ARM (CPUlator)","","","Screenshot"],
    ["3 – Sim. RISC-V (RARS)","","","Screenshot"],
    ["4 – Divisão / div por zero","","","Saída terminal"],
    ["5 – Comparação arquitetural","","","Fluxograma"],
    ["6 – Standalone LCD I2C","","","Foto/vídeo"],
]
la_tbl_data = [[Paragraph(c, ParagraphStyle("th4", fontName=BASE_B, fontSize=10, textColor=colors.white, leading=13))
                for c in la_data[0]]]+\
              [[Paragraph(c, ParagraphStyle("td4", fontName=BASE, fontSize=10, leading=13))
                for c in r] for r in la_data[1:]]
la_tbl = Table(la_tbl_data, colWidths=[3.8*cm, 3.5*cm, 4.5*cm, 3.7*cm], repeatRows=1)
la_tbl.setStyle(tbl_style())
story.append(la_tbl)
story.append(sp(12))

# Espaços para anotações
for i in range(8):
    story.append(HRFlowable(width="100%", thickness=0.3, color=colors.lightgrey, spaceAfter=18))

# ══════════════════════════════════════════════════════════════════════════════
#  REFERÊNCIAS ABNT
# ══════════════════════════════════════════════════════════════════════════════
story += [
    PageBreak(),
    Paragraph("REFERÊNCIAS", secao), hr(),
    Paragraph(
        "ESPRESSIF SYSTEMS. <i>ESP32-C3 Technical Reference Manual</i>. v0.4. Shanghai: "
        "Espressif Systems, 2023. Disponível em: https://www.espressif.com/sites/default/files/"
        "documentation/esp32-c3_technical_reference_manual_en.pdf. Acesso em: 1 jul. 2026.", abnt_ref),
    sp(4),
    Paragraph(
        "HENNESSY, John L.; PATTERSON, David A. <i>Computer Architecture: A Quantitative Approach</i>. "
        "6. ed. Cambridge: Morgan Kaufmann, 2019.", abnt_ref),
    sp(4),
    Paragraph(
        "PATTERSON, David; WATERMAN, Andrew. <i>The RISC-V Reader: An Open Architecture Atlas</i>. "
        "1. ed. [S. l.]: Strawberry Canyon, 2017.", abnt_ref),
    sp(4),
    Paragraph(
        "RASPBERRY PI FOUNDATION. <i>Raspberry Pi 3 Model B Product Brief</i>. Cambridge: "
        "Raspberry Pi Foundation, 2016. Disponível em: https://datasheets.raspberrypi.com/"
        "rpi3/raspberry-pi-3-model-b-product-brief.pdf. Acesso em: 1 jul. 2026.", abnt_ref),
    sp(4),
    Paragraph(
        "TANENBAUM, Andrew S.; BOS, Herbert. <i>Sistemas Operacionais Modernos</i>. "
        "4. ed. São Paulo: Pearson Prentice Hall, 2015.", abnt_ref),
    sp(4),
    Paragraph(
        "WATERMAN, Andrew et al. <i>The RISC-V Instruction Set Manual</i>. Volume I: "
        "Unprivileged ISA. Document Version 20191213. [S. l.]: RISC-V Foundation, 2019. "
        "Disponível em: https://riscv.org/wp-content/uploads/2019/12/riscv-spec-20191213.pdf. "
        "Acesso em: 1 jul. 2026.", abnt_ref),
    sp(4),
    Paragraph(
        "ARM LIMITED. <i>ARM Cortex-A53 MPCore Processor Technical Reference Manual</i>. "
        "Revision r0p4. Cambridge: Arm Limited, 2016. Disponível em: "
        "https://developer.arm.com/documentation/ddi0500/latest. Acesso em: 1 jul. 2026.", abnt_ref),
]

# ──────────────────────────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont(BASE_I, 9)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(W/2, 1.2*cm,
        f"PCS3732 – Laboratório de Processadores | Planejamento Pré-Aula 08 | Pág. {doc.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print("PDF gerado:", OUTPUT)
