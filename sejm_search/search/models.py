import json
from django.db import models
from data_collection.process_transcript import TranscriptProcessor

class Term(models.Model):
    number = models.IntegerField(unique=True, primary_key=True)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True)
    prints_count = models.IntegerField(null=False)
    prints_count_last_changed = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.number}. kadencja Sejmu RP ({self.start_date} - {self.end_date})"
    

class MP(models.Model):
    first_name = models.CharField(null=False, max_length=255, unique=False)
    second_name = models.CharField(null=True, max_length=255, unique=False)
    family_name = models.CharField(null=False, max_length=255, unique=False)
    #first_last_name = models.CharField(null=False, max_length=255, unique=False)
    birth_date = models.DateField(null=True)
    name = models.CharField(max_length=255, null=False, unique=False)

    # Overriding the save method to automatically create name based on first_name and second_name
    # API provides a firstLastName field but it often contains errors (inconsistent content for the same MP, middle names etc.)
    # name will be used for matching MPs with transcripts
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.first_and_family_name()
        super().save(*args, **kwargs)

    def first_and_family_name(self):
        return self.first_name + " " + self.family_name
    
    #club = models.CharField(max_length=255)
    #district_name = models.CharField(max_length=100, null=True)
    #education_level = models.CharField(max_length=100, null=True)
    #first_name = models.CharField(max_length=255, null=False)
    #last_name = models.CharField(max_length=255, null=False)
    #second_name = models.CharField(max_length=255, null=True)
    #number_of_votes = models.IntegerField()
    #profession = models.CharField(max_length=255)
    #voivodeship = models.CharField(max_length=100)
    #email = models.EmailField()
    #term = models.IntegerField()

#class Club(models.Model):
#    id = models.CharField(primary_key=True, max_length=20, null=False, unique=True) # we may have a problem with uniquness

#class ClubTermMP(models.Model):
#    mp = models.ForeignKey("MP", on_delete=models.CASCADE)
#    term = models.ForeignKey("Term", on_delete=models.CASCADE)
#    club = models.ForeignKey("Club", on_delete=models.CASCADE)


class TermMP(models.Model):
    term = models.ForeignKey("Term", on_delete=models.CASCADE)
    mp = models.ForeignKey("MP", on_delete=models.CASCADE)
    mp_term_id = models.IntegerField() # This field stores the specific ID given to the MP for that term

    class Meta:
        unique_together = ('mp_term_id', 'term', 'mp')


class PoliticalParty(models.Model):
    # what happens when an MP changes party?
    # what when a party changes its name?
    pass

class Committee(models.Model):
    name = models.CharField(max_length=255, unique=False)
    nameGenitive = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=False)
    scope = models.TextField(null=True)
    compositionDate = models.DateField(null=True)
    appointmentDate = models.DateField(null=True)
    phone = models.CharField(max_length=20, null=True)
    _type = models.CharField(max_length=20, null=True)
    term = models.ForeignKey("Term", on_delete=models.CASCADE)
    member_ids = models.JSONField(null=True)
    
    #COMMITTEE_TYPES = [
    #    ("STANDING", "stała"),
    #]

    def __str__(self):
        return self.name


class GuestSpeaker(models.Model):
    name = models.CharField(max_length=255, default="") # default to be changed?
    # They are linked with specific sittings via statements 


# Why it doesn't seem like a good idea to create char pks: https://stackoverflow.com/questions/52070462/django-generate-custom-id
class Sitting(models.Model):
    committee = models.ForeignKey("Committee", on_delete=models.CASCADE) # careful with the cascades
    term = models.ForeignKey("Term", on_delete=models.CASCADE) # not strictly necessary
    number = models.IntegerField()
    date = models.DateField()
    agenda = models.TextField() # already present in the json - has to be parsed
    closed = models.BooleanField()
    remote = models.BooleanField()
    jointWith = models.JSONField(default=list, null=True)
    # video? could be useful for users

    class Meta:
        unique_together = ('committee', 'term', 'number')
        indexes = [
            models.Index(fields = ['date'])
        ]


class LegislativeFile(models.Model):
    number = models.IntegerField(unique=False)
    term = models.ForeignKey("Term", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    # document_date
    # change_date


class Transcript(models.Model):
    sitting = models.OneToOneField("Sitting", on_delete=models.CASCADE)
    text = models.TextField() # Text or JSON?

    def get_structured_data_from_transcript(self):
        processor = TranscriptProcessor(self.text) # this self refers to the model
        return processor.get_structured_data_from_transcript()
    
    def get_speaker_list(self):
        processor = TranscriptProcessor(self.text)
        return processor.get_speaker_list()


class Statement(models.Model):
    '''
    Full statement by a single mp / guest divided into threads (paragraphs).
    '''
    speaker = models.ForeignKey("MP", on_delete=models.CASCADE, null=True)
    guest_speaker = models.ForeignKey("GuestSpeaker", on_delete=models.CASCADE, null=True)
    transcript = models.ForeignKey("Transcript", on_delete=models.CASCADE)
    #sitting = models.ForeignKey("Sitting", on_delete=models.CASCADE)
    #text = models.TextField()
    place_in_transcript = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['place_in_transcript'])
        ]


class Paragraph(models.Model):
    # matching based on the party affiliation encoded in the transcripts might be a solution...
    '''
    Single thread (paragraph) in a statement.
    '''
    statement = models.ForeignKey("Statement", on_delete=models.CASCADE)
    place_in_statement = models.IntegerField()
    speaker_mp = models.ForeignKey("MP", on_delete=models.CASCADE, null=True)
    speaker_guest = models.ForeignKey("GuestSpeaker", on_delete=models.CASCADE, null=True)
    sitting = models.ForeignKey("Sitting", on_delete=models.CASCADE)
    committee = models.ForeignKey("Committee", on_delete=models.CASCADE)
    term = models.ForeignKey("Term", on_delete=models.CASCADE)
    
    text = models.TextField()
    dense_vector = models.JSONField(null=True)
    
    class Meta:
        indexes = [
            models.Index(fields = ['place_in_statement']),
            models.Index(fields = ['statement']),
            models.Index(fields = ['speaker_mp']),
            models.Index(fields = ['committee']),
        ]

    @property
    def prepare_dense_vector(self):
        vector_data = json.loads(self.dense_vector)
        print(vector_data)
        if isinstance(vector_data, list) and len(vector_data) == 768:
            return [float(v) for v in vector_data]
        return [0.0] * 768


class CommitteeTermMP(models.Model):
    committee = models.ForeignKey("Committee", on_delete=models.CASCADE)
    term = models.ForeignKey("Term", on_delete=models.CASCADE)
    mp = models.ForeignKey("MP", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('committee', 'term', 'mp')
