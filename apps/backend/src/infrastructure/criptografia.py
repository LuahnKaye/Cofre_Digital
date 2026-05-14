import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from application.servicos import ServicoDeCriptografia

class MotorDeCriptografia(ServicoDeCriptografia):
    """
    Implementação robusta de criptografia de envelope usando AES-256-GCM.
    
    Esta classe utiliza uma Key Encryption Key (KEK) mestre para cifrar 
    Data Encryption Keys (DEKs) únicas para cada segredo.
    """

    def __init__(self, chave_mestre_hex: str):
        """
        Inicializa o motor com a KEK (Chave Mestra).
        
        Args:
            chave_mestre_hex (str): Chave mestra em formato hexadecimal ou string.
        """
        # Derivamos uma chave de 32 bytes (256 bits) a partir da string mestre
        salt = b'cofre_digital_salt_estatico' # Em prod, ideal usar algo do Vault
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        self.kek = AESGCM(kdf.derive(chave_mestre_hex.encode()))

    def cifrar(self, texto_puro: str) -> str:
        """
        Cifra o texto usando uma DEK nova e protege a DEK com a KEK.
        
        Formato do retorno (base64):
        IV_DEK(12) + DEK_CIFRADA(32+16) + IV_TEXTO(12) + TEXTO_CIFRADO(n+16)
        """
        # 1. Gerar uma DEK (Data Encryption Key) aleatória de 256 bits
        dek_pura = AESGCM.generate_key(bit_length=256)
        aesgcm_dek = AESGCM(dek_pura)

        # 2. Cifrar a DEK com a KEK
        iv_dek = os.urandom(12)
        dek_cifrada = self.kek.encrypt(iv_dek, dek_pura, None)

        # 3. Cifrar o texto puro com a DEK
        iv_texto = os.urandom(12)
        texto_cifrado = aesgcm_dek.encrypt(iv_texto, texto_puro.encode(), None)

        # 4. Empacotar tudo em um único blob e codificar em base64
        pacote = iv_dek + dek_cifrada + iv_texto + texto_cifrado
        return base64.b64encode(pacote).decode('utf-8')

    def decifrar(self, texto_cifrado_base64: str) -> str:
        """
        Desempacota o blob, recupera a DEK usando a KEK e decifra o texto.
        """
        try:
            pacote = base64.b64decode(texto_cifrado_base64)
            
            # Índices para desempacotamento
            # IV_DEK(12) | DEK_CIFRADA(32+16=48) | IV_TEXTO(12) | TEXTO_CIFRADO(...)
            idx_dek_cifrada = 12
            idx_iv_texto = 60
            idx_texto_cifrado = 72

            iv_dek = pacote[:idx_dek_cifrada]
            dek_cifrada = pacote[idx_dek_cifrada:idx_iv_texto]
            iv_texto = pacote[idx_iv_texto:idx_texto_cifrado]
            texto_cifrado = pacote[idx_texto_cifrado:]

            # 1. Decifrar a DEK usando a KEK
            dek_pura = self.kek.decrypt(iv_dek, dek_cifrada, None)
            aesgcm_dek = AESGCM(dek_pura)

            # 2. Decifrar o texto usando a DEK
            texto_puro = aesgcm_dek.decrypt(iv_texto, texto_cifrado, None)
            
            return texto_puro.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Falha na decodificação ou decriptografia: {str(e)}")
