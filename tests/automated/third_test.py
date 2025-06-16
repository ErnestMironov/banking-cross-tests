# Author: Миронов Эрнест Арвович
# Automated tests for THIRD.md test cases

import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
from selenium.common.exceptions import TimeoutException

class BankAppTests(unittest.TestCase):

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

    def open_app(self, balance=0, reserved=0):
        url = f"{self.base_url}/?balance={balance}&reserved={reserved}"
        self.driver.get(url)
        self.select_ruble_card()

    def select_ruble_card(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
        except TimeoutException:
            self.fail("Рублевая карта не найдена или не кликабельна.")

    def enter_card_number(self, card_number):
        try:
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys(card_number)
        except TimeoutException:
            self.fail("Поле для ввода номера карты не найдено.")

    def enter_amount(self, amount):
        try:
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            amount_input.clear()
            amount_input.send_keys(amount)
        except TimeoutException:
            self.fail("Поле для ввода суммы не найдено.")
    
    def get_amount(self):
        try:
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            return amount_input.get_attribute("value")
        except TimeoutException:
            self.fail("Поле для ввода суммы не найдено.")


    def click_transfer_button(self):
        try:
            transfer_button = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "g-button"))
            )
            transfer_button.click()
        except TimeoutException:
            self.fail("Кнопка 'Перевести' не найдена или не кликабельна.")


    def confirm_transfer(self):
        try:
            alert = self.wait.until(EC.alert_is_present())
            alert.accept()
        except TimeoutException:
            self.fail("Всплывающее окно подтверждения не появилось.")

    def get_balance(self):
        try:
            balance_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "rub-sum"))
            )
            return int(balance_element.text.replace('\'', ''))
        except TimeoutException:
            self.fail("Элемент баланса не найден.")

    def get_reserved(self):
        try:
            reserved_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "rub-reserved"))
            )
            return int(reserved_element.text.replace('\'', ''))
        except TimeoutException:
            self.fail("Элемент резерва не найден.")

    def get_commission(self):
        try:
            commission_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "comission"))
            )
            return int(commission_element.text)
        except TimeoutException:
            self.fail("Элемент комиссии не найден.")

    def is_transfer_button_enabled(self):
        try:
            transfer_button = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "g-button"))
            )
            return transfer_button.is_enabled()
        except TimeoutException:
            return False

    def get_error_message(self):
        try:
            error_message_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='Недостаточно средств на счете']"))
            )
            return error_message_element.text
        except TimeoutException:
            return ""


    def is_amount_input_enabled(self):
        try:
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//h3[text()='Сумма перевода:']"))
            )
            return amount_input.is_enabled()
        except TimeoutException:
            return False


    # TC-011
    @pytest.mark.xfail(reason="Известный баг: Некорректно отображаются данные счета после перевода")
    def test_tc_011_correct_balance_after_transfer(self):
        try:
            self.open_app(balance=30000, reserved=20000)
            self.enter_card_number("1234567890123456")
            self.enter_amount("1000")
            self.click_transfer_button()
            self.confirm_transfer()

            expected_reserved = 21000
            expected_balance = 29000

            actual_reserved = self.get_reserved()
            actual_balance = self.get_balance()

            self.assertEqual(actual_reserved, expected_reserved, "Резерв не изменился")
            self.assertEqual(actual_balance, expected_balance, "Баланс не изменился")
        except Exception as e:
            self.fail(f"Тест TC-011 не пройден: {str(e)}")


    # TC-012
    def test_tc_012_correct_commission_value(self):
        try:
            self.open_app(balance=30000)
            self.enter_card_number("1234567890123456")
            self.enter_amount("1000")
            expected_commission = 100
            actual_commission = self.get_commission()

            self.assertEqual(actual_commission, expected_commission, "Значение комиссии после ввода суммы некорректно")
        except Exception as e:
            self.fail(f"Тест TC-012 не пройден: {str(e)}")


    # TC-013
    def test_tc_013_insufficient_funds_error(self):
         try:
            self.open_app(balance=30000)
            self.enter_card_number("1234567890123456")
            self.enter_amount("30000")
            expected_error_message = "Недостаточно средств на счете"
            actual_error_message = self.get_error_message()

            self.assertFalse(self.is_transfer_button_enabled(), "Кнопка 'Перевести' должна быть недоступна")
            self.assertEqual(actual_error_message, expected_error_message, "Текст ошибки некорректен")
         except Exception as e:
            self.fail(f"Тест TC-013 не пройден: {str(e)}")

    # TC-014
    def test_tc_014_amount_input_disabled_with_invalid_card(self):
        try:
            self.open_app(balance=30000)
            self.enter_card_number("111111111111")
            self.assertFalse(self.is_amount_input_enabled(), "Поле 'Сумма перевода' должно быть недоступно")
        except Exception as e:
            self.fail(f"Тест TC-014 не пройден: {str(e)}")

    # TC-015
    @pytest.mark.xfail(reason="Известный баг: Разрешен перевод нулевой суммы")
    def test_tc_015_transfer_button_disabled_for_zero_amount(self):
        try:
            self.open_app(balance=30000)
            self.enter_card_number("1234567890123456")
            self.enter_amount("0")

            self.assertFalse(self.is_transfer_button_enabled(), "Кнопка 'Перевести' должна быть неактивна")
        except Exception as e:
            self.fail(f"Тест TC-015 не пройден: {str(e)}")

    # TC-016 
    @pytest.mark.xfail(reason="Известный баг: Некорректная обработка дробных сумм")
    def test_tc_016_correct_handling_of_fractional_amounts(self):
        try:
            self.open_app(balance=30000)
            self.enter_card_number("1234567890123456")
            self.enter_amount("100.50")
            expected_amount = "100.50"
            actual_amount = self.get_amount()
           
            self.assertEqual(actual_amount, expected_amount, "Дробная сумма обрабатывается некорректно")
        except Exception as e:
            self.fail(f"Тест TC-016 не пройден: {str(e)}")


if __name__ == '__main__':
    unittest.main()