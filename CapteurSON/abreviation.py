# Création d'une bibliothèque permettant de definir la entier de manière plus simple, ex : 40000 -> 40k

def abreviation(num):
    prefixe = ['', 'K', 'M', 'G', 'T']
    index = 0

    while num >= 1000 and index < len(prefixe) -1:
        num /= 1000
        index += 1

    return f"{num:.2f}{prefixe[index]}"