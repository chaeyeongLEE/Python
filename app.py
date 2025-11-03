print("[BOOT] app.py loaded")
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

# for 반복문
# for i in 반복할범위 : 반복해줄코드
for i in range(0,3) : print("당근")

중고차들 = ['K5', 'BMW', 'Tico']
for i in 중고차들 : print(i)

중고차들2 = [10, 20, 30]
for i in 중고차들2 : print(i+1)

# for n in range(1, 10) : print("짝수:",n*2)

for dan in range(2,5) :
    for num in range(1,10) :
        print(dan*num)


def 인사하기() : print('안녕하세요 중고차신뢰딜러 차은우입니다')
인사하기()

def 모자(숫자) : print(숫자 + 2)
모자(2)

def 수학연산(x) : return x + 2
결과 = 수학연산(4)
print(결과)
