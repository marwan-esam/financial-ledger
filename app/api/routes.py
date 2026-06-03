from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import schemas
from app.db import database
from app.models import models
from app.core import security

# Inittialize the router
router = APIRouter()

# Endpoint to create a new account
@router.post("/accounts/")
def createAccount(account: schemas.AccountCreate, db: Session = Depends(database.get_db)):
  if account.initial_deposit < 0:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Initial deposit cannot be negative.")
  
  # Create the SQLAlchemy model instance
  new_account = models.Account(
    owner_name=account.owner_name,
    balance=account.initial_deposit
  )

  # Add and commit to the database
  db.add(new_account)
  db.commit()
  db.refresh(new_account)

  return new_account


@router.post("/transactions/")
def create_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.Account = Depends(security.get_current_user)
):
    # Security logic: You can only send your own money
    if transaction.sender_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to move funds from this account")

    # Basic logic checks before hitting the database
    if transaction.amount <= 0:
      raise HTTPException(status_code=400, detail="Amount must be greater than zero")
    
    if transaction.sender_id == transaction.receiver_id:
      raise HTTPException(status_code=400, detail="Cannot send money to yourself")
    
    # Fetch both accounts and explicitly lock them for this specific transaction
    sender = db.query(models.Account).filter(models.Account.id == transaction.sender_id).with_for_update().first()
    receiver = db.query(models.Account).filter(models.Account.id == transaction.receiver_id).with_for_update().first()

    # Verify both accounts actually exist
    if not sender:
      raise HTTPException(status_code=404, detail="Sender account not found")
    
    if not receiver:
      raise HTTPException(status_code=404, detail="Receiver account not found")
    
    # Perform the mathematical transfer
    sender.balance -= transaction.amount
    receiver.balance += transaction.amount

    # Create the receipt
    new_transaction = models.Transaction(
      amount=transaction.amount,
      sender_id=transaction.sender_id,
      receiver_id=transaction.receiver_id
    )

    db.add(new_transaction)

    # Commit everything at once. if any change above failed, none of this saves
    db.commit()
    db.refresh(new_transaction)

    return new_transaction



@router.get("/accounts/{account_id}/history", response_model=schemas.AccountHistoryResponse)
def get_account_history(
  account_id: int,
  db: Session = Depends(database.get_db),
  current_user: models.Account = Depends(security.get_current_user)
):
  # Security logic (IDOR Protection): You can only view your own history
  if account_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this account history")
  # Find the core account
  account = db.query(models.Account).filter(models.Account.id == account_id).first()
  if not account:
    raise HTTPException(status_code=404, detail="Account not found")
  
  # Find all transactions where this account was the sender
  sent_tx = db.query(models.Transaction).filter(models.Transaction.sender_id == account_id).all()

  # Find all transactions where this account was the receiver
  received_tx = db.query(models.Transaction).filter(models.Transaction.receiver_id == account_id).all()

  # Format the database rows into dictionaries for the JSON response
  sent_list = [{"transaction_id": tx.id, "amount": tx.amount, "to_account": tx.receiver_id, "time": tx.timestamp} for tx in sent_tx]
  received_list = [{"transaction_id": tx.id, "amount": tx.amount, "from_account": tx.sender_id, "time": tx.timestamp} for tx in received_tx]

  return {
    "account_id": account.id,
    "owner_name": account.owner_name,
    "current_balance": account.balance,
    "transactions_sent": sent_list,
    "transactions_received": received_list
  }


@router.post("/token")
def login_for_accecss_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
  # Search the database for the user requesting access
  user = db.query(models.Account).filter(models.Account.owner_name == form_data.username).first()

  if not user:
    raise HTTPException(status_code=404, detail="Account not found")
  

  # The account exists. Generate the acccess token
  access_token = security.create_access_token(data={"user_id": user.id})


  # Return it in the JSON structure that frontend applications expect
  return {"access_token": access_token, "token_type": "bearer"}

