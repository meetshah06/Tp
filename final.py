import time
# Delcare POT and MOT
pot = ['START', 'USING', 'LTORG', 'DROP', 'DS', 'DC', 'END', 'EQU']

mot = {"LA":["41", 4, "RX"], "SR":["1B", 2, "RR"], "L":["58", 4, "RX"], "AR":["1A", 2, "RR"], "A":["5A", 4, "RX"], "ST":["50", 4, "RX"], "C":["59", 4, "RX"], "LR":["18", 2, "RR"], "BR":["HEHE", 2, "RR"], "BNE":["YAY", 4, "RR"]}

loc = 0
intermediate = []
# Symbol ID Value Length A/R
symbol = {}
# Literal ID Value Length A/R
literal = {}
# Open the file
f = open('test3.txt', 'r')
# Get all the text
text = f.read()
# print(text)
# Split all different lines
lines = text.split('\n')
start = time.time()
# Iterate through each line 
for line in lines:
  # To check if already found in pot
  potflag = 0
  # Used to store Intermediate Code of each line
  temp =[]
  # print(line)
  # Multiple spaces into single space
  line = ' '.join(line.split())
  # print(line)
  # Remove the space after ','
  line = ','.join(line.split(', '))
  # print(line)
  words = line.split()
  if(len(words)==0):
    continue
  # Iterate through POT
  for p in pot:
    # If POT found
    if(p in words):
      # print("directive =",p)
      if p == 'START':
        # print("in start")
        temp.append('')
        temp.append(' '.join(words[1:]))
        # Store in dict
        symbol[words[0]] = [len(symbol), int(words[2]), 1, 'R']
        # Update the loc
        loc = int(words[2])


      elif p == 'USING' or p == 'DROP':
        # print("in using")
        # Better printing
        temp.append('')
        # Add the using statement to temp
        temp.append(' '.join(words).replace('*', str(loc)))

      elif p == 'DS':
        print("in ds")
        temp.append(str(loc))
        temp.append(words[1])
        temp.append(words[2])
        # If already present in symbol table, then update that else add new entry
        ID = symbol[words[0]][0] if words[0] in symbol else len(symbol)
        # Store in symbol table
        symbol[words[0]] = [ID, loc, 4, 'R']
        # Update the loc
        loc += 4*int(words[2][:-1])
      
      elif p == 'DC':
        print("in dc")
        temp.append(str(loc))
        temp.append(words[1])
        temp.append(words[2])
        # Calc no of operands
        num = len(line.split(','))
        # If already present in symbol table, then update that else add new entry
        ID = symbol[words[0]][0] if words[0] in symbol else len(symbol)
        # Store in symbol table
        symbol[words[0]] = [ID, loc, 4, 'R']
        # Update the loc
        loc += 4*num
      
      elif p == 'EQU':
        # Store value specified or current location if value is *
        temp = words[2]
        if '*' in temp:
          # print(type(temp))
          temp = temp.replace('*', str(loc))
          # print(temp)
        val = eval(temp)
        # val = words[2] if words[2] != '*' else loc
        ra = 'A' if '*' in words[2] else 'R'

        # If already present in symbol table, then update that else add new entry
        ID = symbol[words[0]][0] if words[0] in symbol else len(symbol)
        # Store in symbol table
        symbol[words[0]] = [ID, int(val), 1, ra]

      elif p == 'LTORG' or p == 'END':
        # print("in ltorg")
        temp.append(str(loc))
        temp.append('-----') if p == 'LTORG' else temp.append('END')
        # Set loc to the nearest multiple of 8
        if(loc % 8 != 0):
          loc = loc + (8-loc%8)
        
        for k in literal:
          if(literal[k][1] == '-'):
            literal[k][1] = loc
            loc += 4
      # POT used
      potflag = 1
      # If IC is written
      if(len(temp) != 0):
        # Add to intermediate code
        intermediate.append(temp)
      break
  # Directive present, do not check in MOT
  if(potflag == 1):
    continue
  # Iterate through MOT
  for m in mot:
    # If present with label or without label
    if m == words[0] or m == words[1]:
      # If m is in 1st index i.e label is present
      if m == words[1]:
        # Remove the label and store it
        label = words.pop(0)
        # Add to symbol table
        symbol[label] = [len(symbol), loc, 4, 'R']
      
      # Since label is popped, now words[0]=mnemonic and words[2]=operand
      if ',=' in words[1]:
        # Extract the literal
        lit = words[1][words[1].index('=')+1:]
        # Add to literal table
        literal[lit] = [len(literal), '-', 4, 'R']

      elif ',' in words[1]:
        # Separate the left and right symbols in operand
        symbolR = words[1][words[1].index(',')+1:]
        symbolL = words[1][:words[1].index(',')]

        # if '(' in symbolR:
        #   index = symbolR[symbolR.index('(')+1:symbolR.index(')')]
        #   symbolR = symbolR[:symbolR.index('(')]

        # If symbol is not present in symbol table then add it
        if symbolR not in symbol and not symbolR.isnumeric():
          symbol[symbolR] = [len(symbol), '-', '-', '-']
        if symbolL not in symbol and not symbolL.isnumeric():
          symbol[symbolL] = [len(symbol), '-', '-', '-']

      # Add the current loc to temp  
      temp.append(str(loc))
      # Update the location
      loc += mot[m][1]
  
  # Add the mnemonic to temp
  temp.append(words[0])

  if(len(words) > 1):
    # If multiple operands
    if ',' in words[1]:
      # Separate left and right operands
      left = words[1][:words[1].index(',')]
      right = words[1][words[1].index(',')+1:]
      # If symbol present in symbol table
      if(left in symbol):
        # Generate intermediate code and append
        temp.append('ID#'+str(symbol[left][0]))
      else:
        temp.append(' '+ left)
      
      # If symbol present in symbol table 
      if(right in symbol):
        # Add to previously added temp
        temp[-1] += ',ID#' + str(symbol[right][0])
      # If literal present in literal table; +2 for '='
      elif(words[1][words[1].index(',')+2:] in literal):
        temp[-1] += ',LT#'+str(literal[words[1][words[1].index('=')+1:]][0])
      else:
        temp[-1] += right
    # Else if only a single operand present
    elif(words[1] in symbol):
      temp.append('ID#' + str(symbol[words[1]][0]))
    else:
      temp.append(words[1])
  intermediate.append(temp)

end = time.time()
print("Symbol Table")
for key in symbol:
  print(key, symbol[key])

print()

print("Literal Table")
for key in literal:
  print(key, literal[key])

print('Intermediate Code')
for i in intermediate:
  print('\t\t'.join(i))

print("Time =", end-start)