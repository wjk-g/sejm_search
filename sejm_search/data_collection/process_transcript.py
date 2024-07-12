
from bs4 import BeautifulSoup
from string import ascii_letters
import re

class TranscriptProcessor():
    def __init__(self, html):
        self.html = html
        self.soup = self.create_soup_obj()
        self.transcript_section = self.get_transcript_as_text()
        self.speakers = self.get_speaker_list()

    def __repr__(self):
        print(f"Transcript of ... ")


    def create_soup_obj(self):
        return BeautifulSoup(self.html, 'html.parser')

    def get_transcript_as_text(self):
        transcript_section = self.soup.find('section', class_='transcript')
        return str(transcript_section)

    def convert_soup_to_text(self):
        return str(self.soup)
    
    def split_transcript_on_p_tags(self):
        return self.transcript_section.split("<p>")

    @staticmethod
    def fits_speaker_pattern(text_chunk: str) -> bool:
        # Conditions
        starts_with_b_tag = text_chunk.startswith("<b>")
        starts_with_dash = text_chunk.startswith("<b>–")
        starts_with_short_dash = text_chunk.startswith("<b>-")
        starts_with_num_plus_parenthesis = any(text_chunk.startswith(f"<b>{i})") for i in range(1, 100))
        # 4th char is a letter and 5th symbol is ")"
        starts_with_letter_plus_parenthesis = len(text_chunk) > 4 and text_chunk[3] in ascii_letters and text_chunk[4] == ')'
        
        if not starts_with_b_tag:
            return False
        
        meets_all_conditions = (
            not starts_with_dash
            and not starts_with_short_dash
            and not starts_with_num_plus_parenthesis
            and not starts_with_letter_plus_parenthesis
        )

        return meets_all_conditions

    @staticmethod
    def split_text_chunk(text_chunk: str) -> list[str]:
        return text_chunk.split('<br')

    @staticmethod
    def get_speaker_name_and_rest(text_chunk: str):
        pattern1 = '<b>.*?<\/b>&nbsp;<b>.*?<\/b>'
        pattern2 = '<b>.*?</b>'
        break_point = '<br/>'
        match1 = re.search(pattern1, text_chunk)
        match2 = re.search(pattern2, text_chunk)
        if match1:
            speaker_name_dirty = match1.group(0)
        elif match2:
            speaker_name_dirty = match2.group(0)
        else:
            if break_point in text_chunk:
            # TODO Works for some really badly formatted text -- very rare
                speaker_name_dirty = text_chunk.split(break_point, 1)[0]
            else:
                speaker_name_dirty = ""
            
        
        # In some cases there's nothing following the breakpoint
        
        try:
            remaining_text = text_chunk.split(break_point, 1)[1]
        except IndexError as e:
            print(e)
            print(f"Error occured for chunk: {text_chunk}")
            remaining_text = ""
            #<p><b>Prezes zarządu PGNiG SA Grażyna Piotrowska-Oliwa:</b>
            #<p>(<i>wypowiedź poza mikrofonem</i>)
        
        if speaker_name_dirty:
            return speaker_name_dirty, remaining_text
        return "", remaining_text

    @staticmethod
    def clean_utterance(utterance):
        return (
            utterance.replace("<br/>", "").
            replace("\r", "").
            replace("\n", "").
            replace("\r\n", "").
            replace("</p>", "").
            replace("</section>", "").
            replace("\xa0", "").
            replace("<b>", "").
            replace("</b>", "").
            replace("<i></i>", "").
            replace("<i>", "").
            replace("</i>", "").
            strip()
        )
        

    @staticmethod
    def clean_speaker_name(speaker_name_dirty: str) -> str:
        # Clean like you would any other utterance
        name_clean = TranscriptProcessor.clean_utterance(speaker_name_dirty)
        # And do some name specific cleaning
        return (
            name_clean.replace(":", "").
            replace("&nbsp;", " ")
        )


    def is_in_speaker_list(self, speaker_name):
        return speaker_name in self.speakers

    @staticmethod
    def remove_until_first_speaker(lst):
        while lst and not lst[0][0]:
            lst.pop(0)
        return lst


    def separate_speakers_and_statements(self):

        transcript_split = self.split_transcript_on_p_tags()
        soup = self.create_soup_obj()
        speakers = self.get_speaker_list()
        
        transcript_processed = []

        for text_chunk in transcript_split:
            if self.fits_speaker_pattern(text_chunk):
                speaker_name_dirty, remaining_text = self.get_speaker_name_and_rest(text_chunk)
                if speaker_name_dirty:
                    speaker_name_clean = self.clean_speaker_name(speaker_name_dirty)
                    if self.is_in_speaker_list(speaker_name_clean):
                        transcript_processed.append((True, speaker_name_clean))
                        clean_chunk = self.clean_utterance(remaining_text)
                        transcript_processed.append((False, clean_chunk))
            else:
                clean_chunk = self.clean_utterance(text_chunk)
                transcript_processed.append((False, clean_chunk))
        
        transcript_processed = self.remove_until_first_speaker(transcript_processed)
        
        return transcript_processed
    
    # GET STRUCTURED DATA
    def get_structured_data_from_transcript(self):

        transcript_processed = self.separate_speakers_and_statements()
        data = []
        statement = {}

        for is_speaker, text_chunk in transcript_processed:
            
            if is_speaker:
                try:
                    if statement:
                        data.append(statement)
                except NameError as e:
                    print(e)
                statement = {}
                statement["speaker"] = text_chunk
                statement["utterances"] = []
            else:
                if text_chunk != "":
                    try:
                        statement["utterances"].append(text_chunk)
                    except NameError as e:
                        print(e)

        #Append last statement
        data.append({
            "speaker": statement.get("speaker", "error"),
            "utterances": statement.get("utterances", "error"),
        })

        return data 
    
    # GET SPEAKERS AND COMMITTEES
    def get_committees_from_transcript(self):
        committee_tag = self.soup.find('h2', string='Komisje:')
        # Find the next list after the <h2> tag
        committe_list = committee_tag.find_next(['ul', 'ol'])
        committees = committe_list.contents # [<li>Komisja Etyki Poselskiej /nr 1/</li>]
        return committees
    

    def get_speaker_list(self):
        # Find the speakers list:
        speakers_tag = self.soup.find('h2', string='Mówcy:')
        speakers_list = speakers_tag.find_next(['ul', 'ol'])
        speakers = speakers_list.contents # [<li>Poseł Izabela Katarzyna Mrzygłocka /KO/</li>, <li>Poseł Jacek Świat /PiS/</li>, <li>Marszałek Sejmu Elżbieta Witek</li>]

        # Converting speaker names to str and cleaning them up
        clean_speaker_names = [self.clean_speaker_name_from_list(speaker.get_text()) for speaker in speakers]
        return clean_speaker_names

    @staticmethod
    def clean_speaker_name_from_list(speaker_name: str) -> str:
        # Replacing /PartyName/ with (PartyName)
        # Removing whitespaces
        return (
            speaker_name.
            rstrip("\n").
            replace('/', '(', 1).replace('/', ')', 1).
            replace("\r", "")
        )

