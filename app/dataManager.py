from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

Base = declarative_base()

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

Session = sessionmaker(bind=engine) 

TournamentArcher = Table('tournamentArcher', Base.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('tournamentId', Integer, ForeignKey('tournament.id', ondelete='CASCADE')),
                         Column('archerId', Integer, ForeignKey('archer.id', ondelete='CASCADE')))


class Tournament(Base):
    __tablename__ = 'tournament'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    rounds = Column(Integer)
    archers = relationship('Archer', secondary=TournamentArcher, back_populates='tournaments')

class Archer(Base):
    __tablename__ = 'archer'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    score = Column(Integer) 
    club = Column(String) 
    tournaments = relationship('Tournament', secondary=TournamentArcher, back_populates='archers')

class Club(Base):
    __tablename__ = 'club'
    name = Column(String, primary_key = True)
    firstColor = Column(String)
    secondColor = Column(String)
    logo = Column(String)


Base.metadata.create_all(engine)

# Tornament functions

def getTournamentCollection(name, id):
    session = Session() 

    tournamentQuery = session.query(Tournament)
    if id != None:
        tournamentQuery = tournamentQuery.filter(Tournament.id == id)
    if name != None:
        tournamentQuery = tournamentQuery.filter(Tournament.name == name)
    
    tournamentResults = tournamentQuery.all()
        

    tournamentList = []
    for tournament in tournamentResults:
        if tournament.rounds is not None:
            rounds = tournament.rounds
        else:
            rounds = 'Not specified'
        tournamentDict = {'name': tournament.name, 'id': tournament.id, 'rounds': rounds}
        tournamentList.append(tournamentDict)
    return tournamentList

def insertTournament(name):
    session = Session() 
    
    newTournament = Tournament(name=name)
    session.add(newTournament)
    session.commit()

def getTournament(id):
    session = Session()
    tournament = session.query(Tournament).get(id)
    if tournament != None:
        if tournament.rounds is not None:
            rounds = tournament.rounds
        else:
            rounds = 'Not specified'
        tournamentDict = {'name': tournament.name, 'id': tournament.id, 'rounds': rounds}
        return tournamentDict
    else:
        raise Exception("Tournament does not exist.")
    
def updateTournament(id, name, rounds):
    session = Session() 
    
    tournament = session.query(Tournament).get(id)

    if tournament == None:
        raise Exception("Tournament does not exist.")

    if name != None:
        tournament.name = name
    if rounds != None:
        rounds = int(rounds)
        tournament.rounds = rounds

    session.commit()

def deleteTournament(id):
    session = Session() 

    tournament = session.query(Tournament).get(id)

    if tournament == None:
        raise Exception("Tournament does not exist.")
    
    session.query(Tournament).filter(Tournament.id == id).delete()

    session.commit()

#Archer functions

def getArcherCollection(t_id, name, id, score, club):
    session = Session() 


    archerQuery = session.query(Archer).filter(Archer.tournaments.any(id = t_id))# filters by tournament

    if id != None:
        archerQuery = archerQuery.filter(Archer.id == id)
    if name != None:
        archerQuery = archerQuery.filter(Archer.name == name)
    if score != None:
        archerQuery = archerQuery.filter(Archer.score == score)
    if club != None:
        clubEndpoint = 'http://192.168.1.4:8000/api/clubs/' + str(club)
        archerQuery = archerQuery.filter(Archer.club == clubEndpoint)
    
    archerResults = archerQuery.all()

    archerList = []
    for archer in archerResults:
        archerDict = {'name': archer.name, 'id': archer.id, 'club': archer.club, 'score': archer.score}
        archerList.append(archerDict)
    return archerList

def insertArcher(t_id, name, club):
    session = Session() 

    club_ = session.query(Club).get(club)
    if club_ is None:
        raise Exception("Club doesn't exist.")
    clubEndpoint = 'http://192.168.1.4:8000/api/clubs/' + str(club)

    
    newArcher = Archer(name=name, club=clubEndpoint, score=0) # Score is initialized at 0.

    tournament = session.query(Tournament).get(t_id)
    newArcher.tournaments.append(tournament)
    session.add(newArcher)
    session.commit()

def getArcher(t_id, id):
    session = Session()
    archer = session.query(Archer).filter(Archer.tournaments.any(id = t_id), Archer.id == id).first()# filters by tournament
    if archer != None:
        archerDict = {'name': archer.name, 'id': archer.id, 'club': archer.club, 'score': archer.score}
        return archerDict
    else:
        raise Exception("Archer is not registered in this tournament.")
    
def updateArcher(t_id, id, name, addScore):
    session = Session() 
    
    archer = session.query(Archer).filter(Archer.tournaments.any(id = t_id), Archer.id == id).first()# filters by tournament

    if archer == None:
        raise Exception("Archer is not registered in this tournament.")

    if name != None:
        archer.name = name
    if addScore != None:
        addScore = int(addScore)
        archer.score += addScore

    session.commit()

def deleteArcher(t_id, id):
    session = Session() 

    archer = session.query(Archer).filter(Archer.tournaments.any(id = t_id), Archer.id == id).first()# filters by tournament

    if archer == None:
        raise Exception("Archer is not registered in this tournament.")
    
    archerToDelete = session.query(Archer).filter(Archer.id == id).first()
    session.delete(archerToDelete)

    session.commit()

# Club functions

def getClubCollection(name):
    session = Session() 

    clubQuery = session.query(Club)

    if name != None:
        clubQuery = clubQuery.filter(Club.name == name)
    
    clubResults = clubQuery.all()
        

    clubList = []
    for club in clubResults:
        clubDict = {'name': club.name, 'firstColor': club.firstColor, 'secondColor': club.secondColor, 'logo': club.logo}
        clubList.append(clubDict)
    return clubList


def getClub(name):
    session = Session()
    club = session.query(Club).get(name)
    if club != None:
        clubDict = {'name': club.name, 'firstColor': club.firstColor, 'secondColor': club.secondColor, 'logo': club.logo}
        return clubDict
    else:
        raise Exception("Club does not exist.")

# internal function
def insertClub(name, firstColor, secondColor, logo):
    session = Session() 

    newClub = Club(name=name, firstColor=firstColor, secondColor=secondColor, logo=logo)
    session.add(newClub)
    session.commit()

