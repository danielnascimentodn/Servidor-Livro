from fastapi import FastAPI, WebSocket
from ariadne.asgi import GraphQL
from resolvers import query,mutation, subscription
from banco import init_db
from ariadne import make_executable_schema
from ariadne import gql

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#Definindo as origens permitidas pelo CORS
origins =[
    "https://localhost",
    "https://localhost:8000", #Se o frontend estiver na porta 8000
]

#Confirgura CORS para permitir requesições de outras origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Inicia banco de dados 
init_db() 

subscribers =[]

type_defs = gql("""
    type Author{
        id:ID!
        name:String!   
    }
            
    type Book{
        id:ID!
        title:String!
        authors:[Author!]!       
    }  

    type Query{
        authors:[Author!]!
        books:[Book!]!
    }

    type Mutation{
        createAuthor(name:String!):Author!            
        updateAuthor(id:Int!,name:String!):Author!
        deleteAuthor(id:Int!): Boolean!
                
        createBook(title:String!,authorIds:[Int!]!):Book!
        updateBook(id:Int!,title:String!,authorIds:[Int!]!):Book!
        deleteBook(id:Int!):Boolean!               
    }
                
    type Subcription{
        bookAdicionado: Book        
    }
""")
schema = make_executable_schema(type_defs, query, mutation, subscription)

#configura o endpoint GraphQl
graphql_app=GraphQL(schema,debug=True)

#Adicionando a rota HTTP para GraphQL (GET e POST)
app.add_route("/graphql", graphql_app)

#Adicionar a rota WS para lidar com o Subscription
@app.websocket("/graphql")
async def  websocket_endpoint(websocket:WebSocket):
    await websocket.accept()

    subscribers.append(websocket)

    try:
        while True:
            data = await websocket.receive_text() 

            await websocket.send_text(data)
    except Exception as e:
        print(f"erro Exception:{e}")
    finally:
        subscribers.remove(websocket)

@app.get("/")
def read_root():
    return {"message":"Servidor GraphQl!"}
