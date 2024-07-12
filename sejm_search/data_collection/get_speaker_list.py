
from bs4 import BeautifulSoup
from typing import TypeAlias

BS: TypeAlias = BeautifulSoup


def create_soup_obj(html):
    return BeautifulSoup(html, 'html.parser')


def get_committees_from_transcript(soup: BS) -> BS:
    committee_tag = soup.find('h2', string='Komisje:')
    # Find the next list after the <h2> tag
    committe_list = committee_tag.find_next(['ul', 'ol'])
    committees = committe_list.contents # [<li>Komisja Etyki Poselskiej /nr 1/</li>]
    return committees


def get_speaker_list(soup: BS) -> list[str]:
    # Find the speakers list:
    speakers_tag = soup.find('h2', string='Mówcy:')
    speakers_list = speakers_tag.find_next(['ul', 'ol'])
    speakers = speakers_list.contents # [<li>Poseł Izabela Katarzyna Mrzygłocka /KO/</li>, <li>Poseł Jacek Świat /PiS/</li>, <li>Marszałek Sejmu Elżbieta Witek</li>]

    # Converting speaker names to str and cleaning them up
    clean_speaker_names = [clean_speaker_name_from_list(speaker.get_text()) for speaker in speakers]
    return clean_speaker_names


def clean_speaker_name_from_list(speaker_name: str) -> str:
    # Replacing /PartyName/ with (PartyName)
    # Removing whitespaces
    return (
        speaker_name.
        rstrip("\n").
        replace('/', '(', 1).replace('/', ')', 1).
        replace("\r", "")
    )

