def pnMatrix(n, t):
#     lê numero do lado matrix quadrada (n) e o tipo (t) e converte em pares de p/n
#     [E]Distribuição igual: - [AC]Focada em circuitos aritméticos (somadores, ALU): - somador completo:
#     XOR: x                 - XOR: 3x                                               - XOR: 2x
#     AND: x                 - AND: 2x                                               - AND: 2x
#     OR:  x                 - OR:  1x                                               - OR:  1x
#     Diferentes portas      - 
#     vizinhas
    matrix = [[0, 0]]*n*n
    
    #Caso distribuição igual
    if t == 'E':
        for i in range(len(matrix)):
            if (i%3 + i//n)%3==0:
                matrix[i]=[0,1]
            elif (i%3 + i//n)%3==1:
                matrix[i]=[1,0]
            else:
                matrix[i]=[1,1]
    #Caso AC
    if t == 'E':
        for i in range(len(matrix)):
                
                
    # Parte de teste/Matrix visual
    #print(matrix)
    for i in range(n):
        for j in range(n):
            print(matrix[i*n+j], ' ', end='')
        print('\n')
