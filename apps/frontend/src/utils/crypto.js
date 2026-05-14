import CryptoJS from 'crypto-js'

/**
 * Utilitário de Criptografia no Lado do Cliente (Zero-Knowledge).
 */

export const gerarChaveAleatoria = () => {
    return CryptoJS.lib.WordArray.random(16).toString()
}

export const cifrarNoCliente = (texto, chave) => {
    // Usamos AES para cifrar o texto no navegador
    return CryptoJS.AES.encrypt(texto, chave).toString()
}

export const decifrarNoCliente = (textoCifrado, chave) => {
    try {
        const bytes = CryptoJS.AES.decrypt(textoCifrado, chave)
        const original = bytes.toString(CryptoJS.enc.Utf8)
        if (!original) throw new Error("Falha na decifração")
        return original
    } catch (e) {
        throw new Error("Chave inválida ou dados corrompidos")
    }
}
