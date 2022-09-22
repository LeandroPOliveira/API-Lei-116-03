from fastapi import FastAPI, Path
from typing import Optional
import pyodbc
import string
from pydantic import BaseModel

app = FastAPI()

lmdb = r'C:\Users\loliveira\PycharmProjects\API\API-Lei-116\lista_servicos.accdb;'
cnx = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'r'DBQ=' + lmdb)
cursor = cnx.cursor()
cursor.execute('select * from municipios')
desc = cursor.description
results = [tuple(str(item) for item in i) for i in cursor.fetchall()]

column_names = [col[0] for col in desc]
dados = [dict(zip(column_names, row)) for row in results]


class Item(BaseModel):
    cod_iss: str
    aliq_iss: str


class UpdateItem(BaseModel):
    aliq_iss: Optional[str] = None


@app.get("/")
def hello_world_root():
    return {"Hello": "World"}


@app.get('/get-item/{municipio}/{cod_iss}')
def get_item(
        municipio: str = Path(
            None,
            description="Preencha o nome da prefeitura desejada"), cod_iss: str = None):

    search = list(filter(lambda x: x["municipio"] == string.capwords(municipio) and x["cod_iss"] == cod_iss, dados))

    if not search:
        return {'Error': 'Item does not exist'}

    return {'Item': search}


@app.post('/create-item/{municipio}/{cod_iss}')
def create_item(municipio: str, cod_iss: str, item: Item):
    search = list(filter(lambda x: x["municipio"] == municipio and x["cod_iss"] == cod_iss, dados))

    if search:
        return {'Error': 'Item exists'}

    item = item.dict()
    item['municipio'] = municipio
    item['cod_iss'] = cod_iss

    dados.append(item)
    return item


@app.put('/update-item/{cod_serv}')
def update_item(municipio: str, cod_iss: str, item: UpdateItem):

    search = list(filter(lambda x: x["municipio"] == municipio and x["cod_iss"] == cod_iss, dados))

    if not search:
        return {'Item': 'Does not exist'}

    if item.aliq_iss is not None:
        search[0]['aliq_iss'] = item.aliq_iss

    return search


@app.delete('/delete-item/{municipio}/{cod_iss}')
def delete_item(municipio: str, cod_iss: str):
    search = list(filter(lambda x: x["municipio"] == municipio and x["cod_iss"] == cod_iss, dados))

    if not search:
        return {'Item': 'Does not exist'}

    for i in range(len(dados)):
        if dados[i]['municipio'] == municipio and dados[i]['cod_iss'] == cod_iss:
            del dados[i]
            break
    return {'Message': 'Item deleted successfully'}
