import json
import urllib.request


def get_all_video_in_channel(channel_id):
    api_key = ""

    base_video_url = "https://www.youtube.com/watch?v="
    base_search_url = "https://www.googleapis.com/youtube/v3/search?"

    first_url = (
        base_search_url
        + f"key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=25"
    )

    video_links = {}
    url = first_url
    while True:
        inp = urllib.request.urlopen(url, timeout=1)
        resp = json.load(inp)

        for i in resp["items"]:
            if i["id"]["kind"] == "youtube#video":
                print(i["snippet"]["title"])
                video_links[i["id"]["videoId"]] = {
                    "url": base_video_url + i["id"]["videoId"],
                    "title": i["snippet"]["title"],
                }

        next_page_token = resp["nextPageToken"]
        url = first_url + f"&pageToken={next_page_token}"
        return video_links


print(get_all_video_in_channel("UCzqu2LpKSFhvaS9n189xgAA"))
