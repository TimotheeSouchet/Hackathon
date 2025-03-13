import csv;
import os;
import time;
import folium;
from folium.plugins import BeautifyIcon;
from geopy.distance import geodesic;
import math;

# PUIG Thomas - RT1 - Hackathon 2025 - Livrable pour le commanditaire SUEZ - Heatmap

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "DonneesHeatmap.csv ")

def FixLat(latitude):
    if latitude >110:
        latitude = latitude - 360
    return latitude

# >Vérification que le fichier de données est présent dans le dossier racine

if not os.path.isfile(file_path):
    print(f"/!\ Le fichier de données est manquant /!\ \nImpossible de trouver le fichier de données: {file_path}.\nFermeture du programme.")
    quit()

# >Ouverture et lecutre (extraction des données nécessaires)

with open(file_path, newline='') as csvfile:
    data = list(csv.DictReader(csvfile))
    limit = 0 # 0 pour tous
    currRow = 0
    count,full = {},{}
    print("---- LECTURE DES ENREGISTREMENTS ----")
    debut = time.time()
    if limit == 0:
        limit = len(data)-1
    print(f"{limit+1} enregistrements à traiter.\n")

    for row in data:
        print(f">{int(currRow/limit*100)}% - {int((time.time()-debut)*10)/10}s",end="\r")
        if not row['Animal_ID'] in count:
            count[row['Animal_ID']] = 0
            full[row['Animal_ID']] = [0,[float(row['Latitude'])],[float(row['Longitude'])],[row['Location_Timestamp_UTC']]]
        else:
            count[row['Animal_ID']] += 1
            full[row['Animal_ID']][0] += 1
            full[row['Animal_ID']][1].append(float(row['Latitude']))
            full[row['Animal_ID']][2].append(float(row['Longitude']))
            full[row['Animal_ID']][3].append(row['Location_Timestamp_UTC'])

        if currRow == limit-1:
            break
        currRow += 1

    print("                                     ",end="\r")
    print(f">100% - {int((time.time()-debut)*10)/10}s\n")
    tot = 0
    somm = 0
    for i in count:
        somm += count[i]
        tot += 1
    print(f"---- LECTURE TERMINEE ----\n\nEffectué en {int((time.time()-debut)*10)/10} secondes.\n{len(count)} animaux, moyenne de {int(somm/tot)} entrées par animal.\n")
    
    # >Dump de données pour debug
    valide = False
    while not valide:
        saisie = input("Voulez vous accéder aux données brutes?\n(Y/N) > ")
        if saisie.lower() == "y" or saisie.lower() == "yes" or saisie.lower() == "oui":
            valide = True
            dump = True
        elif saisie.lower() == "n" or saisie.lower() == "no" or saisie.lower() == "non":
            valide = True
            dump = False
        else:
            print("\n/!\ Saisie invalide. Veuillez répondre par oui (Y) ou non (N).")
    if dump:
        print(f"Format d'enregistrement:\n[ 'ID_ANIMAL': [ Nombre_Enregistrements , [-Latitudes-] , [-longitudes-] , [-dates-] ] ]\n\n---- DONNEES ----\n\n{full}\n\nFormat d'enregistrement:\n[ 'ID_ANIMAL': [ Nombre_Enregistrements , [-Latitudes-] , [-longitudes-] , [-dates-] ] ]\n\n---- FIN DES DONNEES ----")
    
    # >Sauvegarde de carte des déplacements de chaque animal
    valide = False
    while not valide:
        saisie = input("\nVoulez vous procéder à une sauvegarde du trajet de chaque animal dans sa propre carte? Cela peut engendrer un temps de traitement visible.\n(Y/N) > ")
        if saisie.lower() == "y" or saisie.lower() == "yes" or saisie.lower() == "oui":
            valide = True
            sauvegarde = True
        elif saisie.lower() == "n" or saisie.lower() == "no" or saisie.lower() == "non":
            valide = True
            sauvegarde = False
        else:
            print("\n/!\ Saisie invalide. Veuillez répondre par oui (Y) ou non (N).")
        
    if sauvegarde == True:
        print("\n---- DEBUT DE LA SAUVEGARDE ----\n")
        debut = time.time()
        currFull = 0
        limit = 0 # 0 = tous, debug

        # Pour chaque oiseau, on crée une carte avec chaque enregistrement, le tout lié, avec dégradé de couleur et date en tooltip
        for i in full:
            map = folium.Map(location=[20,-100], tiles="OpenStreetMap", zoom_start=2)

            print("                                         ",end="\r")
            print(f"{currFull+1}/{len(full)+1} - {int((time.time() - debut)*10)/10}s - Animal: {i}",end="\r")

            for j in range(0,len(full[i][1])):
                color = ('{:02X}' * 3).format(255, int(j/3), 0)
                if j/3 >255:
                    color = "FFFF00"

                folium.Marker([full[i][1][j],FixLat(full[i][2][j])], tooltip = f'{full[i][3][j]}', icon=BeautifyIcon(icon_shape='rectangle-dot', border_color=f'#{color}', border_width=5)).add_to(map)
                if j != 0:
                    folium.PolyLine([[full[i][1][j], FixLat(full[i][2][j])], [full[i][1][j-1], FixLat(full[i][2][j-1])]], color=f'#{color}').add_to(map)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, rf"Cartes\{i}.html")
            map.save(file_path)

            currFull+=1
            if currFull > limit and limit != 0:
                break

        print("                                         ",end="\r")
        print(f"{len(count)}/{len(count)}\n\n---- SAUVEGARDE TERMINEE ----\n\nEffectué en {int((time.time() - debut)*10)/10} secondes.\nEmplacement: {script_dir}\Cartes\ \n")

    # >Sauvegarde de carte des points d'intéret (POI)
    valide = False
    while not valide:
        saisie = input("\nVoulez vous produire une carte des points d'intérêt (haute concentration d'animaux)? Cela peut engendrer un temps de traitement visible.\n(Y/N) > ")
        if saisie.lower() == "y" or saisie.lower() == "yes" or saisie.lower() == "oui":
            valide = True
            produire = True
        elif saisie.lower() == "n" or saisie.lower() == "no" or saisie.lower() == "non":
            valide = True
            produire = False
        else:
            print("\n/!\ Saisie invalide. Veuillez répondre par oui (Y) ou non (N).")
    
    if produire:
        print("\n---- DEBUT DU REGROUPEMENT ----\n")
        debut = time.time()
        defaultDistRegroup = 750
        defaultMinPoints = 300
        
        distRegroup = input(f"Voulez vous changer la valeur de la distance de regroupement? (Par défaut -> {defaultDistRegroup}km)\n/!\ Plus la distance sera petite, plus il y aura de groupes et donc de temps de traitement.\n(Nombre [km]) > ")
        if distRegroup == "":
            print(f"Valeur par défault sélectionnée: {defaultDistRegroup}km")
            distRegroup = defaultDistRegroup
        else:
            try:
                float(distRegroup)
                distRegroup = float(distRegroup)
                print(f"Distance de regroupement: {distRegroup}km")
            except:
                print(f"\nValeur incorrect. Utilisation de la valeur par défaut: {defaultDistRegroup}km")
                distRegroup = defaultDistRegroup

        minPoints = input(f"\nVoulez vous changer la valeur de points minimum nécessaires pour un groupe? (Par défaut -> {defaultMinPoints} points)\n(Nombre) > ")
        if minPoints == "":
            print(f"Valeur par défault sélectionnée: {defaultMinPoints}\n")
            minPoints = defaultMinPoints
        else:
            try:
                float(minPoints)
                minPoints = float(minPoints)
                print(f"Minimum de points pour le regroupement: {minPoints}\n")
            except:
                print(f"\nValeur incorrect. Utilisation de la valeur par défaut: {defaultMinPoints}\n")
                minPoints = defaultMinPoints

        coords = []
        for i in full:
            curr = []
            for j in range(0,len(full[i][1])):
                if j!= 0 and geodesic([full[i][1][j],FixLat(full[i][2][j])],curr[-1]).kilometers < distRegroup/2:
                    curr[-1] = [full[i][1][j],FixLat(full[i][2][j])]
                else:
                    curr.append([full[i][1][j],FixLat(full[i][2][j])])
                    
            coords.append(curr)

        map = folium.Map(location=[20,-100], tiles="OpenStreetMap", zoom_start=2)

        # On parcourt les coordonnées pour créer des groupes qui rassemblent en fonction de la distance
        groupsCoords = []
        for i in range(0,len(coords)-1):
            curr = 0
            for j in coords[i]:
                barre = ['-']*len(coords[i])
                for k in range(0,curr):
                    barre[k] = "#"
                txt = ""
                for k in barre:
                    txt+=k
                print(f">Animal {i+1}/{len(coords)}: {txt} {curr}/{len(coords[i])}                    ",end="\r")
                curr+=1
                for k in range(i+1,len(coords)):
                    for l in coords[k]:
                        dist = geodesic(j,l).kilometers
                        if dist < distRegroup:
                            unique = True
                            for m in groupsCoords:
                                if geodesic(l,m[0]).kilometers < distRegroup:
                                    unique = False
                                    m[1] += 1
                            if unique:
                                groupsCoords.append([l,1,distRegroup])

        # On rassemble les zones qui s'entrecoupent
        for i in groupsCoords:
            for j in groupsCoords:
                if (geodesic(i[0],j[0]).kilometers < i[2] or geodesic(i[0],j[0]).kilometers < j[2]) and i != j and i[1] > minPoints and j[1] > minPoints:
                        if i[2] < j[2]:
                            i[0] = j[0]
                            i[2] = j[2]
                        i[1] += j[1]
                        groupsCoords.remove(j)
                            
                elif i != j and geodesic(i[0],j[0]).kilometers <= i[2]+j[2] and i[1] > minPoints and j[1] > minPoints:
                    c1,c2,r1,r2 = i[0],j[0],i[2],j[2]
                    vect = [c2[0]-c1[0],c2[1]-c1[1]]
                    dist = math.sqrt(vect[0]**2+vect[1]**2)
                    r3 = (r1+r2+dist)/2
                    vect = [vect[0]/dist,vect[1]/dist]
                    P = [c2[0]+vect[0]*r2,c2[1]+vect[1]*r2]
                    c3 = [P[0]-vect[0]*r3,P[1]-vect[1]*r3]
                    r3 = (r1+r2+geodesic(i[0],j[0]).kilometers)/2
                    i[0] = c3
                    i[1] += j[1]
                    i[2] = r3
                    groupsCoords.remove(j)

        # Enfin on place les points sur la carte
        for i in groupsCoords:
            if i[1]>minPoints:
                folium.Marker(i[0], tooltip=f"{i[1]} enregistrements").add_to(map)
                folium.Circle(
                    i[0],
                    radius=i[2]*1000,
                    fill_opacity=0.4,
                    stroke = False,
                    opacity=1,
                    fill_color="green",
                ).add_to(map)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, rf"POI.html")
        map.save(file_path)
        print(f"Effectué en {int((time.time()-debut)*10)/10} secondes.                                          \nEmplacement: {script_dir}\POI\ ")

print("\n---- FIN DU PROGRAMME ----")