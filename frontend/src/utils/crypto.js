import CryptoJS from 'crypto-js'

// 确保环境变量已设置且密钥长度正确
const SECRET_KEY = CryptoJS.enc.Utf8.parse(import.meta.env.VITE_APP_CRYPTO_SECRET)

// 密钥验证
if (!SECRET_KEY || SECRET_KEY.toString() === '') {
  throw new Error('CRYPTO_SECRET 环境变量未正确配置')
}

// AES加密函数
export function encrypt(data) {
  const ciphertext = CryptoJS.AES.encrypt(JSON.stringify(data), SECRET_KEY, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7
  }).toString()
  return ciphertext
}

// 解密函数
export function decrypt(ciphertext) {
  try {
    const bytes = CryptoJS.AES.decrypt(ciphertext, SECRET_KEY, {
      mode: CryptoJS.mode.ECB,
      padding: CryptoJS.pad.Pkcs7
    })
    const decrypted = JSON.parse(bytes.toString(CryptoJS.enc.Utf8))
    return decrypted
  } catch (error) {
    console.error('解密失败:', error)
    return null
  }
}

// 加密存储Token
export function saveToken(token) {
  const ciphertext = CryptoJS.AES.encrypt(token, SECRET_KEY, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7
  }).toString()
  localStorage.setItem('authToken', ciphertext)
}

// 解密获取Token
export function getToken() {
  const ciphertext = localStorage.getItem('authToken')
  if (!ciphertext) return null

  try {
    const bytes = CryptoJS.AES.decrypt(ciphertext, SECRET_KEY, {
      mode: CryptoJS.mode.ECB,
      padding: CryptoJS.pad.Pkcs7
    })
    const decrypted = bytes.toString(CryptoJS.enc.Utf8)
    return decrypted
  } catch (error) {
    console.error('解密 Token 失败:', error)
    removeToken()
    return null
  }
}

// 清除Token
export function removeToken() {
  localStorage.removeItem('authToken')
}
