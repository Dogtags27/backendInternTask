from datetime import datetime
from flask import jsonify
from app.models import db, Contact
from sqlalchemy import or_, and_


def identify_user(data):
    email = data.get("email")
    phone = data.get("phoneNumber")

    if not email and not phone:
        return jsonify({"error": "Email or phoneNumber is required"}), 400

    matching_contacts = Contact.query.filter(
        or_(Contact.email == email, Contact.phoneNumber == phone)
    ).order_by(Contact.createdAt).all()
    
    if not matching_contacts:
        new_contact = Contact(
            email=email,
            phoneNumber=phone,
            linkPrecedence="primary",
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow()
        )
        db.session.add(new_contact)
        db.session.commit()

        return jsonify({
            "contact": {
                "primaryContactId": new_contact.id,
                "emails": [new_contact.email],
                "phoneNumbers": [new_contact.phoneNumber],
                "secondaryContactIds": []
            }
        }), 200
        
    contact_ids = set()
    primary_contacts = []
    all_related_contacts = set()

    for contact in matching_contacts:
        if contact.linkPrecedence == "primary":
            primary_contacts.append(contact)
            all_related_contacts.add(contact)
        elif contact.linkedId:
            root_primary = Contact.query.filter_by(id=contact.linkedId).first()
            primary_contacts.append(root_primary)
            all_related_contacts.add(contact)
            all_related_contacts.add(root_primary)

    primary_contacts = list({c.id: c for c in primary_contacts}.values())
    
    final_primary = sorted(primary_contacts, key=lambda c: c.createdAt)[0]
    final_primary_id = final_primary.id

    for other_primary in primary_contacts:
        if other_primary.id != final_primary_id:
            other_primary.linkPrecedence = "secondary"
            other_primary.linkedId = final_primary_id
            other_primary.updatedAt = datetime.utcnow()
            db.session.add(other_primary)

            secondaries = Contact.query.filter_by(linkedId=other_primary.id).all()
            for sec in secondaries:
                sec.linkedId = final_primary_id
                sec.updatedAt = datetime.utcnow()
                db.session.add(sec)

    db.session.commit()
    
    unified_contacts = Contact.query.filter(
        or_(
            Contact.id == final_primary_id,
            Contact.linkedId == final_primary_id
        )
    ).order_by(Contact.createdAt).all()

    emails = set()
    phones = set()
    secondary_ids = []
    exact_match_found = False

    for c in unified_contacts:
        if c.email == email and c.phoneNumber == phone:
            exact_match_found = True
        emails.add(c.email)
        phones.add(c.phoneNumber)
        if c.linkPrecedence == "secondary":
            secondary_ids.append(c.id)

    if not exact_match_found:
        new_contact = Contact(
            email=email,
            phoneNumber=phone,
            linkPrecedence="secondary",
            linkedId=final_primary_id,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow()
        )
        db.session.add(new_contact)
        db.session.commit()
        secondary_ids.append(new_contact.id)
        emails.add(email)
        phones.add(phone)

    response = {
        "contact": {
            "primaryContatctId": final_primary.id,
            "emails": list(emails),
            "phoneNumbers": list(phones),
            "secondaryContactIds": secondary_ids
        }
    }

    return jsonify(response), 200
