from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from .. database import get_db

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


@router.get('/', response_model=List[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db),
                    current_user: models.User = Depends(
                        oauth2.get_current_user),
                    limit: int = 10, skip: int = 0, search: Optional[str] = ''):
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.user_id == current_user.id, models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return results


@router.get('/{id}', response_model=schemas.PostOut)
async def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id,
                                                                                                          models.Post.user_id == current_user.id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post con id: {id} no se encontro')

    return post


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_post(post: schemas.PostCreate,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):
    new_post = models.Post(user_id=current_user.id, **post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.put('/{id}', response_model=schemas.PostResponse)
async def update_post(id: int, post: schemas.PostCreate,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):
    query_post = db.query(models.Post).filter(
        models.Post.id == id, models.Post.user_id == current_user.id)

    if query_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post con id: {id} no se encontro')

    query_post.update(post.model_dump(exclude_none=True),
                      synchronize_session=False)
    db.commit()

    update_post = query_post.first()

    return update_post


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id,
                                        models.Post.user_id == current_user.id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post con id: {id} no se encontro')

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
