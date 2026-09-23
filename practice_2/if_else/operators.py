age = int(input("Enter your age: "))
student = input("Are you a student? (yes/no): ")

if age >= 18 and student == "yes":
    print("Adult student")

if age < 18 or student == "no":
    print("Not an adult student")

if not student == "yes":
    print("You are not a student")