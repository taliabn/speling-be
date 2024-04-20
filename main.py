from sortedcontainers import SortedList, SortedDict
from english_words import get_english_words_set
import string
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


def load_web2_words():
	return get_english_words_set(['web2'], lower=True, alpha=True)

def load_words_from_file(file='words_list.txt'):
	with open(file) as word_file:
		valid_words = set(word_file.read().split())
	return valid_words

# hopefully this is legal...
def scrape_nyt_puzzle(url="https://www.nytimes.com/puzzles/spelling-bee"):
	driver = webdriver.Firefox()
	try:
		driver.get(url)
		time.sleep(1)
		eles = driver.find_elements(By.CLASS_NAME, "cell-letter")
		letters = [ele.get_attribute("innerHTML").lower() for ele in eles]
	except Exception as e:
		print(f"error scraping NYT page: \n {e}\n\nProceeding with a random puzzle instead")
		letters = gen_random_puzzle()
	finally:
		driver.close()
	return letters[0], letters[1:]

def gen_random_puzzle():
	vowels = ['A', 'E', 'I', 'O', 'U']
	# guarantee at least 2 vowels for playability
	letters = random.sample(vowels, 2)
	letters.extend(random.sample(string.ascii_uppercase, 7))
	letters = list(set(letters))[:7]
	return letters[0], letters[1:]

def gen_pangram_puzzle(valid_words):
	# TODO:cache these
	candidates = [word for word in valid_words if len(set(word))==7]
	pangram = random.choice(candidates)
	letters = [l for l in set(pangram)]
	random.shuffle(letters)
	return letters[0], letters[1:]

def shuffle_puzzle_repr(req_letter, letters_lower):
	letters = [letter.upper() for letter in letters_lower]
	random.shuffle(letters)
	return f"\t  {letters[0]}  {letters[1]}\n\t{letters[2]}  {req_letter.upper()}  {letters[3]}\n\t  {letters[4]}  {letters[5]}"

def main():
	print("Welcome to Speling Be!")
	# generate puzzle
	valid_words = load_words_from_file("words_list.txt")
	use_nyt = input("Would you like to play today's NYT puzzle instead of a randomly generated one? (y/n)\n> ")
	if "y" in use_nyt.lower():
		req_letter, letters = scrape_nyt_puzzle()
	else:
		req_letter, letters = gen_pangram_puzzle(valid_words)
	all_letters_lower = [l.lower() for l in letters]
	all_letters_lower.append(req_letter.lower())
	puzzle_repr = shuffle_puzzle_repr(req_letter, letters)
	# get solutions
	min_word_len = 4
	possible_words = SortedList([word for word in valid_words if (len(word)>=min_word_len and all(char in all_letters_lower for char in word) and req_letter in word)])
	len_dict = SortedDict()
	# get distribution of lengths
	for word in possible_words:
		l = len(word)
		len_dict.setdefault(l, []).append(word)
	found_words = []
	print(puzzle_repr, f"\nThere are {len(possible_words)} possible words")
	
	# main gameplay loop
	while True:
		cmd = input("> ").split()
		cmd = [c.lower() for c in cmd]
		if cmd[:0] == ":h":
			help_text = "available commands:\n\t:c cheat\n\t:d\n\t:h help (this page)\n\t:l display letters in the puzzle\n\t:q quit\n\t:w display words already found"
			print(help_text)
		elif cmd[0] == ":l":
			if len(cmd)>1 and cmd[1] == "-s":
				puzzle_repr = shuffle_puzzle_repr(req_letter, letters)
			print(puzzle_repr)
		elif cmd[0] == ":q":
			print("Goodbye!")
			break
		elif cmd[0] == ":w":
			print(f"You have found {len(found_words)}/{len(possible_words)} words:\n{', '.join(found_words)}")
		elif cmd[0] == ":c":
			if len(cmd)>2 and cmd[1]=="-n" and cmd[2].isnumeric():
				candidates = len_dict.get(int(cmd[2]), possible_words)
			else:
				candidates = possible_words
			candidates = [word for word in candidates if word not in found_words]
			if not candidates:
				print("Congrats, you found them all!")
			else:
				word = random.choice(candidates)
				print(word)
				found_words.append(word)
		elif cmd[0] == ":a":
			if len(cmd)>1 and cmd[1]=="-d":
				for length, words in len_dict.items():
					print(f"{length}: {' '.join(words)}")
			else:
				print(" ".join(possible_words))
		elif cmd[0] == ":d":
			print("word length distribution\nletters: found/total")
			found_len_dict = {}
			for word in found_words:
				l = len(word)
				found_len_dict.setdefault(l, []).append(word)
			for length, words in len_dict.items():
				print(f"\t{length}: {len(found_len_dict.get(length, []))}/{len(words)}")
		else:
			guess = cmd[0]
			if len(guess)<min_word_len:
				print("Too short")
			elif not all(char in all_letters_lower for char in guess):
				print("Not all letters in\n", puzzle_repr)
			elif req_letter not in guess:
				print(f'Missing center letter "{req_letter.upper()}"')
			elif guess not in possible_words:
				print("Not in word list")
			elif guess in found_words:
				print("Already found")
			else:
				found_words.append(guess)

if __name__ == "__main__":
	main()
