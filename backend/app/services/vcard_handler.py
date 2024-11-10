# backend/app/services/vcard_handler.py
from typing import List, Dict, Optional
from datetime import datetime
import vobject
import base64
from ..models.models import Contact
from ..schemas.contact import ContactCreate
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

class VCardHandler:
    @staticmethod
    def parse_vcard(vcard_content: str) -> List[Dict]:
        """Parse VCard content and return a list of contact dictionaries"""
        contacts = []
        
        # Split content into individual vcards if multiple exist
        vcard_parts = vcard_content.split("BEGIN:VCARD")
        
        for part in vcard_parts:
            if not part.strip():
                continue
                
            try:
                vcard = vobject.readOne("BEGIN:VCARD" + part)
                contact_data = {}
                
                # Basic information
                if hasattr(vcard, 'n') and vcard.n.value:
                    contact_data['last_name'] = vcard.n.value.family
                    contact_data['first_name'] = vcard.n.value.given
                
                if hasattr(vcard, 'org') and vcard.org.value:
                    contact_data['company'] = vcard.org.value[0]
                
                # Handle multiple email addresses
                if hasattr(vcard, 'email'):
                    for email in vcard.email_list:
                        email_type = email.type_param and email.type_param[0].lower()
                        if email_type == 'work':
                            contact_data['work_email'] = email.value
                        elif email_type == 'home':
                            contact_data['home_email'] = email.value
                        elif email_type == 'other':
                            contact_data['other_email'] = email.value
                        else:
                            contact_data['email'] = email.value
                
                # Handle multiple phone numbers
                if hasattr(vcard, 'tel'):
                    for tel in vcard.tel_list:
                        tel_type = tel.type_param and tel.type_param[0].lower()
                        if tel_type == 'cell':
                            contact_data['mobile_phone'] = tel.value
                        elif tel_type == 'home':
                            contact_data['home_phone'] = tel.value
                        elif tel_type == 'work':
                            contact_data['work_phone'] = tel.value
                        elif tel_type == 'main':
                            contact_data['main_phone'] = tel.value
                        elif tel_type == 'iphone':
                            contact_data['iphone'] = tel.value
                        else:
                            contact_data['other_phone'] = tel.value
                
                # Handle addresses
                if hasattr(vcard, 'adr'):
                    for adr in vcard.adr_list:
                        adr_type = adr.type_param and adr.type_param[0].lower()
                        address_parts = [
                            p for p in [
                                adr.value.street,
                                adr.value.city,
                                adr.value.region,
                                adr.value.code,
                                adr.value.country
                            ] if p
                        ]
                        address = ', '.join(address_parts)
                        
                        if adr_type == 'home':
                            contact_data['home_address'] = address
                        elif adr_type == 'work':
                            contact_data['work_address'] = address
                
                # Handle birthday
                if hasattr(vcard, 'bday'):
                    try:
                        contact_data['birthday'] = datetime.strptime(
                            vcard.bday.value,
                            "%Y-%m-%d"
                        )
                    except ValueError:
                        pass
                
                # Handle photo
                if hasattr(vcard, 'photo'):
                    try:
                        photo_data = vcard.photo.value
                        # Check file size (5MB limit)
                        if len(photo_data) <= 5 * 1024 * 1024:
                            contact_data['photo'] = photo_data
                    except Exception:
                        pass
                
                # Handle notes
                if hasattr(vcard, 'note'):
                    contact_data['notes'] = vcard.note.value
                
                # Handle URLs
                if hasattr(vcard, 'url'):
                    for url in vcard.url_list:
                        url_type = url.type_param and url.type_param[0].lower()
                        if 'linkedin' in url.value.lower():
                            contact_data['linkedin'] = url.value
                        elif 'facebook' in url.value.lower():
                            contact_data['facebook'] = url.value
                        else:
                            contact_data['homepage'] = url.value
                
                contacts.append(contact_data)
                
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error parsing vCard: {str(e)}"
                )
        
        return contacts

    @staticmethod
    async def import_contacts(
        db: Session,
        file: UploadFile,
        user_id: int,
        preview_only: bool = False
    ) -> Dict:
        """Import contacts from a VCard file"""
        content = await file.read()
        vcard_content = content.decode('utf-8', errors='ignore')
        
        parsed_contacts = VCardHandler.parse_vcard(vcard_content)
        
        if preview_only:
            return {
                "preview": parsed_contacts,
                "total": len(parsed_contacts)
            }
        
        imported = []
        duplicates = []
        
        for contact_data in parsed_contacts:
            # Check for duplicates
            existing_contact = VCardHandler._find_duplicate(db, contact_data)
            
            if existing_contact:
                duplicates.append({
                    "imported": contact_data,
                    "existing": existing_contact
                })
                continue
            
            # Create new contact
            contact = ContactCreate(**contact_data)
            db_contact = Contact(**contact.dict(), created_by=user_id)
            db.add(db_contact)
            imported.append(contact_data)
        
        db.commit()
        
        return {
            "imported": imported,
            "duplicates": duplicates,
            "total_processed": len(parsed_contacts)
        }

    @staticmethod
    def _find_duplicate(db: Session, contact_data: Dict) -> Optional[Contact]:
        """Check for duplicate contacts based on email, phone, and name"""
        queries = []
        
        # Check emails
        for email_field in ['email', 'work_email', 'home_email', 'other_email']:
            if contact_data.get(email_field):
                queries.append(getattr(Contact, email_field) == contact_data[email_field])
        
        # Check phones
        for phone_field in ['mobile_phone', 'home_phone', 'work_phone', 'main_phone']:
            if contact_data.get(phone_field):
                queries.append(getattr(Contact, phone_field) == contact_data[phone_field])
        
        # Check name
        if contact_data.get('first_name') and contact_data.get('last_name'):
            queries.append(
                (Contact.first_name == contact_data['first_name']) &
                (Contact.last_name == contact_data['last_name'])
            )
        
        if not queries:
            return None
        
        return db.query(Contact).filter(or_(*queries)).first()

    @staticmethod
    def export_contacts(contacts: List[Contact]) -> str:
        """Export contacts to VCard format"""
        output = []
        
        for contact in contacts:
            vcard = vobject.vCard()
            
            # Add name
            vcard.add('n')
            vcard.n.value = vobject.vcard.Name(
                family=contact.last_name or '',
                given=contact.first_name or ''
            )
            
            # Add formatted name
            vcard.add('fn')
            vcard.fn.value = f"{contact.first_name} {contact.last_name}".strip()
            
            # Add organization
            if contact.company:
                vcard.add('org')
                vcard.org.value = [contact.company]
            