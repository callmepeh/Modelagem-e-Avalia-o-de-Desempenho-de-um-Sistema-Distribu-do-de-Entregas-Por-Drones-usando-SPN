# Entregas por drones — Trabalho 07 (SPN)

Repositório de dados, configurações e código de geração dos gráficos do artigo **Modelagem e Avaliação de Desempenho de um Sistema Distribuído de Entregas por Drones Usando Redes de Petri Estocásticas**.

## Link do vídeo no YouTube: 
**  **

## Regenerar as figuras do artigo

Requer Python 3, pandas e Matplotlib. Na raiz do projeto:

```bash
python3 -m pip install -r requirements.txt
python3 gerar_graficos_jupiter.py
```

O script lê as métricas exportadas pelo Jupiter nas pastas `dados/E1_demanda`, `dados/E2_frota`, `dados/E3_capacidade` e `dados/E4_combinado`. Ele recria as Figuras 3–6 do artigo em `figs/fig_E1.pdf` a `figs/fig_E4.pdf`, também em PNG, e grava os pontos efetivamente usados em `figs/dados_figuras.csv`.

Na Figura 3, os pontos são resultados Jupiter. As linhas tracejadas de MRT vêm da validação cruzada CTMC em `dados/validacao_cruzada_ctmc.csv`; a linha CTMC de utilização é calculada por `100 × λ × 22 / 4`, com MPT de 22 min e quatro drones, como descrito no artigo. O script não simula nem inventa resultados.

## Organização

- `artigo/`: PDF final do artigo IEEE.
- `modelo/`: configuração de execução no Jupiter e imagem do modelo SPN.
- `dados/E1_demanda/` a `dados/E4_combinado/`: CSVs nomeados por experimento e cenário.
- `dados/brutos/`: exportações originais do Jupiter, mantidas sem alteração.
- `dados/manifesto_experimentos.csv`: associação entre cenários, CSVs organizados e arquivos brutos de origem.
- `dados/tabela_consolidada_resultados.csv`: resultados consolidados apresentados no artigo.
- `dados/validacao_cruzada_ctmc.csv`: valores usados na comparação independente com CTMC.
- `dados/dimensionamento_whatif_sla.csv`: análise complementar de dimensionamento.
- `figs/`: figuras reproduzíveis incluídas no artigo e dados dos gráficos.
- `gerar_graficos_jupiter.py`: script de geração das figuras.

Os CSVs com nomes de cenário são cópias organizadas das exportações correspondentes. Consulte o manifesto para rastrear cada cópia até o CSV original. Os gráficos são compatíveis com os valores publicados no artigo, incluindo as quatro comparações E1–E4.

## Artigo

O artigo tem seis páginas e inclui os resultados, a discussão e as referências. O vídeo e o endereço deste repositório devem ser adicionados ao PDF final nos campos de disponibilidade antes da submissão, se ainda não tiverem sido atualizados.
