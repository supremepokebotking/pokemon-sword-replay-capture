
with open('aws_ready_dialog_text.txt', 'w', encoding="utf-8") as writer:
    # Alternatively you could use
    with open('pokemon_dialog_text.txt', 'r', encoding="utf-8") as reader:
        # Further file processing goes here
        # Read and print the entire file line by line
        line = reader.readline().strip()
        writer.write('%s!\n'%(line))
        while line != '':  # The EOF char is an empty string
            line = reader.readline().strip()
            writer.write('%s!\n'%(line))
