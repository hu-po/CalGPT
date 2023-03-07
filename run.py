"""
    Use speech to describe calendar events and generate a .ical file, which you can import into Google Calendar.
"""

import logging
import os
import time
from datetime import datetime

import openai
import sounddevice as sd
from icalendar import Calendar, Event
from scipy.io.wavfile import write

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def speech_to_text(
    # Sampling frequency
    fs=44100, #4999
    channels=2,
    # Max recording duration
    max_record_sec=5,
    # Recording file buffer
    record_buffer_path="/tmp/calgpt_vocal_buffer.wav",
):
    # Record audio
    log.info(f"\n Recording Starting")
    time_start_recording = time.time()
    myrecording = sd.rec(int(max_record_sec * fs),
                         samplerate=fs, channels=channels)
    while time.time() - time_start_recording < max_record_sec:
        log.info(f"Recording: {time.time() - time_start_recording:.2f} seconds\r")
        # if input("\t\t Stop recording? (y/n) ") == "y":
        #     sd.stop()
        #     break
    log.debug(
        f"\n Recording Stopped, duration: {time.time() - time_start_recording:.2f} seconds")

    # Save as WAV file
    # TODO: Can this be avoided?
    time_start_filewrite = time.time()
    write(record_buffer_path, fs, myrecording)
    myrecording = open(record_buffer_path, "rb")
    log.debug(
        f"\n File write duration: {time.time() - time_start_filewrite:.2f} seconds")

    # Transcribe audio with OpenAI Whisper
    time_start_transcribe = time.time()
    transcript = openai.Audio.transcribe("whisper-1", myrecording)
    text = transcript["text"]
    log.debug(
        f"\n Transcription duration: {time.time() - time_start_transcribe:.2f} seconds")
    log.info(f"\n Transcript: \n\t{text}")

    return text


def text_to_calendar(
        # Text to convert to calendar
        text,
        # Path to .ics file
        calendar_ics_filepath="test.ics",
        # Which GPT model to use
        model="gpt-3.5-turbo"
):

    # API Request for In-Context Learning
    EXAMPLES = [
        (
            "I want to go to the dentist on March 8th, 2023 from 9am to 10:30am",
            "Dentist,datetime(2023,3,8,9,0,0),datetime(2023,3,8,10,30,0)"
        ),
        (
            "Today is March 6th, 2023. I want to workout on Tuesday from 2pm to 4pm. I also want to workout on Thursday from noon to 2pm.",
            "Workout.datetime(2023,3,7,14,0,0).datetime(2023,3,7,16,0,0)|Workout.datetime(2023,3,9,12,0,0).datetime(2023,3,9,14,0,0)"
        ),

    ]
    context = []
    for prompt, answer in EXAMPLES:
        context += [{"role": "user", "content": prompt},
                    {"role": "assistant", "content": answer}]

    # API Request for In-Context Learning
    openai.api_key = os.getenv("OPENAI_API_KEY")
    time_start_gptapi = time.time()
    log.info(f"\n GPT API Request Starting")
    _response = openai.ChatCompletion.create(
        model=model,
        messages=context + [
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0,
        n=1,
        max_tokens=200,
    )
    response: str = _response['choices'][0]['message']['content']
    log.debug(
        f"\n GPT API Request duration: {time.time() - time_start_gptapi:.2f} seconds")
    log.info(f"\n Response: \n\t{response}")

    # Convert response to .ics file
    time_start_ics_export = time.time()
    calendar = Calendar()
    for line in response.split("|"):
        text, start, end = line.split(".")
        event = Event()
        event.add('summary', text)
        # evaluate start string as python
        # TODO: This is security risk
        event.add('dtstart', eval(start))
        event.add('dtend', eval(end))
        calendar.add_component(event)
    with open(calendar_ics_filepath, 'wb') as f:
        f.write(calendar.to_ical())
    log.debug(
        f'\n .ics export duration: {time.time() - time_start_ics_export:.2f} seconds')
    log.info(f'Calendar exported to .ics file {calendar_ics_filepath}')


if __name__ == "__main__":

    text = speech_to_text()
    text_to_calendar(text)
