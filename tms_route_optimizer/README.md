# Manual de Uso - TMS Route Optimizer

## Sumário

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Configuração Inicial](#configuração-inicial)
4. [Como Usar](#como-usar)
5. [Entendendo os Resultados](#entendendo-os-resultados)
6. [Criando Pedidos a partir da Otimização](#criando-pedidos-a-partir-da-otimização)
7. [Dicas e Boas Práticas](#dicas-e-boas-práticas)
8. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O módulo **TMS Route Optimizer** utiliza o Google OR-Tools para otimizar rotas de
entrega, considerando:

- Capacidade de peso e volume dos veículos
- Distâncias entre pontos (cálculo Haversine)
- Custos por quilômetro e custo mínimo por viagem
- Múltiplos veículos e múltiplas paradas

O algoritmo resolve um problema de VRP (Vehicle Routing Problem) para encontrar a melhor
distribuição de paradas entre os veículos disponíveis.

---

## Pré-requisitos

1. **Dependências Python**: O módulo requer `ortools` instalado

   ```bash
   pip install ortools
   ```

2. **Módulos Odoo necessários**:

   - `tms` (Transport Management System)
   - `tms_delivery_stops`
   - `tms_vehicle_capacity`
   - `base_geolocalize`

3. **Dados configurados**:
   - TMS Team com depósito padrão configurado
   - Veículos com capacidades e custos definidos
   - Paradas de entrega com geolocalização

---

## Configuração Inicial

### 1. Configurar o TMS Team

Acesse **TMS > Configuração > Teams** e configure:

- **Allowed Vehicle Types**: Tipos de veículos permitidos para este time
- **Default Depot Location**: Localização do depósito (deve ter coordenadas de
  latitude/longitude)

**Importante**: O depósito deve ter geolocalização configurada (`partner_latitude` e
`partner_longitude`).

### 2. Configurar Veículos

Em **Fleet > Vehicles**, cada veículo deve ter:

- **Weight Capacity**: Capacidade de peso (kg)
- **Volume Capacity**: Capacidade de volume (m³)
- **Cost per KM**: Custo por quilômetro
- **Minimum Trip Cost**: Custo mínimo da viagem
- **TMS Team**: Time ao qual o veículo pertence
- **Vehicle Type**: Tipo do veículo (deve estar nos tipos permitidos do time)

### 3. Criar Pedidos TMS com Paradas

Crie pedidos TMS (**TMS > Orders**) com paradas de entrega. Cada parada deve ter:

- **Partner**: Cliente/endereço (com geolocalização configurada)
- **Weight**: Peso da carga (kg)
- **Volume**: Volume da carga (m³)
- **Scheduled Date**: Data/hora prevista para entrega
- **State**: Estado `draft` (para serem incluídas na otimização)

**Importante**: Todos os parceiros (clientes) devem ter coordenadas de geolocalização
configuradas.

---

## Como Usar

### Passo 1: Acessar o Route Optimizer

Navegue até **TMS > Route Optimizer** no menu principal.

### Passo 2: Criar Nova Otimização

Clique em **Criar** para iniciar uma nova otimização.

### Passo 3: Preencher Dados Básicos

Preencha os campos:

- **Name**: Nome da otimização (gerado automaticamente com data/hora)
- **Team**: Selecione o time TMS
- **Optimization Date**: Data da otimização
- **Date From**: Data/hora inicial para buscar paradas
- **Date To**: Data/hora final para buscar paradas

**Dica**: Ao selecionar o Team e as datas, as paradas são automaticamente carregadas
(paradas em estado `draft` dentro do período selecionado).

### Passo 4: Selecionar Paradas de Entrega

Na seção **Delivery Stops**, você verá as paradas encontradas automaticamente. Você
pode:

- Adicionar paradas manualmente clicando em **Adicionar uma linha**
- Remover paradas que não devem ser otimizadas
- Verificar se todas as paradas têm geolocalização (necessário)

**Importante**: Todas as paradas selecionadas devem ter coordenadas de
latitude/longitude configuradas nos seus parceiros.

### Passo 5: Executar a Otimização

Clique no botão **Run Optimization** na parte superior do formulário.

O sistema irá:

1. Validar os dados (paradas, veículos, geolocalizações)
2. Calcular a matriz de distâncias entre todos os pontos
3. Resolver o problema de VRP usando OR-Tools
4. Exibir os resultados

**Tempo de processamento**: Depende do número de paradas e veículos. Para 8-10 paradas,
geralmente leva alguns segundos.

### Passo 6: Analisar os Resultados

Após a otimização, você verá:

#### Resumo Geral

- **Total Cost**: Custo total de todas as rotas
- **Total Distance**: Distância total percorrida (km)
- **Total Vehicles Used**: Número de veículos utilizados
- **Optimization Time**: Tempo gasto na otimização (segundos)

#### Aba "Routes"

Lista todas as rotas geradas, mostrando para cada veículo:

- **Vehicle**: Veículo atribuído
- **Stop Count**: Número de paradas na rota
- **Total Distance**: Distância da rota (km)
- **Total Weight**: Peso total transportado (kg)
- **Total Volume**: Volume total transportado (m³)
- **Weight Utilization**: Percentual de utilização da capacidade de peso
- **Volume Utilization**: Percentual de utilização da capacidade de volume
- **Route Cost**: Custo total da rota

#### Aba "Raw Result"

Mostra o resultado bruto em formato JSON, útil para debug ou integrações.

### Passo 7: Visualizar Detalhes de uma Rota

Clique em uma rota na lista para ver detalhes:

- Informações do veículo
- Utilização de capacidade (com gráficos)
- Custos detalhados
- **Google Maps URL**: Link para visualizar a rota no Google Maps
- **Waze URL**: Link para navegação no Waze
- Lista de paradas na ordem otimizada

---

## Entendendo os Resultados

### Estrutura da Solução

Cada rota gerada contém:

1. **Depósito** → **Parada 1** → **Parada 2** → ... → **Parada N** → **Depósito**

Todas as rotas começam e terminam no depósito configurado no time.

### Métricas de Utilização

- **Weight Utilization**: `(Peso Total / Capacidade de Peso) × 100`
- **Volume Utilization**: `(Volume Total / Capacidade de Volume) × 100`

Valores próximos a 100% indicam melhor aproveitamento da capacidade.

### Cálculo de Custo

Custo de cada rota:

```
Custo = Custo Mínimo + (Distância × Custo por KM)
```

Custo total = Soma dos custos de todas as rotas geradas.

---

## Criando Pedidos a partir da Otimização

Após analisar os resultados e estiver satisfeito com a otimização:

1. Clique no botão **Create Orders** (disponível apenas quando a otimização está
   concluída)
2. O sistema criará automaticamente:
   - Um pedido TMS para cada rota
   - As paradas de entrega na ordem otimizada
   - Vinculará o veículo ao pedido
3. Você será redirecionado para a lista de pedidos criados

**Importante**: As paradas originais terão seu estado atualizado para `scheduled`.

---

## Dicas e Boas Práticas

### 1. Geolocalização Precisa

- Certifique-se de que todos os endereços têm coordenadas corretas
- Use o módulo `base_geolocalize` para geocodificar endereços automaticamente

### 2. Capacidades dos Veículos

- Configure capacidades realistas baseadas nos veículos reais
- Considere margem de segurança (não configure 100% da capacidade teórica)

### 3. Custos

- Configure custos por KM baseados em dados reais (combustível, manutenção, etc.)
- O custo mínimo por viagem ajuda a evitar viagens muito curtas não rentáveis

### 4. Período de Busca

- Selecione períodos adequados para agrupar entregas próximas
- Evite períodos muito longos que podem resultar em muitas paradas

### 5. Número de Veículos

- Tenha veículos suficientes para atender todas as paradas
- O algoritmo distribuirá as paradas entre os veículos disponíveis

### 6. Tempo de Otimização

- O tempo padrão é 300 segundos (5 minutos)
- Para muitas paradas (>50), pode ser necessário aumentar este tempo
- Configure em: **Configuração > Parâmetros Técnicos > Parâmetros do Sistema**

**Parâmetros disponíveis**:

- `tms.route_optimizer.max_time_seconds`: Tempo máximo para otimização (padrão: 300
  segundos)
- `tms.route_optimizer.max_deliveries`: Número máximo de entregas (padrão: 100)

### 7. Revisar Resultados

- Sempre revise as rotas geradas antes de criar os pedidos
- Verifique se a distribuição faz sentido geograficamente
- Use os links do Google Maps para visualizar as rotas

---

## Troubleshooting

### Erro: "No delivery stops to optimize"

**Causa**: Nenhuma parada foi selecionada.

**Solução**:

- Verifique o período de datas (Date From/Date To)
- Certifique-se de que há paradas em estado `draft` no período
- Adicione paradas manualmente se necessário

### Erro: "Stop [Nome] has no geolocation coordinates"

**Causa**: Um parceiro não tem coordenadas de latitude/longitude.

**Solução**:

- Acesse o parceiro (Contacts)
- Configure `partner_latitude` e `partner_longitude`
- Use o módulo `base_geolocalize` para geocodificar automaticamente

### Erro: "No vehicles available for this team"

**Causa**: Não há veículos configurados para o time ou os tipos de veículo não
correspondem.

**Solução**:

- Verifique se há veículos vinculados ao time
- Confirme que os tipos de veículo dos veículos estão nos "Allowed Vehicle Types" do
  time
- Configure veículos com capacidades e custos

### Erro: "No feasible solution found"

**Causa**: Não é possível atender todas as paradas com os veículos disponíveis
(capacidade insuficiente).

**Solução**:

- Verifique se a capacidade total dos veículos é suficiente para o peso/volume total
- Adicione mais veículos ao time
- Remova algumas paradas da otimização
- Aumente as capacidades dos veículos (se realista)

### Otimização muito lenta

**Causa**: Muitas paradas ou tempo de otimização insuficiente.

**Solução**:

- Aumente o parâmetro `tms.route_optimizer.max_time_seconds`
- Considere dividir as paradas em múltiplas otimizações (por região, por exemplo)

### Rotas não parecem otimizadas

**Causa**: Pode ser devido a várias razões (número de veículos, capacidades, distâncias,
etc.).

**Solução**:

- Verifique se as coordenadas estão corretas
- Aumente o tempo de otimização
- Revise as capacidades e custos dos veículos
- Considere agrupar paradas por região antes de otimizar

---

## Exemplo Prático

### Cenário: 8 entregas em São Paulo

1. **Configuração**:

   - Time: "Team Route Optimizer - São Paulo"
   - Depósito: "Depósito - Rua Luar do Sertão" (-23.6912741, -46.7982916)
   - 2 Veículos: Capacidade 500 kg, 10 m³, R$ 2,50/km, R$ 50,00 mínimo

2. **Paradas**:

   - 8 clientes em São Paulo com pesos e volumes variados
   - Total: 500 kg, 10,2 m³

3. **Otimização**:

   - Sistema divide as paradas entre 2 veículos
   - Calcula rotas otimizadas considerando distâncias
   - Gera URLs do Google Maps para cada rota

4. **Resultado**:
   - 2 rotas geradas
   - Distribuição equilibrada de carga
   - Custos calculados
   - Pedidos podem ser criados automaticamente

---

## Suporte Técnico

Para problemas ou dúvidas:

1. Verifique este manual primeiro
2. Revise a seção de Troubleshooting
3. Consulte os logs do Odoo para erros detalhados
4. Verifique se todas as dependências estão instaladas (`ortools`)

---

**Versão do Módulo**: 18.0.1.0.0 **Autor**: KMEE, Odoo Community Association (OCA)
**Licença**: AGPL-3
