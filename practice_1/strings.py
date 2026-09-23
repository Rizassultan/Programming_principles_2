a = str(input('write str with at least 7 characters: '))
while len(a) < 7:
  a = input("at least 7 characters!!!: ")
print("word part starting from 2nd letter ending with 5th(including) letter:", a[1:5])

print("in upper case:", a.upper())

b = "Lebron James"
age_of_lebron = 41
print(f"{b} is still playing in NBA and his age is {age_of_lebron}!")