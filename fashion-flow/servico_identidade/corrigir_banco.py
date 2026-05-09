from banco_de_dados import motor_do_banco
from sqlalchemy import text

def corrigir_banco():
    print("Tentando adicionar coluna 'nome'...")
    try:
        with motor_do_banco.connect() as conexao:
            # Comando SQL puro para alterar a tabela
            conexao.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS nome VARCHAR;"))
            conexao.commit()
            print("Sucesso! Coluna 'nome' adicionada ou ja existente.")
    except Exception as e:
        print(f"Erro ao atualizar banco: {e}")

if __name__ == "__main__":
    corrigir_banco()
