from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import database

# Initialize the application
app = FastAPI()

# Dependency to open and close the database connection per request
def get_db():
  db = database.SessionLocal()
  try:
    yield db
  finally:
    db.close()


# Pydantic model for input validation
class AccountCreate(BaseModel):
  owner_name: str
  initial_deposit: float


# Endpoint to create a new account
@app.post("/accounts/")
def createAccount(account: AccountCreate, db: Session = Depends(get_db)):
  if account.initial_deposit < 0:
    raise HTTPException(status_code=400, detail="Initial deposit cannot be negative.")
  
  # Create the SQLAlchemy model instance
  new_account = database.Account(
    owner_name=account.owner_name,
    balance=account.initial_deposit
  )

  # Add and commit to the database
  db.add(new_account)
  db.commit()
  db.refresh(new_account)

  return new_account


class TransactionCreate(BaseModel):
  sender_id: int
  receiver_id: int
  amount: float


@app.post("/transactions/")
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
  # Basic logic checks before hitting the database
  if transaction.amount <= 0:
    raise HTTPException(status_code=400, detail="Amount must be greater than zero")
  
  if transaction.sender_id == transaction.receiver_id:
    raise HTTPException(status_code=400, detail="Cannot send money to yourself")
  
  # Fetch both accounts and explicitly lock them for this specific transaction
  sender = db.query(database.Account).filter(database.Account.id == transaction.sender_id).with_for_update().first()
  receiver = db.query(database.Account).filter(database.Account.id == transaction.receiver_id).with_for_update().first()

  # Verify both accounts actually exist
  if not sender:
    raise HTTPException(status_code=404, detail="Sender account not found")
  
  if not receiver:
    raise HTTPException(status_code=404, detail="Receiver account not found")
  
  # Perform the mathematical transfer
  sender.balance -= transaction.amount
  receiver.balance += transaction.amount

  # Create the receipt
  new_transaction = database.Transaction(
    amount=transaction.amount,
    sender_id=transaction.sender_id,
    receiver_id=transaction.receiver_id
  )

  db.add(new_transaction)

  # Commit everything at once. if any change above failed, none of this saves
  db.commit()
  db.refresh(new_transaction)

  return new_transaction


class AccountHistoryResponse(BaseModel):
  account_id: int
  owner_name: str
  current_balance: float
  transactions_sent: list[dict]
  transactions_received: list[dict]

@app.get("/accounts/{account_id}/history", response_model=AccountHistoryResponse)
def get_account_history(account_id: int, db: Session = Depends(get_db)):
  # Find the core account
  account = db.query(database.Account).filter(database.Account.id == account_id).first()
  if not account:
    raise HTTPException(status_code=404, detail="Account not found")
  
  # Find all transactions where this account was the sender
  sent_tx = db.query(database.Transaction).filter(database.Transaction.sender_id == account_id).all()

  # Find all transactions where this account was the receiver
  received_tx = db.query(database.Transaction).filter(database.Transaction.receiver_id == account_id).all()

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
