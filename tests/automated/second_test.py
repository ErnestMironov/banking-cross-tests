# Author: Ягунов Денис Алексеевич
# Automated tests for SECOND.md test cases

import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import pytest


class BankServiceBoundaryTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.base_url = "http://localhost:8000"
        cls.wait = WebDriverWait(cls.driver, 5)
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
    
    def is_transfer_button_enabled(self):
        try:
            transfer_button = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "g-button"))
            )
            return transfer_button.is_enabled()
        except TimeoutException:
            return False
    
    def test_06_correct_boundary_balance_values(self):
        try:
            # Тест с нулевым балансом
            self.driver.get(f"{self.base_url}/?balance=0&reserved=0")
            
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            self.assertEqual(balance_element.text, "0")
            
            # Тест с минимальным балансом
            self.driver.get(f"{self.base_url}/?balance=1&reserved=0")
            
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            self.assertEqual(balance_element.text, "1")
            
            # Тест с большим балансом
            self.driver.get(f"{self.base_url}/?balance=999999&reserved=0")
            
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            self.assertEqual(balance_element.text, "999'999")
            
        except Exception as e:
            self.fail(f"Boundary balance values test failed: {str(e)}")
    
    def test_06_correct_boundary_reserved_values(self):
        try:
            # Тест с нулевым балансом
            self.driver.get(f"{self.base_url}/?balance=0&reserved=0")
            
            reserved_element = self.driver.find_element(By.XPATH, "//span[@id='rub-reserved']")
            self.assertEqual(reserved_element.text, "0")
            
            # Тест с минимальным балансом
            self.driver.get(f"{self.base_url}/?balance=0&reserved=1")
            
            reserved_element = self.driver.find_element(By.XPATH, "//span[@id='rub-reserved']")
            self.assertEqual(reserved_element.text, "1")
            
            # Тест с большим балансом
            self.driver.get(f"{self.base_url}/?balance=0&reserved=999999")
            
            reserved_element = self.driver.find_element(By.XPATH, "//span[@id='rub-reserved']")
            self.assertEqual(reserved_element.text, "999'999")
            
        except Exception as e:
            self.fail(f"Boundary reserved values test failed: {str(e)}")

    @pytest.mark.xfail(reason="Известный баг: валидация параметра balance некорректно работает для отрицательных значений")
    def test_06_incorrect_boundary_balance_value_less_then_zero(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=-1&reserved=0")
            
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            self.assertEqual(balance_element.text, "0")
            
        except Exception as e:
            self.fail(f"Boundary balance values test failed: {str(e)}")


    @pytest.mark.xfail(reason="Известный баг: валидация параметра balance некорректно работает для огромных значений")
    def test_06_incorrect_boundary_balance_value_more_then_max(self):
        try:
            # Тест с балансом больше максимально возможного. 
            balance = 10**20
            self.driver.get(f"{self.base_url}/?balance={balance}&reserved=0")
            
            # Максимально возножное значение не определено, поэтому будет выбрано вручную
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            expected_value = "10'000'000'000"
            self.assertEqual(balance_element.text, expected_value)
            
        except Exception as e:
            self.fail(f"Boundary balance values test failed: {str(e)}")

    @pytest.mark.xfail(reason="Известный баг: валидация параметра reserved некорректно работает для отрицательных значений")
    def test_06_incorrect_boundary_reserved_value_less_then_zero(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=0&reserved=-1")
            
            reserved_element = self.driver.find_element(By.XPATH, "//span[@id='rub-reserved']")
            self.assertEqual(reserved_element.text, "0")
            
        except Exception as e:
            self.fail(f"Boundary reserved values test failed: {str(e)}")

    @pytest.mark.xfail(reason="Известный баг: валидация параметра reserved некорректно работает для огромных значений")
    def test_06_incorrect_boundary_reserved_value_more_then_max(self):
        try:
            # Тест с балансом больше максимально возможного. 
            reserved = 10**20
            self.driver.get(f"{self.base_url}/?balance=0&reserved={reserved}")
            
            # Максимально возножное значение не определено, поэтому будет выбрано вручную
            reserved_element = self.driver.find_element(By.XPATH, "//span[@id='rub-reserved']")
            expected_value = "10'000'000'000"
            self.assertEqual(reserved_element.text, expected_value)
            
        except Exception as e:
            self.fail(f"Boundary reserved values test failed: {str(e)}")

    @pytest.mark.xfail(reason="Известный баг: валидация номера карты не фильтрует лишние символы")
    def test_07_card_number_validation_boundary_cases_exceeding_character_limit(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=30000&reserved=20000")
            
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            
            card_input.clear()
            card_input.send_keys("12345678901234567890")
            
            current_value = card_input.get_attribute("value")
            self.assertTrue(len(current_value.replace(" ", "")) <= 16)
        except Exception as e:
            self.fail(f"Card number boundary validation test failed: {str(e)}")

    def test_07_card_number_validation_boundary_cases_filtering_of_extra_characters(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=30000&reserved=20000")
            
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            
            card_input.clear()
            card_input.send_keys("1234abcd56 78!@9012#$% 1234")
            
            current_value = card_input.get_attribute("value")
            expected_value = '1234 5678 9012 1234'

            self.assertEqual(current_value, expected_value)
            
        except Exception as e:
            self.fail(f"Card number boundary validation test failed: {str(e)}")
    
    @pytest.mark.xfail(reason="Известный баг: комиссия округляется неверно")
    def test_08_commission_calculation_rounding_down(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=10000&reserved=0")
            
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

            # Тест округления вниз для 199 -> комиссия должна быть 10
            amount_input.clear()
            amount_input.send_keys("199")
            
            commission_element = self.driver.find_element(By.XPATH, "//span[@id='comission']")
            self.assertEqual(commission_element.text, "10")

            # Тест округления вниз для 55 -> комиссия должна быть 5
            amount_input.clear()
            amount_input.send_keys("55")
            
            commission_element = self.driver.find_element(By.XPATH, "//span[@id='comission']")
            self.assertEqual(commission_element.text, "5")
        except Exception as e:
            self.fail(f"Commission rounding test failed: {str(e)}")
    
    @pytest.mark.xfail(reason="Известный баг: Кнопка перевода недоступна при равном значении баланса и суммы перевода + коммиссия")
    def test_09_transfer_amount_and_balance_amount_equal(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=11000&reserved=0")

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
            amount_input.send_keys(9999)

            self.assertTrue(self.is_transfer_button_enabled(), "Кнопка 'Перевести' должна быть доступна")

            amount_input.clear()
            amount_input.send_keys(10000)

            self.assertTrue(self.is_transfer_button_enabled(), "Кнопка 'Перевести' должна быть доступна")
        except Exception as e:
            self.fail(f"Transfer amount and balance amount equal test failed: {str(e)}")
    
    
    @pytest.mark.xfail(reason="Известный баг: NaN вместо 0 при невалидных параметрах URL")
    @pytest.mark.xfail(reason="Известный баг: Параметр reserved может быть больше balance")
    def test_10_behavior_with_different_URL_parametersl(self):
        try:
            self.driver.get(f"{self.base_url}/")
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            reserved_element = self.driver.find_element(By.XPATH, "//span[@id='rub-reserved']")

            self.assertEqual(balance_element.text, "0", f"Invalid URL param balance should show '0', but got: {balance_element.text}")
            self.assertEqual(reserved_element.text, "0", f"Invalid URL params reserved should show '0', but got: {reserved_element.text}")

            self.driver.get(f"{self.base_url}/?balance=abc&reserved=xyz")
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            reserved_element = self.driver.find_element(By.XPATH, "//span[@id='rub-reserved']")
            
            self.assertEqual(balance_element.text, "0", f"Invalid URL param balance should show '0', but got: {balance_element.text}")
            self.assertEqual(reserved_element.text, "0", f"Invalid URL params reserved should show '0', but got: {reserved_element.text}")

            self.driver.get(f"{self.base_url}/?reserved=5000&balance=1000")
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            reserved_element = self.driver.find_element(By.XPATH, "//span[@id='rub-reserved']")
            
            self.assertEqual(reserved_element.text, "0", f"Invalid URL params reserved should show '0', but got: {reserved_element.text}")

        except Exception as e:
            self.fail(f"URL params validation test failed: {str(e)}")
    
    @pytest.mark.xfail(reason="Известный баг: кнопка перевода не блокируется для отрицательных сумм")
    def test_11_negative_amounts_acceptance(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=10000&reserved=0")
            time.sleep(2)
            
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
            amount_input.send_keys("-100")
            
            transfer_buttons = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Перевести')]")
            
            if len(transfer_buttons) > 0:
                button = transfer_buttons[0]
                self.assertFalse(button.is_enabled(), "Transfer button should be disabled for negative amounts")
        except Exception as e:
            self.fail(f"Negative amounts test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main() 