

def factorial(n):
  f = 1
  while (n > 1):
    f = f*n
    n = n-1
  return f

if __name__ == '__main__':
    myNum = 10
    print("Factorial of 5 is ", factorial(n=myNum))
