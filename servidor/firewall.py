import subprocess

# Portas que o projeto permite bloquear
PORTAS_PERMITIDAS = {8080}

# Prefixo das regras criadas pelo projeto
PREFIXO_REGRA = "ProjetoRedes_Bloqueio_"


def validar_porta(porta):
    """
    Verifica se a porta informada é válida
    e se está autorizada para os testes.
    """
    if type(porta) is not int:
        raise ValueError("A porta deve ser um número inteiro.")

    if porta not in PORTAS_PERMITIDAS:
        raise ValueError("Porta não autorizada para bloqueio.")

    return porta


def nome_regra(porta):
    """
    Gera o nome da regra do firewall.
    """
    validar_porta(porta)

    return f"{PREFIXO_REGRA}{porta}"


def executar_powershell(comando):
    """
    Executa um comando PowerShell no Windows.
    """
    resultado = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            comando
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15
    )

    return resultado


def consultar_regra(porta):
    """
    Verifica se a regra existe e está habilitada.
    """
    regra = nome_regra(porta)

    comando = (
        f"$r = Get-NetFirewallRule -Name '{regra}' "
        "-ErrorAction SilentlyContinue; "
        "if ($null -eq $r) { exit 1 }; "
        "if ($r.Enabled -eq 'True' -and "
        "$r.Action -eq 'Block' -and "
        "$r.Direction -eq 'Inbound') { exit 0 }; "
        "exit 2"
    )

    resultado = executar_powershell(comando)

    if resultado.returncode == 0:
        return True

    if resultado.returncode == 1:
        return False

    raise RuntimeError(
        "Não foi possível confirmar o estado da regra."
    )


def bloquear_porta(porta):
    """
    Cria uma regra para bloquear conexões TCP
    de entrada na porta especificada.
    """
    regra = nome_regra(porta)

    try:
        if consultar_regra(porta):
            return {
                "sucesso": True,
                "mensagem": "A regra de bloqueio já está ativa."
            }

        comando = (
            "$ErrorActionPreference = 'Stop'; "
            f"New-NetFirewallRule -Name '{regra}' "
            f"-DisplayName '{regra}' "
            "-Direction Inbound "
            "-Protocol TCP "
            f"-LocalPort {porta} "
            "-Action Block "
            "-Profile Any "
            "-Enabled True | Out-Null"
        )

        resultado = executar_powershell(comando)

        if resultado.returncode != 0:
            return {
                "sucesso": False,
                "mensagem": resultado.stderr.strip()
            }

        if not consultar_regra(porta):
            raise RuntimeError("Regra não foi ativada.")

        return {
            "sucesso": True,
            "mensagem": f"Porta {porta} bloqueada com sucesso."
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "mensagem": str(erro)
        }


def desbloquear_porta(porta):
    """
    Remove a regra de bloqueio criada pelo projeto.
    """
    regra = nome_regra(porta)

    try:
        if not consultar_regra(porta):
            return {
                "sucesso": True,
                "mensagem": "A regra já está ausente."
            }

        comando = (
            "$ErrorActionPreference = 'Stop'; "
            f"Remove-NetFirewallRule -Name '{regra}'"
        )

        resultado = executar_powershell(comando)

        if resultado.returncode != 0:
            return {
                "sucesso": False,
                "mensagem": resultado.stderr.strip()
            }

        if consultar_regra(porta):
            raise RuntimeError("A regra continua ativa.")

        return {
            "sucesso": True,
            "mensagem": f"Porta {porta} desbloqueada."
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "mensagem": str(erro)
        }