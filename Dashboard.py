import streamlit as st
import requests 
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
##Criando a barra lateral
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região',regioes)

if regiao == 'Brasil':
    regiao = ''
#Filtro por ano
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(),'ano':ano}
##Criando a barra lateral
response = requests.get(url,params=query_string)
dados = pd.DataFrame.from_dict(response.json())
#Alterando formato da data para datetime
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'],format = '%d/%m/%Y')
#Filtro por vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores',dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

##Tabelas
receita_estados = dados.groupby('Local da compra')['Preço'].sum()
#drop_duplicates: remove linhas duplicadas após a realização do merge entre as tabelas
#subset: parâmetro que indica que queremos somente nomes únicos
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(receita_estados,left_on='Local da compra',right_index=True).sort_values('Preço',ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço',ascending=False)
###Tabela vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))
###Tabelas Desafio
quantidade_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
quantidade_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(quantidade_estados,left_on='Local da compra',right_index=True).sort_values('Preço',ascending=False)

vendas_mensais = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].count().reset_index()
vendas_mensais['Ano'] = vendas_mensais['Data da Compra'].dt.year
vendas_mensais['Mês'] = vendas_mensais['Data da Compra'].dt.month_name()

quantidade_venda_estados = dados.groupby('Local da compra')[['Preço']].count()
quantidade_venda_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra']].merge(quantidade_venda_estados,left_on='Local da compra',right_index=True).sort_values('Preço',ascending=False)

venda_categorias = dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False)

#Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                    lat='lat',
                                    lon='lon',
                                    scope='south america', # por padrão, o gráfico mostra o mapa mundi, mas como queremos somente informações do Brasil, colocaremos o escopo da América do Sul
                                    size='Preço',
                                    template='seaborn',
                                    hover_name='Local da compra', #para que quando passarmos o mouse sobre o círculo, nos seja informado o nome;
                                    hover_data={'lat':False,'lon':False},#para que não mostre as informações de latitude e longitude ao passar o mouse sobre o círculo;
                                    title='Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                                x = 'Mês',
                                y = 'Preço',
                                markers=True, #para identificar pontos como marcadores nos meses;
                                range_y=(0,receita_mensal.max()),#uma tupla identificando que o gráfico começa a partir de zero, e não a partir dos valores da tabela, e vai até o valor máximo de "receita_mensal";
                                color='Ano',# a cor será alterada com base na informação do ano;
                                line_dash='Ano', #para alterar o formato da linha com base na informação do ano;
                                title='Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto=True,
                             title = 'Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,text_auto=True,title='Receita por categoria') #Não precisa de informar o eixo x e y porque só tem as duas informações necessárias no grafico (categorias e preço)
fig_receita_categorias.update_layout(yaxis_title = 'Receita')
###Graficos desafios
fig_mapa_vendas = px.scatter_geo(quantidade_estados,
                                        lat='lat',
                                        lon='lon',
                                        scope='south america', # por padrão, o gráfico mostra o mapa mundi, mas como queremos somente informações do Brasil, colocaremos o escopo da América do Sul
                                        size='Preço',
                                        template='seaborn',
                                        hover_name='Local da compra', #para que quando passarmos o mouse sobre o círculo, nos seja informado o nome;
                                        hover_data={'lat':False,'lon':False},#para que não mostre as informações de latitude e longitude ao passar o mouse sobre o círculo;
                                        title='Quantidade de vendas por Estado')

fig_vendas_mensais = px.line(vendas_mensais,
                                x = 'Mês',
                                y = 'Preço',
                                markers=True, #para identificar pontos como marcadores nos meses;
                                range_y=(0,vendas_mensais.max()),#uma tupla identificando que o gráfico começa a partir de zero, e não a partir dos valores da tabela, e vai até o valor máximo de "receita_mensal";
                                color='Ano',# a cor será alterada com base na informação do ano;
                                line_dash='Ano', #para alterar o formato da linha com base na informação do ano;
                                title='Quantidade de vendas mensais')
fig_vendas_mensais.update_layout(yaxis_title='Quantidade de vendas')

fig_quantidade_venda_estados = px.bar(quantidade_venda_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto=True,
                             title = 'Top estados (Quantidade de vendas)')
fig_quantidade_venda_estados.update_layout(yaxis_title = 'Quantidade de vendas')

fig_venda_categorias = px.bar(venda_categorias,                            
                             text_auto=True,
                             title = 'Quantidade de vendas por categoria de produto')
fig_venda_categorias.update_layout(showlegend=False, yaxis_title = 'Vendas por categoria')
fig_venda_categorias.update_xaxes(tickangle=0) # Ajustando a rotação do eixo X



## Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])
with aba1:
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita,use_container_width=True)
        st.plotly_chart(fig_receita_estados,use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal,use_container_width=True)
        st.plotly_chart(fig_receita_categorias,use_container_width=True)
with aba2:
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(),'R$'))     
        st.plotly_chart(fig_mapa_vendas,use_container_width=True)   
        st.plotly_chart(fig_quantidade_venda_estados,use_container_width=True)   
    with coluna2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))        
        st.plotly_chart(fig_vendas_mensais,use_container_width=True)   
        st.plotly_chart(fig_venda_categorias,use_container_width=True)   
with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores',2,10,5)
    coluna1,coluna2 = st.columns(2)    
    with coluna1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(),'R$'))   
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum',ascending=True).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum',ascending=True).head(qtd_vendedores).index, # para selecionar o número de vendedores;
                                        text_auto = True,
                                        title=f'Top {qtd_vendedores} vendedores (receita)')     
        fig_receita_vendedores.update_layout(xaxis_title = 'Valor total de vendas')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))        
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count',ascending=True).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count',ascending=True).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')   
        fig_vendas_vendedores.update_layout(xaxis_title = 'Quantidade total de vendas')
        st.plotly_chart(fig_vendas_vendedores)


#st.dataframe(dados) #Exibindo o dataframe na página



