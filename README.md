[![Build Status](https://github.com/seatgeek/thefuzz/actions/workflows/ci.yml/badge.svg)](https://github.com/seatgeek/thefuzz)

# TheFuzz

Fuzzy string matching like a boss. It uses [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance) to calculate the differences between sequences in a simple-to-use package.

## Requirements

- Python 3.8 or higher
- [rapidfuzz](https://github.com/maxbachmann/RapidFuzz/)

### For testing

- pycodestyle
- hypothesis
- pytest

## Installation

### Using pip via PyPI

```bash
pip install thefuzz
```

### Using pip via GitHub

```bash
pip install git+git://github.com/seatgeek/thefuzz.git@0.19.0#egg=thefuzz
```

### Adding to your `requirements.txt` file (run `pip install -r requirements.txt` afterwards)

```bash
git+ssh://git@github.com/seatgeek/thefuzz.git@0.19.0#egg=thefuzz
```

### Manually via GIT

```bash
git clone git://github.com/seatgeek/thefuzz.git thefuzz
cd thefuzz
python setup.py install
```

## Usage

<details>
<summary>Basic String Matching Functions</summary>

# Basic String Matching Functions

These functions return a similarity score between two strings as an integer between 0 and 100, where 100 is a perfect match.

### Parameters for Ratio Functions

- **s1: str** – First string to compare
- **s2: str** – Second string to compare
- **force_ascii: bool** – If True, only ASCII characters are allowed (non-ASCII are removed)
- **full_process: bool** – If True, preprocess both strings before comparison (lowercasing, trimming, etc.)

### ratio

A straightforward similarity measure that compares two processed strings.

```python
>>> fuzz.ratio("Hello", "hello")
100
```

### partial_ratio

Finds the most similar substring in `s2` that matches a portion of `s1`.

```python
>>> fuzz.partial_ratio("Hello World", "Hello")
100
```

### QRatio (Quick Ratio)

A fast ratio that includes processing by default. Respects `force_ascii` and `full_process`:

```python
>>> fuzz.QRatio("this is a test", "THIS IS A TEST", force_ascii=True, full_process=True)
100

>>> fuzz.QRatio("this is a test", "THIS IS A TEST", force_ascii=False, full_process=False)
73
```

### WRatio (Weighted Ratio)

A more complex ratio that considers length differences and token-based comparisons:

```python
>>> fuzz.WRatio("this is a test", "THIS IS A TEST", force_ascii=True, full_process=True)
100
```

### UQRatio (Unicode Quick Ratio)

Same as QRatio but preserves unicode characters (no ASCII forcing):

```python
>>> fuzz.UQRatio("Hello こんにちは", "HELLO こんにちは")
100
```

### UWRatio (Unicode Weighted Ratio)

Same as WRatio but preserves unicode characters:

```python
>>> fuzz.UWRatio("Hello こんにちは", "HELLO こんにちは")
100
```
</details>

---
<details>
<summary>Token-Based Functions</summary>

# Token-Based Functions

Token-based functions split the strings into word tokens, and then compare sets or sorted lists of these tokens for more flexible matching.

### token_set_ratio

Finds common tokens in both strings and compares them:

```python
>>> fuzz.token_set_ratio("fuzzy was a bear", "fuzzy fuzzy was a bear", force_ascii=True, full_process=True)
100
```

### token_sort_ratio

Sorts the tokens alphabetically before comparing, compensating for unordered sequences:

```python
>>> fuzz.token_sort_ratio("fuzzy was a bear", "fuzzy fuzzy was a bear", force_ascii=True, full_process=True)
84
```

### partial_token_set_ratio

Partial matching using token sets:

```python
>>> fuzz.partial_token_set_ratio("test string", "test", force_ascii=True, full_process=True)
# returns an int score

>>> fuzz.partial_token_set_ratio("test string", "test", force_ascii=False, full_process=False)
# returns an int score
```

### partial_token_sort_ratio

Partial matching after sorting tokens:

```python
>>> fuzz.partial_token_sort_ratio("test string", "string test", force_ascii=True, full_process=True)
# returns an int score

>>> fuzz.partial_token_sort_ratio("test string", "string test", force_ascii=False, full_process=False)
# returns an int score
```
</details>

---
<details>
<summary>The `process` Module</summary>

# The `process` Module

The `process` module provides functions to search through a collection of choices and retrieve the best matches to a given query. It supports custom scorers and processors, lists or dictionary inputs, and score thresholds.

### Parameters for Process Functions

- **query: str** – The search query.
- **choices: Union[List[str], Dict[Any, str]]** – The collection to search. If a dictionary, keys are returned with matches.
- **processor: Optional[Callable[[str], str]]** – Custom function to process choices before matching.
- **scorer: Callable[[str, str], float]** – Function used to score matches (default: `fuzz.WRatio`).
- **limit: Optional[int]** – Maximum number of matches to return.
- **score_cutoff: Optional[float]** – Minimum score required for a match to be returned.

### extractWithoutOrder

Returns a generator of matches without sorting them by score, useful when you just want to iterate:

```python
>>> choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
>>> list(process.extractWithoutOrder("new york jets", choices, score_cutoff=50))
[('New York Jets', 100), ('New York Giants', 78)]

# With all parameters:
>>> list(process.extractWithoutOrder("query", choices,
...     processor=lambda x: x.lower(),
...     scorer=fuzz.ratio,
...     score_cutoff=50))
```

### extractBests

Similar to `extract()` but takes a `score_cutoff` and returns a sorted list of the best results:

```python
>>> process.extractBests("new york jets", choices, score_cutoff=80, limit=2)
[('New York Jets', 100)]
```

### extract

Similar to `extractBests` but defaults to returning the top 5 matches (or another limit):

```python
>>> process.extract("new york jets", choices, 
...     processor=lambda x: x.lower(),
...     scorer=fuzz.ratio,
...     limit=2)
[('New York Jets', 100), ('New York Giants', 78)]
```
### extractOne

Returns only the single best match above a certain score cutoff:

```python
>>> choices_dict = {"a": "Atlanta Falcons", "b": "New York Jets"}
>>> process.extractOne("new york jets", choices_dict)
("New York Jets", 100, "b")
```

**Example Using File Paths:**

You can specify a scorer to handle special cases, such as matching file paths:

```python
>>> songs = [
...   "/music/library/good/System of a Down/2005 - Hypnotize/01 - Attack.mp3",
...   "/music/library/good/System of a Down/2005 - Hypnotize/10 - She's Like Heroin.mp3"
... ]
>>> process.extractOne("System of a down - Hypnotize - Heroin", songs)
('/music/library/good/System of a Down/2005 - Hypnotize/01 - Attack.mp3', 86)
>>> process.extractOne("System of a down - Hypnotize - Heroin", songs, scorer=fuzz.token_sort_ratio)
("/music/library/good/System of a Down/2005 - Hypnotize/10 - She's Like Heroin.mp3", 61)
```

### dedupe

Removes duplicates from a list by grouping fuzzy matches above a certain threshold and returning a representative item (longest string, then alphabetical):

```python
>>> contains_dupes = ['Frodo Baggin', 'Frodo Baggins', 'F. Baggins', 'Samwise G.', 'Gandalf']
>>> process.dedupe(contains_dupes, threshold=70)
['Frodo Baggins', 'Samwise G.', 'Gandalf']
```

To use a custom scorer for deduping:

```python
>>> process.dedupe(contains_dupes, threshold=70, scorer=fuzz.token_set_ratio)
# Returns deduped list
```
</details>

---

<details>
<summary>The `utils` Module</summary>

# The `utils` Module

The `utils` module provides functions for preprocessing and normalizing strings.

### Parameters for `utils.full_process`

- **s: str** – The input string.
- **force_ascii: bool** – If True, remove non-ASCII characters.

### Examples

```python
>>> utils.full_process("Hello こんにちは", force_ascii=True)
'hello'

>>> utils.full_process("Hello こんにちは", force_ascii=False)
'hello こんにちは'

>>> utils.ascii_only("Hello こんにちは")
'Hello '
```
</details>

---

<details>
<summary>Putting It All Together</summary>

# Putting It All Together

To perform a fuzzy match with custom parameters, consider:

```python
query = "Hello World"
choices = ["hello world", "Hello, Earth", "Helloworld"]

# Using a custom processor and scorer
best_matches = process.extract(
    query,
    choices,
    processor=lambda x: x.lower(),
    scorer=fuzz.ratio,
    limit=3
)
print(best_matches)
```
</details>

---

<details>
<summary>Glossary of Common TheFuzz Parameters</summary>

## Glossary of Common TheFuzz Parameters:

1. **force_ascii (bool)**  
   Whether to remove non-ASCII characters from the input strings before scoring.  
   - `True`: Only ASCII characters are retained; all others are stripped.  
   - `False`: Preserves Unicode characters.  
   
   This parameter ensures uniformity when comparing strings with different character sets, or can help with performance and consistency if you know that all data should be ASCII.

2. **full_process (bool)**  
   Determines whether the input strings are fully processed before scoring. This typically involves lowercasing, trimming whitespace, and removing non-alphanumeric characters.  
   - `True`: Applies a thorough preprocessing step to clean and normalize the strings before comparison.  
   - `False`: Uses the strings as-is (or with minimal processing).

   This helps ensure a fair comparison, ignoring differences in case, punctuation, or extraneous whitespace.

3. **choices (List[str] or Dict[Any, str])**  
   The collection of items you are searching through.  
   - If a list, each element is a string choice to match against.  
   - If a dictionary, keys map to string values. The matching occurs against the values, and the key is returned alongside the value and score.

   Allows flexible input formats for searching.

4. **processor (Callable[[str], str])**  
   A custom function that transforms each choice before matching.  
   - By default, `full_process` is used.  
   - You can provide a lambda or function to standardize, clean, or extract a particular part of each choice.

   Useful for applying specialized preprocessing logic beyond the default normalization.

5. **scorer (Callable[[str, str], float])**  
   The function used to calculate the similarity score between two strings.  
   - Defaults often rely on `fuzz.WRatio`.  
   - Can be replaced with other scorers like `fuzz.ratio` or your own custom function.

   This parameter allows you to control how “closeness” or “similarity” is measured.

6. **score_cutoff (float)**  
   The minimum score required for a match to be considered valid.  
   - If set to a certain value (e.g., 75), only matches scoring that high or higher are returned.  
   
   Helps filter out weak matches and focus only on those above a certain similarity threshold.

7. **query (str)**  
   The string or term you are searching for within the set of choices.  
   - This is the user input or reference string you want to find closest matches to.

   The main input that guides the search through your choices.

8. **limit (int or None)**  
   The maximum number of matches to return.  
   - If set to `5`, only the top 5 matches are returned.  
   - If `None`, it may return all matches that meet the criteria, depending on the function.

   Useful for limiting results to the best matches rather than receiving a large list.

9. **procprocessor (Optional[Callable[[str], str]])**  
   This is a parameter occasionally referenced in type hints (e.g., in `extractOne`), meant to denote a typo or variant of `processor`. It functions similarly to `processor`, transforming the query or choices before scoring. If present, treat it like `processor`.

   Generally, you can consider `processor` and `procprocessor` the same type of parameter, used to define custom string preprocessing functions. (In the official library, you’d normally just see `processor`.)

**Other Parameters (Contextual):**  
- **threshold (float)**: Used in functions like `dedupe` to determine the similarity score at which items are considered duplicates.  
- **scorer (Callable[[str, str], float])**: Already defined above, but worth emphasizing that different scorers define different ways of calculating similarity.  
- **Any additional custom parameters in utility or process functions** are often related to controlling their behavior, such as whether to return certain types of results, or how to handle special cases.

This glossary provides a quick reference to common parameters, their roles, and how changing them affects the fuzzy matching process.
</details>
