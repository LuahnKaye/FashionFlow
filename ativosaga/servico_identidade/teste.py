from rotas_autenticacao import registrar_usuario
from esquemas import UsuarioCriar
from banco_de_dados import obter_banco

usuario_data = UsuarioCriar(nome="Luahn Kaye Local", email="luahnkaye_local@gmail.com", senha="123")
banco_gen = obter_banco()
banco = next(banco_gen)

try:
    resultado = registrar_usuario(usuario_data, banco)
    print("Sucesso:", resultado)
except Exception:
    import traceback
    traceback.print_exc()
finally:
    try:
        next(banco_gen)
    except StopIteration:
        pass
