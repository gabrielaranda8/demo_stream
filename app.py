#    streamlit run app_name.py --server.port 5998
from enum import Enum
from io import BytesIO, StringIO
from typing import Union
from datetime import datetime

import pandas as pd
from pandas import read_excel
from pandas import ExcelWriter
from pandas import read_csv
import streamlit as st
import openpyxl

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

st.sidebar.title("Conciliación SENEBI BO")
st.sidebar.header("Carga el valor del USD, luego ambos XLSX de BO")
dolar_bo = st.sidebar.text_input("Precio dolar SENEBI BO", 'dolar')
st.sidebar.markdown("---")

st.sidebar.title("Archivo REINV TSA")
reinv = st.sidebar.file_uploader("Carga tu xlsx de reinversión", type=['xlsx'])
st.sidebar.markdown("---")

# st.sidebar.title("Tenencias ACDI para CNV")
# CNV = st.sidebar.file_uploader("Carga tu xlsx del mes a controlar", type=['xlsx'])
# st.sidebar.markdown("---")

st.sidebar.title("solo TEST para CNV")
TEST = st.sidebar.file_uploader("Carga tu xlsx del mes a controlar TEST", type=['xlsx'])
st.sidebar.markdown("---")

st.sidebar.title("Conci ESCO vs BO")
bo = st.sidebar.file_uploader("Carga tu xlsx de FONDOS COHEN de BO !!!!", type=['xlsx'])
st.sidebar.markdown("---")

st.sidebar.title("LIQUIDACIÓN TSA !!!!!!!!!!!!!!!!!!!!")
liqui_tsa = st.sidebar.file_uploader("Carga tu xlsx de Transferencias TSA de BO !!!!", type=['xlsx'])
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

    if reinv:
        columnas = ['Comitente Número','Moneda','Importe']
        tablero = pd.read_excel(reinv, usecols=columnas, engine='openpyxl')
        tablero_xls = pd.read_excel(reinv,engine='openpyxl')
        comit = tablero['Comitente Número']
        # st.text(comit)

        st.dataframe(tablero)
        # st.table(tablero)
    
        ################################ EXCEL PREPARACION #############################
        
        def crearSheet(archivo):
            archivo = archivo
            # print(archivo)

            sheet = {'Fecha Concertacion':[],
                      'Fecha Vencimiento':[],
                      'Cuenta':[],
                      'Concepto':[],
                      'Debe':[],
                      'Haber':[],
                      'Contraparte - Custodia':[],
                      'Contraparte - Depositante':[],
                      'Contraparte - Cuenta':[]}
    
            for num in archivo.index:
                # print(num)
                
                fecha = datetime.now()
                fecha = fecha.strftime("%d/%m/%Y")

                sheet['Fecha Concertacion'].append(fecha)         
                sheet['Fecha Vencimiento'].append(fecha)         
                sheet['Cuenta'].append(archivo['Comitente Número'][num])         
                sheet['Concepto'].append(archivo['Tipo'][num])        
                sheet['Debe'].append('0,00')         
                sheet['Haber'].append(archivo['Importe'][num])
                sheet['Contraparte - Custodia'].append('CAJAVAL')
                sheet['Contraparte - Depositante'].append('0046')
                sheet['Contraparte - Cuenta'].append(archivo['Comitente Número'][num])

            sheet = pd.DataFrame(sheet)
            return sheet            

        moneda_7000 = tablero_xls['Moneda'] == 'Dolar Renta Exterior - 7.000' 
        moneda_10000 = tablero_xls['Moneda'] == 'Dolar Renta Local - 10.000'
        moneda_8000 = tablero_xls['Moneda'] == 'Pesos Renta - 8.000'
        nuevo7000 = tablero_xls[moneda_7000]
        nuevo10000 = tablero_xls[moneda_10000]
        nuevo8000 = tablero_xls[moneda_8000]

        reinversion_xls = nuevo7000.append(nuevo10000)
        reinversion_xls = reinversion_xls.append(nuevo8000)
      
        reinversion_xls = reinversion_xls.reindex(columns=['Número','Comitente Descripción','Fecha','Moneda','Comitente Número',
            'Importe','Tipo','Banco','Tipo de Cuenta','Sucursal','Cuenta','CBU','Tipo de identificador impositivo','Número de identificador impositivo',
            'Titular','Estado'])

        sheet_7000 = crearSheet(nuevo7000.set_index('Número'))
        sheet_10000 = crearSheet(nuevo10000.set_index('Número'))
        sheet_8000 = crearSheet(nuevo8000.set_index('Número'))

        with ExcelWriter('REINVERSION_FECHA.xlsx') as writer:
            reinversion_xls.to_excel(writer,sheet_name='Sheet1',index=False)
            sheet_7000.to_excel(writer,sheet_name='7000',index=False)  
            sheet_10000.to_excel(writer,sheet_name='10000',index=False)  
            sheet_8000.to_excel(writer,sheet_name='8000',index=False)  
        
        control_file = 'REINVERSION_FECHA.xlsx'
        with open(control_file, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
        st.markdown(download_button_str, unsafe_allow_html=True) 


        ################### EXCEL SUBIDA A BO ####################

        ############### ESP 7000 ##################################

        with ExcelWriter('7000_FECHA.xlsx') as writer:
            sheet_7000.to_excel(writer,sheet_name='7000',index=False) 
        
        control_file = '7000_FECHA.xlsx'
        with open(control_file, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
        st.markdown(download_button_str, unsafe_allow_html=True)
        

        ############### ESP 10000 ##################################

        with ExcelWriter('10000_FECHA.xlsx') as writer:
            sheet_10000.to_excel(writer,sheet_name='10000',index=False) 
        
        control_file = '10000_FECHA.xlsx'
        with open(control_file, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
        st.markdown(download_button_str, unsafe_allow_html=True)

        ############### ESP 8000 ##################################

        with ExcelWriter('8000_FECHA.xlsx') as writer:
            sheet_8000.to_excel(writer,sheet_name='8000',index=False) 
        
        control_file = '8000_FECHA.xlsx'
        with open(control_file, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
        st.markdown(download_button_str, unsafe_allow_html=True)   







        ################################ EXCEL PREPARACION #############################
     

        
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
    
    if dolar_bo!='dolar':
        # if control_boletos:
        #     control_bole = control_bole
        # if arancel:
        #     arancel = arancel 
        control_boletos = st.file_uploader("Carga tu xlsx BOLETOS", type=['xlsx'])
        arancel = st.file_uploader("Carga tu xlsx ARANCELES", type=['xlsx'])   
        ################################################################################################################################
        columnas = ["Tipo de Operación","Número de Boleto","Comitente - Número","Fecha de concertación","Instrumento - Símbolo","Cantidad","Moneda","Bruto"]
        

        if control_boletos and arancel:
            aranceles = pd.read_excel(arancel, engine='openpyxl')
            control = pd.read_excel(control_boletos, engine='openpyxl', usecols=columnas)
            control = control.reindex(columns=columnas)
        ################################################################################################################################




            ###### FLITRAMOS POR SOLO OPERACIONES SENEBI ####################

            # senebis = ["Compra SENEBI","Compra SENEBI Colega Pesos","Compra SENEBI CP  Letras","Compra SENEBI CP ON","Compra SENEBI Dólar Cable CP Letras",
            #            "Compra SENEBI Dolar MEP","Venta SENEBI","Venta SENEBI Cable","Venta SENEBI Colega Pesos","Venta Senebi CP Letras","Venta SENEBI Letras Dolar MEP CP",
            #            "Venta Senebi Pesos ON CP"]
            datos = []
            # print(control)
            for e in control.values:
                if "SENEBI" in e[0]:
                    if "Compra" in e[0]:
                        e[7] = 0 - e[7]
                    datos.append(e)
                elif "Senebi" in e[0]:
                    if "Compra" in e[0]:
                        e[7] = 0 - e[7]
                    datos.append(e)    

            datos = pd.DataFrame(datos, columns=columnas)


                

            # print(datos)



            ################  AGREGAMOS LA FILA "INTERES" Y LUEGO SI SON EN DOLARES MULTIPLICAMOS POR EL PRECIO DOLAR ###############3

            datos['interes'] = datos["Bruto"]
            for valor,moneda in enumerate(datos["Moneda"]):
                # print(moneda)
                if moneda!="$":
                    datos['interes'][valor] = float(datos["Bruto"][valor])*float(dolar_bo)

            # for e in datos.values:
            #     if "Compra" in e[0]:
            #         e[8] = 0 - e[8]        



            ##############  AGREGAMOS LOS ARANCELES X MANAGER SENEBI #########################
            solo_aranceles = []
            for e in aranceles.values:
                if "SENEBI" in e[9]:
                    # print(e)
                    solo_aranceles.append(e)
                elif "Senebi" in e[9]:
                    solo_aranceles.append(e)  

            datos_aranceles = pd.DataFrame(solo_aranceles, columns=aranceles.columns)
            # print(solo_aranceles["'SENEBI'"])      






            ##################### REORDENAMOS LAS COLUMNAS ##################################
            # datos = datos[["'Boleto'","'Operacion'","'Comitente'","'Nombre de la Cuenta'","'Especie'","'Imp_Bruto'","interes","'Valor_Nominal'","'Moneda'","'Total_Neto'","'Precio'"]]



            ###########   GUARDAMOS NUEVO EXCEL CON AMBAS SHEETS #######################
            with ExcelWriter('control_senebi_fecha.xlsx') as writer:
                datos.to_excel(writer,sheet_name='CONTROL',index=False)
                datos_aranceles.to_excel(writer,sheet_name='AxM',index=False)  
            control_file = 'control_senebi_fecha.xlsx'
            with open(control_file, 'rb') as f:
                s = f.read()

            download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
            st.markdown(download_button_str, unsafe_allow_html=True)  

    st.sidebar.info('\nEsta app fue creada usando Streamlit y es mantenida por [gabriel aranda]('
                    'https://www.linkedin.com/in/gabriel-alejandro-aranda-02714a151/).\n\n'
                    ) 
    
    if TEST:
        test_fondos = pd.read_excel(TEST, engine='openpyxl')

        coor = st.file_uploader("Carga tu xlsx COORPORATIVO", type=['xls'])
        pymes = st.file_uploader("Carga tu xlsx PYME", type=['xls'])

        if coor and pymes:

            coor = pd.read_excel(coor)
            pymes = pd.read_excel(pymes)

            # test_fondos['TIPO'] = test_fondos['Custodia']
            tipo = []
            # print(coor['Código de Interfaz'])
            st.dataframe(coor['Código de Interfaz'])

            for contador, e in enumerate(test_fondos['Cuenta - Nro']):
                print(e)


                if e in coor['Número de Custodia'].values:
                    tipo.append("COORPORATIVO")

                elif e in pymes['Número de Custodia'].values:
                    tipo.append("PYMES")

                else:
                    tipo.append("NADA")

            test_fondos['TIPO'] = tipo
            st.dataframe(test_fondos)
            ###########   GUARDAMOS NUEVO EXCEL CON AMBAS SHEETS #######################
            with ExcelWriter('DATOS_CNV.xlsx') as writer:
                test_fondos.to_excel(writer,index=False) 
            control_file = 'DATOS_CNV.xlsx'
            with open(control_file, 'rb') as f:
                s = f.read()

            download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
            st.markdown(download_button_str, unsafe_allow_html=True)                 

    if bo:

        columnas = ['Comitente - Descripción','Instrumento - Símbolo','Instrumento - Denominación','Cuenta - Nro','Saldo Total']
        archivo_bo = pd.read_excel(bo, usecols=columnas, engine='openpyxl')
        archivo_esco_plus = st.file_uploader("Carga tu xlsx de PLUS de ESCO !!!!!!", type=['xls'])
        archivo_esco_crf = st.file_uploader("Carga tu xlsx de CRF de ESCO !!!!!!", type=['xls'])
        archivo_esco_crfDOL = st.file_uploader("Carga tu xlsx de CRF DOLAR de ESCO !!!!!!", type=['xls'])
        archivo_esco_crfPYMES = st.file_uploader("Carga tu xlsx de CRF PYMES de ESCO !!!!!!", type=['xls'])


        def conciliarEsco(archivo_bo,archivo_esco):
            archivo_esco = archivo_esco
            archivo_bo = archivo_bo
            
            conci_LISTA_esco = {'NOMBRE':[],'COMITENTE':[],'CP QUE FALTAN EN BO':[]}
            
            for comitente in archivo_esco.index:

                esco_cp = archivo_esco.loc[comitente]
                esco_nombre = esco_cp['Nombre']
                esco_cp = esco_cp['Cuotapartes']

                if esco_cp > 0:
                    
                    if comitente in archivo_bo.index:

                        bo_cp = archivo_bo.loc[comitente]
                        bo_cp = bo_cp['Saldo Total']

                        if esco_cp == bo_cp:

                            conci_LISTA_esco['COMITENTE'].append(comitente)
                            conci_LISTA_esco['NOMBRE'].append(esco_nombre)
                            conci_LISTA_esco['CP QUE FALTAN EN BO'].append('COINCIDE EXACTO')
                        
                        else:
                            dif = esco_cp - bo_cp
                            conci_LISTA_esco['COMITENTE'].append(comitente)
                            conci_LISTA_esco['NOMBRE'].append(esco_nombre)
                            conci_LISTA_esco['CP QUE FALTAN EN BO'].append(dif)
                        
                    else: 
                        conci_LISTA_esco['COMITENTE'].append(comitente)
                        conci_LISTA_esco['NOMBRE'].append(esco_nombre)
                        conci_LISTA_esco['CP QUE FALTAN EN BO'].append('NO ESTÁ EL COMIT EN BO')

            return conci_LISTA_esco            

        def conciliarBO(archivo_bo,archivo_esco):
            
            archivo_esco = archivo_esco
            archivo_bo = archivo_bo

            conci_LISTA_bo = {'NOMBRE':[],'COMITENTE':[],'CP QUE FALTAN EN ESCO':[]}

            for comitente in archivo_bo.index:

                bo_cp = archivo_bo.loc[comitente]
                bo_nombre = bo_cp['Comitente - Descripción']
                bo_cp = bo_cp['Saldo Total']

                if bo_cp > 0:
                    
                    if comitente in archivo_esco.index:

                        esco_cp = archivo_esco.loc[comitente]
                        esco_cp = esco_cp['Cuotapartes']

                        if bo_cp == esco_cp:

                            conci_LISTA_bo['COMITENTE'].append(comitente)
                            conci_LISTA_bo['NOMBRE'].append(bo_nombre)
                            conci_LISTA_bo['CP QUE FALTAN EN ESCO'].append('COINCIDE EXACTO')
                        else:
                            dif = bo_cp - esco_cp
                            conci_LISTA_bo['COMITENTE'].append(comitente)
                            conci_LISTA_bo['NOMBRE'].append(bo_nombre)
                            conci_LISTA_bo['CP QUE FALTAN EN ESCO'].append(dif)
                        
                    else: 
                        conci_LISTA_bo['COMITENTE'].append(comitente)
                        conci_LISTA_bo['NOMBRE'].append(bo_nombre)
                        conci_LISTA_bo['CP QUE FALTAN EN ESCO'].append('NO ESTÁ EL COMIT EN ESCO')

            return conci_LISTA_bo     

        if archivo_esco_plus:
            
            ######### Descarto las columnas que no me sirven y dejo limpio el excel ##########
            archivo_esco_plus = pd.read_excel(archivo_esco_plus)
            archivo_esco_plus.set_axis(['0', 'Clase', 'Número','Nombre','4','5','Cuotapartes'], 
                    axis='columns', inplace=True)
            nuevo = archivo_esco_plus.drop([0,1,2,3],axis=0)
            # data.loc[1,2[columna,columna]]
            

            ########### PRIMERO FILTRAMOS POR LOS PLUS A #######################
            plus_a = nuevo['Clase'] == 'A - Minorista'
            plusa = nuevo[plus_a].set_index('Número')
           
            plusbo = archivo_bo['Instrumento - Símbolo'] == 'PLUS'
            plus_BO = archivo_bo[plusbo].set_index('Cuenta - Nro') 

            archivo_plusA_esco = conciliarEsco(plus_BO,plusa)
            archivo_plusA_bo = conciliarBO(plus_BO,plusa)
            
           
            ################ HACEMOS LA CONCI CREANDO UN NUEVO DATAFRAME ##############  

            ########### LUEGO FILTRAMOS POR LOS PLUS B #######################
            plus_B = nuevo['Clase'] == 'B - Institucional'
            plusB = nuevo[plus_B].set_index('Número')

            plusBbo = archivo_bo['Instrumento - Símbolo'] == 'PLUSB'
            plusB_BO = archivo_bo[plusBbo].set_index('Cuenta - Nro')
            
            archivo_plusB_esco = conciliarEsco(plusB_BO,plusB)
            archivo_plusB_bo = conciliarBO(plusB_BO,plusB)

            
            conci_lista_plusa_esco = pd.DataFrame(archivo_plusA_esco)
            conci_lista_plusa_bo = pd.DataFrame(archivo_plusA_bo)
            conci_lista_plusB_esco = pd.DataFrame(archivo_plusB_esco)
            conci_lista_plusB_bo = pd.DataFrame(archivo_plusB_bo)

            with ExcelWriter('CONCI_PLUS_COHEN.xlsx') as writer:
                conci_lista_plusa_esco.to_excel(writer,sheet_name='PLUSA_ESCO',index=False)
                conci_lista_plusa_bo.to_excel(writer,sheet_name='PLUSA_BO',index=False)  
                conci_lista_plusB_esco.to_excel(writer,sheet_name='PLUSB_ESCO',index=False)  
                conci_lista_plusB_bo.to_excel(writer,sheet_name='PLUSB_BO',index=False)  
            
            control_file = 'CONCI_PLUS_COHEN.xlsx'
            with open(control_file, 'rb') as f:
                s = f.read()

            download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
            st.markdown(download_button_str, unsafe_allow_html=True)  

        if archivo_esco_crf:
            
            ######### Descarto las columnas que no me sirven y dejo limpio el excel ##########
            archivo_esco_crf = pd.read_excel(archivo_esco_crf)
            archivo_esco_crf.set_axis(['0', 'Clase', 'Número','Nombre','4','5','Cuotapartes'], 
                    axis='columns', inplace=True)
            nuevo = archivo_esco_crf.drop([0,1,2,3],axis=0)
            # data.loc[1,2[columna,columna]]
            

            ########### PRIMERO FILTRAMOS POR LOS CRF A #######################
            crf_a = nuevo['Clase'] == 'A - Fisicas'
            crfa = nuevo[crf_a].set_index('Número')
           
            crfbo = archivo_bo['Instrumento - Símbolo'] == 'CRF'
            crf_BO = archivo_bo[crfbo].set_index('Cuenta - Nro') 

            archivo_crfA_esco = conciliarEsco(crf_BO,crfa)
            archivo_crfA_bo = conciliarBO(crf_BO,crfa)

            ########### LUEGO FILTRAMOS POR LOS CRF B #######################
            crf_B = nuevo['Clase'] == 'B - Fis o Jur'
            CRFB = nuevo[crf_B].set_index('Número')

            crfBbo = archivo_bo['Instrumento - Símbolo'] == 'CRFB'
            crfB_BO = archivo_bo[crfBbo].set_index('Cuenta - Nro')
            
            archivo_crfB_esco = conciliarEsco(crfB_BO,CRFB)
            archivo_crfB_bo = conciliarBO(crfB_BO,CRFB)

            ########### LUEGO FILTRAMOS POR LOS CRF C #######################
            crf_C = nuevo['Clase'] == 'C - Juridicas'
            CRFC = nuevo[crf_C].set_index('Número')

            crfCbo = archivo_bo['Instrumento - Símbolo'] == 'CRFC'
            crfC_BO = archivo_bo[crfCbo].set_index('Cuenta - Nro')
            
            archivo_crfC_esco = conciliarEsco(crfC_BO,CRFC)
            archivo_crfC_bo = conciliarBO(crfC_BO,CRFC)

            ########### LUEGO FILTRAMOS POR LOS CRF D #######################
            crf_D = nuevo['Clase'] == 'D - Juridicas'
            CRFD = nuevo[crf_D].set_index('Número')

            crfDbo = archivo_bo['Instrumento - Símbolo'] == 'CRFD'
            crfD_BO = archivo_bo[crfDbo].set_index('Cuenta - Nro')
            
            archivo_crfD_esco = conciliarEsco(crfD_BO,CRFD)
            archivo_crfD_bo = conciliarBO(crfD_BO,CRFD)

            
            conci_lista_crfa_esco = pd.DataFrame(archivo_crfA_esco)
            conci_lista_crfa_bo = pd.DataFrame(archivo_crfA_bo)
            conci_lista_crfB_esco = pd.DataFrame(archivo_crfB_esco)
            conci_lista_crfB_bo = pd.DataFrame(archivo_crfB_bo)
            conci_lista_crfC_esco = pd.DataFrame(archivo_crfC_esco)
            conci_lista_crfC_bo = pd.DataFrame(archivo_crfC_bo)
            conci_lista_crfD_esco = pd.DataFrame(archivo_crfD_esco)
            conci_lista_crfD_bo = pd.DataFrame(archivo_crfD_bo)

            with ExcelWriter('CONCI_CRF_COHEN.xlsx') as writer:
                conci_lista_crfa_esco.to_excel(writer,sheet_name='CRFA_ESCO',index=False)
                conci_lista_crfa_bo.to_excel(writer,sheet_name='CRFA_BO',index=False)  
                conci_lista_crfB_esco.to_excel(writer,sheet_name='CRFB_ESCO',index=False)  
                conci_lista_crfB_bo.to_excel(writer,sheet_name='CRFB_BO',index=False)  
                conci_lista_crfC_esco.to_excel(writer,sheet_name='CRFC_ESCO',index=False)  
                conci_lista_crfC_bo.to_excel(writer,sheet_name='CRFC_BO',index=False)  
                conci_lista_crfD_esco.to_excel(writer,sheet_name='CRFD_ESCO',index=False)  
                conci_lista_crfD_bo.to_excel(writer,sheet_name='CRFD_BO',index=False)  
            
            control_file = 'CONCI_CRF_COHEN.xlsx'
            with open(control_file, 'rb') as f:
                s = f.read()

            download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
            st.markdown(download_button_str, unsafe_allow_html=True)    

        if archivo_esco_crfDOL:
            
            ######### Descarto las columnas que no me sirven y dejo limpio el excel ##########
            archivo_esco_crfDOL = pd.read_excel(archivo_esco_crfDOL)
            archivo_esco_crfDOL.set_axis(['0', 'Clase', 'Número','Nombre','4','5','Cuotapartes'], 
                    axis='columns', inplace=True)
            nuevo = archivo_esco_crfDOL.drop([0,1,2,3],axis=0)
            # data.loc[1,2[columna,columna]]
            

            ########### PRIMERO FILTRAMOS POR LOS CRF DOL A #######################
            crf_DOLa = nuevo['Clase'] == 'A - Fis'
            crfDOLa = nuevo[crf_DOLa].set_index('Número')
           
            crfDOLAbo = archivo_bo['Instrumento - Símbolo'] == 'CRF DOL'
            crf_DOLABO = archivo_bo[crfDOLAbo].set_index('Cuenta - Nro') 

            archivo_crfDOLA_esco = conciliarEsco(crf_DOLABO,crfDOLa)
            archivo_crfDOLA_bo = conciliarBO(crf_DOLABO,crfDOLa)

            ########### LUEGO FILTRAMOS POR LOS CRF DOL B #######################
            crf_DOLB = nuevo['Clase'] == 'B - Jur'
            CRFDOLB = nuevo[crf_DOLB].set_index('Número')

            crfDOLBbo = archivo_bo['Instrumento - Símbolo'] == 'CRF DOL B'
            crfDOLB_BO = archivo_bo[crfDOLBbo].set_index('Cuenta - Nro')
            
            archivo_crfDOLB_esco = conciliarEsco(crfDOLB_BO,CRFDOLB)
            archivo_crfDOLB_bo = conciliarBO(crfDOLB_BO,CRFDOLB)

            ########### LUEGO FILTRAMOS POR LOS CRF DOL I #######################
            crf_DOLI = nuevo['Clase'] == 'I'
            CRFDOLI = nuevo[crf_DOLI].set_index('Número')

            crfDOLIbo = archivo_bo['Instrumento - Símbolo'] == 'CRF DOL I'
            crfDOLI_BO = archivo_bo[crfDOLIbo].set_index('Cuenta - Nro')
            
            archivo_crfDOLI_esco = conciliarEsco(crfDOLI_BO,CRFDOLI)
            archivo_crfDOLI_bo = conciliarBO(crfDOLI_BO,CRFDOLI)

            
            conci_lista_crfDOLa_esco = pd.DataFrame(archivo_crfDOLA_esco)
            conci_lista_crfDOLa_bo = pd.DataFrame(archivo_crfDOLA_bo)
            conci_lista_crfDOLB_esco = pd.DataFrame(archivo_crfDOLB_esco)
            conci_lista_crfDOLB_bo = pd.DataFrame(archivo_crfDOLB_bo)
            conci_lista_crfDOLI_esco = pd.DataFrame(archivo_crfDOLI_esco)
            conci_lista_crfDOLI_bo = pd.DataFrame(archivo_crfDOLI_bo)
            
            with ExcelWriter('CONCI_CRFDOL_COHEN.xlsx') as writer:
                conci_lista_crfDOLa_esco.to_excel(writer,sheet_name='CRFDOLA_ESCO',index=False)
                conci_lista_crfDOLa_bo.to_excel(writer,sheet_name='CRFDOLA_BO',index=False)  
                conci_lista_crfDOLB_esco.to_excel(writer,sheet_name='CRFDOLB_ESCO',index=False)  
                conci_lista_crfDOLB_bo.to_excel(writer,sheet_name='CRFDOLB_BO',index=False)  
                conci_lista_crfDOLI_esco.to_excel(writer,sheet_name='CRFDOLI_ESCO',index=False)  
                conci_lista_crfDOLI_bo.to_excel(writer,sheet_name='CRFDOLI_BO',index=False)   
            
            control_file = 'CONCI_CRFDOL_COHEN.xlsx'
            with open(control_file, 'rb') as f:
                s = f.read()

            download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
            st.markdown(download_button_str, unsafe_allow_html=True)           

        if archivo_esco_crfPYMES:
            
            ######### Descarto las columnas que no me sirven y dejo limpio el excel ##########
            archivo_esco_crfPYMES = pd.read_excel(archivo_esco_crfPYMES)
            archivo_esco_crfPYMES.set_axis(['0', 'Clase', 'Número','Nombre','4','5','Cuotapartes'], 
                    axis='columns', inplace=True)
            nuevo = archivo_esco_crfPYMES.drop([0,1,2,3],axis=0)
            # data.loc[1,2[columna,columna]]
            

            ########### PRIMERO FILTRAMOS POR LOS PYMES #######################
            PYMES_B = nuevo['Clase'] == 'B - Institucional'
            PYMESB = nuevo[PYMES_B].set_index('Número')
           
            PYMESbo = archivo_bo['Instrumento - Símbolo'] == 'PYMES'
            PYMES_BO = archivo_bo[PYMESbo].set_index('Cuenta - Nro') 

            archivo_PYMESA_esco = conciliarEsco(PYMES_BO,PYMESB)
            archivo_PYMESA_bo = conciliarBO(PYMES_BO,PYMESB)
            
           
            ################ HACEMOS LA CONCI CREANDO UN NUEVO DATAFRAME ##############  

            conci_lista_PYMESB_esco = pd.DataFrame(archivo_PYMESA_esco)
            conci_lista_PYMESB_bo = pd.DataFrame(archivo_PYMESA_bo)

            with ExcelWriter('CONCI_PYMES_COHEN.xlsx') as writer: 
                conci_lista_PYMESB_esco.to_excel(writer,sheet_name='PYMESB_ESCO',index=False)  
                conci_lista_PYMESB_bo.to_excel(writer,sheet_name='PYMESB_BO',index=False)  
            
            control_file = 'CONCI_PYMES_COHEN.xlsx'
            with open(control_file, 'rb') as f:
                s = f.read()

            download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
            st.markdown(download_button_str, unsafe_allow_html=True)  

    if liqui_tsa:
        archivo = pd.read_excel(liqui_tsa, engine='openpyxl')

        nuevo_xls = []
        solo_inmediato = []
       
        for linea in archivo.values:
            
            comitente = linea[0]
            codigo = linea[1]
            tipo = linea[3]
            cantidad = linea[4]
            tratamiento = linea[5]


            if tipo == 'Venta':
                for op in archivo.values:
                    if op[0]==comitente and op[1]==codigo and op[3]=='Compra' and op[4]>=cantidad:
                        linea[5] = 'Diferido'
                    elif op[0]==comitente and op[1]==codigo and op[3]=='Compra' and op[4]<cantidad:
                        diferencia = linea[4] - op[4]
                        solo_inmediato.append([comitente,codigo,'NADA',tipo,diferencia,tratamiento])
                        linea[4] = op[4]
                        linea[5] = 'Diferido'

            nuevo_xls.append(linea)  
 
        columnas = ['Comitente - Número','Instrumento - Código caja','Instrumento - Símbolo','Transferencia - Tipo','Transferencia - Cantidad Total','Transferencia - Tratamiento'] 
        nuevo_xls = pd.DataFrame(nuevo_xls, columns=columnas)              
        solo_inmediato = pd.DataFrame(solo_inmediato, columns=columnas)              
        

        st.dataframe(nuevo_xls)
        # print(solo_inmediato)


        ################################ EXCEL PREPARACION #############################
     

        
        lista_tsa= []

        # -----------------PRIMERAS DOS LINEAS OBLIGATORIAS DEL TXT------------------------------------------
        linea1 = "00Aftfaot    20"+hora+"1130560000000"
        lista_tsa.append(linea1)      

        incio = "\r\n"+"0"+hora+"FTFAOT0046"+"\r\n"
        lista_tsa.append(incio)

        # -----------------AGREGAMOS LINEAS SEGUN LA CANTIDAD DE SUCRI QUE TENGAMOS-----------------------------------------

        # especie = 5 digitos 
        # cuotas = 00000000000.0000000  ( 11 y 7) 
        # comitente = 9 digitos 
        especie = 0
        cuotas = 0
        comitente = 0

        for valor,comit in enumerate(nuevo_xls['Comitente - Número']):
            especie = str(nuevo_xls['Instrumento - Código caja'][valor])
            cuotas = str(nuevo_xls['Transferencia - Cantidad Total'][valor])
            tipo = str(nuevo_xls['Transferencia - Tratamiento'][valor])
            lado = str(nuevo_xls['Transferencia - Tipo'][valor])
            comitente = str(comit)  
            
            if tipo=='Diferido' and lado=='Venta':

                ################ AGREGO EL FORMATO A NUESTRO ARCHIVO
                lista_tsa.append("1'D'E'0046'"+comitente+"'"+especie+"       '"+cuotas+"'7046'10000'N'00'0000'0000'N"+"\r\n")
            elif tipo=='Inmediato' and lado=='Venta':

                ################ AGREGO EL FORMATO A NUESTRO ARCHIVO
                lista_tsa.append("1'I'E'0046'"+comitente+"'"+especie+"       '"+cuotas+"'7046'10000'N'00'0000'0000'N"+"\r\n")    
       

        # LINEA EJEMPLO
        #"1'I'E'0046'000000003'"+especie+"       '"+cuotas+"'0046'"+comitente+"'N'00'0000'0000'N"

        # ------------------------AGREGAMOS LINEA FINAL---------------------------------------

        # LINEA FINAL
        num_lineas = len(lista_tsa)-1 # restamos la primera que no cuenta
        # print(len(str(num_lineas)))
        if len(str(num_lineas))==1:
            num_lineas = "0" + str(num_lineas)
        linea_final = "99Aftfaot    20"+hora+"1130560000000"+str(num_lineas)+"\r\n"
        lista_tsa.append(linea_final)

        # AGREAGR NUMERO DE FILAS A LA PRIMER LINEA
        lista_tsa[0] = lista_tsa[0]+str(num_lineas)

        datos=open("modelo_cris_tsa.txt","w")
        datos.writelines(lista_tsa)
        datos.close()


        nuevo = "modelo_cris_tsa.txt"
        with open(nuevo, 'rb') as f:
            s = f.read()
            print(s)

        download_button_str = download_button(s, nuevo, f'Archivo CRIS TSA {nuevo}')
        st.markdown(download_button_str, unsafe_allow_html=True)


        ################################ TSA EXTRA PREPARACION #############################
     

        
        tsa_extra= []

        # -----------------PRIMERAS DOS LINEAS OBLIGATORIAS DEL TXT------------------------------------------
        linea1_extra = "00Aftfaot    20"+hora+"1130560000000"
        tsa_extra.append(linea1_extra)      

        incio_extra = "\r\n"+"0"+hora+"FTFAOT0046"+"\r\n"
        tsa_extra.append(incio_extra)

        # -----------------AGREGAMOS LINEAS SEGUN LA CANTIDAD DE SUCRI QUE TENGAMOS-----------------------------------------

        # especie = 5 digitos 
        # cuotas = 00000000000.0000000  ( 11 y 7) 
        # comitente = 9 digitos 
        especie_extra = 0
        cuotas_extra = 0
        comitente_extra = 0

        for valor,comit in enumerate(solo_inmediato['Comitente - Número']):
            especie_extra = str(solo_inmediato['Instrumento - Código caja'][valor])
            cuotas_extra = str(solo_inmediato['Transferencia - Cantidad Total'][valor])
            # tipo = str(solo_inmediato['Transferencia - Tratamiento'][valor])
            # lado = str(solo_inmediato['Transferencia - Tipo'][valor])
            comitente_extra = str(comit)  
            
            # if tipo=='Diferido' and lado=='Venta':

            #     ################ AGREGO EL FORMATO A NUESTRO ARCHIVO
            #     tsa_extra.append("1'D'E'0046'"+comitente_extra+"'"+especie_extra+"       '"+cuotas_extra+"'7046'1000'N'00'0000'0000'N"+"\r\n")
            # elif tipo=='Inmediato' and lado=='Venta':

                ################ AGREGO EL FORMATO A NUESTRO ARCHIVO
            tsa_extra.append("1'I'E'0046'"+comitente_extra+"'"+especie_extra+"       '"+cuotas_extra+"'7046'10000'N'00'0000'0000'N"+"\r\n")    
       

        # LINEA EJEMPLO
        #"1'I'E'0046'000000003'"+especie+"       '"+cuotas+"'0046'"+comitente+"'N'00'0000'0000'N"

        # ------------------------AGREGAMOS LINEA FINAL---------------------------------------

        # LINEA FINAL
        num_lineas_extra = len(tsa_extra)-1 # restamos la primera que no cuenta
        # print(len(str(num_lineas_extra)))
        if len(str(num_lineas_extra))==1:
            num_lineas_extra = "0" + str(num_lineas_extra)
        linea_final_extra = "99Aftfaot    20"+hora+"1130560000000"+str(num_lineas_extra)+"\r\n"
        tsa_extra.append(linea_final_extra)

        # AGREAGR NUMERO DE FILAS A LA PRIMER LINEA
        tsa_extra[0] = tsa_extra[0]+str(num_lineas_extra)

        datos_extra=open("modelo_extra_tsa.txt","w")
        datos_extra.writelines(tsa_extra)
        datos_extra.close()


        nuevo_extra = "modelo_extra_tsa.txt"
        with open(nuevo_extra, 'rb') as f:
            s = f.read()
            print(s)

        download_button_str = download_button(s, nuevo_extra, f'Archivo EXTRA TSA {nuevo_extra}')
        st.markdown(download_button_str, unsafe_allow_html=True)





        with ExcelWriter('TSA_OPS.xlsx') as writer:
                nuevo_xls.to_excel(writer,sheet_name='TSA',index=False)  
            
        control_file = 'TSA_OPS.xlsx'
        with open(control_file, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, control_file, f'EXCEL LISTO {control_file}')
        st.markdown(download_button_str, unsafe_allow_html=True)              
                        

if __name__ == '__main__':
    main()      