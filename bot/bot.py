from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from random import random
from time import sleep
import requests
import getpass
import pyautogui

win_width = pyautogui.size()[0]
win_height = pyautogui.size()[1]

root = input('Enter the API endpoint for the Chatbot: ')

# get response from machine learning API to generate text responses
def get_response(question):
	response = requests.get(root + 'api/chat', json = {'speaker': 'Michael Lu', 'msg': question})

	if response.json()['status'] == 'success':
		answer = response.json()['data']['output']
		print('Me:', question)
		print('Sadmanda:', answer)
		return answer
	else:
		print('Error...')
		return ''

# bot chats with users in facebook comments or facebook messenger
def facebook_chat(mode = 'comment'):
	# get user credentials
	username = input('Enter your Facebook Username: ')
	password = getpass.getpass('Enter your Facebook Password: ')


	# login to facebook
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument("--incognito")
	driver = webdriver.Chrome('chromedriver.exe', options = chrome_options)
	driver.get('http://facebook.com')

	driver.find_element_by_id('email').send_keys(username)
	driver.find_element_by_id('pass').send_keys(password)
	driver.find_element_by_id('loginbutton').click()
	# driver.find_element_by_xpath("//button[@name='login']").click()
	print('Logging in...')
	sleep(random() * 5)

	if mode == 'comment':
		# bot chats in comments under a facebook post
		# navigate to a post where the bot was tagged in
		print('Going to notifications...')
		driver.get(driver.current_url +  'notifications')
		sleep(random() * 1.5)

		soup = BeautifulSoup(driver.page_source, 'html.parser')
		notification_links = soup.findAll('a', {'class': '_1_0e'})

		print('Going to tagged post...')
		mention_links = [link for link in notification_links if 'mentioned you' in link.find('div', {'class': '_4l_v'}).find('span').findAll('span')[-1].text]
		driver.get(mention_links[0]['href'])
		sleep(random() * 1.5)

		num_msgs = 0
		last_msg = ''
		sent_msgs = {}
		num_ignored_msgs = 0

		# save the button that lets the bot reply to the comment where it was tagged
		reply_links = driver.find_elements_by_class_name('_6qw5')
		reply_link_idx = len(reply_links) - 1

		while True:
			# if no new comments detected for a while, refresh the page to check for new comments
			if num_ignored_msgs > 5:
				print('Message ignored...')
				print('Refreshing page...')
				driver.get(driver.current_url + '&refresh_id=' + str(random() * 500))
				sleep(random() * 4 + 3)
				num_ignored_msgs = 0

				print('Checking comments...')
				reply_links = driver.find_elements_by_class_name('_6qw5')
				reply_links[reply_link_idx].click()
				sleep(random() * 2)

			# find all comments
			soup = BeautifulSoup(driver.page_source, 'html.parser')
			msg_spans = soup.findAll('span', {'class': '_3l3x'})
			msgs = [msg_span.find('span').text for msg_span in msg_spans if msg_span.find('span')]

			print()
			print('Last discovered message:', msgs[-1], 'Last recorded message:', last_msg)
			print('Number of discovered messages:', len(msgs), 'Number of recorded messages:', num_msgs)
			print()

			# check if most recent comment is new and has not yet been recorded
			if msgs[-1].strip() not in sent_msgs and (msgs[-1] != last_msg or len(msgs) > num_msgs):
				last_msg = msgs[-1]
				print('Message:', last_msg)
				response = get_response(last_msg)

				if response == '':
					response += '...'

				print('Response:', response)

				# reply with the output from the machine learning API
				reply_links = driver.find_elements_by_class_name('_6qw5')
				last_reply_link = reply_links[-1]
				last_reply_link.click()
				sleep(random() * 2)
				pyautogui.typewrite(response)
				sleep(random() * 1.5)
				pyautogui.press('enter')
				sleep(random() * 10)

				last_msg = response
				sent_msgs[last_msg] = 1
				num_msgs = len(msgs) + 1
				num_ignored_msgs = 0
			else:
				# increment the counter for the number of iterations for when no new comments have been detected
				num_ignored_msgs += 1

			sleep(random() * 10 + 5)
	else:
		print('Going to Messenger...')
		friend_chat_path = input('Enter the URL for your friend\'s Messenger chat: ')
		driver.get(friend_chat_path)
		sleep(random() * 1.5 + 7)

		num_msgs = 0
		last_msg = ''
		sent_msgs = {}
		num_ignored_msgs = 0

		while True:
			# if no new comments detected for a while, double text
			if num_ignored_msgs > 10:
				print('Message ignored...')
				msgs.append('haha xd' + msgs[int(random() * len(msgs))] + 'lol funny')
				num_ignored_msgs = 0

			# find all messages
			soup = BeautifulSoup(driver.page_source, 'html.parser')
			msg_spans = soup.findAll('span', {'class': '_58nk'})
			msgs = [msg_span.text for msg_span in msg_spans]

			print()
			print('Last discovered message:', msgs[-1], 'Last recorded message:', last_msg)
			print('Number of discovered messages:', len(msgs), 'Number of recorded messages:', num_msgs)
			print()

			# check if most recent comment is new and has not yet been recorded
			if msgs[-1] not in sent_msgs and (msgs[-1] != last_msg or len(msgs) > num_msgs):
				last_msg = msgs[-1]
				print('Message:', last_msg)
				response = get_response(last_msg)

				if response == '':
					response += '...'

				# reply with the output from the machine learning API
				print('Response:', response)
				pyautogui.click(win_width * 0.65, win_height * 0.94)
				sleep(random() * 2)
				pyautogui.typewrite(response)
				sleep(random() * 1.5)
				pyautogui.press('enter')

				last_msg = response
				sent_msgs[last_msg] = 1
				num_msgs = len(msgs) + 1
				num_ignored_msgs = 0
			else:
				# increment the counter for the number of iterations for when no new messages have been detected
				num_ignored_msgs += 1

			sleep(random() * 1.5 + 1)

	sleep(1000)

# 
def console_chat():
	question = ''
	while question != 'exit()':
		question = input('Me: ')
		response = requests.get(root + 'api/chat', json = {'speaker': 'Michael Lu', 'msg': question})

		if response.json()['status'] == 'success':
			answer = response.json()['data']['output']
			print('Sadmanda:', answer)
		else:
			print('Error...')

if __name__ == '__main__':
	mode = input('Choose a bot mode for Facebook (comment or chat): ').lower()
	facebook_chat(mode = mode)
	# console_chat()