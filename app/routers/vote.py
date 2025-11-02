from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from .. import models, oauth2
from .. import schemas
from .. database import get_db

router = APIRouter(
    prefix='/votes',
    tags=['Votes']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def vote(vote: schemas.Vote,
               db: Session = Depends(get_db),
               current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    
    if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'post with id {vote.post_id} does not exist')
            
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)

    vote_exists = vote_query.first()
    if vote.dir == 1:
        if vote_exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'user {current_user.id} has already voted on post {vote.post_id}')

        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()

        return {'message': 'Vote recorded successfully'}
    else:
        if not vote_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'vote does not exist')

        vote_query.delete(synchronize_session=False)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
