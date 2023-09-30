import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_utils import enrich_match
from dotenv import load_dotenv
from extra import chatgpt
from helpers import GAMETYPE

load_dotenv("../../.env")

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


with open(f"{__location__}/matches.json", "r") as f:
    data = json.load(f)


def test_blah():
    pass


enriched_match = enrich_match(data[0], GAMETYPE.REGULARSEASON)

summary = chatgpt.write_gpt_summary(enriched_match)
print(summary)
# print(json.dumps(enriched_match, indent=4, sort_keys=True))
