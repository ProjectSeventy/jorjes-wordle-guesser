import re

from word_lists import answer_words, accepted_words

INFORMATION_GAIN = True
HARD_MODE = False

#Reduce a potential guess list according to constraints
def remove_words(words, found_positions, not_letters, found_letters, not_positions):
    for f in found_positions:
        words = [word for word in words if word[f[1]] == f[0]]
    for f in not_letters:
        words = [word for word in words if f not in word]
    for f in found_letters:
        words = [word for word in words if f in word]        
    for f in not_positions:
        words = [word for word in words if word[f[1]] != f[0]]
    return words

#Lookiing to see if all words fall into a pattern of only 1-3 letters changing
#Returns number of variable letters/positions to check them in
#Approximately 'if making guesses that follow all discovered rules, how many guesses to try all possibilities?'
def find_min_regex_score(words):
    base_pattern = words[0]
    all = ' '.join(words)
    #Pattern is a simple way of getting strings for 10000, 01000, 00100 etc. for all patterns of 1, 2 or 3 ones.
    #This is used to insert regex wildcards into guesses
    for pattern in [16, 8, 4, 2, 1, 24, 20, 18, 17, 12, 10, 9, 6, 5, 3, 7, 11, 13, 14, 19, 21, 22, 25, 26, 28]:
        pattern = format(pattern, '05b')
        base_pattern_check = ''.join([letter if pattern[i] == '0' else '.' for i, letter in enumerate(base_pattern)])
        #Check to see if one of these regex patterns fits every potential word
        match = re.findall(base_pattern_check, all)
        if len(match) == len(words):
            #If so, calculate the number of letters to be checked (letters replaced by wildcards) divided by number of positions to check with (wildcards)
            return (len(set([letter for letter in all if letter not in base_pattern_check])))/len([l for l in base_pattern_check if l == '.'])
    return 0

full_words = answer_words + accepted_words

no_guesses = 0
found_letters = []
not_letters = []
found_positions = []
not_positions = []

while(True):
    #Remove invalid words
    answer_words = remove_words(answer_words, found_positions, not_letters, found_letters, not_positions)
    potential_words = []
    ig_flag = False
    guess_flag = False
    
    #First guess is pre-calculated
    if no_guesses == 0:
        if INFORMATION_GAIN:
            if HARD_MODE:
                potential_words = [('raile', 0)]
            else:
                potential_words = [('stare', 0)]
        else:
            potential_words = [('slate', 0)]
    
    #InfoGain guess for first guess if there are more than 2 options left
    elif no_guesses == 1 and INFORMATION_GAIN:
        if len(answer_words) > 2:
            ig_flag = True
    
    #Check whether InfoGain should be used for a later guess
    elif len(answer_words) > 2 and INFORMATION_GAIN:
        val = find_min_regex_score(answer_words)
        if val >= 6-no_guesses:
            ig_flag = True

    #InfoGain
    if ig_flag:
        #Score each letter for each position, based on it's likelihood to reduce the number of potential words
        letters_per_ig = [{}, {}, {}, {}, {}]
        for i in range(0, 5):
            for letter in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']:
                total = len(answer_words)
                correct_pos_chance = len([word for word in answer_words if word[i] == letter])/total
                other_pos_chance = len([word for word in answer_words if letter in word and word[i] != letter ])/total
                no_pos_chance = 1-correct_pos_chance-other_pos_chance
                letters_per_ig[i][letter] = round((correct_pos_chance*(1-correct_pos_chance))
                                                              + (other_pos_chance*(1-other_pos_chance)) 
                                                              + (no_pos_chance*(1-no_pos_chance)), 3)
       
        #Total the scores per letter for each word it's possible to guess
        if HARD_MODE:
            #If playing on hard mode, only allow guesses that follow the learned rules
            #Currently follows both positive and negative constraints, but the latter *may* not be required by hard mode rules
            full_words_clipped = answer_words + remove_words(full_words, found_positions, not_letters, found_letters, not_positions)
            for word in full_words_clipped:
                potential_words.append((word, sum([letters_per_ig[n][l] for n, l in enumerate(word)])))
        else:
            for word in full_words:
                potential_words.append((word, sum([letters_per_ig[n][l] for n, l in enumerate(word)])))
        #Penalise scores with repeated letters
        potential_words = [(word[0], word[1]-(5-len(list(set(word[0]))))) if len(list(set(word[0]))) < 5 else word for word in potential_words]
        
    #If information gain was not used, score words based on likelihood of characters appearing in each position
    if len(potential_words) == 0:
        guess_flag = True
        
        #Count the frequency of each letter by position
        letters_per = [{}, {}, {}, {}, {}]
        for word in answer_words:
            for i in range(0, 5):
                letters_per[i][word[i]] = letters_per[i].get(word[i], 0) + 1

        #Convert frequencies to percentages (score)
        for freqs in letters_per:
            for k, v in freqs.items():
                freqs[k] = round(v / len(answer_words), 3)
        
        #Total the scores per letter for each word it's possible to guess
        for word in answer_words:
            potential_words.append((word, sum([letters_per[n][l] for n, l in enumerate(word)])))
    
    #Sort the possible guesses by score
    potential_words = sorted(potential_words, key=lambda item: item[1], reverse=True)

    #If making a guess rather than an information gathering move, print most likely options
    if guess_flag:
        num_potential = len(potential_words)
        print('Potential guesses (ranked):')
        for i in range (0, min(5, num_potential)):
            print(potential_words[i][0])
        if num_potential > 5:
            print('{} more...'.format(num_potential-5))
        print('')
    
    guess = potential_words[0][0]
    print('Try: ' + guess)
    
    likelihood = round(100/len(potential_words), 1)
    if guess_flag:
        print('({}% chance of being correct)'.format(likelihood))
    
    
    if input('\nSuccess? y/n \n') == 'y':
        break
    if no_guesses > 6:
        break
    
    places = input('If any positions correct, input here (spaces for blanks), else enter \n')
    letters = input('If any other letters correct, input here, else enter \n')
    print('\n----------\n')
    
    new_letters = [letter for letter in letters]
    
    #Add positions from guess feedback
    if len(places) > 0:
        for key, item in enumerate(places):
            if item != ' ':
                if (item, key) not in found_positions:
                    found_positions.append((item, key))
                    new_letters.append(item)
    
    #Add letters from guess feedback
    found_letters = list(set(found_letters + new_letters))
    
    wrong_places = [letter if letter in found_letters else ' ' for letter in guess]
    wrong_letters = [letter for letter in guess if letter not in found_letters]
    
    #Add wrong positions from guess feedback
    for key, item in enumerate(wrong_places):
        if item != ' ' and (item, key) not in not_positions + found_positions:
            not_positions.append((item, key))
    
    #Add wrong letters from guess feedback
    not_letters = list(set(not_letters + wrong_letters))
    
    no_guesses += 1