def find_by_email(db, email):  #사용자가 존재하는지 확인해줌
    return db.users.find_one({"email": email})

def create_user(db, user_data): #신규 사용자 넣고 id 리턴
    result = db.users.insert_one(user_data)
    return str(result.inserted_id)