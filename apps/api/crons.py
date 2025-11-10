from fastapi import APIRouter
from fastapi_crons import Crons

cron_router = APIRouter()
crons = Crons(cron_router)
