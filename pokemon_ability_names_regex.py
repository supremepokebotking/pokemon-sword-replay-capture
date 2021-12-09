
import io

filepath = 'all_ability_names.txt'

seen_names = []

#with open(filepath) as fp:
with io.open(filepath,'r',encoding='utf-8',errors='ignore') as fp:
   ability_name = fp.readline()
   cnt = 1
   while ability_name:
#       print("Line {}: {}".format(cnt, line.strip()))
        ability_name = fp.readline().strip()
        if ability_name == '':
            continue

        if ability_name not in seen_names:
            seen_names.append(ability_name)


ability_names_insert = '('

for i, atk in enumerate(seen_names):
    ability_names_insert += atk
    if i < (len(seen_names) -1):
        ability_names_insert += '|'


ability_names_insert += ')'
print(ability_names_insert)
print(len(seen_names))
