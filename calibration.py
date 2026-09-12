import machine
import time

def avg(given_list: list) -> float:
  total = 0
  for item in given_list:
    total = total + item

  return (total/len(given_list))

moisture = machine.ADC(27)

print("Waiting 10 seconds before starting data read")

for i in range(10):
  raw_value = moisture.read_u16()
  print(raw_value)
  time.sleep(1)

print("Taking 30 data points")

data = []

for i in range(30):
  value = moisture.read_u16()
  data.append(value)
  print(value)
  time.sleep(1)

print(f"Data: {data}")
print(f"Max value: {max(data)}\nMin value: {min(data)}\n Avg value: {avg(data)}")