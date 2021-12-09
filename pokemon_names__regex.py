import io

filepath = 'all_pokemon_names.txt'

seen_names = []

#with open(filepath) as fp:
with io.open(filepath,'r',encoding='utf-8',errors='ignore') as fp:
   pokemon_name = fp.readline()
   cnt = 1
   while pokemon_name:
#       print("Line {}: {}".format(cnt, line.strip()))
        pokemon_name = fp.readline().strip()
        if pokemon_name == '':
            continue

        if pokemon_name not in seen_names:
            seen_names.append(pokemon_name)


pokemon_names_insert = '('

for i, atk in enumerate(seen_names):
    pokemon_names_insert += atk
    if i < (len(seen_names) -1):
        pokemon_names_insert += '|'


pokemon_names_insert += ')'
print(pokemon_names_insert)
print(len(seen_names))
