# Quick Start - TMS Route Optimizer

## Fluxo Rápido de Uso

```
1. Configurar Time TMS
   └── Definir depósito com geolocalização
   └── Definir tipos de veículos permitidos

2. Configurar Veículos
   └── Capacidades (peso e volume)
   └── Custos (por KM e mínimo)
   └── Vincular ao Time

3. Criar Pedidos TMS com Paradas
   └── Paradas em estado 'draft'
   └── Clientes com geolocalização
   └── Definir peso e volume

4. Executar Otimização
   └── TMS > Route Optimizer > Criar
   └── Selecionar Time e período
   └── Verificar paradas selecionadas
   └── Clicar em "Run Optimization"

5. Analisar Resultados
   └── Verificar rotas geradas
   └── Verificar utilização de capacidade
   └── Ver URLs do Google Maps/Waze

6. Criar Pedidos
   └── Clicar em "Create Orders"
   └── Pedidos serão criados automaticamente
```

## Checklist de Pré-requisitos

- [ ] Módulo `ortools` instalado (`pip install ortools`)
- [ ] Time TMS configurado com depósito e tipos de veículos
- [ ] Veículos configurados com capacidades e custos
- [ ] Pedidos TMS criados com paradas em estado `draft`
- [ ] Todos os parceiros têm geolocalização configurada

## Campos Obrigatórios

### Time TMS

- Default Depot Location (com latitude/longitude)
- Allowed Vehicle Types

### Veículos

- Weight Capacity (kg)
- Volume Capacity (m³)
- Cost per KM
- Minimum Trip Cost
- TMS Team

### Paradas

- Partner (com latitude/longitude)
- Weight (kg)
- Volume (m³)
- Scheduled Date
- State = 'draft'

## Comandos Úteis

### Instalar OR-Tools

```bash
pip install ortools
```

### Verificar parâmetros do sistema

```
Configuração > Parâmetros Técnicos > Parâmetros do Sistema
- tms.route_optimizer.max_time_seconds (padrão: 300)
- tms.route_optimizer.max_deliveries (padrão: 100)
```

## Troubleshooting Rápido

| Erro                    | Solução                                                         |
| ----------------------- | --------------------------------------------------------------- |
| "No delivery stops"     | Verificar período de datas e estado das paradas                 |
| "No geolocation"        | Configurar latitude/longitude nos parceiros                     |
| "No vehicles available" | Verificar veículos do time e tipos permitidos                   |
| "No feasible solution"  | Capacidade insuficiente - adicionar veículos ou remover paradas |

## Exemplo de Dados Demo

O módulo inclui dados demo com:

- 1 Depósito em São Paulo
- 8 Clientes com coordenadas reais
- 2 Veículos (500 kg, 10 m³, R$ 2,50/km)
- 1 Pedido TMS com 8 paradas

Para usar os dados demo:

1. Instale o módulo com `--load-language` se necessário
2. Os dados demo serão carregados automaticamente
3. Acesse TMS > Route Optimizer e use o time "Team Route Optimizer - São Paulo"
