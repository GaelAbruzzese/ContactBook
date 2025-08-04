import unittest
from src.contact import Contact

class TestContact(unittest.TestCase):

    def setUp(self):
        self.contact = Contact(
            name="Alice",
            surname="Smith",
            phone={'mobile': ['12345'], 'home': ['67890']},
            email={'personal': ['alice@example.com'], 'work': []},
            address="123 Main St"
        )

    def test_initialization_defaults(self):
        c = Contact(name="Bob", surname="Brown")
        self.assertEqual(c.phone, {'home': [], 'mobile': [], 'work': [], 'other': []})
        self.assertEqual(c.email, {'personal': [], 'work': [], 'other': []})
        self.assertEqual(c.address, "")
        self.assertIsNone(c.id)

    def test_initialization_error(self):
        c = Contact(name="Bob", surname="Brown", phone={'other':"123-456"})
        self.assertEqual(c.phone['other'], ["error"])
        self.assertEqual(c.email, {'personal': [], 'work': [], 'other': []})
        self.assertEqual(c.address, "")
        self.assertIsNone(c.id)

    def test_initialization_invalid_phone(self): # check
        with self.assertRaises(TypeError):
          Contact(name="Bob", surname="Brown", phone=1.2)

    def test_initialization_invalid_email(self): # check
        with self.assertRaises(TypeError):
          Contact(name="Bob", surname="Brown", email=123)            

    def test_phone_normalization_error(self):
        c = Contact(name="Charlie", surname="Doe", phone="555-1234")
        self.assertEqual(c.phone, {"other": ["error"]})

    def test_phone_normalization_str(self):
        c = Contact(name="Charlie", surname="Doe", phone="5551234")
        self.assertEqual(c.phone, {"other": ["5551234"]})

    def test_phone_normalization_int(self):
        c = Contact(name="Charlie", surname="Doe", phone=5551234)
        self.assertEqual(c.phone, {"other": ["5551234"]})


    def test_phone_normalization_list(self):
        c = Contact(name="Dana", surname="White", phone=["111", "222"])
        self.assertEqual(c.phone, {"other": ["111", "222"]})

    def test_email_normalization_str(self):
        c = Contact(name="Ed", surname="Green", email="ed@mail.com")
        self.assertEqual(c.email, {"other": ["ed@mail.com"]})

    def test_email_normalization_error1(self):
        c = Contact(name="Ed", surname="Green", email="@mail.com")
        self.assertEqual(c.email, {"other": ["error"]})

    def test_email_normalization_error2(self):
        c = Contact(name="Ed", surname="Green", email="ed@mail")
        self.assertEqual(c.email, {"other": ["error"]})

    def test_email_normalization_error3(self):
        c = Contact(name="Ed", surname="Green", email="ed@.com")
        self.assertEqual(c.email, {"other": ["error"]})

    def test_email_normalization_error4_and_match(self):
        c = Contact(name="Ed", surname="Green", email="edmail.com")
        self.assertEqual(c.email, {"other": ["error"]})
        self.assertTrue(c.email,"error")

    def test_email_normalization_long_domain(self):
        c = Contact(name="Ed", surname="Green", email="ed@mail.co.uk")
        self.assertEqual(c.email, {"other": ["ed@mail.co.uk"]})

    def test_one_field_match_basic(self):
        self.assertTrue(self.contact.one_field_match("name", "Alice"))
        self.assertTrue(self.contact.one_field_match("surname", "Smith"))
        self.assertFalse(self.contact.one_field_match("address", "Wrong St"))

    def test_one_field_match_phone_label(self):
        self.assertTrue(self.contact.one_field_match("phone", "12345", label="mobile"))
        self.assertFalse(self.contact.one_field_match("phone", "12345", label="home"))

    def test_one_field_match_email_any(self):
        self.assertTrue(self.contact.one_field_match("email", "alice@example.com"))
        self.assertFalse(self.contact.one_field_match("email", "bob@example.com"))

    def test_one_field_match_invalid_field(self):
        with self.assertRaises(ValueError):
          self.contact.one_field_match("birthday","test")
            
    def test_one_field_match_invalid_label(self):
        self.assertFalse(self.contact.one_field_match("phone", "12345", label="nolabel"))
                
    def test_matches_all(self):
        self.assertTrue(self.contact.matches('all', ('name', 'Alice'), ('surname', 'Smith')))
        self.assertFalse(self.contact.matches('all', ('name', 'Alice'), ('surname', 'Wrong')))
        self.assertTrue(self.contact.matches('all', ('name', 'Alice')))
        self.assertFalse(self.contact.matches('all', ('surname', 'Wrong')))
        self.assertTrue(self.contact.matches('all', ('name', 'Alice'), ('phone', "12345", "mobile")))
        self.assertFalse(self.contact.matches('all', ('name', 'Alice'), ('phone', "12345", "other")))

    def test_matches_any(self):
        self.assertTrue(self.contact.matches('any', ('surname', 'Smith'), ('name', 'Bob')))
        self.assertFalse(self.contact.matches('any', ('surname', 'Jones'), ('address', 'Nowhere')))
        self.assertTrue(self.contact.matches('any', ('phone', '12345'), ('name', 'Bob')))
        self.assertFalse(self.contact.matches('any', ('surname', 'Jones'), ('email', 'no@mail.com')))

    def test_update_one_simple_field(self):
        self.contact.update_one("address", "456 New Ave")
        self.assertEqual(self.contact.address, "456 New Ave")

    def test_update_one_phone_replace(self):
        self.contact.update_one("phone", "99999", label="mobile", mode="replace")
        self.assertEqual(self.contact.phone["mobile"], ["99999"])

    def test_update_one_phone_replace_error(self):
        self.contact.update_one("phone", "999-99", label="mobile", mode="replace")
        self.assertEqual(self.contact.phone["mobile"], ["12345"])

    def test_update_one_mail_replace_error(self):
        self.contact.update_one("email", "no.mail", mode="add")
        self.assertEqual(self.contact.email,{'personal': ['alice@example.com'], 'work': []})

    def test_update_one_phone_add(self):
        self.contact.update_one("phone", "55555", label="home", mode="add")
        self.assertIn("55555", self.contact.phone["home"])
        self.assertIn("67890", self.contact.phone["home"])

    def test_update_one_phone_add_no_label(self):
        self.contact.update_one("phone", "77777", mode="add")
        self.assertIn("77777",self.contact.phone["other"])

    def test_update_multiple(self):
        updates = [
            {'field': 'name', 'value': 'Alicia'},
            {'field': 'phone', 'value': '00000', 'label': 'work', 'mode': 'add'},
            {'field': 'email', 'value': 'new@mail.com', 'mode': 'replace'}
        ]
        self.contact.update_multiple(updates)
        self.assertEqual(self.contact.name, "Alicia")
        self.assertIn("00000", self.contact.phone["work"])
        self.assertEqual(self.contact.email["personal"], ['alice@example.com'])
        self.assertEqual(self.contact.email["work"], [])
        self.assertIn("other", self.contact.email)
        self.assertEqual(self.contact.email["other"], ["new@mail.com"])

    def test_invalid_field_update_raises(self):
        with self.assertRaises(ValueError):
            self.contact.update_one("unknown", "test")

    def test_invalid_match_argument_length(self):
        with self.assertRaises(ValueError):
            self.contact.matches('all', ('name',))  # too short

    def test_invalid_match_mode(self):
        with self.assertRaises(ValueError):
            self.contact.matches('invalid_mode', ('name', 'Alice'))


if __name__ == '__main__':
    unittest.main() #argv=[''], verbosity=2, exit=False