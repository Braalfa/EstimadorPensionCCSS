import tabula
import requests
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
         'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def toDate(data):
    [mes, ano] = data.split('/')[0:2]
    mes = meses.index(mes)+1
    return datetime.datetime(int(ano), mes, 1)

def loadInflacion():
    # Carga
    url = "https://gee.bccr.fi.cr/indicadoreseconomicos/Cuadros/frmVerCatCuadro.aspx?CodCuadro=2732&Idioma=1&FecInicial=1976/01/31&FecFinal=2021/05/31&Filtro=0&Exportar=True"
    indices = requests.get(url, allow_redirects=True)
    inflacionDF = pd.read_html(indices.content, decimal=',', thousands='.')[0]
    # Subseccion
    inflacionDF = inflacionDF[[0, 2]]
    inflacionDF = inflacionDF[:][5:]
    # Columnas
    inflacionDF = inflacionDF.rename(columns={0: 'Periodo', 2: 'Variacion'})
    # Fecha
    inflacionDF['Periodo'] = inflacionDF['Periodo'] .apply(toDate)
    inflacionDF = inflacionDF.set_index(['Periodo'])
    # Numerico
    inflacionDF['Variacion'] = inflacionDF['Variacion'].apply(pd.to_numeric, errors='coerce')
    inflacionDF['Variacion'] = inflacionDF['Variacion'].apply(lambda x: x+1)
    #Return
    return inflacionDF ['Variacion']

def loadCuotas():
    # Cargar
    cuotasDF = tabula.read_pdf("pension.pdf", pages="all")
    # Redefinir
    cuotasDF = pd.concat(cuotasDF)[['Periodo', 'Salario/Ingreso']]
    cuotasDF = cuotasDF.dropna()
    # Fechas
    cuotasDF['Periodo'] = pd.to_datetime(cuotasDF['Periodo'], format='%d/%m/%Y')
    cuotasDF = cuotasDF.set_index(['Periodo'])
    # Numerico
    cuotasDF['Salario/Ingreso'] = cuotasDF['Salario/Ingreso'].apply(lambda x: x.replace(',', ''))
    cuotasDF['Salario/Ingreso'] = cuotasDF['Salario/Ingreso'].apply(pd.to_numeric, errors='coerce')
    return cuotasDF

def valorActual(fecha, valor, inflacionDF):
    fechaSiguiente = fecha + relativedelta(months=1)
    cambioAgregado = inflacionDF[fechaSiguiente:].aggregate('prod')
    return valor*cambioAgregado

cuotasDF = loadCuotas()
inflacionDF = loadInflacion()
salarioPromedioRestante = 770000
anosRestantes = 7
cuotasDF = cuotasDF.apply()

# in order to print first 5 lines of Table

# def main():
#     file = open('pension.pdf', 'rb')
#     fileReader = PyPDF2.PdfFileReader(file)
#     fileReader.decrypt("")
#     print(fileReader.getPage(0).extractText())
#
# if __name__ == '__main__':
#     main()

