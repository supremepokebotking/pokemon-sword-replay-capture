from pokemon_voices.voice_fetcher import *
import json

def play_audio_remote(utterances):
    utterances_json = json.dumps(utterances)

    cmd_to_execute = '%s' % (utterances_json)
    server = '192.168.0.57'
    username = 'jetsonquest'
    password = '2wsx!QAZ'
    ssh = paramiko.SSHClient()
    ssh.connect(server, username=username, password=password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)


def play_audio_local(utterances):
    utterances_json = json.dumps(utterances)
    generate_audio(utterances_json)

    #Play Sample
    play_local_result_file()
