from flask import Flask, jsonify, request, send_file, json, abort, redirect, Response, render_template, Blueprint
import dataManager, operator

main = Blueprint('main', __name__)

@main.route('/api')
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/docs')
def docs():
    return render_template('docs.html')

# Tournament request handlers

@main.route('/api/tournaments', methods=['GET', 'POST'])
def tournamentCollectionRequestHandler():
    if request.method == 'GET':
        
        name = request.args.get('name', None)
        id = request.args.get('id', None)

        tournaments = dataManager.getTournamentCollection(name, id)
        tournaments = sorted(tournaments, key=operator.itemgetter('id'))

        if len(tournaments) == 0:
            if name == None and id == None:
                abort(400, 'There are no registered tournaments.')
            else:
                abort(400, 'There are no matching results.')
        jsonData = json.dumps({"tournaments":tournaments}, sort_keys=False, indent=4) 
        return Response(jsonData, mimetype='application/json')
    
    elif request.method == 'POST':

        name = request.form['name']

        try:
            dataManager.insertTournament(name)
        except Exception as e:
            abort(400, e)
        return successMessage('Tournament created successfuly.')
    

@main.route('/api/tournaments/<id>', methods=['GET', 'PATCH', 'DELETE'])
def tournamentRequestHandler(id):
    if request.method == 'GET':
        try:
            tournament = dataManager.getTournament(id)
        except Exception as e:
            abort(404, e)
        jsonData = json.dumps(tournament, sort_keys=False, indent=4)  
        return Response(jsonData, mimetype='application/json')
    
    elif request.method == 'PATCH':
        name = request.form.get('name')
        rounds = request.form.get('rounds')
        if rounds is not None:
            validateInt(rounds, 'rounds')
        
        try:
            dataManager.updateTournament(id, name, rounds)
        except Exception as e:
            abort(400, e)
        return successMessage('Tournament updated successfuly.')
    
    elif request.method == 'DELETE':
        try:
            dataManager.deleteTournament(id)
        except Exception as e:
            abort(400, e)
        return successMessage('Tournament deleted successfuly.')
    
# Archer request handlers

@main.route('/api/tournaments/<t_id>/archers', methods=['GET', 'POST'])
def archerCollectionRequestHandler(t_id):
    if request.method == 'GET':
        
        name = request.args.get('name', None)
        id = request.args.get('id', None)
        score = request.args.get('score', None)
        club = request.args.get('club', None)

        archers = dataManager.getArcherCollection(t_id, name, id, score, club)
        archers = sorted(archers, key=operator.itemgetter('id'))

        if len(archers) == 0:
            if name == None and id == None and score == None and club == None:
                abort(400, 'There are no archers registered in this tournament.')
            else:
                abort(400, 'There are no matching results.')
        jsonData = json.dumps({"archers":archers}, sort_keys=False, indent=4) 
        return Response(jsonData, mimetype='application/json')
    
    elif request.method == 'POST':

        name = request.form['name']
        club = request.form['club']

        try:
            dataManager.insertArcher(t_id, name, club)
        except Exception as e:
            abort(400, e)
        return successMessage('Archer registered successfuly.')


@main.route('/api/tournaments/<t_id>/archers/<id>', methods=['GET', 'PATCH', 'DELETE'])
def archerRequestHandler(t_id, id):
    if request.method == 'GET':
        try:
            archer = dataManager.getArcher(t_id, id)
        except Exception as e:
            abort(404, e)
        jsonData = json.dumps(archer, sort_keys=False, indent=4)  
        return Response(jsonData, mimetype='application/json')
    
    elif request.method == 'PATCH':
        name = request.form.get('name')
        addScore = request.form.get('addScore')
        if addScore is not None:
            validateInt(addScore, 'addScore')
        
        try:
            dataManager.updateArcher(t_id, id, name, addScore)
        except Exception as e:
            abort(400, e)
        return successMessage('Archer updated successfuly.')
    
    elif request.method == 'DELETE':
        try:
            dataManager.deleteArcher(t_id, id)
        except Exception as e:
            abort(400, e)
        return successMessage('Archer deleted successfuly.')


# Club request handlers

@main.route('/api/clubs', methods=['GET'])
def clubCollectionRequestHandler():
    if request.method == 'GET':
        
        name = request.args.get('name', None)

        clubs = dataManager.getClubCollection(name)
        clubs = sorted(clubs, key=operator.itemgetter('name'))

        if len(clubs) == 0:
            if name == None:
                abort(400, 'There are no registered clubs.')
            else:
                abort(400, 'There are no matching results.')
        jsonData = json.dumps({"clubs":clubs}, sort_keys=False, indent=4) 
        return Response(jsonData, mimetype='application/json')

@main.route('/api/clubs/<name>', methods=['GET'])
def clubRequestHandler(name):
    if request.method == 'GET':
        try:
            club = dataManager.getClub(name)
        except Exception as e:
            abort(404, e)
        jsonData = json.dumps(club, sort_keys=False, indent=4)  
        return Response(jsonData, mimetype='application/json')
    

# Error and Success messages

@main.errorhandler(400)
def errorHandlerBadRequest(error):
    response = jsonify({'error':{'message': str(error.description),
                        'code' : 400}})
    response.content_type = "application/json"
    return response, 400

@main.errorhandler(404)
def errorHandlerNotFound(error):
    response = jsonify({'error':{'message': 'Resource not found.',
                        'code' : 404}})
    response.content_type = "application/json"
    return response, 404

@main.errorhandler(405)
def errorHandlerNotFound(error):
    response = jsonify({'error':{'message': 'Method not allowed.',
                        'code' : 405}})
    response.content_type = "application/json"
    return response, 405

def successMessage(message):
    response = jsonify({'message': message,
                        'code' : 200})
    response.content_type = "application/json"
    return response, 200

# Type validation

# Only validates numeric strings
def validateInt(integer, name):
    if type(integer) is str:
        if integer.isnumeric():
            integer = int(integer)
        else:
            e = Exception(f"{name} must be an Integer")
            abort(400, e)

