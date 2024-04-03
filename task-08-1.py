from colorama import Fore, Back, Style
from collections import UserDict
import datetime
from functools import wraps
import pickle
import os

class Field:
    def __init__(self, value):
        if self.__is_valid(value):
            self.value = value
        else:
            raise ValueError
        
    def __is_valid(value):
        return True

    def __str__(self):
        return str(self.value)

class Name(Field):
    # реалізація класу

    def __init__(self, value):
        if self.__is_valid(value):
            self.value = value
        else:
            raise ValueError

    def __is_valid(self, value):
        if len(value)>0:
            return True
        raise ValueError

class Phone(Field):
    # Реалізовано валідацію номера телефону (має бути перевірка на 10 цифр).

    def __init__(self, value):
        if self.__is_valid(value):
            self.value = value
        else:
            raise ValueError

    def __is_valid(self, value):
        if value.isdigit() and len(value) == 10:
            return True
        raise ValueError

class Birthday(Field):
    def __init__(self, value):
        if self.__is_valid(value):
            self.value = value
        else:
            raise ValueError(f"birthday type error")

    def __is_valid(self, value):
        try:
            mydate = datetime.datetime.strptime(value, "%d.%m.%Y")
            value = mydate
            return True
        except ValueError:
            raise ValueError(f"Invalid date format. Use DD.MM.YYYY")
    
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        return (f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday.value if self.birthday else None}")

    def add_phone(self, phone) -> bool:
        my_phone = Phone(phone)
        found = False
        for phone_stored in self.phones:
            if phone_stored.value == phone:
                found = True
        if not found:
            self.phones.append(my_phone)
        return not found

    def remove_phone(self, phone):
        f = Phone(phone)
        for user_phone in self.phones:
            if user_phone.value == f.value:
                del self.phones[self.phones.index(user_phone)]

    def edit_phone(self, old_phone, new_phone):
        phone_old = Phone(old_phone)
        phone_new = Phone(new_phone)
        self.remove_phone(phone_old.value)
        self.add_phone(phone_new.value)

    def find_phone(self, phone):
        f = Phone(phone)
        for user_phone in self.phones:
            if f.value == user_phone.value:
                return user_phone            
        return None

    def add_birthday(self, birth_day):
        self.birthday = Birthday(birth_day)

    def update_birthday(self, new_birth_day):
        self.add_birthday(self, new_birth_day)

# --------------------
class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name] = record

    def find(self, name):
        for user_name, record in self.data.items():
            if user_name.value == name:
                return record
        return None

    def delete(self, name):
        for user_name, record in self.data.items():
            if user_name.value == name:
                del self.data[record.name]
                break

    def get_upcoming_birthdays(self) -> dict:

        birth_dict = UserDict()
        datecurr = datetime.datetime.now()
        current_year = datecurr.year

        # обробляємо перелік користувачів та дат
        for user_name, record in self.data.items():
            if record.birthday == None:
                continue

            birth_str = record.birthday.value
            birth_datetime = datetime.datetime.strptime(birth_str, "%d.%m.%Y")
            birth_datetime = birth_datetime.replace(year = current_year)

            # Перевірка, чи вже минув день народження в цьому році. Якщо минув, рухаємо дату на наступний рік.
            if birth_datetime.toordinal() < datecurr.toordinal():
                birth_datetime = birth_datetime.replace(year=current_year+1)
            date_diff = birth_datetime.toordinal() - datecurr.toordinal()

            if date_diff <= 7:
                wd = birth_datetime.weekday()
                if wd >= 5:
                    birth_datetime = birth_datetime + datetime.timedelta(days=7-wd)
                birth_dict[user_name.value] = datetime.datetime.strftime(birth_datetime, "%d.%m.%Y")

        return birth_dict

def input_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            if func.__name__ == "add_contact":
                return(f'{func.__name__} : use ADD [name] [phone]\nGive me name and phone (10 digits) please')
            elif func.__name__ == "change_contact":
                return(f'{func.__name__} : use CHANGE [name] [phone]\nGive me name and phone (10 digits) please')
            elif func.__name__ == "add-birthday":
                return(f'{func.__name__} : Enter the argument for the Birthday')
            return(f'{func.__name__} : Enter the argument for the command')
        except TypeError:
            if func.__name__ == "get_contact":
                return(f'{func.__name__} : use PHONE [name]\nGive me name please')
            return(f'{func.__name__} : Enter the argument for the command')
        except KeyError:
            if func.__name__ == "get_contact":
                return(f'{func.__name__} : Give me correct name please')
            return(f'{func.__name__} : Enter the argument for the command')
        except Exception as e:
            if func.__name__ == "get_contact":
                return(f'{func.__name__} : use PHONE [name]\nGive me name please')
            elif func.__name__ == "del_contact":
                return(f'{func.__name__} : use DEL [name]\nGive me name')
            elif func.__name__ == "print_contact":
                return(f'{func.__name__} : print_contact datetime error')           
            elif func.__name__ == "show-birthday":
                return(f'{func.__name__} : use SHOW-BIRTHDAY [name]\nGive me name please')          
            return(f'{func.__name__} : Enter the argument for the command')
    return wrapper

@input_error
def say_hello():
    return "How can I help you?"

@input_error
def parse_input(cmd_line:str):
    info = cmd_line.split(" ")
    info[0] = info[0].strip(" ").lower()
    return info

@input_error
def add_contact(args, book: AddressBook) -> str:
    name, phone = args
    record = book.find(name)
    if record == None:
        record = Record(name)
        message = "contact added"
    else:
        message = "contact's phone updated"
    if not record.add_phone(phone):
        message = "contact's phone already exist"
    book.add_record(record)
    return message

@input_error
def change_contact(args, book: AddressBook) -> str:
    name, phone_old, phone_new = args
    record = book.find(name)   
    if record is None:
        message = "contact not found"
    else:
        found_id = 0
        message = "contact's phone not found and not updated"
        while found_id<len(record.phones):
            if record.phones[found_id].value == phone_old:
                record.phones[found_id] = Phone(phone_new)
                message = "contact's phone updated"
                break
            else:
                found_id +=1
#        record.edit_phone(old_phone, phone)
    return message      

@input_error
def del_contact(args, book: AddressBook) -> str:
    name = args[0]
    record = book.find(name)
    if record == None:
        message = "contact not found"
    else:
        book.delete(name)
        message = "contact deleted"
    return message      

@input_error
def print_contact(book: AddressBook):
    items = list()
    for name, record in book.data.items():
        s = f'{name.value} : '
        s+= f'phones: {'; '.join(p.value for p in record.phones)}'
        if record.birthday != None:
            s+= ', birthday: '+record.birthday.value
        items.append(s)
    return items

@input_error
def get_contact(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record == None:
        return "contact not found"
    plist = []
    for i in range(0, len(record.phones)):
        plist.append(record.phones[i].value)
    return plist


@input_error
def add_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    record.birthday = Birthday(args[1])
    return "birthday added"

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record.birthday is None:
        return "birthday not set"
    else:
        return record.birthday.value

@input_error
def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()

def curr_date():
    dt = datetime.datetime.now()
    return dt.strftime("%Y-%m-%d")

def curr_time():
    dt = datetime.datetime.now()
    return dt.strftime("%H:%M:%S")

import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


@input_error
def main():

    #fn
    adrbookname = "addressbook.pkl"
    # Створення нової адресної книги
    
    if  os.path.exists(adrbookname):
        book = load_data(adrbookname)
    else:
        book = AddressBook()

    CLI_header = '****************************************\n'\
                 '**         command line assistant     **\n'\
                 '****************************************\n'
    
    print(Fore.GREEN, CLI_header, Style.RESET_ALL, sep="")
    print(say_hello())
    while True:
        print(Fore.CYAN, "Type here your command", Style.RESET_ALL, end="")
        text = input(': ')
        cmds = parse_input(text)
        cmds[0]=cmds[0].lower()
        if cmds[0]=='help':
            print(CLI_header)
            print('type "list" to see all commands')
        elif cmds[0]=='list':
            print(  'bye, exit, close\t- exit from assistant\n'\
                    'all\t\t\t- print all contact book\n'\
                    'add name phone\t\t- add phone to contact list\n'\
                    'add-birthday name date\t- add or update birthday (date in format DD.MM.YYYY)\n'\
                    'del name\t\t- delete contact from list\n'\
                    'change name phone1 phone2\t- update phone number for name\n'\
                    'show-birthday name\t- show Birthday for name\n'\
                    'birthdays\t\t- display all upcoming birthdays in a next 7 days\n'\
                    'phone name\t\t- get phone number for name\n'\
                    'hello\t\t\t- greetings from bot\n'\
                    'help\t\t\t- get help\n'\
                    'date\t\t\t- get current date\n'\
                    'time\t\t\t- get current time\n'\
                    'list\t\t\t- get commands list')
        elif cmds[0] in ['bye','exit','close']:
            print(Fore.YELLOW, 'good bye', Style.RESET_ALL)
            break
        elif cmds[0]=='hello':
            print(say_hello())
        elif cmds[0]=='add':
            print(add_contact(cmds[1:], book))
        elif cmds[0]=='del':
            print(del_contact(cmds[1:], book))
        elif cmds[0]=='change':
            print(change_contact(cmds[1:], book))
        elif cmds[0]=='phone':
            us_list = get_contact(cmds[1:], book)
            if len(us_list) == 0:
                print(Fore.MAGENTA, 'no phones', Style.RESET_ALL)
            else:
                print('phone list:')
                for line_cont in us_list:
                    print(line_cont)
        elif cmds[0]=='all':
            us_list = print_contact(book)
            if len(us_list) == 0:
                print(Fore.MAGENTA, 'no contacts', Style.RESET_ALL)
            else:
                print('contact list:')
                for line_cont in us_list:
                    print(line_cont)
        elif cmds[0]=='add-birthday':
            print(add_birthday(cmds[1:], book))
        elif cmds[0]=='show-birthday':
            print(show_birthday(cmds[1:], book))
        elif cmds[0]=='birthdays':
            us_list=birthdays(book)
            if len(us_list)==0:
                print(Fore.MAGENTA, 'No upcoming birthdays, try again later or use ALL command to see birthdays', Style.RESET_ALL)
            else:
                print('nearest birthdays in a next 7 days:')
                for name, date in us_list.items():
                    print(f'{name}:\t{date}')
        elif cmds[0]=='date':
            print(curr_date())
        elif cmds[0]=='time':
            print(curr_time())
        else:
            print(Fore.RED, f'I don\'t understand {cmds[0]}', Style.RESET_ALL)

    #pkl
    save_data(book, adrbookname)

if __name__ == "__main__":
    main()
