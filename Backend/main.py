from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas, database, auth

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to ["http://127.0.0.1:5500"] for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# Create tables
#models.Base.metadata.drop_all(bind=database.engine)  # drops all tables
models.Base.metadata.create_all(bind=database.engine)
print("Database recreated!")

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = auth.get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,  
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
    "msg": "User registered successfully",
    "user": schemas.UserOut.from_orm(new_user)
}

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/items", response_model=schemas.ItemOut)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    new_item = models.Item(
        name=item.name,
        price=item.price,
        owner_id=current_user.id  # <- link item to current user
        
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
 
    return schemas.ItemOut(
        id=new_item.id,
        name=new_item.name,
        price=new_item.price,
        owner_name=current_user.username,
        created_at=new_item.created_at
        
    )


@app.get("/items", response_model=list[schemas.ItemOut])
def get_items(db: Session = Depends(database.get_db)):
    items = db.query(models.Item).all()
    return [
        schemas.ItemOut(
            id=i.id,
            name=i.name,
            price=i.price,
            owner_name=i.owner.username if i.owner else "Unknown",
            created_at=i.created_at
        )
        for i in items
    ]

@app.put("/items/{item_id}")
def update_item(item_id: int, updated: schemas.ItemCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = updated.name
    item.price = updated.price
    db.commit()
    return {"msg": "Item updated"}

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"msg": "Item deleted"}
