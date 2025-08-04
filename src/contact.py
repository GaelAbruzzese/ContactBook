from dataclasses import dataclass, field
from typing import Optional
import re

# Default factories for phone/email fields
def default_phone_dict() -> dict:
    return {'home': [], 'mobile': [], 'work': [], 'other': []}

def default_email_dict() -> dict:
    return {'personal': [], 'work': [], 'other': []}

@dataclass
class Contact:
    """
    A class to store and manage a single contact entry.
    Includes support for multiple phone numbers and emails with labeled categories.

    Example contact:
    {
      "name": "Alice",
      "surname": "Smith",
      "phone": {
        "home": ["1234","5678"],
        "mobile": ["1234567890"],
      },
      "email": {
        "personal": ["alice@example.com"]
      },
      "address": "123 Main Street"
    }
    """
    name: str
    surname: str
    phone: dict[str, list[str]] = field(default_factory=default_phone_dict)
    email: dict[str, list[str]] = field(default_factory=default_email_dict)
    address: str = ""
    id: Optional[int] = field(default=None, init=False, compare=False)

    EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+(\.\w+)*$" # regex for email format, requires a @ not at the beginning or end, requires a domain. No checks on the existance of the domain.

    def __post_init__(self):
        # Normalize name and surname
        if isinstance(self.name,str) and isinstance(self.surname,str):
            self.name = self.name.capitalize()
            self.surname = self.surname.capitalize()
        else:
            raise TypeError("Invalide type for name and surname.")

        # Normalize phone input
        if isinstance(self.phone, (str,int)):
            self.phone = {"other": [str(self.phone) if str(self.phone).isdigit() else "error"]}
        elif isinstance(self.phone, list):
            self.phone = {"other": [str(x) if str(x).isdigit() else "error" for x in self.phone]}
        elif isinstance(self.phone, dict):
            for label, numbers in self.phone.items():
                self.phone[label] = [str(n) if str(n).isdigit() else "error" for n in (numbers if isinstance(numbers, list) else [numbers])]
        else:
            raise TypeError("Invalid type for phone number.") # do I want to raise an error or just a warning?
        if any(x=="error" for x_l in self.phone.values() for x in x_l):
            print("Some phone numbers were not numeric and could not be loaded. They have been stored as 'error'.\nThese can be found using the search function and searching for the value 'error'.")

        # Normalize email input
        if isinstance(self.email, str):
            self.email = {"other": [self.email if re.match(self.EMAIL_REGEX,self.email) else 'error']}
        elif isinstance(self.email,list):
            self.email = {"other": [str(e) if re.match(self.EMAIL_REGEX,e) else 'error' for e in self.email]}
        elif isinstance(self.email, dict):
            for label, emails in self.email.items():
                self.email[label] = [str(e) if re.match(self.EMAIL_REGEX,e) else 'error' for e in (emails if isinstance(emails, list) else [emails])]
        else:
            raise TypeError("Invalid type for email.")
        if any(x=="error" for x_l in self.email.values() for x in x_l):
            print("Some emails did not respect the email format (text_or_puntuation@text.text-optional.text) and could not be loaded. They have been stored as 'error'.\nThese can be found using the search function and searching for the value 'error'.")

    def name_eq(self,other):
        return self.name==other.name and self.surname==other.surname
    
    def display(self):
        """Prints a readable representation of the contact."""
        print(f"\n[{self.id}] - {self.name} {self.surname}")
        for label, numbers in self.phone.items():
            if numbers:
                print(f"  {label.title()} Phones: {', '.join(numbers)}")
        for label, emails in self.email.items():
            if emails:
                print(f"  {label.title()} Emails: {', '.join(emails)}")
        if self.address:
            print(f"  Address: {self.address}")
        print("-" * 40)

    def one_field_match(self, field_name: str, search_value: str, label: str = None) -> bool:
        """
        Checks if a value matches in a given field.
        Supports optional labels for phone/email fields.
        """
        if not hasattr(self, field_name):
            raise ValueError("Invalid field.")

        field_value = getattr(self, field_name)

        if isinstance(field_value, dict):
            if label:
                return search_value in field_value.get(label, [])
            else:
                return any(search_value in values for values in field_value.values())

        elif isinstance(field_value, str):
            return search_value.lower() == field_value.lower()

        return False

    def matches(self, how='all', *args) -> bool:
        """
        Checks if the contact matches multiple criteria.
        Each arg must be a tuple of 2 or 3 elements: (field, value[, label])
        Modes:
            - 'all': All criteria must match
            - 'any': At least one must match
        """
        if any(len(arg)<2 or len(arg)>3 for arg in args):
          raise ValueError("Invalid length fo matching criteria. Provide filed name and value, optional label.")

        if how == 'all':
            return all(
                self.one_field_match(*arg) if len(arg) == 2 else self.one_field_match(*arg[:2], label=arg[2])
                for arg in args
            )
        elif how == 'any':
            return any(
                self.one_field_match(*arg) if len(arg) == 2 else self.one_field_match(*arg[:2], label=arg[2])
                for arg in args
            )
        else:
            raise ValueError("Invalid match mode. Use 'all' or 'any'.")

    def update_one(self, field_name: str, new_value, label: str = 'other', mode: str = "replace") -> bool:
        """
        Update a field in the contact.
        For dict fields (phone/email), support 'add' or 'replace' under labels.
        """

        #validation for phone numbers and email addresses
        if field_name == 'phone':
            if not str(new_value).isdigit():
              print("Invalid phone number. Operation aborted.")
              return False
            if label not in ['other','home', 'mobile', 'work']:
              print("Invalid label. Operation aborted.")
              return False

        elif field_name == 'email':
            if not re.match(self.EMAIL_REGEX,new_value):
              print("Invalid email format. Operation aborted.")
              return False
            if label not in ['other','personal', 'work']:
              print("Invalid label. Operation aborted.")
              return False

        if field_name in ['name', 'surname', 'address']:
            setattr(self, field_name, new_value)
            return True

        elif field_name in ['phone', 'email']:
            target_dict = getattr(self, field_name)
       
            if mode == 'replace':
                target_dict[label] = [str(new_value)] if isinstance(new_value, (str,int)) else [str(v) for v in new_value] # does this read lists? will it transform lists into strings?
                return True
            elif mode == 'add':
                target_dict.setdefault(label, [])
                target_dict[label].extend([str(new_value)] if isinstance(new_value, (str,int)) else [str(v) for v in new_value])
                return True

        else:
            raise ValueError("Invalid field name.")

    def update_multiple(self, updates: list[dict]):
        """
        Update multiple fields in one call.
        Each item must be a dict with keys: field, value, and optionally label, mode
        """
        res = []
        for update_item in updates:
            if 'field' not in update_item or 'value' not in update_item:
                continue
            res.append(self.update_one(
                field_name=update_item['field'],
                new_value=update_item['value'],
                label=update_item.get('label','other'),
                mode=update_item.get('mode', 'replace')
            ))
        return any(res)
