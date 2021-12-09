import json
import enum
import shutil
import os
import subprocess
import re
import sys
import numpy as np


print(sys.path)

prefolder = ''
if True:
    prefolder = 'pokemon_voices/'

workspace_dir = prefolder+'workspace/'
audio_dir = prefolder+'mp3s/'

concat_file = 'input.ts'
result_mp3 = 'result.mp3'
sox_result_wav = 'sox_result.wav'
result_wav = 'result.wav'
result_raw = 'result.raw'

class VoicePack(int, enum.Enum):
    DEFAULT = 0
    GIRL_1 = 1

    def get_json_directory(self):
        if self == VoicePack.DEFAULT:
            return 'full_pokemon_names.mp3'
        if self == VoicePack.GIRL_1:
            return 'full_attacks_names.mp3'

with open(prefolder+'pokemon_names_voice.json') as f:
    pokemon_names_voice_json = json.load(f)
with open(prefolder+'attack_names_voice.json') as f:
    attack_names_voice_json = json.load(f)
with open(prefolder+'dialog_text_voice.json') as f:
    dialog_text_voice_json = json.load(f)
with open(prefolder+'extra_attack_names_voice.json') as f:
    extra_attack_names_voice_json = json.load(f)

class MediaType(int, enum.Enum):
    POKEMON = 0
    ATTACK = 1
    DIALOG = 2
    POKEMON_EXTRAS = 3
    ATTACK_EXTRAS = 4
    DIALOG_EXTRAS = 5

    def get_media_file(self):
        if self == MediaType.POKEMON:
            return 'full_pokemon_names.mp3'
        if self == MediaType.ATTACK:
            return 'full_attacks_names.mp3'
        if self == MediaType.DIALOG:
            return 'full_dialog_text.mp3'

    def get_json_file(self):
        if self == MediaType.POKEMON:
            return pokemon_names_voice_json
        if self == MediaType.ATTACK:
            return attack_names_voice_json
        if self == MediaType.DIALOG:
            return dialog_text_voice_json
        if self == MediaType.POKEMON_EXTRAS:
            return dialog_text_voice_json
        if self == MediaType.ATTACK_EXTRAS:
            return extra_attack_names_voice_json
        if self == MediaType.DIALOG_EXTRAS:
            return dialog_text_voice_json


sample = [(MediaType.POKEMON, 'pikachu'), (MediaType.DIALOG, 'used'), (MediaType.ATTACK, 'thunder')]
extras = [MediaType.POKEMON_EXTRAS, MediaType.ATTACK_EXTRAS, MediaType.DIALOG_EXTRAS]
#when remote, read from a file to construct this
def construct_audio_clip(segments):
    with open(workspace_dir+concat_file, 'w', encoding="utf-8") as writer:

        construction = ''
        sox_construction = ''
        parts = 1
        for segment in segments:
            media_type = segment[0]
            if type(media_type) is int:
                media_type = MediaType(media_type)


            key = segment[1]
            # Clean up key
            key = re.sub(r'\W+', '', key).lower()

            if media_type in extras:
                extras_json = media_type.get_json_file()
                audio_files = extras_json[key]
                chosen_file = np.random.choice(audio_files)
                part_filename = 'part%d.mp3' % parts
                construction += "file '%s'\n" % (part_filename)
                sox_construction += "%s%s " % (workspace_dir,part_filename)
                writer.write("file '%s'\n" % (part_filename))
                #copy mp3 into workspace
                shutil.copyfile(audio_dir+chosen_file, workspace_dir+part_filename)
                parts += 1
                continue


            #Pokemon not required to exist
            if media_type == MediaType.POKEMON:
                if key not in pokemon_names_voice_json:
                    key = 'digimon'

            media_info = media_type.get_json_file()[key]
            media_file = media_type.get_media_file()
            start_time = media_info['start']
            stop_time =  media_info['stop']
            distance_time = stop_time - start_time
            print(media_file)
            print(media_info)
            part_filename = 'part%d.mp3' % parts
            construction += "file '%s'\n" % (part_filename)
            sox_construction += "%s%s " % (workspace_dir,part_filename)
            writer.write("file '%s'\n" % (part_filename))
            subprocess.call('ffmpeg -ss %.3f -i %s -to %.3f %s ' % (start_time, audio_dir+media_file, distance_time, workspace_dir+part_filename), shell=True)
            parts += 1

    return construction, sox_construction


def is_special_attack(attack_name):

    if attack_name in extra_attack_names_voice_json:
        return [(MediaType.ATTACK_EXTRAS, attack_name)]
    return None


def generate_audio(utterances_json):
    try:
        shutil.rmtree(workspace_dir)
    except OSError as e:
        pass

    os.mkdir(workspace_dir)

    utterances = json.loads(utterances_json)


    output, sox_output = construct_audio_clip(utterances)
#    subprocess.call('sox %s -r 16000 -c 1 -b 16 %s' % (sox_output, workspace_dir+sox_result_wav), shell=True)
    subprocess.call('ffmpeg -safe 0 -f concat -i %s -acodec copy %s' % (workspace_dir+concat_file, workspace_dir+result_mp3), shell=True)
    subprocess.call('ffmpeg -safe 0 -f concat -i %s -acodec pcm_s16le -ac 2 %s' % (workspace_dir+concat_file, workspace_dir+result_wav), shell=True)
    subprocess.call('ffmpeg -safe 0 -f concat -i %s -acodec pcm_s16le -f s16le -ac 1 -ar 16000 %s' % (workspace_dir+concat_file, workspace_dir+result_raw), shell=True)
    print(output)

def play_local_result_file():
    #Play Sample
    subprocess.call('ffplay -autoexit -i %s' % (workspace_dir+result_mp3), shell=True)

def push_audio_to_mic():
    #Play Sample
    subprocess.call('ffplay -autoexit -i %s' % (workspace_dir+result_mp3), shell=True)

def run_sample():
    sample_json = json.dumps(sample)
    generate_audio(sample_json)

    play_local_result_file()




if __name__ == '__main__':
    run_sample()
