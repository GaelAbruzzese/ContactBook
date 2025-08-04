import json
import csv
from contact import Contact  # adjust import path as needed

class ContactBook:
    """
    A class to store and manage multiple Contact objects.
    """

    def __init__(self):
        self.contacts: list[Contact] = []
        self.next_id: int = 1
        self.modified: bool = False  # Track unsaved changes

    def __repr__(self):
        return f"<ContactBook: {len(self.contacts)} contacts>"

    def __str__(self):
        return f"ContactBook with {len(self.contacts)} contacts"

    def __eq__(self,other):
        return all(c in self.contacts for c in other.contacts) and (c in other.contacts for c in self.contacts)

    def count_contacts(self) -> int:
        """
        Return and print the total number of contacts.
        """
        return len(self.contacts)

    def add_contact(self, contact: Contact):
        """
        Add a contact to the book and assign it a unique ID.
        """
        if isinstance(contact,Contact):
          contact.id = self.next_id
          self.contacts.append(contact)
          self.next_id += 1
          self.modified = True
        else:
          print("The object is not a contact. Contact not added.")

    def search_contacts(self, how='all', show='all', *criteria) -> list[Contact] | bool:
        """
        Return a list of contacts matching the given criteria.
        Does not display results — for CLI to handle.
        """
        if show == 'first':
          for c in self.contacts:
            if c.matches(how, *criteria):
              return [c]
          return []
        elif show == 'all':
          return [c for c in self.contacts if c.matches(how, *criteria)]
        else:
          print("Invalid input. Show can be 'all' or 'first'.")
          return False

    def remove_contact(self, contact: Contact): # check integration with CLI (search contact first)
        """
        Remove a contact from the book.
        """
        if isinstance(contact,Contact):
            if contact in self.contacts:
                self.contacts.remove(contact)
                self.modified = True
            else:
                print("Contact not found in the book.")
        else:
            print("The object is not a contact. Contact not removed.")

    def update_contact(self, contact: Contact, updates: list[dict]): # check integration with CLI (search contact first)
        """
        Update a given contact with one or more fields.
        """
        try:
            res = contact.update_multiple(updates)
            if res: #if aborted, returns False; else True
                self.modified = True
        except Exception as e:
            print(f"Update failed. Exception: {e}")

    def save_to_json(self, file_path: str): 
        """
        Save the contact book to a JSON file.
        This function does not check if the file ovrewrites an existing one, this is handled in the CLI.
        """
        try:
            data = {"contacts": [c.__dict__ for c in self.contacts]}
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            self.modified = False
            print(f"Contact book saved to {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")

    def load_from_json(self, file_path: str):
        """
        Load contacts from a JSON file.
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            for entry in data.get("contacts", []):
                contact = Contact(
                    name=entry.get("name", ""),
                    surname=entry.get("surname", ""),
                    phone=entry.get("phone", {}),
                    email=entry.get("email", {}),
                    address=entry.get("address", "")
                )
                contact.id = self.next_id
                self.contacts.append(contact)
                self.next_id += 1
            self.modified = False # True?
            print(f"{len(self.contacts)} contacts loaded from {file_path}")
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"Error loading file: {e}")

    def display_all_contacts(self):
        """
        Display all contacts.
        """
        if not self.contacts:
            print("No contacts to display.")
            return

        print(f"\nThere are {self.count_contacts()} contacts.\n")
        for contact in self.contacts:
            contact.display()

    def get_contact_by_id(self, id: int) -> Contact | bool:
        """
        Retrieve a contact by its ID.
        """
        for c in self.contacts:
            if c.id == id:
                return c
        return False


'''
consider adding



# --- CSV EXPORT ---
    def export_to_csv(self, file_path: str):
        """
        Export all contacts to a CSV file.
        Each phone/email label is stored as semicolon-separated entries.
        """
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Surname", "Address", "Phones", "Emails"])

            for contact in self.contacts:
                phones = "; ".join(
                    f"{label}:{','.join(numbers)}" for label, numbers in contact.phone.items() if numbers
                )
                emails = "; ".join(
                    f"{label}:{','.join(emails)}" for label, emails in contact.email.items() if emails
                )

                writer.writerow([
                    contact.id, contact.name, contact.surname, contact.address, phones, emails
                ])

        print(f"Exported {len(self.contacts)} contacts to {file_path}")

    # --- CSV IMPORT ---
    def import_from_csv(self, file_path: str):
        """
        Import contacts from a CSV file.
        Assumes labels and values are separated by ':' and values by ','.
        """
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    phone_dict = {}
                    email_dict = {}

                    # Parse phones
                    phone_data = row.get("Phones", "")
                    for group in phone_data.split(";"):
                        if ":" in group:
                            label, nums = group.strip().split(":", 1)
                            phone_dict[label.strip()] = [n.strip() for n in nums.split(",")]

                    # Parse emails
                    email_data = row.get("Emails", "")
                    for group in email_data.split(";"):
                        if ":" in group:
                            label, ems = group.strip().split(":", 1)
                            email_dict[label.strip()] = [e.strip() for e in ems.split(",")]

                    contact = Contact(
                        name=row.get("Name", ""),
                        surname=row.get("Surname", ""),
                        address=row.get("Address", ""),
                        phone=phone_dict,
                        email=email_dict
                    )
                    self.add_contact(contact)

            print(f"Imported contacts from {file_path}")

        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"Error importing from CSV: {e}")

    # --- TXT EXPORT ---
    def export_to_txt(self, file_path: str):
        """
        Export all contacts to a TXT file in readable format.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for contact in self.contacts:
                    f.write(f"[{contact.id}] - {contact.name} {contact.surname}\n")

                    for label, numbers in contact.phone.items():
                        if numbers:
                            f.write(f"  {label.title()} Phones: {', '.join(numbers)}\n")

                    for label, emails in contact.email.items():
                        if emails:
                            f.write(f"  {label.title()} Emails: {', '.join(emails)}\n")

                    if contact.address:
                        f.write(f"  Address: {contact.address}\n")
                    f.write("-" * 40 + "\n")

            print(f"Exported {len(self.contacts)} contacts to {file_path}")

        except Exception as e:
            print(f"Error exporting to TXT: {e}")



import csv

file_path='test_book.csv'
with open(file_path, 'w', newline='') as csvfile:
    fieldnames = ['name', 'surname', 'phone', 'email', 'address']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for contact in test_file:
        phone_str = "; ".join([f"{label}: {', '.join(nums)}" for label, nums in contact['phone'].items()])
        email_str = "; ".join([f"{label}: {', '.join(emails)}" for label, emails in contact['email'].items()])
        
        writer.writerow({
            'name': contact['name'],
            'surname': contact['surname'],
            'phone': phone_str,
            'email': email_str,
            'address': contact['address']
        })

print(f"Contacts saved to CSV: {file_path}")

def save_contacts_as_txt(file_path='test_contact_book.txt'):
    with open(file_path, 'w') as txtfile:
        for contact in contacts:
            phone_str = "; ".join([f"{label}: {', '.join(nums)}" for label, nums in contact['phone'].items()])
            email_str = "; ".join([f"{label}: {', '.join(emails)}" for label, emails in contact['email'].items()])
            txtfile.write(f"Name: {contact['name']} {contact['surname']}\n")
            txtfile.write(f"Phone(s): {phone_str}\n")
            txtfile.write(f"Email(s): {email_str}\n")
            txtfile.write(f"Address: {contact['address']}\n")
            txtfile.write("-" * 40 + "\n")

    print(f"Contacts saved to TXT: {file_path}")

def read_contacts_from_csv(file_path: str):
    contacts = []
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            phone = {}
            email = {}

            if row['phone']:
                for item in row['phone'].split(";"):
                    label, *nums = item.strip().split(":")
                    phone[label.strip()] = [n.strip() for n in ":".join(nums).split(",")]

            if row['email']:
                for item in row['email'].split(";"):
                    label, *emails = item.strip().split(":")
                    email[label.strip()] = [e.strip() for e in ":".join(emails).split(",")]

            contact = {
                "name": row['name'].strip(),
                "surname": row['surname'].strip(),
                "phone": phone,
                "email": email,
                "address": row['address'].strip()
            }
            contacts.append(contact)
    return contacts

def read_contacts_from_txt(file_path: str):
    contacts = []
    with open(file_path, 'r') as f:
        lines = f.readlines()

    current_contact = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('---'):
            if current_contact:
                contacts.append(current_contact)
                current_contact = {}
            continue

        if line.startswith("Name:"):
            parts = line[len("Name:"):].strip().split()
            current_contact["name"] = parts[0]
            current_contact["surname"] = " ".join(parts[1:])
        elif line.startswith("Phone(s):"):
            phone_data = line[len("Phone(s):"):].strip()
            phone = {}
            for item in phone_data.split(";"):
                if ":" in item:
                    label, numbers = item.split(":", 1)
                    phone[label.strip()] = [n.strip() for n in numbers.strip().split(",")]
            current_contact["phone"] = phone
        elif line.startswith("Email(s):"):
            email_data = line[len("Email(s):"):].strip()
            email = {}
            for item in email_data.split(";"):
                if ":" in item:
                    label, addresses = item.split(":", 1)
                    email[label.strip()] = [e.strip() for e in addresses.strip().split(",")]
            current_contact["email"] = email
        elif line.startswith("Address:"):
            current_contact["address"] = line[len("Address:"):].strip()

    # Append last contact if file doesn't end with separator
    if current_contact:
        contacts.append(current_contact)

    return contacts

'''
