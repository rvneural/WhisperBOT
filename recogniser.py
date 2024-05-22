import speech_recognition as sr
from pydub import AudioSegment
import moviepy.editor as mp
import os

"""    class RecognizeBot:
     states = ['get file', 'ready', 'transcribe', 'done', 'error']
     transitions = [
        {'trigger': 'get file', 'source': 'start', 'dest': 'get file'},
        {'trigger': 'recognize', 'source': 'get file', 'dest': 'ready'},
        {'trigger': 'rec_r', 'source': 'ready', 'dest': 'transcribe'},
        {'trigger': 'transcribe', 'source': 'transcribe', 'dest': 'done'}]"""

#Перевод аудио в текст
formalist = ['mp3', 'wav', 'ogg', 'flv', 'm4a']


def recognize_audio(path: str, audio_format: str) -> str:


    audio_file = path + '.wav'

    if audio_format not in formalist:
        raise Exception()
    if audio_format == 'mp3':
        sound = AudioSegment.from_mp3(path)
        sound.export(audio_file, format="wav")
    elif audio_format == 'ogg':
        sound = AudioSegment.from_ogg(path)
        sound.export(audio_file, format="wav")
    elif audio_format == 'flv':
        sound = AudioSegment.from_flv(path)
        sound.export(audio_file, format="wav")
    elif audio_format == 'm4a':
        sound = AudioSegment.from_file(path, format='mpeg')
        sound.export(audio_file, format="wav")
    else:
        audio_file = path

    r = sr.Recognizer()
    audio = sr.AudioFile(audio_file)

    with audio as source:
        r.adjust_for_ambient_noise(source)
        audio_data = r.record(source)

    return r.recognize_whisper(audio_data, model='large', show_dict=False, language='ru')



def recognize_video(path: str) -> str:
    return recognize_audio(extract_audio(path), 'wav')


def extract_audio(video_path: str) -> str:
    file = video_path.split('.')[0] + '.wav'
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(file)

    video.close()

    if os.path.exists(video_path):
        os.remove(video_path)

    return file

