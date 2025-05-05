from bson import ObjectId

def serialize_mongo_doc(doc):
    """
    Convierte recursivamente todos los ObjectId de un documento en strings.
    """
    if isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    elif isinstance(doc, dict):
        return {
            key: serialize_mongo_doc(value)
            for key, value in doc.items()
        }
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc
