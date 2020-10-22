
from enum import Enum
from io import BytesIO, StringIO
from typing import Union

import pandas as pd
from pandas import read_excel
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
st.sidebar.title("Upload Your File")
filename = st.sidebar.file_uploader("Choose a file", type=['xlsx', 'csv'])
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
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

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
    
     

        datos=open("suscri_tsa1.txt","w")
        lista_suscri= []

        # -----------------PRIMERAS DOS LINEAS OBLIGATORIAS DEL TXT------------------------------------------
        linea1 = "00Aftfaot    20"+hora+"1130560000000"
        lista_suscri.append(linea1)

        incio = "\n"+"0"+hora+"FTFAOT0046"+"\n"
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
                lista_suscri.append("1'I'E'0046'000000003'"+especie+"       '"+cuotas+"'0046'"+comitente+"'N'00'0000'0000'N"+"\n")
       

        # LINEA EJEMPLO
        #"1'I'E'0046'000000003'"+especie+"       '"+cuotas+"'0046'"+comitente+"'N'00'0000'0000'N"

        # ------------------------AGREGAMOS LINEA FINAL---------------------------------------

        # LINEA FINAL
        num_lineas = len(lista_suscri)-1 # restamos la primera que no cuenta
        linea_final = "99Aftfaot    20"+hora+"11305600000000"+str(num_lineas)+"\n"
        lista_suscri.append(linea_final)

        # AGREAGR NUMERO DE FILAS A LA PRIMER LINEA
        lista_suscri[0] = lista_suscri[0]+str(num_lineas)


        datos.writelines(lista_suscri)
        datos.close() 

        nuevo = "suscri_tsa1.txt"
        with open(nuevo, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, nuevo, f'Click here to download {nuevo}')
        st.markdown(download_button_str, unsafe_allow_html=True)

        os.remove("suscri_tsa1.txt")
