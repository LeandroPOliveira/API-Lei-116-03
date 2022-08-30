from fastapi import FastAPI, Path
import pyodbc

app = FastAPI()

lmdb = r'C:\Users\loliveira\PycharmProjects\API\lista_servicos.accdb;'
cnx = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'r'DBQ=' + lmdb)
cursor = cnx.cursor()
cursor.execute('select * from tabela_iss')
desc = cursor.description
results = [tuple(str(item) for item in i) for i in cursor.fetchall()]

column_names = [col[0] for col in desc]
dados = [dict(zip(column_names, row)) for row in results]

print(dados)


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
def get_item(descricao: str):
    search = list(filter(lambda x: descricao in x["descricao"], dados))

    if not search:
        return {'item': 'Does not exist'}

    return {'Item': search[0]}


@app.post('/create-item/{cod_serv}')
def create_item(cod_serv: int, item: Item):

    search = list(filter(lambda x: x["id"] == cod_serv, dados))

    if search:
        return {'Error': 'Item exists'}

    item = item.dict()
    item['servico'] = cod_serv

    dados.append(item)
    return item


@app.put('/update-item/{cod_serv}')
def update_item(cod_serv: int, item: UpdateItem):

    search = list(filter(lambda x: x["servico"] == cod_serv, dados))

    if not search:
        return {'Item': 'Does not exist'}

    if item.descricao is not None:
        search[0]['descricao'] = item.name

    return search


@app.delete('/delete-item/{cod_serv}')
def delete_item(cod_serv: int):
    search = list(filter(lambda x: x["servico"] == cod_serv, dados))

    if not search:
        return {'Item': 'Does not exist'}

    for i in range(len(dados)):
        if dados[i]['servico'] == cod_serv:
            del dados[i]
            break
    return {'Message': 'Item deleted successfully'}