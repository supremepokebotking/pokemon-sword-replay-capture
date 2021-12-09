import re
import json

pokemon_names = []

silence_start_regex = 'silence_start:\s(\d*\.?\d*)'
silence_end_regex = 'silence_end:\s(\d*\.?\d*)'
silence_duration_regex = 'silence_duration:\s(\d*\.?\d*)'

with open('full_pokemon_names.txt', 'r', encoding="utf-8") as reader:
    # Alternatively you could use
    line = reader.readline().strip()
    data = {'name': line}
    pokemon_names.append(data)
    while line != '':  # The EOF char is an empty string
        line = reader.readline().strip()
        if line == '':
            continue
        data = {'name': line}
        pokemon_names.append(data)

i = 0
start_time = 0.0
stop_time = None
pokemon_names_json = {}
with open('full_pokemon_names_silences.txt', 'r', encoding="utf-8") as reader:
    # Further file processing goes here
    # Read and print the entire file line by line
    while i < len(pokemon_names) - 1:  # The EOF char is an empty string
        silence_start_line = reader.readline().strip()
        silence_stop_duration_line = reader.readline().strip()
#        print(silence_start_line)
#        print(silence_stop_duration_line)

        try:
            stop_time = float(re.search(silence_start_regex, silence_start_line).group(1))
        except:
            print(silence_start_line)
            print(silence_stop_duration_line)
            raise

        # add some duration for spacing?
        duration_time = float(re.search(silence_duration_regex, silence_stop_duration_line).group(1) )
        duration_time = min(0.2, duration_time/2)

        stop_time += duration_time

        data = pokemon_names[i]
        start_time_mod = 0.0
        if start_time != 0.0:
            start_time_mod = 0.1
        data['start'] = start_time - start_time_mod
        data['stop'] = stop_time
        data['distance'] = stop_time - start_time
        key = re.sub(r'\W+', '', data['name']).lower()
        pokemon_names_json[key] = data


        

        # Update, start_time becomes end_time
        i += 1
        start_time = float(re.search(silence_end_regex, silence_stop_duration_line).group(1))

    # For last item only
    # Set manually
    data = pokemon_names[len(pokemon_names)-1]
    start_time_mod = 0.1
    data['start'] = start_time - start_time_mod
    data['stop'] = -1
    data['distance'] = 1.29


#        break


print(pokemon_names[25:35])
#print(pokemon_names[783:785])
#print(pokemon_names[709:713])

print(json.dumps(pokemon_names_json))

