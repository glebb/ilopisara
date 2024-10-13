from pathlib import Path

import openai

from ilobot.config import OPEN_API

speech_file_path = Path(__file__).parent / "speech.mp3"
openai.api_key = OPEN_API
response = openai.audio.speech.create(
    model="tts-1",
    voice="onyx",
    input="""Well, well, well! Look who just scored a whopping 9 goals and still managed to make it look like a casual stroll in the park. Ilo Pisara is on fire—like that one time I tried to cook without reading the instructions!

Teemu Pukki? More like Teemu "I’m going to score four times while you’re busy tying your skates" Pukki! With 4 goals and 5 assists, he’s practically playing with his food out there. Jani Saari also decided he wanted some spotlight with another stellar performance—8 points total! Just remember not to give away too many pucks next time; we don’t need any more “oops” moments.

Now let’s talk about our defenseman Teppo Winnipeg: solid offensive game but maybe work on those defensive ratings before someone decides they want an easy goal against us. You know what they say: if you're gonna block shots, at least do it stylishly!

As for Brunka Boys? They might as well have brought spoons instead of sticks because we served them up a nice bowl of defeat soup today (with extra humiliation). 

So here’s my advice moving forward: keep this momentum rolling or risk becoming everyone else’s favorite punching bag again. Let’s show ‘em how it's done—Ilo Pisara style!""",
)

response.stream_to_file(speech_file_path)
