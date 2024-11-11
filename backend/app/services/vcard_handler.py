# backend/app/services/vcard_handler.py
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import vobject
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from ..models.models import Contact, Tag
from ..schemas.contact import ContactCreate

class VCardHandler:
    """Handler for VCard import and export operations."""
    
    @staticmethod
    def _parse_phone_numbers(vcard: vobject.vCard) -> Dict[str, str]:
        """Parse phone numbers from vCard."""
        phones = {}
        if hasattr(vcard, 'tel'):
            for tel in vcard.tel_list:
                tel_type = tel.type_param[0].lower() if tel.type_param else 'other'
                if tel_type == 'cell':
                    phones['mobile_phone'] = tel.value
                elif tel_type == 'home':
                    phones['home_phone'] = tel.value
                elif tel_type == 'work':
                    phones['work_phone'] = tel.value
                elif tel_type == 'main':
                    phones['main_phone'] = tel.value
                elif tel_type == 'iphone':
                    phones['iphone'] = tel.value
                else:
                    phones['other_phone'] = tel.value
        return phones

    @staticmethod
    def _parse_emails(vcard: vobject.vCard) -> Dict[str, str]:
        """Parse email addresses from vCard."""
        emails = {}
        if hasattr(vcard, 'email'):
            for email in vcard.email_list:
                email_type = email.type_param[0].lower() if email.type_param else 'other'
                if email_type == 'work':
                    emails['work_email'] = email.value
                elif email_type == 'home':
                    emails['home_email'] = email.value
                elif email_type == 'other':
                    emails['other_email'] = email.value
                else:
                    emails['email'] = email.value
        return emails

    @staticmethod
    def _parse_addresses(vcard: vobject.vCard) -> Dict[str, str]:
        """Parse addresses from vCard."""
        addresses = {}
        if hasattr(vcard, 'adr'):
            for adr in vcard.adr_list:
                adr_type = adr.type_param[0].lower() if adr.type_param else 'other'
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
                    addresses['home_address'] = address
                elif adr_type == 'work':
                    addresses['work_address'] = address
                else:
                    addresses['other_address'] = address
        return addresses

    @staticmethod
    def parse_vcard(vcard_content: str) -> List[Dict]:
        """Parse VCard content and return a list of contact dictionaries."""
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
                
                # Parse phones, emails, and addresses
                contact_data.update(VCardHandler._parse_phone_numbers(vcard))
                contact_data.update(VCardHandler._parse_emails(vcard))
                contact_data.update(VCardHandler._parse_addresses(vcard))
                
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
                        if len(photo_data) <= 5 * 1024 * 1024:  # 5MB limit
                            contact_data['photo'] = photo_data
                    except Exception:
                        pass
                
                # Handle notes
                if hasattr(vcard, 'note'):
                    contact_data['notes'] = vcard.note.value
                
                # Handle URLs
                if hasattr(vcard, 'url'):
                    for url in vcard.url_list:
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
    def _check_duplicate(db: Session, contact_data: Dict) -> Optional[Contact]:
        """Check for duplicate contacts."""
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
    async def import_contacts(
        db: Session,
        file: UploadFile,
        user_id: int,
        preview_only: bool = False
    ) -> Dict:
        """Import contacts from a VCard file."""
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
            existing_contact = VCardHandler._check_duplicate(db, contact_data)
            
            if existing_contact:
                duplicates.append({
                    "imported": contact_data,
                    "existing": existing_contact
                })
                continue
            
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

# backend/app/services/vcard_handler.py (continued...)

    @staticmethod
    def export_contacts(contacts: List[Contact]) -> str:
        """Export contacts to VCard format."""
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
            
            # Add phone numbers
            if contact.mobile_phone:
                tel = vcard.add('tel')
                tel.value = contact.mobile_phone
                tel.type_param = ['CELL']
                
            if contact.home_phone:
                tel = vcard.add('tel')
                tel.value = contact.home_phone
                tel.type_param = ['HOME']
                
            if contact.work_phone:
                tel = vcard.add('tel')
                tel.value = contact.work_phone
                tel.type_param = ['WORK']
                
            if contact.main_phone:
                tel = vcard.add('tel')
                tel.value = contact.main_phone
                tel.type_param = ['MAIN']
                
            if contact.other_phone:
                tel = vcard.add('tel')
                tel.value = contact.other_phone
                tel.type_param = ['OTHER']
            
            # Add email addresses
            if contact.email:
                email = vcard.add('email')
                email.value = contact.email
                email.type_param = ['HOME']
                
            if contact.work_email:
                email = vcard.add('email')
                email.value = contact.work_email
                email.type_param = ['WORK']
                
            if contact.other_email:
                email = vcard.add('email')
                email.value = contact.other_email
                email.type_param = ['OTHER']
            
            # Add addresses
            if contact.home_address:
                adr = vcard.add('adr')
                adr.value = vobject.vcard.Address(street=contact.home_address)
                adr.type_param = ['HOME']
                
            if contact.work_address:
                adr = vcard.add('adr')
                adr.value = vobject.vcard.Address(street=contact.work_address)
                adr.type_param = ['WORK']
            
            # Add birthday
            if contact.birthday:
                bday = vcard.add('bday')
                bday.value = contact.birthday.strftime("%Y-%m-%d")
            
            # Add photo
            if contact.photo:
                photo = vcard.add('photo')
                photo.value = contact.photo
                photo.encoding_param = 'b'
                photo.type_param = ['JPEG']
            
            # Add notes
            if contact.notes:
                note = vcard.add('note')
                note.value = contact.notes
            
            # Add URLs
            if contact.homepage:
                url = vcard.add('url')
                url.value = contact.homepage
                
            if contact.linkedin:
                url = vcard.add('url')
                url.value = contact.linkedin
                url.type_param = ['linkedin']
                
            if contact.facebook:
                url = vcard.add('url')
                url.value = contact.facebook
                url.type_param = ['facebook']
            
            # Add revision timestamp
            rev = vcard.add('rev')
            rev.value = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            
            output.append(vcard.serialize())
        
        return "\n".join(output)

    @staticmethod
    def merge_contacts(
        db: Session,
        source_id: int,
        target_id: int,
        user_id: int
    ) -> Contact:
        """
        Merge two contacts, keeping the target contact and deleting the source.
        """
        source = db.query(Contact).filter(Contact.id == source_id).first()
        target = db.query(Contact).filter(Contact.id == target_id).first()
        
        if not source or not target:
            raise HTTPException(
                status_code=404,
                detail="One or both contacts not found"
            )
        
        # Update empty fields in target with data from source
        for field in Contact.__table__.columns.keys():
            if field not in ['id', 'created_at', 'updated_at', 'created_by']:
                target_value = getattr(target, field)
                source_value = getattr(source, field)
                if target_value is None and source_value is not None:
                    setattr(target, field, source_value)
        
        # Merge tags
        for tag in source.tags:
            if tag not in target.tags:
                target.tags.append(tag)
        
        # Delete source contact
        db.delete(source)
        db.commit()
        db.refresh(target)
        
        return target

    @staticmethod
    def find_duplicates(db: Session, user_id: int) -> List[Tuple[Contact, Contact, float]]:
        """
        Find potential duplicate contacts based on similarity.
        Returns a list of tuples (contact1, contact2, similarity_score).
        """
        from difflib import SequenceMatcher
        
        contacts = db.query(Contact).filter(Contact.created_by == user_id).all()
        duplicates = []
        
        for i, contact1 in enumerate(contacts):
            for contact2 in contacts[i+1:]:
                score = 0
                total_fields = 0
                
                # Compare names
                if contact1.first_name and contact2.first_name:
                    score += SequenceMatcher(
                        None, 
                        contact1.first_name.lower(), 
                        contact2.first_name.lower()
                    ).ratio()
                    total_fields += 1
                
                if contact1.last_name and contact2.last_name:
                    score += SequenceMatcher(
                        None, 
                        contact1.last_name.lower(), 
                        contact2.last_name.lower()
                    ).ratio()
                    total_fields += 1
                
                # Compare emails
                if contact1.email and contact2.email:
                    score += float(contact1.email.lower() == contact2.email.lower())
                    total_fields += 1
                
                # Compare phones
                if contact1.mobile_phone and contact2.mobile_phone:
                    score += float(
                        contact1.mobile_phone.strip() == contact2.mobile_phone.strip()
                    )
                    total_fields += 1
                
                if total_fields > 0:
                    similarity = score / total_fields
                    if similarity > 0.8:  # Threshold for considering as duplicate
                        duplicates.append((contact1, contact2, similarity))
        
        return sorted(duplicates, key=lambda x: x[2], reverse=True)
