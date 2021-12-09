import re

used_attack_regex = '.*used .*!'

seen_attacks = []

filepath = 'all_attacks_raw.txt'
import io

#with open(filepath) as fp:
with io.open(filepath,'r',encoding='utf-8',errors='ignore') as fp:
   line = fp.readline()
   cnt = 1
   while line:
#       print("Line {}: {}".format(cnt, line.strip()))
       line = fp.readline().strip()

       if re.search(used_attack_regex, line):
           attack_name = line[line.index('used '):-1].replace('used ', '').strip()
           if attack_name not in seen_attacks:
               seen_attacks.append(attack_name)
           
       cnt += 1


attack_names_insert = '('

for i, atk in enumerate(seen_attacks):
    attack_names_insert += atk
    if i < (len(seen_attacks) -1):
        attack_names_insert += '|'


attack_names_insert += ')'
print(attack_names_insert)
print(len(seen_attacks))
