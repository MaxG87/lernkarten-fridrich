# Generate Lernkarten for Rubik's Cube - Fridrich Method

This project provides Lernkarten (learning cards) for memorizing the algorithms
needed to solve a Rubik's Cube using the Fridrich Method (CFOP). Two kinds of
cards are provided:

* Anki flashcards for spaced repetition learning
* physical printable cards for offline study

The icons will be generated from provided algorithms, so that the icons are
guaranteed to match the algorithms exactly.

All SVGs, CSVs and PDFs are easily regenerable using the provided scripts.
However, they are added here so that users can directly use them without
getting into technical details.

## Using the Lernkarten

### Anki Flashcards

Each flashcard folder contains icons and a file `ankiCardSet.csv`. In order to import them
into Anki, follow these steps:

* copy the SVG files into Anki's media collection folder (see
  [here](https://superuser.com/q/963526/913769) for how to find it)
* import the `ankiCardSet.csv` file using Anki's import function

Now you should see the cards in your Anki collection.

### Physical Printable Cards

The printable cards are provided as PDF files. They are designed to be printed
two-sided. Then the algorithms will be on the back of the corresponding icons.

The PDFs are designed to be cuttable in batches, allowing for more convenient
preparation.

## Regenerating the Lernkarten

## Acknowledgements

I want to thank Andy Klise of https://www.kungfoomanchu.com/ for providing
excellent guides. Without these I wouldn't have started learning the
Fridrich Method in the first place.

Another great source of algorithms was Feliks Zemdegs project
https://www.cubeskills.com/. The provided algorithms there allowed me to fine
tune the algorithms used in this project.

While there are some cube visualization tools available online, none of them
match the brilliance of https://visualcube.api.cubing.net. It is feature-rich,
scriptable and produces impressive icons.

Last but not least I want to thank the anonymous contributor of Anki cubing
flashcards found [here](https://ankiweb.net/shared/by-author/916788332).
They were a great starting point for creating my own Anki cards.
