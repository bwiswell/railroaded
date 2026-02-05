from typing import Optional

import seared as s


@s.seared
class Agency(s.Seared):
    '''
    A GTFS dataclass model for records found in `agency.txt`. Identifies a 
    transit agency.

    Attributes:
        id (str):
            the unique ID of the transit agency
        email (Optional[str]):
            the customer service email of the transit agency
        fare_url (Optional[str]):
            the URL of a fare or ticket website for the transit agency
        lang (Optional[str]):
            the primary language used by the transit agency
        name (str):
            the name of the transit agency
        phone (Optional[str]):
            the voice telephone number for the transit agency
        timezone (str):
            the timezone where the transit agency is located
        url (str):
            the URL of the transit agency
    '''
    
    ### ATTRIBUTES ###
    # Model ID
    id: str = s.Str(data_key='agency_id', missing='')
    '''the unique ID of the transit agency'''
    
    # Required fields
    name: str = s.Str(data_key='agency_name', required=True)
    '''the name of the transit agency'''
    timezone: str = s.Str(data_key='agency_timezone', required=True)
    '''the timezone where the transit agency is located'''
    url: str = s.Str(data_key='agency_url', required=True)
    '''the URL of the transit agency'''

    # Optional fields
    email: Optional[str] = s.Str(data_key='agency_email')
    '''the customer service email of the transit agency'''
    fare_url: Optional[str] = s.Str(data_key='agency_fare_url')
    '''the URL of a fare or ticket website for the transit agency'''
    lang: Optional[str] = s.Str(data_key='agency_lang')
    '''the primary language used by the transit agency'''
    phone: Optional[str] = s.Str(data_key='agency_phone')
    '''the voice telephone number for the transit agency'''