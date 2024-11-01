#O nome desse arquivo será o nome da página que será inserida no aplicativo
from operator import index
import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data #Armazena em memória o último filtro, evitando refazer as conversões novamente caso seja clicado no download sem modifica-los
def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8')
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso',icon="✅")
    time.sleep(5)
    sucesso.empty()

st.set_page_config(layout='wide')
st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')
with st.expander('Colunas'):
    #O segundo parâmetro são as opções dentro da lista que queremos visualizar no componente.
    colunas = st.multiselect('Selecione as colunas',list(dados.columns),list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos',dados['Produto'].unique(),dados['Produto'].unique())
with st.sidebar.expander('Categoria do produto'):
    categoria_produtos = st.multiselect('Selecione a categoria',dados['Categoria do Produto'].unique(),dados['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    #Ao invés de escolher um valor específico, passamos uma tupla com valor mínimo 0 e máximo 5000 como terceiro parâmetro
    preco = st.slider('Selecione o preço',0,5000,(0,5000))
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data',(dados['Data da Compra'].min(),dados['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione o vendedor',dados['Vendedor'].unique(),dados['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o local da compra',dados['Local da compra'].unique(),dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação da compra'):
    #Ao invés de escolher um valor específico, passamos uma tupla com valor mínimo 0 e máximo 5000 como terceiro parâmetro
    avaliacao_compra = st.slider('Selecione a avaliação da compra',1,5,(1,5))

query = ''' 
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
`Categoria do Produto` in @categoria_produtos and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao_compra[0] <= `Avaliação da compra` <= @avaliacao_compra[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')
st.markdown('Escreva um nome para o arquivo')
coluna1,coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('',label_visibility='collapsed',value='dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv',data=converte_csv(dados_filtrados),file_name=nome_arquivo,mime='txt/csv',on_click=mensagem_sucesso)
