import unittest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.contact_book_cli import ContactBookCLI
from src.contact_book import ContactBook, Contact


class TestContactBookCLI(unittest.TestCase):
    def setUp(self):
        print("running setup")
        self.cli = ContactBookCLI()
        self.cli.book = ContactBook()
        self.cli.saved = True

        # Define file name and path
        self.filename = "test_contacts"
        self.filepath = os.path.join(".", self.filename + ".json")

        # Create dummy existing JSON file
        with open(self.filepath, "w") as f:
            json.dump({"contacts": [{'name':'John','surname':'Doe','phone':{'mobile':['33854'],'home':['073323']}}]}, f)

    def tearDown(self):
        # Clean up the dummy file after test
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    @patch('builtins.input', side_effect=['3']) 
    @patch('builtins.print')
    def test_run_exit(self, mock_print, mock_input): #ok
        self.cli.run()
        mock_print.assert_any_call("Goodbye!")

    @patch('builtins.input', side_effect=['2','0','6','3'])
    @patch('builtins.print')
    def test_display_empty_book(self, mock_print, mock_input):
        self.cli.run()
        self.assertIsInstance(self.cli.book, ContactBook)
        
        mock_print.assert_any_call("No contacts to display.")

    @patch('builtins.input', side_effect=[
        #'3',       # find_contact_menu: mode
        'all',     # search_mode
        'first',   # display mode
        'name',    # field
        'Alice',   # value
        'n'     # end input
    ])
    @patch('builtins.print')
    def test_find_contact_menu1(self, mock_print, mock_input):
        contact1 = Contact(name='Alice', surname='Smith', phone={}, email={})
        contact2 = Contact(name='Alice', surname='White', phone={}, email={})
        self.cli.book.search_contacts = MagicMock()
        self.cli.book.contacts = [contact1,contact2]
        self.cli.find_contact_menu()
        self.cli.book.search_contacts.assert_called_once_with('all', 'first', ('name', 'Alice', None))

    @patch('builtins.input', side_effect=[
        #'3',       # find_contact_menu: mode
        'all',     # search_mode
        'all',   # display mode
        'name',    # field
        'Alice',   # value
        'n'     # end input
    ])
    @patch('builtins.print')
    def test_find_contact_menu2(self, mock_print, mock_input):
        contact1 = Contact(name='Alice', surname='Smith', phone={}, email={})
        contact2 = Contact(name='Alice', surname='White', phone={}, email={})
        self.cli.book.search_contacts = MagicMock()
        self.cli.book.contacts = [contact1,contact2]
        self.cli.find_contact_menu()
        self.cli.book.search_contacts.assert_called_once_with('all', 'all', ('name', 'Alice', None))

    @patch('builtins.input', side_effect=[
        #'3',       # find_contact_menu: mode
        'any',     # search_mode
        'all',   # display mode
        'surname',    # field
        'Smith',   # value
        'y',     # second criteria
        'name',    # field
        'Bob',   # value
        'n'     # end input
    ])
    @patch('builtins.print')
    def test_find_contact_menu3(self, mock_print, mock_input):
        contact1 = Contact(name='Alice', surname='Smith', phone={}, email={})
        contact2 = Contact(name='Bob', surname='White', phone={}, email={})
        self.cli.book.search_contacts = MagicMock()
        self.cli.book.contacts = [contact1,contact2]
        self.cli.find_contact_menu()
        self.cli.book.search_contacts.assert_called_once_with('any', 'all', ('surname', 'Smith', None), ('name', 'Bob', None))

    @patch("builtins.input", side_effect=[
        "test_contacts",  # filename
        ".",              # directory
        "y"               # confirm overwrite
    ])
    def test_overwrite_confirmed(self, mock_input):
        self.cli.save_book_menu()
        self.assertTrue(os.path.exists(self.filepath))

        with open(self.filepath, "r") as f:
            data = json.load(f)

        self.assertEqual(len(data["contacts"]),0)
        self.assertEqual(data["contacts"], [])

    @patch("builtins.input", side_effect=[
        "test_contacts",  # filename
        ".",              # directory
        "n"               # decline overwrite
    ])
    def test_overwrite_declined(self, mock_input):
        # Capture the original content
        with open(self.filepath, "r") as f:
            original_data = json.load(f)

        self.cli.save_book_menu()

        # File content should remain unchanged
        with open(self.filepath, "r") as f:
            data = json.load(f)
        self.assertEqual(data, original_data)

    @patch('builtins.input', side_effect=[
        #'5',              # save option
        'testfile',       # file name
        '/fake/path',     # path
    ])
    @patch('builtins.print')
    def test_save_book_menu(self, mock_print, mock_input):
        self.cli.book.save_to_json = MagicMock()
        self.cli.save_book_menu()
        self.cli.book.save_to_json.assert_called_with('/fake/path/testfile.json')
        self.assertTrue(self.cli.saved)

    @patch('builtins.input', side_effect=[
        'y'  # Confirm removal
    ])
    @patch('builtins.print')
    def test_remove_contact_menu_single_match_confirmed(self, mock_print, mock_input):
        contact = Contact(name='Jane', surname='Doe', phone={}, email={}, address='Test')
        contact.id = 1
        self.cli.book.contacts = [contact]
        self.cli.book.remove_contact = MagicMock()
        self.cli.find_contact_menu = MagicMock(return_value=[contact])

        self.cli.remove_contact_menu()

        self.cli.book.remove_contact.assert_called_once_with(contact)
        self.assertFalse(self.cli.saved)

    @patch('builtins.input', side_effect=[
        '1'  # ID to remove
    ])
    @patch('builtins.print')
    def test_remove_contact_menu_multiple_matches_by_id(self, mock_print, mock_input):
        contact1 = Contact(name='John', surname='Smith', phone={}, email={}, address='')
        contact1.id = 1
        contact2 = Contact(name='Jane', surname='Smith', phone={}, email={}, address='')
        contact2.id = 2

        self.cli.book.contacts = [contact1, contact2]
        self.cli.find_contact_menu = MagicMock(return_value=[contact1, contact2])
        self.cli.book.remove_contact = MagicMock()

        self.cli.remove_contact_menu()

        self.cli.book.remove_contact.assert_called_once()
        self.assertFalse(self.cli.saved)

    @patch('builtins.input', side_effect=[
        'invalid',  # invalid selection
        '6',        # exit
        'y'         # confirm
    ])
    @patch('builtins.print')
    def test_book_menu_invalid_selection(self, mock_print, mock_input):
        self.cli.book.count_contacts = MagicMock(return_value=0)
        self.cli.book_menu()
        mock_print.assert_any_call("Invalid selection. Try again.")

    @patch('builtins.input', side_effect=[
        'y'  # repeat search
    ])
    @patch('builtins.print')
    def test_update_contact_menu_no_match(self, mock_print, mock_input):
        self.cli.find_contact_menu = MagicMock(return_value=[])
        self.cli.update_contact_menu()  # Verifies it handles empty search

    @patch('builtins.input', side_effect=[
        '1',  # load from file
        '/invalid/path/file.json',
        '3'
    ])
    @patch('builtins.print')
    def test_add_contact_menu_invalid_file(self, mock_print, mock_input):
        self.cli.book.load_from_json = MagicMock(side_effect=FileNotFoundError("File not found"))

        try:
            self.cli.load_contact_book()
        except FileNotFoundError:
            self.fail("CLI should catch file errors, not raise them.")

    @patch('builtins.input', side_effect=[
        '1',              # choose load
        'failed_test.json',  # path
        '6',
        '3'
    ])
    @patch('builtins.print')
    def test_load_file_not_found(self, mock_print, mock_input):
        self.cli.run()
        self.assertEqual(len(self.cli.book.contacts),0)
        mock_print.assert_any_call("Goodbye!")

    @patch('builtins.input', side_effect=[
        '1',              # choose load
        'test_contacts.json',  # path
        '6',
        '3'
    ])
    @patch('builtins.print')
    def test_load_file(self, mock_print, mock_input):
        self.cli.run()
        self.assertEqual(len(self.cli.book.contacts),1)
        mock_print.assert_any_call("Goodbye!")

    @patch('builtins.input', side_effect=[
        'n'  # abort
    ])
    @patch('builtins.print')
    def test_remove_contact_menu_abort(self, mock_print, mock_input):
        contact1 = Contact(name='A', surname='B', phone={}, email={}, address='')
        contact1.id = 1
        contact2 = Contact(name='C', surname='D', phone={}, email={}, address='')
        contact2.id = 2

        self.cli.saved = True
        self.cli.book.contacts = [contact1, contact2]
        self.cli.find_contact_menu = MagicMock(return_value=[contact1, contact2])

        self.cli.remove_contact_menu()
        self.assertTrue(self.cli.saved)
        self.cli.book.remove_contact = MagicMock()
        self.cli.book.remove_contact.assert_not_called()

    @patch('builtins.input', side_effect=[
        '6',   # return to main menu
        'n',    # do not proceed
        '6',
        'y',
        '3'
    ])
    @patch('builtins.print')
    def test_unsaved_exit_aborted(self, mock_print, mock_input):
        self.cli.saved = False
        self.cli.book_menu()
        mock_input.assert_any_call("Unsaved changes. Exit without saving? (y/n): ") 


if __name__ == '__main__':

    unittest.main()
