# Simulador de execução fora de ordem com scoreboard - MO401 - 1s2023

## Objetivo Geral

Neste trabalho vamos desenvolver um simulador de execução fora de ordem com a técnica de scoreboarding. O simulador deve receber como entrada dois arquivos:

- Programa a ser executado, em assembly do RISC-V, contendo apenas instruções de um determinado subconjunto (especificado abaixo). Um exemplo de programa é:

```assembly
fld f1, 0(x1)
fld f5, 0(x1)
fdiv f2, f4, f5
```

- Configuração das Unidades Funcionais, indicando a quantidade de unidades de cada tipo, e o número de ciclos necessários para completar a execução naquela unidade. Um exemplo de configuração é:

#### Se não passada uma configuração, a default é utilizada

```assembly
integer 1 1
mult 2 4
add 1 2
div 1 10
```

## The Code

### pip installing the project

```bash
git clone https://github.com/Nicolas-Moliterno/Scoreboarding.git
pip3 install -r requirements.txt
```

## Run the code

### Via shell, using the command

```bash
python3 scoreboard.py <NAME_FILE>.s
```
