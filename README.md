# Jorje's Wordle Guesser
This is a system I put together to automatically solve Wordle. The system prompts the user with a word to try, and then enter the feedback from the site. This system has a 100% success rate (on normal mode), with over 50% of words guessed within 3 guesses. It relies on the wordlist Wordle uses, so may lessen in effectiveness if Wordle changes it's list and I neglect to update the system.

### Usage
##### Normal Usage
I must admit, usability was not the focus when making this tool. It's not particularly unwieldy, but neither is it particularly user friendly.
The system will prompt the user with a guess to try, and asks whether or not this was the word. Simply answer with `y` or `n`, for yes or no.

It will then ask for any letters found in the correct position, filling uncertain letter slots as spaces. For example, if the guess was `throw`, and the final `o` was in the correct position, the correct input would be three spaces, followed by an `o`. In cases where no letters are in the correct position, just hitting enter is sufficient. If you have already inputted that a letter is in a certain position from a previous guess, it is not necessary, though neither is it detrimental, to input it again.

The user will then be prompted to input any other letters that were correct, though not in the correct place. These should be entered in an unbroken string, though in any order. For example, if the guess was `throw`, and the `t` and the `r` were correct, the correct input would be either `tr` or `rt`. Again, if you have already inputted that a letter correct from a previous guess, it is not necessary, though neither is it detrimental, to input it again.

Based on this input, the system will then suggest another guess. This repeats until either the user inputs that the correct word has been identified, or there are no guesses remaining.

The system has two modes of guessing that it may use. Initially it uses an information gain guess, guessing a word unlikely or impossible to be correct, in order to most effectively cut down the list of potential words. It may also make a standard guess, which is it's best guess at the word, that will still cut down the remaining options as much as possible if it's incorrect. In these cases, it will list the top 5 most likely words above the prompted guess, as well as a percentage chance of correctness. **Guessing a word other than that prompted will prevent the program from making an accurate guess if it is wrong.**

Finally, it is worth noting that giving the system the wrong feedback will either lead to it making incorrect guesses, or crashing.

##### Other Modes
The system is actually three systems. At the top of the file are two flags - `INFORMATION_GAIN` and `HARD_MODE`. The latter simply changes the standard system to only suggest words that are legal in hard mode. `INFORMATION_GAIN` allows the system to make guesses unlikely to be correct but are useful in narrowing down the list of potential words. In standard usage, it is enabled. Disabling it leads to worse results on normal mode, though may be preferable playing on hard mode (results are discussed below). All guesses are hard mode compliant if `INFORMATION_GAIN` is set to `False`, and so it is not necessary to also set `HARD_MODE` to `True`.

### Results
The system has been tested against every word it is possible for Wordle to set as the goal, at the time of writing. The tables below show how many words are guessed for each number of guesses, and the cumulative percentage.

##### System 1 (Normal) -- Default
##### (`INFORMATION_GAIN = True`, `HARD_MODE = False`)
| No. of Guesses | Frequency | Cumulative %age |
| --- | --- | --- |
| 1 | 0 | 0.00% |
| 2 | 43 | 1.86% |
| 3 | 1141 | 51.14% |
| 4 | 891 | 89.63% |
| 5 | 236 | 99.83% |
| 6 | 4 | 100.00% |
| Failed | 0 | 100.00% |

##### System 1 (Hard)
##### (`INFORMATION_GAIN = True`, `HARD_MODE = True`)
| No. of Guesses | Frequency | Cumulative %age |
| --- | --- | --- |
| 1 | 0 | 0.00% |
| 2 | 104 | 4.49% |
| 3 | 972 | 46.48% |
| 4 | 894 | 85.10% |
| 5 | 263 | 96.46% |
| 6 | 64 | 99.22% |
| Failed | 18 | 100.00% |

##### System 2 (Hard)
##### (`INFORMATION_GAIN = False`)
| No. of Guesses | Frequency | Cumulative %age |
| --- | --- | --- |
| 1 | 1 | 0.04% |
| 2 | 146 | 6.35% |
| 3 | 850 | 43.07% |
| 4 | 981 | 85.44% |
| 5 | 275 | 97.32% |
| 6 | 49 | 99.44% |
| Failed | 13 | 100.00% |

This is also shown in the graph below. 

![Bar chart showing the number of words guessed for each number of guesses, for each system](https://i.imgur.com/RyuKPnB.png)

System 1 was designed to sacrifice guesses 1 and 2 in order to greatly increase the chance of getting words on guesses 3 or 4. System 2 is simpler, but on hard mode, fails less often, thus the options are provided to use either.

### Approach
System 2, accessed by setting `INFORMATION_GAIN` to `False` was the first attempt I made. It first calculates a score for each letter in each position, by looking at all the remaining potential words and calculating how likely a letter is to appear in that position. Each potential guess is then scored by summing the score for each letter in the positions they are in. The result of this is that any constraints learnt from feedback will also apply to the guess. This proves to be a fairly effective system, but doesn't make the most of negative constraints and struggles when there are several options for words to try with several letters the same (`grace`, `grade`, `grape`, `grate`, `grave`, and `graze` must be tested in turn, one guess each, until the correct one is guessed).

System 1 has the same basis, but adds an information gain guess. In this case, each letter in each position is given a score based on how much it is likely to reduce the number of potential words. For example, if 30% of candidate words have an `e` second, and 40% have an `e` elsewhere, an `e` in the second position has a score of (0.25 * 0.75) + (0.4 * 0.6) + (0.35 * 0.65). That is, a 30% chance of reducing by 70% (words with an `e` second), a 40% chance of reducing by 60% (words with an `e` elsewhere), and a 35% chance of reducing by 65% (words with no `e` in). Every word possible of being accepted as a guess is scored, by summing the scores of their letters, and the highest scoring word is guessed.

An information gain guess, though very useful, is unlikely to be the correct word, and so one must be careful when to use it. On guess 2, if there are only one or two possible candidate words, it is better to use a system 2 style guess, as it is either guaranteed to be correct, or 50/50 whether it is correct on guess 2 or guess 3. In all other cases, an information gain guess is used, as it is unlikely to guess correctly this turn, and will massively narrow down the possibilities for guess 3.

On each subsequent guess, to account for the `gra*e` problem detailed above, a check is used to approximate the number of guesses needed to try all possibilities. This is done by checking all regex patterns with either one, two, or three letters as wildcards over the list of potential words. This will identify any recurring patterns such as `gra*e`. `*o*er`, and `*a**y` that apply to all remaining potential words. In cases where multiple apply, the one with the fewest wildcards is used, as it is the most general (the function returns at the first found, rather than checking for more, but tests from most to least general). The number of letters to be tested (i.e. the ones replaced by wildcards) is divided by the number of wildcards present, to give an approximate number of guesses needed to try all potential words. For example, with the `gra*e` pattern, there are 6 letters (`c`, `d`, `p`, `t`, `v`, `z`) to be tried in only one place, which would take on average (and exactly in this case) 6 guesses to try all. Alternatively, if the potential words were reduced to `goner`, `foyer`, `lover`, `rover`, `cover`, `joker`, `boxer`, `voter`, `corer`, and `roger`, the pattern `*o*er` would apply, with 13 letters (`g`, `n`, `f`, `y`, `l`, `v`, `r`, `c`, `j`, `k`, `b`, `x`, `t`) over 2 positions, which would take on average 6.5 guesses to try. In cases where there is a pattern found, and it takes more guesses to try than the number of guesses remaining, an information gain guess is calculated. Otherwise, a system 2 style guess is calculated.

Finally, as the first guess will always be the same, it is pre-calculated to be optimal. I calculated the average reduction in potential words for every word accepted by wordle, and ranked them. I then tried each system using each of these as it's first guess, as well as what it would have selected by it's own metrics (`roate` for system 1, `slate` for system 2 - `roate` is also the best for average reduction of potential words). I then hardcoded the starting word that gives the best result for each system, which are shown below.

| Starting Word | System |
| --- | --- |
| System 1 (Normal) | `soare` |
| System 1 (Hard) | `raile` |
| System 2 | `slate` |

Do you disagree that these are all real words? It doesn't matter, Wordle accepts them.