from sortedcontainers import SortedList
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
		letters = [ele.get_attribute("innerHTML").upper() for ele in eles]
	except Exception as e:
		print(f"error scraping NYT page: \n {e}\n\nProceeding with a random puzzle instead")
		letters = gen_random_puzzle()
	finally:
		driver.close()
	return letters

def gen_random_puzzle():
	vowels = ['A', 'E', 'I', 'O', 'U']
	# guarantee at least 2 vowels for playability
	letters = random.sample(vowels, 2)
	letters.extend(random.sample(string.ascii_uppercase, 7))
	letters = list(set(letters))[:7]
	return letters

def gen_pangram_puzzle(valid_words):
	# TODO:cache these
	candidates = [word for word in valid_words if len(set(word))==7]
	print(len(candidates))
	pangram = random.choice(candidates)
	letters = [l.upper() for l in set(pangram)]
	random.shuffle(letters)
	return letters

def main():
	print("Welcome to Speling Be!")
	# generate puzzle
	valid_words = load_words_from_file("words_list.txt")
	use_nyt = input("Would you like to play today's NYT puzzle instead of a randomly generated one? (y/n)\n> ")
	if "y" in use_nyt.lower():
		letters = scrape_nyt_puzzle()
	else:
		letters = gen_pangram_puzzle(valid_words)
	req_letter = letters[0].lower()
	letters_lower = [l.lower() for l in letters]
	puzzle_repr = f"\t  {letters[3]}  {letters[1]}\n\t{letters[2]}  {letters[0]}  {letters[4]}\n\t  {letters[5]}  {letters[6]}"
	# get solutions
	min_word_len = 4
	possible_words = SortedList([word for word in valid_words if (len(word)>=min_word_len and all(char in letters_lower for char in word) and req_letter in word)])
	found_words = []
	print(puzzle_repr, f"\nThere are {len(possible_words)} possible words")
	# main gameplay loop
	while True:
		cmd = input("> ").strip().lower()
		if cmd[:2] == ":h":
			help_text = "available commands:\n\t:c cheat\n\t:h help (this page)\n\t:l display letters in the puzzle\n\t:q quit\n\t:w display words already found"
			print(help_text)
		elif cmd[:2] == ":l":
			print(puzzle_repr)
		elif cmd[:2] == ":q":
			print("Goodbye!")
			break
		elif cmd[:2] == ":w":
			print(f"You have found {len(found_words)}/{len(possible_words)} words:\n{', '.join(found_words)}")
		elif cmd[:2] == ":c":
			while True:
				word = random.choice(possible_words)
				if word not in found_words:
					print(word)
					found_words.append(word)
					break
		elif cmd[:2] == ":a":
			print(" ".join(possible_words))
		else:
			guess = cmd
			if len(guess)<min_word_len:
				print("Too short")
			elif not all(char in letters_lower for char in guess):
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
