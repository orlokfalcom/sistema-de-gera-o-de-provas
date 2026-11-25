import uvicorn
import os

if __name__ == "__main__":
    print("=" * 65)
    print(" GERADOR INTELIGENTE DE AVALIAÇÕES DO ENSINO MÉDIO ")
    print(" 'Uma avaliação. Todas as disciplinas. Inteligência a serviço da educação.' ")
    print("=" * 65)
    print("Iniciando servidor FastAPI e PWA em: http://127.0.0.1:8000")
    print("Swagger / Documentação da API:       http://127.0.0.1:8000/docs")
    print("=" * 65)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
