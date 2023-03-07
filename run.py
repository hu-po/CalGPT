"""
    Use speech to describe calendar events and generate a .ical file, which you can import into Google Calendar.
"""

import os
import openai
from icalendar import Calendar, Event
from datetime import datetime
import sounddevice as sd
from scipy.io.wavfile import write


fs = 44100  # this is the frequency sampling; also: 4999, 64000
seconds = 9  # Duration of recording
myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
print(f"Speak now! Recording for {seconds}")
sd.wait()
print("finished")
# Save as WAV file
write('/tmp/calgpt_vocal_buffer.wav', fs, myrecording)  
myrecording = open("/tmp/calgpt_vocal_buffer.wav", "rb")
transcript = openai.Audio.transcribe("whisper-1", myrecording)
user_prompt = transcript["text"]
# user_prompt = "Today is March 7th, 2023. This Friday I want to eat Sushi from 7pm to 8pm"
print(f"Transcript: {user_prompt}")

# API Request for In-Context Learning
examples = [
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
for prompt, answer in examples:
    context += [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]

# API Request for In-Context Learning
openai.api_key = os.getenv("OPENAI_API_KEY")
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages= context + [
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
    temperature=0,
    n=1,
    max_tokens=100,
)
print(response)

calendar = Calendar()
for line in response['choices'][0]['message']['content'].split("|"):
    text, start, end = line.split(".")
    event = Event()
    event.add('summary', text)
    # evaluate start string as python
    # TODO: This is security risk
    event.add('dtstart', eval(start))
    event.add('dtend', eval(end))
    calendar.add_component(event)

with open('test.ics', 'wb') as f:
    f.write(calendar.to_ical())