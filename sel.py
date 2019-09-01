import os,time

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

class Sel:
	def __init__(self):
		self.display = os.getenv("SEL_DISPLAY", ":99")
		os.environ["DISPLAY"] = self.display
		chrome_options = webdriver.ChromeOptions()
		self.driver = webdriver.Chrome(chrome_options=chrome_options)
		self.timeout = 60
		self.wait = WebDriverWait(self.driver, self.timeout)
		self.max_dump_size = 65536

	def __del__(self):
		if hasattr(self, 'driver'):
			self.driver.quit()

	def get(self, url):
		self.driver.get(url)

	def can_validate_el(self, el):
		if el.get_attribute("type") == "file":
			return False

		return True

	def assert_in_page(self, s, timeout=10):
		return self.assert_in_data(s, self.get_page_source, timeout)

	def find_clickable(self,el_id):
		driver = self.driver
		return self.wait.until(EC.element_to_be_clickable((By.ID, el_id)))

	def can_click_el(self, el):
		if el.get_attribute("type") == "file":
			return False

		return True

	def can_clear_el(self, el):
		if el.get_attribute("type") == "file":
			return False

		return True

	def get_page_id(self):
		return self.driver.find_element_by_tag_name('html')
	def remember_page(self):
		self.old_page_id = self.driver.find_element_by_tag_name('html')
	def wait_for_page_reload(self, timeout=30):
		deadline = time.time() + timeout
		while time.time() < deadline:
			if self.get_page_id() != self.old_page_id:
				print("Page reloaded")
				return
			print("Page not yet reloaded")
			time.sleep(1)
		raise Exception("Page never reloaded")
	def find_by_id(self, el_id):
		return self.driver.find_element_by_id(el_id)

	def select_by_index(self, sel_id, ind):
		sel = Select( self.driver.find_element_by_id(sel_id) )
		sel.select_by_index(ind)

	def select_by_value(self, sel_id, val):
		sel = Select( self.driver.find_element_by_id(sel_id) )
		sel.select_by_value(val)
	def click_by_id(self, el_id):
		self.find_clickable(el_id).click()

	def find_by_xpath(self, xpath):
		return self.driver.find_element_by_xpath(xpath)

	def find_many_by_xpath(self, xpath):
		return self.driver.find_elements_by_xpath(xpath)

	def enter_text(self,el_id,val,wait_for_clickable=True,do_clear=True,validate=True):
		val = str(val)
		print "Setting element " + el_id + " to " + val
		# TODO: this is a hack to work around the clickability of file elements
		# when arranged a certain way. Need to fix it to make it more efficient and clean.
		el = self.driver.find_element_by_id(el_id)
		if wait_for_clickable and self.can_click_el(el):
			el = self.find_clickable(el_id)
		else:
			el = self.driver.find_element_by_id(el_id)

		if do_clear and self.can_clear_el(el):
			el.clear()

		el.send_keys(val)

		if validate and self.can_validate_el(el):
			while el.get_attribute("value") != val:
				if do_clear and self.can_clear_el(el):
					el.clear()
				el.send_keys(val)
				time.sleep(1)

	def get_page_source(self):
		res = self.driver.page_source.encode('ascii','ignore')
		#print "page source is of type " + str(type(res))
		return res

	def assert_el_text(self, el_id, s, timeout=20):
		deadline = time.time() + timeout
		while time.time() < deadline:
			try:
				el = self.find_by_id(el_id)
				if el.text == s:
					return
			except:
				pass
			time.sleep(1)
		raise Exception("Could not find " + s + " in element ID " + el_id + " before timeout")

	def assert_in_data(self, s, fetcher, timeout, *args):
		#print "Asserting " + str(s)
		while True:
			data = fetcher(*args)
			if data.find(s) >= 0:
				return True
			time.sleep(1)
			timeout = timeout - 1
			if timeout <= 0:
				raise Exception("Failed assert: string " + s + " not present in data:\n" +
					data[:self.max_dump_size] +
					"after timeout")

	def __del__(self):
		self.driver.close()
