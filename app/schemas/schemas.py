from pydantic import BaseModel


# Schema for creating a new account
class AccountCreate(BaseModel):
  owner_name: str
  initial_deposit: float

# Schema for creating a transaction
class TransactionCreate(BaseModel):
  sender_id: int
  receiver_id: int
  amount: float


# Schema for the account history response
class AccountHistoryResponse(BaseModel):
  account_id: int
  owner_name: str
  current_balance: float
  transactions_sent: list[dict]
  transactions_received: list[dict]