from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr

# FastAPI app
app = FastAPI()


SQLALCHEMY_DATABASE_URL = "postgresql://admin:1234@localhost/demo1"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "User1"
    User_id = Column(Integer, primary_key=True)
    first_name = Column(String, index=True)
    email = Column(String, index=True)
    password = Column(String)
    phone = Column(String)

    profile = relationship("Profile", back_populates="User1")

class Profile(Base):
    __tablename__ = "profile"
    user_id = Column(Integer, ForeignKey("users.User_id"))
    profile_picture = Column(String)

    user = relationship("User1", back_populates="profile")


class UserRegistrationRequest(BaseModel):
    user_id : str
    first_name: str
    email: EmailStr
    password: str
    phone: str
    profile_picture: str



# creating user registration
@app.post("/register/")
def register_user(user_req: UserRegistrationRequest):
    db = SessionLocal()
    email_exist = db.query(User).filter_by(email=user_req.email).first()
    if email_exist:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        user_id=user_req.user_id,
        first_name=user_req.first_name,
        email=user_req.email,
        password=user_req.password,
        phone=user_req.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    #uploading the Profile images
    profile_query = Profile.__table__.insert().values(
        user_id=user_req.user_id,
        profile_picture=user_req.profile_picture,
    )
    db.add(profile_query)
    db.commit()
    db.refresh(profile_query)
    db.close()

    return {
        "id": user_req.user_id,
        "first_name": user_req.first_name,
        "email": user_req.email,
        "phone": user_req.phone,
        "profile_picture": profile_query,
    }

# Getting user details by user_id
@app.get("/user/{user_id}/", )
def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()
    db.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.user_id,
        "first_name": user.first_name,
        "email": user.email,
        "phone": user.phone,
    }
