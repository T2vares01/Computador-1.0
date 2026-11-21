# Computador-1.0

FPGA
Um FPGA (Field-Programmable Gate Array) é um circuito integrado programável que permite configurar seu hardware internamente após a fabricação. Amplamente usado em sistemas embarcados, comunicações e pesquisa, ele combina flexibilidade de software com desempenho próximo ao de hardware dedicado (ASICs).

Fatos-chave
Sigla: Field-Programmable Gate Array

Configuração: Por memória volátil, via bitstream

Aplicações típicas: Processamento de sinais, controle industrial, aceleração de IA, prototipagem

Vantagem central: Reconfigurável após implantação

Arquitetura e funcionamento
O FPGA é composto por milhares de blocos lógicos programáveis, interconexões configuráveis e blocos de entrada/saída. Esses elementos são definidos por uma “bitstream” — um arquivo gerado a partir de linguagens de descrição de hardware como VHDL ou Verilog — que especifica a lógica e as rotas internas. Essa arquitetura paralela permite alto desempenho e latência reduzida em tarefas específicas.

Desenvolvimento e ferramentas
O desenvolvimento envolve síntese lógica, implementação física e carregamento da configuração no dispositivo. Fabricantes oferecem ferramentas proprietárias, como o Vivado (AMD Xilinx) e o Quartus Prime (Intel), que incluem simulação, análise temporal e otimização. Também existem soluções abertas como Yosys e nextpnr.

Usos e impacto
FPGAs são empregados em data centers, redes 5G, processamento de vídeo, dispositivos médicos e até exploração espacial. Sua capacidade de reprogramação rápida permite adaptar hardware a novos padrões e algoritmos sem fabricar novos chips, reduzindo custos e tempo de desenvolvimento.

Comparação com ASICs e CPUs
Enquanto CPUs são versáteis e ASICs oferecem eficiência máxima, FPGAs ocupam um ponto intermediário: desempenho elevado, menor consumo que software genérico e flexibilidade para modificações futuras — uma vantagem em aplicações de pesquisa e prototipagem industrial.
