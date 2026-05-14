import pytest
from datetime import datetime, timedelta
import sys
import os

# Adiciona src ao path para os testes
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from domain.entidades import Segredo
from infrastructure.criptografia import MotorDeCriptografia

def test_segredo_expiracao():
    """Valida se a lógica de expiração do segredo está correta."""
    data_futura = datetime.now() + timedelta(hours=1)
    data_passada = datetime.now() - timedelta(hours=1)
    
    segredo_valido = Segredo(conteudo_cifrado="abc", data_expiracao=data_futura)
    segredo_expirado = Segredo(conteudo_cifrado="abc", data_expiracao=data_passada)
    
    assert segredo_valido.esta_expirado() is False
    assert segredo_expirado.esta_expirado() is True

def test_segredo_limite_acessos():
    """Valida se o limite de acessos bloqueia o resgate."""
    data_futura = datetime.now() + timedelta(hours=1)
    segredo = Segredo(conteudo_cifrado="abc", data_expiracao=data_futura, acessos_permitidos=1)
    
    assert segredo.pode_ser_acessado() is True
    segredo.registrar_acesso()
    assert segredo.pode_ser_acessado() is False

def test_criptografia_roundtrip():
    """Valida se o que é cifrado pode ser decifrado corretamente."""
    motor = MotorDeCriptografia("chave_teste_123")
    texto_original = "Mensagem Ultra Secreta"
    
    texto_cifrado = motor.cifrar(texto_original)
    assert texto_cifrado != texto_original
    
    texto_decifrado = motor.decifrar(texto_cifrado)
    assert texto_decifrado == texto_original

def test_criptografia_chaves_diferentes():
    """Valida que chaves diferentes não conseguem decifrar os mesmos dados."""
    motor1 = MotorDeCriptografia("chave1")
    motor2 = MotorDeCriptografia("chave2")
    texto = "Segredo"
    
    cifrado = motor1.cifrar(texto)
    
    with pytest.raises(ValueError):
        motor2.decifrar(cifrado)
