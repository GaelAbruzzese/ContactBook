import os
from contact_book import ContactBook
from contact import Contact

class ContactBookCLI:
    def __init__(self):
        self.book = None
        self.saved = True

    def run(self):
        while True:
            print("\nWelcome to your Contact Book manager!")
            print("1. Load an existing Contact Book")
            print("2. Create a new Contact Book")
            print("3. Exit")

            selection = input("Select an option: ").strip()

            if selection == '1':
                self.load_contact_book()
            elif selection == '2':
                self.book = ContactBook()
                print("\nA new contact book has been created.")
                self.book_menu()
            elif selection == '3':
                print("Goodbye!")
                break
            else:
                print("Invalid selection. Try again.")

    def load_contact_book(self):
        path = input("Provide JSON file path: ").strip()
        try:
            self.book = ContactBook()
            self.book.load_from_json(path)
            self.saved = True
            self.book_menu()
        except Exception as e:
            print(f"Error loading contact book: {e}")

    def book_menu(self):
        while True:
            n = self.book.count_contacts()
            if n==0:
              print("\nYour contact book is empty, you have limited menu options.")
            print("\n--- Main Menu ---")
            print("0. Display contacts")
            print("1. Add contact")
            if n > 0:
                print("2. Update contact")
                print("3. Find contact")
                print("4. Remove contact")
            print("5. Save book")
            print("6. Return to main menu")

            selection = input("Choose an option: ").strip()

            if selection == '0':
                self.book.display_all_contacts()
            elif selection == '1':
                self.add_contact_menu()
            elif selection == '2' and n > 0:
                self.update_contact_menu()
            elif selection == '3' and n > 0:
                self.find_contact_menu()
            elif selection == '4' and n > 0:
                self.remove_contact_menu()
            elif selection == '5':
                self.save_book_menu()
            elif selection == '6':
                if not self.saved:
                    confirm = input("Unsaved changes. Exit without saving? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                break
            else:
                print("Invalid selection. Try again.")

    def add_contact_menu(self):
        print("\n--- Add Contact ---")
        name = input("First name: ").strip()
        surname = input("Surname: ").strip()
        address = input("Address (optional): ").strip()

        phone = {}
        while True:
            if input("Do you want to add a new number? (y/n) > ").strip().lower()!='y':
                break
            label = input("Phone label (work/home/mobile/other) or enter to continue without a label: ").strip().lower()
            number = input("Phone number: ").strip().split(' ')
            phone.setdefault(label, []).extend(number)

        email = {}
        while True:
            if input("Do you want to add a new email address? (y/n) > ").strip().lower()!='y':
                break
            label = input("Email label (personal/work/other or enter to continue without a label): ").strip().lower()
            mail = input("Email address: ").strip().split(' ')
            email.setdefault(label, []).extend(mail)

        contact = Contact(name=name, surname=surname, phone=phone, email=email, address=address)
        if contact in self.book.contacts and input("This contact already exists. Do you want to add in again? (y/n) > ").strip().lower()!='y': # it doesn't work, need to define equality detweeen contacts
                return
        elif any(contact.name_eq(c) for c in self.book.contacts):
            if input(f"A contact with this name already exists. Press 'y' to add {contact.name} {contact.surname} as a new contact. Press 'x' to return to main menu and update the existing contact intead.").strip().lower()!='y':
                return
        self.book.add_contact(contact)
        self.saved = False
        print(f"Contact added with ID: {contact.id}")

    def find_contact_menu(self):
        print("\n--- Find Contact ---")
        mode = input("Search mode ('all' to match all criteria or 'any' to match at least one criteria): ").strip().lower()
        show = input("Display mode ('first' to display the first match or 'all' to display all matches): ").strip().lower()

        criteria = []
        valid_fields = ['name', 'surname', 'phone', 'email', 'address']

        while True:
            field = input(f"Field to search ({valid_fields}): ").strip().lower()
            if field not in valid_fields:
                print("Invalid field.")
                continue
            label = None
            if field in ['phone', 'email']:
                label = input("Label (optional): ").strip().lower() or None
            value = input("Search value: ").strip() or ''
            criteria.append((field, value, label))
            if input("Do you want to add another serch criteria? (y/n) > ").strip().lower()!='y':
                break

        matches = self.book.search_contacts(mode, show, *criteria)
        print(f"\nContacts found: {len(matches)}\n")
        for c in matches:
            c.display()

    def remove_contact_menu(self):
        print("\n--- Remove Contact ---")
        matches = self.find_contact_menu()
        if not matches:
            print("No matches found.")
            return

        if len(matches) == 1:
            matches[0].display()
            confirm = input(f"Remove contact ID {matches[0].id}? (y/n): ").strip().lower()
            if confirm == 'y':
                self.book.remove_contact(matches[0])
                self.saved = False
                print("Contact removed.")
            return
        else:
            ids = input("Enter ID(s) to remove, 'all' or 'n' to exit: ").strip()
            to_remove = []
            if ids=='n':
                return
            elif ids == 'all':
                to_remove = matches
            else:
                id_list = ids.split(' ')
                to_remove = [c for c in matches if str(c.id) in id_list]
            for c in to_remove:
                self.book.remove_contact(c)
            self.saved = False
            print(f"Removed {len(to_remove)} contact(s).")

    def update_contact_menu(self):
        print("\n--- Update Contact ---")
        matches = self.find_contact_menu()
        if not matches:
            print("No matches found.")
            return

        if len(matches) > 1:
            for c in matches:
                c.display()
            id_ = input("Enter ID of contact to update: ").strip()
            selected = next((c for c in matches if str(c.id) == id_), None)
            if not selected:
                print("Invalid ID.")
                return
        else:
            selected = matches[0]

        print("Enter new values (leave blank to skip):")
        updates = {}
        for field in ['name', 'surname', 'address']:
            new_val = input(f"New {field}: ").strip()
            if new_val:
                updates[field] = new_val

        # Phone updates
        update_phones = input("Update phone numbers? (y/n): ").strip().lower() # change this
        if update_phones == 'y':
            updates['phone'] = {}
            while True:
                label = input("Phone label (enter to skip): ").strip()
                number = input("Phone number: ").strip()
                updates['phone'].setdefault(label, []).append(number)
                if input("Do you want to update another phone number? (y/n) > ").strip().lower()!='y':
                    break

        update_emails = input("Update email addresses? (y/n): ").strip().lower()
        if update_emails == 'y':
            updates['email'] = {}
            while True:
                label = input("Email label (enter to skip): ").strip()
                email = input("Email address: ").strip()
                updates['email'].setdefault(label, []).append(email)
                if input("Do you want to update another email address? (y/n) > ").strip().lower()!='y':
                    break

        self.book.update_contact(selected, updates)
        self.saved = False
        print("Contact updated.")

    def save_book_menu(self):
        filename = input("File name (no extension): ").strip()
        path = input("Directory to save the file: ").strip()
        full_path = os.path.join(path, f"{filename}.json")

        if os.path.exists(full_path):
          if input(f"The file '{full_path}' already exists. Overwrite? (y/n): ").strip().lower()!='y':
            print("Save aborted.")
            return False
        try:
            self.book.save_to_json(full_path)
            self.saved = True
            print(f"Book saved to {full_path}")
        except Exception as e:
            print(f"Error saving book: {e}")

if __name__ == '__main__':
    cli = ContactBookCLI()
    cli.run() # check this