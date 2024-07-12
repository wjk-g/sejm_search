# Development plan

## Motivation and key functionalities

- The key functionality is to make the transcripts of committee sessions searchable. Potential benefits: 
    - enable engaged citizens to gain a better understanding of the legislative process and track the work of their representatives
    - enable journalists to track the work of Sejm
    - enable the third sector to track who participates in important policy debates and what arguments are raised during discussion

Nice to have functionalities:
    - tracking voting patterns - searching for contentious issues
    - linking committee sessions with concrete legislative outcomes (votes during plenary sessions)

## Data management

I will have to keep my data both in the elasticsearch index and in a traditional PostgreSQL database and update the ES index in batches (e.g. once a month).

## Views

### Home page view

Basic description of the application
Search field ==> Search committee transcripts for a particular phrase.

_Search sends the user to the Search view_

### Search view

Search based on keywords
Vector search - show similar discussions - documents vectorized based on the PAN embeddings / huggingface embeddings
Show on a timeline ==> show top results on a timeline to create a narrative; here there's potential to use htmx for filtering
Each utterance should be linked to a representative
Search with filters ==> party / representative

### Search results view

- responses presented on a timeline ==> link to full transcript for each response
- heat gauge for each utterance + heat graph / mean for each sitting / session
- export options (json; excel)

## Elastic Search tutorial 

Search tutorial: https://www.elastic.co/search-labs/tutorials/search-tutorial/welcome
Examples: https://www.elastic.co/search-labs/tutorials/examples
Embeddings for the Polish language: https://huggingface.co/models?library=sentence-transformers&sort=trending&search=polish
