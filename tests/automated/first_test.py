# Author: Самелюк Юрий Дмитриевич
# Automated tests for FIRST.md test cases
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pytest


class BankServiceTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.base_url = "http://localhost:8000"
        cls.wait = WebDriverWait(cls.driver, 10)
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
    
    def setUp(self):
        self.driver.get(f"{self.base_url}/?balance=30000&reserved=20001")
        time.sleep(2)
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pass
    
    def test_01_balance_display(self):
        """TC-001: Валидация отображения баланса"""
        try:
            balance_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[h2[text()='Рубли']]//p[contains(text(), 'На счету')]"))
            )
            balance_text = balance_element.text
            balance_value = ''.join(filter(str.isdigit, balance_text))
            self.assertEqual(balance_value, "30000")

            reserved_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[h2[text()='Рубли']]//p[contains(text(), 'Резерв')]"))
            )
            reserved_text = reserved_element.text
            reserved_value = ''.join(filter(str.isdigit, reserved_text))
            self.assertEqual(reserved_value, "20001")

        except Exception as e:
            self.fail(f"Balance display test failed: {str(e)}")
    
    def test_02_card_number_validation_correct(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()

            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys("1234567890123456")

            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            self.assertTrue(amount_input.is_displayed())

        except Exception as e:
            self.fail(f"Card number validation test failed: {str(e)}")
    
    def test_03_card_number_validation_incorrect(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys("12345")
            
            time.sleep(1)
            
            amount_inputs = self.driver.find_elements(By.XPATH, "//input[@placeholder='1000']")
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'ошибка') or contains(text(), 'неверн') or contains(@class, 'error')]")
            
            self.assertTrue(len(amount_inputs) == 0 or len(error_elements) > 0)
            
        except Exception as e:
            self.fail(f"Incorrect card number validation test failed: {str(e)}")
    
    @pytest.mark.xfail(reason="Известный баг: поле принимает больше 16 цифр")
    def test_04_bug_001_card_accepts_17_digits(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys("12345678901234567")  # 17 digits
            
            time.sleep(1)
            displayed_value = card_input.get_attribute("value")
            digits_only = displayed_value.replace(" ", "")
            
            self.assertEqual(len(digits_only), 16, f"Card should accept only 16 digits, but accepted {len(digits_only)}")
            
        except Exception as e:
            self.fail(f"Card 17 digits validation test failed: {str(e)}")
    
    @pytest.mark.xfail(reason="Известный баг: комиссия рассчитывается неверно для малых сумм")
    def test_05_bug_002_commission_calculation_small_amounts(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys("1234567890123456")
            
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            amount_input.clear()
            amount_input.send_keys("55")  # Small amount less than 100
            
            time.sleep(1)
            
            commission_element = self.driver.find_element(By.XPATH, "//*[@id='comission']")
            commission_text = commission_element.text
            
            self.assertIn("5", commission_text, f"Commission should be 5 rubles for 55 rubles transfer, but got: {commission_text}")
            
        except Exception as e:
            self.fail(f"Commission calculation test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main() 
