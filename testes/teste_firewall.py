
from servidor.firewall import (
    bloquear_porta,
    desbloquear_porta,
    consultar_regra
)

def main():
    print("================================")
    print(" TESTE DO FIREWALL DO WINDOWS")
    print("================================")

    porta = 8080

    print("\n1 - Bloquear porta")
    print("2 - Consultar regra")
    print("3 - Desbloquear porta")
    print("4 - Sair")

    while True:
        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            resultado = bloquear_porta(porta)
            print(resultado)

        elif opcao == "2":
            try:
                ativa = consultar_regra(porta)
                print("Regra ativa:", ativa)
            except Exception as erro:
                print("Erro:", erro)

        elif opcao == "3":
            resultado = desbloquear_porta(porta)
            print(resultado)

        elif opcao == "4":
            print("Encerrando testes...")
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()