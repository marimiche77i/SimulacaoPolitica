#!/usr/bin/env python3
# coding: utf-8


# SimOp_Entrada_v2r4


import datetime
import locale
import pandas as pd
import random
import sys
import time

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

tstamp = str(datetime.datetime.now())[:19].replace(' ', '_')



# FUNÇÕES #


def check(m):

    print('')
    print(m)
    print('')

    sys.exit()


def log(m):

    print(m, file=arqRelatorio)


def logPrint(m):

    print(m)
    print(m, file=arqRelatorio)


def veiculoDefinir(lstSorteioTipo):

    return ( lstSorteioTipo[random.randint(0, len(lstSorteioTipo) - 1)] - 1 )



# A. INICIALIZAÇÃO

print ( '' )
print ( 100*'=' )
print ( '{:^100}'.format('SIMULAÇÃO REFERÊNCIA ' + tstamp ) )
print ( 100*'=' )
print ( '' )


# Ler arquivo de pedidos:

frmPedidos = pd.read_csv('SimOp_Entrada_Pedidos.csv', encoding='ISO-8859-1', sep='\t').reset_index(drop=True)

frmPedidos['DataEmissao'] = pd.to_datetime(frmPedidos['DataEmissao'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

print ( '' )
print ( 'Pedidos:' )
print ( 100*'-' )
print ( frmPedidos )
print ( 100*'-' )
print ( '' )

qtdPedidos = len(frmPedidos)

frmPedidos['DataEmbarque']  = pd.Series([None] * qtdPedidos)
frmPedidos['DataDespacho']  = pd.Series([None] * qtdPedidos)
frmPedidos['Romaneio']      = pd.Series([None] * qtdPedidos)

# lstDatasOperacionais = frmPedidos['DataEmissao'].unique().tolist()


# Ler arquivo de tipos de veículos:

frmTiposVeiculos = pd.read_csv('SimOp_Entrada_TiposVeiculos.csv', encoding='ISO-8859-1').reset_index(drop=True)

print ( '' )
print ( 'Tipos de veículos:' )
print ( 100*'-' )
print ( frmTiposVeiculos )
print ( 100*'-' )
print ( '' )

lstSorteioTipo = []

for i in range( len(frmTiposVeiculos) ):

    tipo = frmTiposVeiculos.iloc[[i]]

    lstSorteioTipo.append(int(tipo['Tipo']))


# Ler arquivo de custos de transporte:

frmCustosTransporte = pd.read_csv('SimOp_Entrada_CustosTransporte.csv', encoding='ISO-8859-1').reset_index(drop=True)

print ( '' )
print ( 'Custos do transporte:' )
print ( 100*'-' )
print ( frmCustosTransporte[['TipoVeiculo','Faixa','EntregasMin','EntregasMax']] )
print ( 100*'-' )
print ( '' )


# Criar a tabela de custos por pedido:

frmCustosPorPedido = pd.DataFrame(columns=[ 'NotaFiscal',\
                                            'DataEmissao',\
                                            'DataEmbarque',\
                                            'DataDespacho',\
                                            'Romaneio',\
                                            'TranspRedespacho',\
                                            'Tipo',\
                                            'Faixa',\
                                            'ValorNF',\
                                            'CustoTransporte' ])


# Criar a tabela de custos por romaneio:

frmCustosPorRomaneio = pd.DataFrame(columns=[   'Romaneio',\
                                                'QtdPedidos',\
                                                'PesoPedidos',\
                                                'DataDespacho',\
                                                'Tipo',\
                                                'Faixa',\
                                                'CustoTransporte' ])


# Ler constantes definidas pelo pesquisador:


strTexto = 'Identificador: '
IDENTIFICADOR   = input(strTexto) or ''
if IDENTIFICADOR != '' : IDENTIFICADOR = '_' + IDENTIFICADOR


# ~ print ( '' )
# ~ strTexto = 'Data máxima da simulação: [2017-09-30] '
# ~ DATA_MAX   = int(input(strTexto) or '2017-09-30')
DATA_MAX = '2018-01-01'

# ~ print ( '' )
# ~ strTexto = 'Autorizações de embarque: [2] '
# ~ AUTORIZACOES   = int(input(strTexto) or 2)
AUTORIZACOES   = 2

print ( '' )
strTexto = 'Ordenar pedidos (1) como recebido, (2) por peso crescente ou  (3) por peso decrescente: [1] '
ORDEM  = str(input(strTexto) or '1')

# ~ print ( '' )
# ~ strTexto = 'Percentual de volume de despacho: [90] '
# ~ PERC_DESPACHO  = int(input(strTexto) or 90)
PERC_DESPACHO  = 90

# ~ print ( '' )
# ~ strTexto = 'Volume máximo diário de embarque: [90000] '
# ~ Q_MAX_DIARIO  = int(input(strTexto) or 90000)
Q_MAX_DIARIO  = 90000


# Declarar ponteiros e acumuladores:

custoTranspPedido           = 0
custoTranspRomaneio         = 0
custoTranspTotal            = 0

dataCorrente                = None
dataOperacional             = None

qtdAutorizados              = None
pesoAutorizados             = None

qtdRecusados                = None
pesoRecusados               = None

qtdSelecionadosPendente     = None
pesoSelecionadosPendente    = None

qtdSelecionadosNovo         = None
pesoSelecionadosNovo        = None

qtdSelecionadosTotal        = None
pesoSelecionadosTotal       = None

qtdEmbarcados               = None
pesoEmbarcados              = None

romaneioCorrente            = 0

veiculoCorrente             = None


# Declarar variáveis de conveniência:

strTexto    = None

strSaida    = None

strFormato  = None


# Escolher o primeiro veículo:

romaneioCorrente += 1

veiculoCorrente = veiculoDefinir(lstSorteioTipo)

Q_MAXIMO    = frmTiposVeiculos.iloc[veiculoCorrente]['CapPeso']

Q_DESPACHO  = Q_MAXIMO * PERC_DESPACHO / 100

veiculoDescricao = frmTiposVeiculos.iloc[veiculoCorrente]['DescricaoTipo']


# (Gerar a lista de datas operacionais: )

lstDatasOperacionais = frmPedidos['DataEmissao'][frmPedidos['DataEmissao'] <= DATA_MAX].unique().tolist()


# (Criar os relatórios de saída:)

arqRelatorio = open('SimOp' + IDENTIFICADOR + '_Saida_Relatorio_' + tstamp + '.txt', 'w')


arqResultados = open('SimOp' + IDENTIFICADOR + '_Saida_Resultados_' + tstamp + '.csv', 'w')


print('pedidoNF,','pedidoDestino,','pedidoValor,','pedidoPeso,','veiculoRomaneio,','veiculoTipo', file=arqResultados)



# (Imprimir o cabeçário do relatório:)

log( 100*'=' )
log( '{:^100}'.format('R E L A T Ó R I O   G E R A L   D A   S I M U L A Ç Ã O') )
log( 100*'=' )
log( '' )
log( '{:^100}'.format(time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())) )
log( '' )
log( '' )


log( '{:^100}'.format('PARÂMETROS GERAIS') )
log( 100*'-' )
log( '{:50}{:>41n}   kg/dia'.format('Limite contratual de embarque (kg):',  Q_MAX_DIARIO)   )
log( '{:50}{:>41n}       kg'.format('Percentual de despacho (%):',          PERC_DESPACHO)  )
log( '{:50}{:>41n} /seleção'.format('Autorizações:',                        AUTORIZACOES)   )


if ORDEM == '1':

    log( '{:50}{:>50}'.format('Modo de embarque:', 'Ordem original') )

if ORDEM == '2':

    log( '{:50}{:>50}'.format('Modo de embarque:', 'Peso/crescente') )

if ORDEM == '3':

    log( '{:50}{:>50}'.format('Modo de embarque:', 'Peso/Decrescente') )

log( 100*'-' )
log( '' )
log( '' )


# (Imprimir resumo dos pedidos com data da NF, quantidade e peso, bem como se)
# (o volume de novos pedidos está acima da volume máximo de embarque:)

log( '{:^100}'.format('RESUMO DOS PEDIDOS') )
log( 100*'·' )

strFormat = '          {:^20}{:^20}{:^20}{:^20}          '
log( strFormat.format('Data NF', 'Qtd','Peso (kg)', 'Excesso?') )
log( 100*'·' )


for dataOperacional in lstDatasOperacionais:

    qtdPedidos   = frmPedidos['NotaFiscal'][(frmPedidos['DataEmissao']==dataOperacional)].count()

    pesoPedidos  = frmPedidos['Peso'][(frmPedidos['DataEmissao']==dataOperacional)].sum()

    excesso = 'SIM' if pesoPedidos > Q_MAX_DIARIO else ''

    strFormato      = '          {:^20}{:^20n}{:^20n}{:^20}          '
    log ( strFormato.format(dataOperacional, qtdPedidos, pesoPedidos, excesso) )

log( 100*'-' )
log( '' )
log( '' )


log( 100*'-' )
log( '{:^100}'.format('R E S U M O   D O S   E V E N T O S') )
log( 100*'-' )
log( '' )
log( '' )




hrSimulacaoInicio = time.time()

print ( '' )
print ( 100*'=' )
print ( 'Simulação iniciada às ' + time.strftime('%H:%M:%S', time.localtime()) + '.' )
print ( 100*'=' )
print ( '' )



# B. SIMULAÇÃO

for dataOperacional in range( len(lstDatasOperacionais) ):


    # Avançar para a próxima data operacional:

    dataCorrente = lstDatasOperacionais[dataOperacional]


    # Selecionar pedidos emitidos até a data corrente e ainda não embarcados:

    frmSelecionados = frmPedidos [(frmPedidos['DataEmissao'] <= dataCorrente) & (frmPedidos['Romaneio'].isna())]

    frmSelecionados = frmSelecionados.reset_index(drop=True)

    qtdSelecionadosPendente     = len(frmSelecionados[frmSelecionados['DataEmissao'] < dataCorrente ])
    pesoSelecionadosPendente    = frmSelecionados['Peso'][frmSelecionados['DataEmissao'] < dataCorrente ].sum()

    qtdSelecionadosNovo         = len(frmSelecionados[frmSelecionados['DataEmissao'] == dataCorrente ])
    pesoSelecionadosNovo        = frmSelecionados['Peso'][frmSelecionados['DataEmissao'] == dataCorrente ].sum()

    qtdSelecionadosTotal        = len(frmSelecionados)
    pesoSelecionadosTotal       = frmSelecionados['Peso'].sum()


    # (Criar coluna de autorizações na tabela de selecionados:)

    frmSelecionados['Autorizacoes'] = pd.Series([0] * qtdSelecionadosTotal)


    # Ordenar pedidos selecionados:

    if ORDEM == '1':

        frmSelecionados = frmSelecionados.sample(frac=1).reset_index(drop=True)

    if ORDEM == '2':

        frmSelecionados = frmSelecionados.sort_values(by=['DataEmissao', 'Peso' ], ascending=[True,True])

    if ORDEM == '3':

        frmSelecionados = frmSelecionados.sort_values(by=['DataEmissao', 'Peso' ], ascending=[True, False])


# C. AUTORIZAÇÃO

    # ( Zerar variáveis para estatística de seleção e autorização: )

    qtdRecusados = 0
    pesoRecusados = 0

    qtdAutorizados = 0

    # Zerar acumulador:

    pesoAutorizados = 0


    for iPedido in range( len(frmSelecionados.index) ):

        # Avançar para próximo pedido:

        pesoPedido = frmSelecionados.iloc[iPedido]['Peso']


        # Peso do pedido corrente + peso acumulado no veículo fica
        # abaixo do volume máximo diário?

        if (pesoPedido + pesoAutorizados) <= Q_MAX_DIARIO:

            # Sim, atribua autorizações ao pedido:

            frmSelecionados.loc[iPedido,'Autorizacoes'] = AUTORIZACOES

            # Adicione peso do pedido ao acumulado:

            pesoAutorizados = pesoAutorizados + pesoPedido

            # ( Incremente o contador de autorizados: )

            qtdAutorizados = qtdAutorizados + 1

        else:

            # Não (incremente o contador e acumulador dos recusados:)

            qtdRecusados = qtdRecusados + 1

            pesoRecusados = pesoRecusados + pesoPedido


    # ( Imprimir no relatório as estatísticas da seleção e autorização: )

    strFormato = '{:10}      {:>21}{:>21}{:>21}{:>21}'
    print( strFormato.format('', 'Pendentes', '+ Novos', '= Selecionados', 'Autorizados') )

    strFormato = '{:10}      {:>6}{:>15}{:>6}{:>15}{:>6}{:>15}{:>6}{:>15}'
    print( strFormato.format('', 'Qtd', 'kgf', 'Qtd', 'kgf', 'Qtd', 'kgf', 'Qtd', 'kgf' ) )

    strFormato = '{:10}      {:>6}{:>15n}{:>6}{:>15n}{:>6}{:>15n}{:>6}{:>15n}'
    print( strFormato.format(\
                                dataCorrente,\
                                qtdSelecionadosPendente, pesoSelecionadosPendente,\
                                qtdSelecionadosNovo, pesoSelecionadosNovo,\
                                qtdSelecionadosTotal, pesoSelecionadosTotal,\
                                qtdAutorizados, pesoAutorizados) )

    print( '' )


    log( 100*'-' )

    strFormato = '{:10}      {:>21}{:>21}{:>21}{:>21}'
    log( strFormato.format('', 'Pendentes', '+ Novos', '= Doca', 'Autorizados') )

    strFormato = '{:10}      {:>6}{:>15}{:>6}{:>15}{:>6}{:>15}{:>6}{:>15}'
    log( strFormato.format('', 'Qtd', 'kgf', 'Qtd', 'kgf', 'Qtd', 'kgf', 'Qtd', 'kgf' ) )

    strFormato = '{:10}      {:>6}{:>15n}{:>6}{:>15n}{:>6}{:>15n}{:>6}{:>15n}'
    log( strFormato.format(\
                                dataCorrente,\
                                qtdSelecionadosPendente, pesoSelecionadosPendente,\
                                qtdSelecionadosNovo, pesoSelecionadosNovo,\
                                qtdSelecionadosTotal, pesoSelecionadosTotal,\
                                qtdAutorizados, pesoAutorizados) )


    log( 100*'-' )
    log( '' )



    log( '' )
    log( '{:^100}'.format('Pedidos Recusados') )
    log( 100*'·' )

    strFormat = '                    {:^20}{:^20}{:^20}                    '
    log( strFormat.format('Data de Emissão', 'Nota Fiscal','Peso (kg)') )
    log( 100*'·' )


    for i, item in frmSelecionados.iterrows():

        strFormato      = '                    {:^20}{:^20}{:>20n}                    '

        if item['Autorizacoes'] == 0:

            log ( strFormato.format(item['DataEmissao'], item['NotaFiscal'], item['Peso']) )
    log( '' )
    log( '' )


    log( '' )
    log( '{:^100}'.format('Pedidos Autorizados') )
    log( 100*'·' )
    strFormato = '{:>9}{:>20}{:>17}{:>9}{:>12}{:>12}{:>12}{:>9}'
    log(strFormato.format('Romaneio','Veículo','Peso vago (kg)','Pedido','Emissão','Peso (kg)','Embarque?','Autoriz') )
    log( 100*'·' )




# D. EMBARQUE

    # ( Zerar variável para estatística de embarque: )

    qtdEmbarcados    = 0


    # Zerar acumulador:

    pesoEmbarcados   = 0


    while frmSelecionados['Autorizacoes'].sum() > 0:

        for i, selecionado in frmSelecionados[frmSelecionados['Autorizacoes'] > 0].iterrows():


            # Avançar para o próximo pedido com autorizações > 0:

            lstIndicePedidos = frmPedidos.index[ frmPedidos['NotaFiscal'] == selecionado['NotaFiscal'] ].tolist()

            indicePedidoCorrente = lstIndicePedidos[0]

            pesoDisponivel = Q_MAXIMO - pesoEmbarcados

            # ( Imprimir resumo da tentativa no relatório: )

            strFormato = '     {:0>4}{:>20}{:>17n}{:>9}{:>12}{:>12n}'

            print( strFormato.format(\
                                        romaneioCorrente,\
                                        veiculoDescricao,\
                                        pesoDisponivel,\
                                        selecionado['NotaFiscal'],\
                                        selecionado['DataEmissao'],\
                                        selecionado['Peso']) , end='', file=arqRelatorio )


            # Peso do pedido corrente < peso disponível para embarque?

            if selecionado['Peso'] <= pesoDisponivel:


                # Sim, registrar no pedido o número do romaneio e a data de embarque:

                frmPedidos.at[indicePedidoCorrente,'Romaneio'] = romaneioCorrente

                frmPedidos.at[indicePedidoCorrente,'DataEmbarque'] = dataCorrente


                # Incluir o pedido na tabela de custos por pedido:


                frmCustosPorPedido.loc[len(frmCustosPorPedido),:] = [\
                                                                        selecionado['NotaFiscal'],\
                                                                        selecionado['DataEmissao'],\
                                                                        dataCorrente,\
                                                                        None,\
                                                                        romaneioCorrente,\
                                                                        selecionado['TranspRedespacho'],\
                                                                        None,\
                                                                        None,\
                                                                        selecionado['ValorNFs'],\
                                                                        None ]


                # Zerar autorizações do pedido:

                frmSelecionados.at[i,'Autorizacoes'] = 0


                # ( Incrementar contador de embarcados: )

                qtdEmbarcados = qtdEmbarcados + 1


                # Acrescentar peso do pedido corrente ao peso embarcado:

                pesoEmbarcados = pesoEmbarcados + selecionado['Peso']


                # ( Imprimir no relatório a confirmação de embarque: )

                log ( '{:>12}{:>9}'.format('SIM', '0') )


                # ( Imprimir no arquivo de resultados os dados relevantes do embarque: )

                strSaida =  str(selecionado['NotaFiscal']) + ','
                strSaida += str(selecionado['TranspRedespacho']) + ','
                strSaida += str(selecionado['ValorNFs']) + ','
                strSaida += str(selecionado['Peso']) + ','
                strSaida += str(romaneioCorrente) + ','
                strSaida += str(frmTiposVeiculos.iloc[veiculoCorrente]['Tipo'])

                print( strSaida, file=arqResultados )

            else:

                # Não, decrementar as autorizações do pedido corrente:

                frmSelecionados.at[i,'Autorizacoes'] = frmSelecionados.at[i,'Autorizacoes'] - 1


                # ( Imprimir no relatório a recusa de embarque: )

                log ( '{:>12}{:>9}'.format('NÃO', frmSelecionados.at[i,'Autorizacoes']) )

# E. DESPACHO

            # Veículo atingiu o volume de despacho:

            if pesoEmbarcados > Q_DESPACHO:


                # Sim, registrar a data de despacho nos pedidos embarcados:

                frmPedidos.loc[frmPedidos['Romaneio']==romaneioCorrente, 'DataDespacho'] = dataCorrente


                # Registrar a data de despacho e o tipo de veículo na tabela de custos por pedido:

                frmCustosPorPedido.loc[frmCustosPorPedido['Romaneio']==romaneioCorrente, 'DataDespacho']\
                    = dataCorrente

                frmCustosPorPedido.loc[frmCustosPorPedido['Romaneio']==romaneioCorrente, 'Tipo'] =\
                    frmTiposVeiculos.iloc[veiculoCorrente]['Tipo']


                # Obter a quantidade de entregas no despacho:

                lstEntregasDespacho = frmCustosPorPedido.loc[\
                    frmCustosPorPedido['Romaneio']==romaneioCorrente, 'TranspRedespacho'].unique().tolist()

                qtdEntregasDespacho = len(lstEntregasDespacho)


                # Obter a faixa de custos referente ao tipo de veículos e quantidade de entregas:

                faixaCustos =  int(frmCustosTransporte['Faixa'][\

                        ( frmCustosTransporte['TipoVeiculo'] == frmTiposVeiculos.iloc[veiculoCorrente]['Tipo']) &\

                        ( frmCustosTransporte['EntregasMin'] <= qtdEntregasDespacho) &\

                        ( frmCustosTransporte['EntregasMax'] >= qtdEntregasDespacho) ])


                # Registrar na tabela de custo por pedido a faixa de custos para cada pedido no romaneio:

                frmCustosPorPedido.loc[frmCustosPorPedido['Romaneio']==romaneioCorrente, 'Faixa'] = faixaCustos


                # Registrar o despacho na tabela de custos por romaneio:

                frmCustosPorRomaneio.loc[len(frmCustosPorRomaneio),:] = [\
                                                                        romaneioCorrente,\
                                                                        qtdEmbarcados,\
                                                                        pesoEmbarcados,\
                                                                        dataCorrente,\
                                                                        frmTiposVeiculos.iloc[veiculoCorrente]['Tipo'],\
                                                                        faixaCustos,\
                                                                        0 ]


                # Obter e registrar na tabela de custo por pedido o custo do transporte para cada pedido no romaneio:

                lstNFsNoRomaneio = frmPedidos.loc[frmPedidos['Romaneio'] == romaneioCorrente, 'NotaFiscal'].tolist()

                custoTranspRomaneio = 0

                for iNF in range(len(lstNFsNoRomaneio)):

                    indNotaFiscal = frmCustosTransporte.columns.get_loc(str(lstNFsNoRomaneio[iNF]))

                    indFaixaCusto = frmCustosTransporte.index[frmCustosTransporte['Faixa'] == faixaCustos]

                    custoTranspPedido = frmCustosTransporte.iloc[indFaixaCusto[0], indNotaFiscal]

                    frmCustosPorPedido.loc[frmCustosPorPedido['NotaFiscal'] ==\
                        lstNFsNoRomaneio[iNF], 'CustoTransporte'] = custoTranspPedido

                    custoTranspRomaneio = custoTranspRomaneio + custoTranspPedido

                    custoTranspTotal    = custoTranspTotal + custoTranspPedido


                # Registrar o custo total do transporte do romaneio corrente na tabela de custo por romaneio:

                frmCustosPorRomaneio.loc[frmCustosPorRomaneio['Romaneio']==romaneioCorrente, 'CustoTransporte'] =\
                    custoTranspRomaneio


                # ( Imprimir no relatório informações do despacho: )

                log ( '' )
                strFormato = '     {:0>4} DESPACHADO COM {:} PEDIDOS ({:n} kgf) ao custo de R$ {:2n}'
                log ( strFormato.format( romaneioCorrente, qtdEmbarcados, pesoEmbarcados, custoTranspRomaneio ) )
                log ( '' )


                # Incrementar número do romaneio:

                romaneioCorrente = romaneioCorrente + 1


                # Zerar contador e acumulador:

                qtdEmbarcados = 0

                pesoEmbarcados = 0


                # Definir novo veículo:

                veiculoCorrente = veiculoDefinir(lstSorteioTipo)


                # Ajustar parâmetros:

                veiculoDescricao = frmTiposVeiculos.iloc[veiculoCorrente]['DescricaoTipo']

                Q_MAXIMO    = frmTiposVeiculos.iloc[veiculoCorrente]['CapPeso']

                Q_DESPACHO  = Q_MAXIMO * PERC_DESPACHO / 100


                break



    log ( 100*'-')
    log ('')
    log ('')


# ( Exportar CVS de custos: )

frmCustosPorPedido.to_csv('SimOp' + IDENTIFICADOR + '_Saida_CustosPorPedido_' + tstamp + '.csv')

frmCustosPorRomaneio.to_csv('SimOp' + IDENTIFICADOR + '_Saida_CustosPorRomaneio_' + tstamp + '.csv')


# ( Imprimir custo total no relatório: )


log ( '' )
log( '{:^100}'.format('Custo total do transporte: ' + locale.currency(custoTranspTotal, grouping=True) ) )
log ( '' )

print ( '' )
print ( '{:^100}'.format('Veículos abertos: ' + str(romaneioCorrente)) )
print ( '' )

print ( '' )
print ( '{:^100}'.format('Custo total do transporte: ' + locale.currency(custoTranspTotal, grouping=True) ) )
print ( '' )

hrSimulacaoTermino = time.time()



print ( '' )
print ( 100*'-' )
print ( 'Simulação encerrada às ' + time.strftime('%H:%M:%S', time.localtime()) + '.' )
print ( 'Duração da simulação: ' + str(hrSimulacaoTermino - hrSimulacaoInicio) + ' segundos.' )
print ( 100*'=' )

log( '' )
log( '' )
log( '{:^100}'.format('Duração da simulação: ' + str(hrSimulacaoTermino - hrSimulacaoInicio) + ' segundos.') )
log( '' )
log( '' )
