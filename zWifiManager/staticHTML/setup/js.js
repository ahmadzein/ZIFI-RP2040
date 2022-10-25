
let utf8Encode = new TextEncoder("utf-8");

console.log('ch123 yalla')

function encrypt(data,key){
encodeData= utf8Encode.encode(data)
encodeKey= utf8Encode.encode(key)
encodeKeyLength= encodeKey.length-1
console.log('ch123 data key',data,' ', key)
console.log('ch123 encodeData key',encodeData,' ', encodeKey)
encArr = []

encodeData.forEach((item, index) => {
console.log('ch123 loop',encodeKeyLength, item, index, encodeKey[encodeKeyLength])
var calc = item * encodeKey[encodeKeyLength];
console.log('ch123 multi',calc)
  encArr[index] = calc;
  encodeKeyLength--
  if(encodeKeyLength === -1){
  encodeKeyLength = encodeKey.length-1
  }
})

return encArr
}

function decrypt(dataArray,key){
encodeKey= utf8Encode.encode(key)
encodeKeyLength= encodeKey.length-1
console.log('ch123 data key',dataArray,' ', key)
encArr = []

dataArray.forEach((item, index) => {
console.log('ch123 loop',encodeKeyLength, item, index, encodeKey[encodeKeyLength])
var calc = item / encodeKey[encodeKeyLength];
console.log('ch123 multi',calc)
  encArr[index] = calc;
  encodeKeyLength--
  if(encodeKeyLength === -1){
  encodeKeyLength = encodeKey.length-1
  }
})

var deco = new TextDecoder().decode(new Uint8Array(encArr).buffer)
return deco
}

function submitForm(e){
   console.log('ch123',e.target.password.value)
   var encPass = encrypt(e.target.password.value, e.target.secretKey.value)
   e.target.secretKey.value = ''
   e.target.password.value = encPass
   console.log('ch123',encPass ,e.target)
return true

}
