from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Account


# The Signing Key
SECRET_KEY = "this_is_a_much_longer_secret_password_that_is_safe_for_hs256"
# Hashing Algorithm
ALGORITHM = "HS256"
# Security Standard: Tokens should self-destruct after a set time
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
  to_encode = data.copy()
  # Add a strict expiration timestamp to the payload
  expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire})

  # Generate the token
  encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt


# Token extraction tool
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Verification Bouncer
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
  )


  try:
    # Decode the token to get the payload. if the token is expired or modified, this instantly fails
    payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])

    # Extract the public data
    user_id: int = payload.get("user_id")
    if user_id is None:
      raise credentials_exception
    
  except JWTError:
    raise credentials_exception
  
  # Fetch the actual user from PostgreSQL
  user = db.query(Account).filter(Account.id == user_id).first()
  if user is None:
    raise credentials_exception
  
  return user