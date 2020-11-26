#    streamlit run app_name.py --server.port 5998
from enum import Enum
from io import BytesIO, StringIO
from typing import Union

import pandas as pd
from pandas import read_excel
from pandas import ExcelWriter
from pandas import read_csv
import streamlit as st

import time
import sys
import base64
import uuid
import os
import pickle
import uuid
import re
import time

from PIL import Image



hora = time.strftime("%y%m%d")

# image = Image.open('imagen.png')

# st.image(image,
#           use_column_width=False)

st.title("Mini Tablero")
st.info('\nTablero de automatización, podes preguntarme acá [gabriel aranda]('
                    'https://www.linkedin.com/in/gabriel-alejandro-aranda-02714a151/).\n\n'
                    ) 


# Uploader widget
st.sidebar.title("Archivo TSA")
filename = st.sidebar.file_uploader("Carga tu xlsx de suscri", type=['xlsx'])
st.sidebar.markdown("---")



st.sidebar.title("Archivo ESCO")
esco = st.sidebar.file_uploader("Carga tu TXT ESCO", type=['txt'])
st.sidebar.markdown("---")


st.sidebar.title("Conciliación SENEBI")
st.sidebar.header("Carga el valor del USD, luego ambos XLSX")
dolar = st.sidebar.text_input("Precio dolar SENEBI", 'dolar')
st.sidebar.markdown("---")


st.sidebar.title("Archivo REINV TSA")
reinv = st.sidebar.file_uploader("Carga tu xlsx de reinversión", type=['xlsx'])
st.sidebar.markdown("---")


# st.sidebar.title("Archivo COMIS")
# cometas = st.sidebar.file_uploader("Carga tu xlsx de Comisiónes", type=['xlsx'])
# st.sidebar.markdown("---")


def download_button(object_to_download, download_filename, button_text, pickle_it=False):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
    """

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: 0.25em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """
    # print(b64)
    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'
    
    return dl_link


def main():

    if filename:
        columnas = ['Comitente','CodigoCaja','Cuotas']
        tablero = pd.read_excel(filename, usecols=columnas)
        comit = tablero['Comitente']
        # st.text(comit)

        st.dataframe(tablero)
        # st.table(tablero)
    
     

        
        lista_suscri= []

        # -----------------PRIMERAS DOS LINEAS OBLIGATORIAS DEL TXT------------------------------------------
        linea1 = "00Aftfaot    20"+hora+"1130560000000"
        lista_suscri.append(linea1)      

        incio = "\r\n"+"0"+hora+"FTFAOT0046"+"\r\n"
        lista_suscri.append(incio)

        # -----------------AGREGAMOS LINEAS SEGUN LA CANTIDAD DE SUCRI QUE TENGAMOS-----------------------------------------

        # especie = 5 digitos 
        # cuotas = 00000000000.0000000  ( 11 y 7) 
        # comitente = 9 digitos 
        especie = 0
        cuotas = 0
        comitente = 0

        for valor,comit in enumerate(tablero['Comitente']):
            especie = str(tablero['CodigoCaja'][valor])
            cuotas = str(tablero['Cuotas'][valor])
            comitente = str(comit)  
            
            if especie!="nan" and cuotas!="nan" and comitente!="nan":

                #### ESPECIE ###############################################
                especie = str(int(float(especie)))
                #### COMITENTE #############################################
                comitente = str(int(float(comitente)))
                #### CUOTAS ################################################
                cuotas = str(float(cuotas))
                
                ################ AGREGO EL FORMATO A NUESTRO ARCHIVO
                lista_suscri.append("1'I'E'0046'000000003'"+especie+"       '"+cuotas+"'0046'"+comitente+"'N'00'0000'0000'N"+"\r\n")
       

        # LINEA EJEMPLO
        #"1'I'E'0046'000000003'"+especie+"       '"+cuotas+"'0046'"+comitente+"'N'00'0000'0000'N"

        # ------------------------AGREGAMOS LINEA FINAL---------------------------------------

        # LINEA FINAL
        num_lineas = len(lista_suscri)-1 # restamos la primera que no cuenta
        # print(len(str(num_lineas)))
        if len(str(num_lineas))==1:
            num_lineas = "0" + str(num_lineas)
        linea_final = "99Aftfaot    20"+hora+"1130560000000"+str(num_lineas)+"\r\n"
        lista_suscri.append(linea_final)

        # AGREAGR NUMERO DE FILAS A LA PRIMER LINEA
        lista_suscri[0] = lista_suscri[0]+str(num_lineas)

        datos=open("modelo.txt","w")
        datos.writelines(lista_suscri)
        datos.close()


        nuevo = "modelo.txt"
        with open(nuevo, 'rb') as f:
            s = f.read()
            print(s)

        download_button_str = download_button(s, nuevo, f'Archivo TSA {nuevo}')
        st.markdown(download_button_str, unsafe_allow_html=True)

        # os.remove("suscri_tsa1.txt")
    

    if esco:
        df = esco.read()
        archivo = df.decode('utf-8')
        # listo = st.text(archivo)

        suscri = open("suscri.txt", "w") # W puedo editar el archivo, o crea si no esta
        rescate = open("rescate.txt", "w")

        lista_suscri = []
        lista_rescate = []
        
        f = archivo.split(sep=None, maxsplit=-1)

        for x in f:
            # print(x)
            tipo = x[0]
            if tipo=="S":
                valid = x[8]
                if valid!=";":   
                    linea = x[8:-20]+"\r\n"
                    lista_suscri.append(linea)
                          
            elif tipo=="R":
                valid = x[8]
                if valid!=";":
                    linea2 = x[8:]+";"+"\r\n"
                    lista_rescate.append(linea2)
                   

        suscri.writelines(lista_suscri)          
        rescate.writelines(lista_rescate)          
        suscri.close()
        rescate.close()
        


        suscri_file = "suscri.txt"
        rescate_file = "rescate.txt"

        with open(suscri_file, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, suscri_file, f'SUSCRI {suscri_file}')
        st.markdown(download_button_str, unsafe_allow_html=True)  

        with open(rescate_file, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, rescate_file, f'RESCATE {rescate_file}')
        st.markdown(download_button_str, unsafe_allow_html=True) 

    if dolar!='dolar':
        # if control_bole:
        #     control_bole = control_bole
        # if arancel:
        #     arancel = arancel 
        control_bole = st.file_uploader("Carga tu xlsx CONTBOLE", type=['xlsx'])
        arancel = st.file_uploader("Carga tu xlsx ARAXMGER", type=['xlsx'])   
        ################################################################################################################################
        columnas = ["'Boleto'","'Operacion'","'Comitente'","'Nombre de la Cuenta'","'Especie'","'Imp_Bruto'","'Valor_Nominal'","'Total_Neto'","'Moneda'","'Precio'"]
        

        if control_bole and arancel:
            aranceles = pd.read_excel(arancel,sheet_name='ARAXMGER')
            control = pd.read_excel(control_bole,sheet_name='Control_de_Boletos', usecols=columnas)
        ################################################################################################################################




            ###### FLITRAMOS POR SOLO OPERACIONES SENEBI ####################

            senebis = ["CSCN","CSNC","CSNP","VSCN","VSNC","VSNP"]
            datos = []
            for e in control.values:
                if e[1] in senebis:
                    datos.append(e)

            datos = pd.DataFrame(datos, columns=columnas)

            # print(datos)



            ################  AGREGAMOS LA FILA "INTERES" Y LUEGO SI SON EN DOLARES MULTIPLICAMOS POR EL PRECIO DOLAR ###############3

            datos['interes'] = datos["'Imp_Bruto'"]
            for valor,moneda in enumerate(datos["'Moneda'"]):
                # print(moneda)
                if moneda!="Pesos":
                    datos['interes'][valor] = float(datos["'Imp_Bruto'"][valor])*float(dolar)



            ##############  AGREGAMOS LOS ARANCELES X MANAGER QUE SEAN MAYORES A $ 1.0  #########################
            solo_aranceles = []
            for valor, arancel in enumerate(aranceles["'SENEBI'"]):
                if float(arancel) > 1.0:
                    solo_aranceles.append(aranceles.iloc[valor])

            solo_aranceles = pd.DataFrame(solo_aranceles) 
            # print(solo_aranceles["'SENEBI'"])      






            ##################### REORDENAMOS LAS COLUMNAS ##################################
            datos = datos[["'Boleto'","'Operacion'","'Comitente'","'Nombre de la Cuenta'","'Especie'","'Imp_Bruto'","interes","'Valor_Nominal'","'Moneda'","'Total_Neto'","'Precio'"]]



            ###########   GUARDAMOS NUEVO EXCEL CON AMBAS SHEETS #######################
            with ExcelWriter('CONTBOLE_FECHA.xlsx') as writer:
                datos.to_excel(writer,sheet_name='CONTROL',index=False)
                solo_aranceles.to_excel(writer,sheet_name='AxM',index=False)  
            control_file = 'CONTBOLE_FECHA.xlsx'
            with open(control_file, 'rb') as f:
                s = f.read()

            download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
            st.markdown(download_button_str, unsafe_allow_html=True)       

    if reinv:
        columnas = ['Comitente Número','Moneda','Importe']
        tablero = pd.read_excel(reinv, usecols=columnas)
        comit = tablero['Comitente Número']
        # st.text(comit)

        st.dataframe(tablero)
        # st.table(tablero)
    
     

        
        lista_reinv= []

        # -----------------PRIMERAS DOS LINEAS OBLIGATORIAS DEL TXT------------------------------------------
        linea1 = "00Aftfaot    20"+hora+"1130560000000"
        lista_reinv.append(linea1)      

        incio = "\r\n"+"0"+hora+"FTFAOT0046"+"\r\n"
        lista_reinv.append(incio)

        # -----------------AGREGAMOS LINEAS SEGUN LA CANTIDAD DE SUCRI QUE TENGAMOS-----------------------------------------

        # especie = 5 digitos 
        # cuotas = 00000000000.0000000  ( 11 y 7) 
        # comitente = 9 digitos 
        especie = 0
        cuotas = 0
        comitente = 0

        for valor,comit in enumerate(tablero['Comitente Número']):
            especie = str(tablero['Moneda'][valor])
            cuotas = str(tablero['Importe'][valor])
            comitente = str(comit)  
            
            if especie!="nan" and cuotas!="nan" and comitente!="nan":

                #### ESPECIE ###############################################
                especie = especie
                #### COMITENTE #############################################
                comitente = str(int(float(comitente)))
                #### CUOTAS ################################################
                cuotas = str(float(cuotas))

                # renta = [["Dolar Renta Local - 10.000","10000"],["Dolar Renta Exterior - 7.000","7000"],["Pesos renta-8000","8000"]]
                renta = {"Dolar Renta Local - 10.000":"10000","Dolar Renta Exterior - 7.000":"7000","Pesos Renta - 8.000":"8000"}

                if especie in renta:
                    especie = renta[especie]

                    ################ AGREGO EL FORMATO A NUESTRO ARCHIVO
                    lista_reinv.append("1'I'E'0046'"+comitente+"'"+especie+"       '"+cuotas+"'0046'03'N'00'0000'0000'N"+"\r\n")
       

        # LINEA EJEMPLO
        #"1'I'E'0046'000000003'"+especie+"       '"+cuotas+"'0046'"+comitente+"'N'00'0000'0000'N"

        # ------------------------AGREGAMOS LINEA FINAL---------------------------------------

        # LINEA FINAL
        num_lineas = len(lista_reinv)-1 # restamos la primera que no cuenta
        # print(len(str(num_lineas)))
        if len(str(num_lineas))==1:
            num_lineas = "0" + str(num_lineas)
        linea_final = "99Aftfaot    20"+hora+"1130560000000"+str(num_lineas)+"\r\n"
        lista_reinv.append(linea_final)

        # AGREAGR NUMERO DE FILAS A LA PRIMER LINEA
        lista_reinv[0] = lista_reinv[0]+str(num_lineas)

        datos=open("modelo_reinv.txt","w")
        datos.writelines(lista_reinv)
        datos.close()


        nuevo = "modelo_reinv.txt"
        with open(nuevo, 'rb') as f:
            s = f.read()
            print(s)

        download_button_str = download_button(s, nuevo, f'Archivo REINV TSA {nuevo}')
        st.markdown(download_button_str, unsafe_allow_html=True)
    
    st.sidebar.title("Archivo COMIS")
    cometas = st.sidebar.file_uploader("Carga tu xlsx de Comisiónes", type=['xlsx'])
    st.sidebar.markdown("---")
    if cometas:
        cometas = pd.read_excel(cometas)

        cometas.columns = ["FechaConcertacion","FechaVencimiento","NO1","OperacionTipo","ComitenteNumero","ComitenteDescripcion","Cantidad","PorcentajeArancel","NO3","NO4","Ticker","Denominacion"]

        cometas = cometas.drop([0],axis=0)
        cometas = cometas.drop(['NO1', 'NO3', 'NO4'], axis=1)

        cometas = cometas.drop_duplicates(['FechaConcertacion','FechaVencimiento','ComitenteNumero', 'PorcentajeArancel', 'Ticker',"OperacionTipo"], keep='last')

        with ExcelWriter('NUEVO_COMIS.xlsx') as writer:
                cometas.to_excel(writer,sheet_name='COMIS',index=False) 
        nuevo = "NUEVO_COMIS.xlsx"
        with open(nuevo, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, nuevo, f'Archivo COMIS LISTAS {nuevo}')
        st.markdown(download_button_str, unsafe_allow_html=True)


    st.sidebar.info('\nEsta app fue creada usando Streamlit y es mantenida por [gabriel aranda]('
                    'https://www.linkedin.com/in/gabriel-alejandro-aranda-02714a151/).\n\n'
                    ) 
if __name__ == '__main__':
    main()      