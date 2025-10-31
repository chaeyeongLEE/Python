print('안녕'*10)
print(123+456)

풀네임="슈퍼네임"

print(풀네임)
print('차은우'[0:3])

중고차 = ['K5', 'white', [5000, 6000] ]
print(중고차[2][1])

if 'K5' in 중고차 : print('k5 있습니다')

중고차2= {'brand':'bmw', 'model': '520d'}
중고차2['brand'] = 'benz'
print(중고차2['brand'])

print('중고차2.values:', 중고차2.values())
print('중고차2.keys():', 중고차2.keys())
print('중고차2.items()', 중고차2.items())


재고량=10
message='주문가능!!'

if 재고량 < 0 : print(message)
else : print('@@@재고량이 없어요')

if 'K5' in 중고차 : print(message + '캬캬')
if 'brand' in 중고차2 : print(message + '있다있어~~')
if 'brand' in 중고차2 : print(중고차2['brand'])
if 'benz' in 중고차2.values(): print("benz 있다있어~ 🚗💨")
