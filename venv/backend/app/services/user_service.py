# services/user_service.py
from typing import Dict, Optional
from datetime import datetime
from bson import ObjectId
from app import mongo
from dataclasses import dataclass

@dataclass
class UserProfile:
    user_id: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    address: str
    avatar: str
    created_at: datetime
    last_login: datetime

    @classmethod
    def from_db(cls, user_data: Dict) -> 'UserProfile':
        return cls(
            user_id=str(user_data['_id']),
            first_name=user_data['firstName'],
            last_name=user_data['lastName'],
            email=user_data['email'],
            phone_number=user_data.get('phoneNumber', 'N/A'),
            address=user_data.get('address', 'N/A'),
            avatar=user_data.get('avatar', ''),
            created_at=user_data.get('createdAt'),
            last_login=user_data.get('lastLogin')
        )

class UserService:
    @staticmethod
    def get_profile(email: str) -> Optional[UserProfile]:
        user = mongo.db.users.find_one({"email": email})
        return UserProfile.from_db(user) if user else None

    @staticmethod
    def update_profile(email: str, update_data: Dict) -> bool:
        valid_fields = {'phoneNumber', 'address', 'avatar'}
        update_fields = {
            k: v for k, v in update_data.items() 
            if k in valid_fields and (k != 'avatar' or v.startswith("data:image"))
        }
        
        if not update_fields:
            return False
            
        result = mongo.db.users.update_one(
            {"email": email},
            {"$set": update_fields}
        )
        return result.modified_count > 0