import unittest
from src.contact_book import ContactBook
from src.contact import Contact

class TestContactBook(unittest.TestCase):

    def setUp(self):
        print("running setup")
        self.book = ContactBook()
        self.c1 = Contact(name="Alice", surname="Smith", phone={"mobile": ["1234"]})
        self.c2 = Contact(name="Bob", surname="Brown", email={"personal": ["bob@mail.com"]})
        self.c3 = Contact(name="Alice", surname="White", phone={"home": ["5678"]})
        self.book.add_contact(self.c1)
        self.book.add_contact(self.c2)
        self.book.add_contact(self.c3)

    def test_add_contact(self):
        self.assertEqual(self.book.count_contacts(), 3)
        self.assertEqual(self.c1.id, 1)
        self.assertEqual(self.c2.id, 2)
        self.assertEqual(self.c3.id, 3)
        self.assertEqual(self.book.next_id,4)
        self.assertTrue(self.book.modified)

    def test_add_contact_invalid(self):
        self.book.modified = False
        self.book.add_contact("not a contact")
        self.assertEqual(self.book.count_contacts(), 3)
        self.assertEqual(self.book.next_id,4)
        self.assertFalse(self.book.modified)

    def test_search_contacts_all_all(self):
        matches = self.book.search_contacts('all', 'all', ('name', 'Alice'))
        self.assertEqual(len(matches), 2)
        self.assertIn(matches[0].id, [1,3])
        self.assertIn(matches[1].id, [1,3])

    def test_search_contacts_all_first(self):
        matches = self.book.search_contacts('all', 'first', ('name', 'Alice'))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].surname, "Smith")

    def test_search_contacts_no_match(self):
        matches = self.book.search_contacts('all', 'all', ('name', 'Charlie'))
        self.assertEqual(len(matches), 0)

    def test_search_contacts_invalid_input(self):
        matches = self.book.search_contacts('all', 'invalid_input', ('name', 'Alice'))
        self.assertFalse(matches)

    def test_remove_contact(self):
        self.book.modified = False
        self.book.remove_contact(self.c1)
        self.assertEqual(len(self.book.contacts), 2)
        self.assertNotIn(self.c1, self.book.contacts)
        self.assertTrue(self.book.modified)

    def test_remove_contact_not_found(self):
        self.book.modified = False
        self.book.remove_contact(Contact("Jane","Doe"))
        self.assertEqual(len(self.book.contacts), 3)
        self.assertFalse(self.book.modified)

    def test_update_contact(self):
        self.book.modified = False
        updates = [{'field': 'address', 'value': '456 Street'}]
        self.book.update_contact(self.c1, updates)
        self.assertEqual(self.c1.address, '456 Street')
        self.assertTrue(self.book.modified)

    def test_update_contact_fail(self):
        self.book.modified = False
        updates = [{'field': 'missing_field', 'value': 'fail'}]
        self.book.update_contact(self.c1, updates)
        self.assertFalse(self.book.modified)

    def test_get_contact_by_id(self):
        result = self.book.get_contact_by_id(2)
        self.assertEqual(result.name, "Bob")

    def test_display_all_contacts(self):
        self.book.display_all_contacts()  # Just confirms it runs without error

    def test_get_contact_by_id(self):
        c = self.book.get_contact_by_id(1)
        self.assertEqual(c.id,1)
        self.assertEqual(c.name,"Alice")

    def test_get_contact_by_id_not_found(self):
        self.assertFalse(self.book.get_contact_by_id(5))

if __name__ == '__main__':
    unittest.main()
