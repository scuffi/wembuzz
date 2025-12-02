from openai import OpenAI
from models import Event
from settings import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_key,
)


def estimate_crowding(event: Event) -> float:
    completion = client.chat.completions.create(
        model="google/gemma-3-27b-it:free",
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": "You are an expert at estimating event crowding levels. Your task is to analyze events and estimate how crowded they will be on a scale of 1-5, where 1 is average event attendance and 5 is extremely crowded/sold out. Consider factors such as: the event's popularity and appeal, the venue's typical capacity and popularity, the type of event, timing, and historical context. Provide both a numerical rating (1-5) and a clear justification for your estimate.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Please estimate the expected crowding level for this event:

Event Name: {event.name}
Venue: {event.venue}
Description: {event.description}
Start Date: {event.start_date}
End Date: {event.end_date}
Status: {event.status}
Event URL: {event.url}

Venue capacities:
- OVO Arena capacity: 12,500
- Wembley Stadium capacity: 90,000

Based on the event details and the image provided, estimate how crowded this event will be on a scale of 1-5, considering:
- The popularity and appeal of this specific event
- The venue's typical capacity and how popular events at {event.venue}, Wembley, London, UK, usually get
- The type of event and its target audience
- Timing factors (day of week, time of year, etc.)

Assume that any given event will be at least crowded, so a low estimate does not mean the event will be empty, it just means the event will be less crowded than average.
Smaller venues will generally be less crowded than larger venues, so a rating of 1 for OVO Arena is more likely than a rating of 1 for Wembley Stadium.
A 'full' event at a smaller venue (~12.5k attendees) is likely to be around 3/5, a 'full' event at a larger venue (~90k attendees) is likely to be around 5/5.

Please respond with:
1. A integer value rating from 1-5 (where 1 = crowded, 5 = extremely crowded/sold out)
2. A clear justification explaining your reasoning

Format your response as: "Rating: X/5\n\nJustification: [your explanation and estimated footfall]"
""",
                    },
                ],
            },
        ],
    )
    return int(
        completion.choices[0].message.content.split("Rating: ")[1].split("/5")[0]
    )
