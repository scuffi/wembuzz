import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin

from models import Event
from .venue import Venue

WEBSITE_URL = "https://www.wembleystadium.com/events"


class Stadium(Venue):
    def __init__(self):
        super().__init__("Wembley Stadium")

    def get_events(self) -> list[Event]:
        """
        Parse the entire listing page HTML and return all events.
        Targets the outer item divs that wrap each card.
        """
        soup = BeautifulSoup(self.get_page_content(), "html.parser")
        items = soup.select(".fa-filter-content__item .fa-content-promo")
        events: list[Event] = []
        for card in items:
            try:
                events.append(self._parse_event_card(card))
            except Exception:
                continue

        return events

    def get_page_content(self) -> str:
        return requests.get(WEBSITE_URL).text

    def _norm_url(self, url: str | None, base: str = WEBSITE_URL) -> str | None:
        if not url:
            return None
        # handle protocol-relative URLs like //ticketing.wembleystadium.com/...
        if url.startswith("//"):
            return "https:" + url
        return urljoin(base, url)

    def _extract_best_image(self, picture_tag) -> str | None:
        """Pick the first non-empty src from <source srcset> or fallback to <img src>."""
        if not picture_tag:
            return None
        # Try <source> srcset first
        for src in picture_tag.find_all("source"):
            srcset = (src.get("srcset") or "").strip()
            if srcset:
                # srcset may contain multiple entries; take the first URL
                return self._norm_url(srcset.split()[0])
        # Fallback to <img>
        img = picture_tag.find("img")
        if img and img.get("src"):
            return self._norm_url(img["src"])
        return None

    def _parse_datetime(
        self, date_text: str | None, time_text: str | None
    ) -> str | None:
        """Return GMT timezone ISO string for display/storage."""
        if not date_text:
            return None
        date_text = date_text.strip()
        if not time_text or time_text.strip().lower() == "tbc":
            # Date only
            try:
                d = datetime.strptime(date_text, "%d %b %Y").date()
                dt = datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc)
                return dt.isoformat()
            except ValueError:
                return None
        # Date + time
        try:
            dt = datetime.strptime(f"{date_text} {time_text.strip()}", "%d %b %Y %H:%M")
            dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            return None

    def _parse_event_card(self, card: Tag) -> Event:
        """
        Parse a single event card <div class="fa-content-promo ..."> container.
        Works against the exact structure you posted.
        """
        # Image
        picture = card.select_one("picture.responsive-image")
        image_url = self._extract_best_image(picture)

        # Title & description
        title_tag = card.find(["h2", "h3"])
        title = title_tag.get_text(strip=True) if title_tag else ""

        desc_tag = card.find("p")
        description = desc_tag.get_text(strip=True) if desc_tag else None

        # Date & time (two spans with class small-text)
        smalls = [s.get_text(strip=True) for s in card.select(".small-text")]
        date_text = smalls[0] if smalls else None
        time_text = smalls[1] if len(smalls) > 1 else None
        start_local_iso = self._parse_datetime(date_text, time_text)

        # Info URL: the “Find Out More” link inside content promo
        info_a = card.select_one(
            "a.fa-content-promo__block-link, a.cta.cta--alt.cta--primary.cta--primary-btn.cta-align-left"
        )
        info_url = self._norm_url(info_a.get("href")) if info_a else None

        return Event(
            name=title,
            description=description,
            start_date=start_local_iso,
            end_date=start_local_iso,
            url=info_url,
            image_url=image_url,
            status="scheduled",
            venue=self.name,
        )
