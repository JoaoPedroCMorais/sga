from fastapi import FastAPI

app = FastAPI(
    title="SGA API",
    description="API do Sistema de Gerenciamento Acadêmico (CAAI)",
    version="4.0.0",
)

@app.get("/health")
def health_check():
    return {"status": "online", "message": "O motor FastAPI está funcionando perfeitamente!"}