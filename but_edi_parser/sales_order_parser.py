import re
import datetime


class SalesOrderParser:
    def __init__(self, path):
        self._path = path
        self._content = open(self._path, 'r', errors='ignore').read()
        self._segments = self._content.split("'")
        
    def _get_value_from_re(self, pattern):
        value_list = re.findall(pattern, self._content)
        return value_list[0] if len(value_list) > 0 else None
    
    def _get_values_from_re(self, pattern):
        value_list = re.findall(pattern, self._content)
        return value_list if len(value_list) > 0 else None    
    
    def _parse_date(self, str_date):
        if str_date is None:
            return None
        return datetime.datetime.strptime(str_date, "%Y%m%d")
    
    def _parse_address(self, address_content):
        splitted_address = address_content.split('+')
        data = {
            'address_name': splitted_address[0].strip(),
            'address_line1': splitted_address[1].strip(),
            'address_line2': splitted_address[2].strip(),
            'city': splitted_address[3].strip(),
            'region': splitted_address[4].strip(),
            'pincode': splitted_address[5].strip(),
            'country': splitted_address[6].strip()
        } 
        return data
        
    def to_dict(self):
        property_methods = [
            method_name for method_name in dir(self)
            if not callable(getattr(self, method_name)) and method_name[0] != '_'
        ]
        data = {
            method_name: getattr(self, method_name) for method_name in property_methods
        }
        return data
        
    @property
    def order_ref(self):
        pattern = r'BGM\+220\+([\d]+)'
        return self._get_value_from_re(pattern)
    
    @property
    def transaction_date(self):
        pattern = r'DTM\+4:([\d]+)'
        date = self._get_value_from_re(pattern)
        return self._parse_date(date)

    @property
    def document_id(self):
        pattern = r'UNH\+(.+?)\+'
        return self._get_value_from_re(pattern)
    
    @property
    def document_date(self):
        pattern = r'DTM\+137:([\d]+)'
        date = self._get_value_from_re(pattern)
        return self._parse_date(date)    
    
    @property
    def delivery_date(self):
        pattern = r'DTM\+2:([\d]+)'
        date = self._get_value_from_re(pattern)
        return self._parse_date(date)
    
    @property
    def last_delivery_date(self):
        pattern = r'DTM\+63:([\d]+)'
        date = self._get_value_from_re(pattern)
        return self._parse_date(date)
    
    @property
    def customer_ean(self):
        pattern = r'NAD\+BY\+([\d]+)'
        return self._get_value_from_re(pattern) 
    
    @property
    def comments(self):
        pattern = r"FTX\+(AAI|DEL|ZZZ|INV)\++([^']*)'"
        return self._get_values_from_re(pattern)
    
    @property
    def customer(self):
        pattern = r"NAD\+BY\+([\d]+).+?\+(.+?)'"
        data = self._get_value_from_re(pattern)
        if data is None:
            return None
        res = {
            'ean': data[0],
            'address': self._parse_address(data[1])
        }
        return res
    
    @property
    def shipping(self):
        pattern = r"NAD\+DP\+([\d]+).+?\+(.+?)'"
        data = self._get_value_from_re(pattern)
        if data is None:
            return None
        res = {
            'ean': data[0],
            'address': self._parse_address(data[1])
        }
        return res    
    
    @property
    def contacts_and_addresses(self):
        pattern = r"NAD\+(BY|DP|SU|IV)\+([^']*)"
        return self._get_values_from_re(pattern)
    
    @property
    def order_currency(self):
        pattern = r"CUX\+2:([A-Z]*)"
        return self._get_value_from_re(pattern)
    
    @property
    def line_items(self):
        def _get_line_items_segments():
            pattern = r"(LIN.+?)UNS\+S"
            segments_content = self._get_values_from_re(pattern)
            if len(segments_content) == 0:
                raise ValueError("Line Items Not Found")
            segments_list = segments_content[0].split('LIN+')[1:]
            return segments_list
        line_items_segments = _get_line_items_segments()
        line_items = []
        for line_item_content in line_items_segments:
            line_item = LineItemParser(line_item_content)
            line_items.append(line_item.to_dict())

        return line_items
    
    @property
    def total(self):
        pattern = r"MOA\+86:([\d]+[\.\d]*)"
        return self._get_value_from_re(pattern)        
    

class LineItemParser:
    def __init__(self, line_item_content):
        self._content = line_item_content
        
    def _get_value_from_re(self, pattern):
        value_list = re.findall(pattern, self._content)
        return value_list[0] if len(value_list) > 0 else None        
    
    def _get_values_from_re(self, pattern):
        value_list = re.findall(pattern, self._content)
        return value_list if len(value_list) > 0 else None        
    
    def to_dict(self):
        property_methods = [
            method_name for method_name in dir(self)
            if not callable(getattr(self, method_name)) and method_name[0] != '_'
        ]
        data = {
            method_name: getattr(self, method_name) for method_name in property_methods
        }
        return data
    
    @property
    def line_number(self):
        pattern = r"^([\d]+)\+"
        return self._get_value_from_re(pattern)
        
    @property
    def ean(self):
        pattern = r"^[\d]+\++([\d]*)"
        return self._get_value_from_re(pattern)
    
    @property
    def sku(self):
        pattern = r"PIA.+?\+(.+?):"
        return self._get_value_from_re(pattern)
    
    @property
    def description(self):
        pattern = r"IMD\+F\+DSC\+:+(.+?)'"
        return self._get_value_from_re(pattern)
    
    @property
    def qty(self):
        pattern = r"QTY\+21:([\d]+)"
        return self._get_value_from_re(pattern)
    
    @property
    def price(self):
        pattern = r"PRI\+AAA:([\d]+[\.\d]*)"
        return self._get_value_from_re(pattern)
    
    @property
    def total(self):
        pattern = r"MOA\+203:([\d]+[\.\d]*)"
        return self._get_value_from_re(pattern)    
    
    @property
    def tax(self):
        pattern = r"ALC\+C\+([\d]*).+?MOA\+23:([\d]+[\.\d]*)"
        return self._get_value_from_re(pattern)
    
    @property
    def comments(self):
        pattern = r"FTX\+(AAI|ZZZ)\++(.+?)'"
        return self._get_values_from_re(pattern)        