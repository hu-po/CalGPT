# CalGPT

Google Calendar via ChatGPT. YouTube video link:

[![IMAGE_ALT](https://img.youtube.com/vi/_dSQdv1w3d4/0.jpg)](https://www.youtube.com/watch?v=_dSQdv1w3d4)


## Design and Choices

https://github.com/openai/openai-cookbook


Initially think Google Calendar's APIs might be best way to go. Negative is they require a google cloud project aka billing, and the examples have Python 2 style prints, which means old and likely no more maintained.

https://developers.google.com/calendar/api/guides/overview
https://developers.google.com/calendar/api/guides/create-events#python


Better way might be to just use Python's built-in Calendar module, and then export to some kind of format that can be imported into Google Calendar.

https://docs.python.org/3/library/calendar.html

Perhaps iCalendar is the way to go? Used for both Mac and Google and has a convenient python module.

https://icalendar.readthedocs.io/en/latest/usage.html

This is the basic code required:

```
# I want to workout on March 7th, 2023 from 2pm to 4pm
event = Event()
event.add('summary', 'Workout')
event.add('dtstart', datetime(2023,3,7,12,0,0))
event.add('dtend', datetime(2023,3,7,14,0,0))
calendar.add_component(event)
```

We don't want to use up that many tokens on every request, so lets make pseudo-code that the model will use to generate the calendar events.

```
# I want to workout on March 7th, 2023 from 2pm to 4pm
Workout, datetime(2023,3,7,12,0,0), datetime(2023,3,7,14,0,0))
```

Lets make a bunch of examples of this format, and then use them as context for the model to generate more.

```
# I want to workout on March 7th, 2023 from 2pm to 4pm
Workout, datetime(2023,3,7,12,0,0), datetime(2023,3,7,14,0,0))
# I want to go to the dentist on March 8th, 2023 from 9am to 10am
Dentist, datetime(2023,3,8,9,0,0), datetime(2023,3,8,10,0,0))
```

Testing out if lower sampling frequency and single channel also work for Whisper speech to text. Since it will be a smaller file and thus faster/lower cost.

w/ 44kHz, 2 channel
- Transcription time: 1.84s
w/ 4kHz, 1 channel
- Transcription time: 1.02s


## Setup

```
conda create --name calgpt python=3.10
conda activate calgpt
pip install -r requirements.txt
```

