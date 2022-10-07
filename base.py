from fastapi import FastAPI, Path
from typing import List, Optional
import sqlite3
from pydantic import BaseModel


app = FastAPI()

conn = sqlite3.connect('tabela_iss')
cursor = conn.cursor()
cursor.execute('select * from tabela_iss')
desc = cursor.description
results = [tuple(str(item) for item in i) for i in cursor.fetchall()]

column_names = [col[0] for col in desc]
dados = [dict(zip(column_names, row)) for row in results]


class Item(BaseModel):
    descricao: str
    irrf: str
    crf: str
    inss: str
    iss: str


class UpdateItem(BaseModel):
    descricao: Optional[str] = None
    irrf: Optional[str] = None
    crf: Optional[str] = None
    inss: Optional[str] = None
    iss: Optional[str] = None


@app.get("/")
def hello_world_root():
    return {"Hello": "World"}


@app.get('/get-item/{cod_servico}')
def get_item(
        cod_servico: str = Path(
            None,
            description="Fill with ID of the item you want to view")):
    search = list(filter(lambda x: x["servico"] == cod_servico, dados))

    if not search:
        return {'Error': 'Item does not exist'}

    return {'Item': search[0]}


@app.get('/por_descricao')
def get_item(descricao: Optional[str] = None):
    search = list(filter(lambda x: descricao in x["descricao"], dados))

    if not search:
        return {'item': 'Does not exist'}

    return {'Item': search[0]}


@app.post('/create-item/{cod_serv}')
def create_item(cod_serv: str, item: Item):
    search = list(filter(lambda x: x["servico"] == cod_serv, dados))

    if search:
        return {'Error': 'Item exists'}

    item = item.dict()
    item['servico'] = cod_serv

    dados.append(item)
    return item


@app.put('/update-item/{cod_serv}')
def update_item(cod_serv: str, item: UpdateItem):

    search = list(filter(lambda x: x["servico"] == cod_serv, dados))

    if not search:
        return {'Item': 'Does not exist'}

    if item.descricao is not None:
        search[0]['descricao'] = item.descricao

    if item.irrf is not None:
        search[0]['irrf'] = item.irrf

    if item.crf is not None:
        search[0]['crf'] = item.crf

    if item.inss is not None:
        search[0]['inss'] = item.inss

    if item.iss is not None:
        search[0]['iss'] = item.iss

    return search


@app.delete('/delete-item/{cod_serv}')
def delete_item(cod_serv: str):
    search = list(filter(lambda x: x["servico"] == cod_serv, dados))

    if not search:
        return {'Item': 'Does not exist'}

    for i in range(len(dados)):
        if dados[i]['servico'] == cod_serv:
            del dados[i]
            break
    return {'Message': 'Item deleted successfully'}