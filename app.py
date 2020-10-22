#    streamlit run app_name.py --server.port 5998
from enum import Enum
from io import BytesIO, StringIO
from typing import Union

import pandas as pd
from pandas import read_excel
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


hora = time.strftime("%y%m%d")
# Uploader widget
st.sidebar.title("Archivo TSA")
filename = st.sidebar.file_uploader("Carga tu xlsx de suscri", type=['xlsx'])
st.sidebar.markdown("---")



st.sidebar.title("Archivo ESCO")
esco = st.sidebar.file_uploader("Carga tu TXT ESCO", type=['txt'])
st.sidebar.markdown("---")






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
    print(b64)
    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'
    
    return dl_link



# print('gggggggggggg')
if __name__ == '__main__':
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
        linea_final = "99Aftfaot    20"+hora+"1130560000000"+str(num_lineas)+"\r\n"
        lista_suscri.append(linea_final)

        # AGREAGR NUMERO DE FILAS A LA PRIMER LINEA
        lista_suscri[0] = lista_suscri[0]+str(num_lineas)

        datos=open("modelo.txt","w")
        datos.writelines(lista_suscri)
        datos.close()

        # ver = open("modelo.txt")
        # ver2 = ver.readline()
        # print(ver2)
        
        


        # st.table(lista_suscri)
        # otro=open("otrooo.txt","w")
        # otro.writelines(lista_suscri)
        # otro.close()

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
        listo = st.text(archivo)

        suscri = open("suscri.txt", "w") # W puedo editar el archivo, o crea si no esta
        rescate = open("rescate.txt", "w")

        lista_suscri = []
        lista_rescate = []
        
        f = archivo.split(sep=None, maxsplit=-1)

        for x in f:
            print(x)
            tipo = x[0]
            if tipo=="S":
                valid = x[8]
                if valid!=";":   
                    linea = x[8:-21]+"\r\n"
                    lista_suscri.append(linea)
                          
            elif tipo=="R":
                valid = x[8]
                if valid!=";":
                    linea2 = x[8:-1]+";"+"\r\n"
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
       


# archi1=open("datos.txt","w") 
# archi1.write("Primer línea.\r\n") 
# archi1.write("Segunda línea.\n") 
# archi1.write("Tercer línea.\n")  
# archi1.close() 