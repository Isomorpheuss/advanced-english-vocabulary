# Goals

The goal of this project is to produce a wordlist of advanced English vocabulary which is _less_ arbitrary. The idea is to take wordlists from several sources (GRE prep, SAT prep, Improve-your-vocab books, etc), look at intersections of the lists, and check word frequencies to gauge real-world usage. The latter task is difficult because of inflections and derived words.

# If you just want to look at the lists

Outputs are found in the output folder. Every file is sorted from most frequent word to least frequent word. Each list has a text file with just the words, and a CSV file with the word, Zipf frequency, and number of intersections.

# Inflections and Derived Words

Here is my strategy for dealing with inflections and derived words. Use an extensive English wordlist like the one found here https://github.com/dwyl/english-words. Lookup every word in the union of my vocab wordlists using the English wordlist. Look at a small neighborhood around the word (say, 10 above and below). Then use a stemming algorithm on every one of those 21 words, and compare the 20 stems to the 1 target stem. Every matching stem is considered a derived word or an inflection. Then look up the word frequencies of each of these derived words or inflections, take the sum, take the Zipf, and consider that as the frequency of the "word". Choose the derived word or inflection with the maximum frequency among the group as the representative word for that group.

This doesn't yet address prefixes. Stemming/lemmatization for English typically doesn't deal with prefixes, and clearly prefixed words wouldn't be near in the dictionary so this approach wouldn't work anyway. Keep a list of common prefixes. For each valid derived word or inflection for a given target word, try adding a prefix to that word and checking if it's in the English wordlist. If so, add it as a derived word or inflection, find the frequency, etc as above. In this case, don't use any prefixed words as representatives since they may conflict with other words. Do use them to calculate the frequency.

# Limitations

This approach is limited in some ways.

## Several POS

This doesn't account for part-of-speech. Words with multiple POS with different definitions will have inaccurate frequencies.

Words such as: appropriate, alloy, concert, pinch, badger, base, etc

The most frequent inflection for "quixotic" is given as "quixote". This is probably because of the proper noun "Don Quixote" inflating the numbers for "quixote".

## Words Separated by Spaces

This doesn't account for phrases like "de facto". If the first field in the CSV has multiple words, it just grabs the first word. For this, among other, reasons in the final list I chop off the top x words of highest frequency to filter the junk words.

## Imprecisions with stemming, prefixing

Stemming algorithms aren't perfect. Sometimes words have the same stem (algorithmically) but aren't related. Sometimes words are related but have different stems (algorithmically). Sometimes prefixing a word results in a different word entirely: sect, intersect, trisect.

## Special characters don't work

blasé, cliché

# Checking the work

If you want to see what inflection or derived words were associated with what stem, check the "stemdict.txt" file.
